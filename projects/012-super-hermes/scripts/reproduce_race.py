"""Reproduce the upstream race with a controlled thread interleaving, offline."""
import ast
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import platform
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / "SOURCE.json").read_text(encoding="utf-8"))
    entry = next(x for x in manifest["files"] if x["upstream_path"] == "examples/circuit_breaker.py")
    content = (ROOT / entry["local_path"]).read_bytes()
    assert sha256(content).hexdigest() == entry["sha256"], "Upstream snapshot changed"
    source = content.decode("utf-8-sig")
    tree = ast.parse(source)
    assert all(isinstance(n, (ast.Import, ast.ImportFrom, ast.ClassDef)) or
               (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str))
               for n in tree.body), "Unexpected top-level execution in example"
    namespace = {"__name__": "upstream_example"}
    exec(compile(tree, "<pinned-upstream-example>", "exec"), namespace)
    state = namespace["State"]
    breaker = namespace["CircuitBreaker"](failure_threshold=1, recovery_timeout=30)
    breaker._state = state.OPEN
    breaker._last_failure_time = time.time() - 60
    line = next(i for i, text in enumerate(source.splitlines(), 1) if "self._state = State.HALF_OPEN" in text)
    ready, resume = threading.Event(), threading.Event()
    result = {}

    def trace(frame, event, arg):
        if frame.f_code is type(breaker).state.fget.__code__ and event == "line" and frame.f_lineno == line:
            ready.set()
            if not resume.wait(5):
                raise TimeoutError("Transition was not resumed")
        return trace

    def reader():
        sys.settrace(trace)
        try:
            result["stale_reader_observed_state"] = breaker.state.value
        except BaseException as exc:
            result["worker_error"] = repr(exc)
        finally:
            sys.settrace(None)

    worker = threading.Thread(target=reader, daemon=True)
    worker.start()
    try:
        assert ready.wait(5), "Reader never reached the transition"
        breaker._on_failure()
        result["state_after_new_failure"] = breaker._state.value
        result["new_failure_age_seconds"] = round(time.time() - breaker._last_failure_time, 6)
    finally:
        resume.set()
    worker.join(5)
    assert not worker.is_alive(), "Reader did not finish"
    assert "worker_error" not in result, result
    assert result["state_after_new_failure"] == "open", result
    assert result["stale_reader_observed_state"] == "half_open", result
    assert result["new_failure_age_seconds"] < breaker.recovery_timeout, result
    result.update({"race_reproduced": True, "configured_cooldown_seconds": breaker.recovery_timeout,
                   "transition_line": line, "upstream_revision": manifest["revision"],
                   "method": "sys.settrace pauses reader after expired-time check and before state write; main thread records a new failure; reader resumes.",
                   "scope": "A controlled interleaving demonstrates the race; no LLM or Hermes session was executed.",
                   "python": platform.python_version(), "platform": platform.platform(),
                   "executed_at": datetime.now().astimezone().isoformat()})
    output = ROOT / "web/assets/race-reproduction.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
