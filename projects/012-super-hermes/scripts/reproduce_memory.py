"""Measure a known unbounded-cache defect; does not invoke Hermes or an LLM."""
import argparse
from datetime import datetime, timezone
import gc
from hashlib import sha256
import importlib.util
import inspect
import json
from pathlib import Path
import platform
import subprocess
import sys
import tracemalloc

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "web/assets/memory-demo/cache_fixture.py"
CHECKPOINTS = (0, 200, 400, 600, 800)


def worker(mode):
    spec = importlib.util.spec_from_file_location("cache_fixture", FIXTURE)
    fixture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)
    cache = fixture.BoundedCache(32) if mode == "bounded" else fixture.UnboundedCache()
    gc.collect()
    tracemalloc.start(1)
    baseline = tracemalloc.take_snapshot()
    baseline_current, _ = tracemalloc.get_traced_memory()
    samples = []
    completed = 0
    for requests in CHECKPOINTS:
        while completed < requests:
            cache.get("same-request" if mode == "repeated" else f"request-{completed}")
            completed += 1
        # Reachable cached values survive full collection. No response is held by this loop.
        gc.collect()
        current, peak = tracemalloc.get_traced_memory()
        samples.append({"requests": requests, "entries": len(cache.cache),
                        "traced_growth_bytes": current - baseline_current,
                        "traced_peak_bytes": peak})
    final_snapshot = tracemalloc.take_snapshot()
    changes = final_snapshot.compare_to(baseline, "lineno")
    source_lines = FIXTURE.read_text(encoding="utf-8").splitlines()
    allocations = []
    for stat in changes:
        frame = stat.traceback[0]
        if Path(frame.filename).resolve() == FIXTURE.resolve() and stat.size_diff > 0:
            allocations.append({"file": "cache_fixture.py", "line": frame.lineno,
                                "source": source_lines[frame.lineno - 1].strip(),
                                "growth_bytes": stat.size_diff, "blocks": stat.count_diff})
    # Clear the retaining reference, then check the same traced allocation line.
    cache.clear()
    gc.collect()
    cleared_snapshot = tracemalloc.take_snapshot()
    cleared_changes = cleared_snapshot.compare_to(baseline, "lineno")
    cleared_growth = sum(stat.size_diff for stat in cleared_changes
                         if Path(stat.traceback[0].filename).resolve() == FIXTURE.resolve())
    tracemalloc.stop()
    allocation_line = inspect.getsourcelines(fixture.make_response)[1] + 1
    payload_after_clear = sum(stat.size_diff for stat in cleared_changes
                              if Path(stat.traceback[0].filename).resolve() == FIXTURE.resolve()
                              and stat.traceback[0].lineno == allocation_line)
    payload_growth = next(row["growth_bytes"] for row in allocations if row["line"] == allocation_line)
    expected_entries = {"unbounded": 800, "bounded": 32, "repeated": 1}[mode]
    assert samples[-1]["entries"] == expected_entries
    assert payload_growth >= expected_entries * fixture.PAYLOAD_BYTES
    assert abs(cleared_growth) < fixture.PAYLOAD_BYTES
    assert payload_after_clear == 0
    return {"mode": mode, "samples": samples, "allocation_growth": allocations,
            "payload_allocation_line": allocation_line,
            "fixture_growth_bytes_after_clear": cleared_growth,
            "payload_growth_bytes_after_clear": payload_after_clear,
            "payload_bytes": fixture.PAYLOAD_BYTES,
            "capacity": 32 if mode == "bounded" else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", choices=("unbounded", "bounded", "repeated"))
    args = parser.parse_args()
    if args.worker:
        print(json.dumps(worker(args.worker)))
        return
    cases = []
    for mode in ("unbounded", "bounded", "repeated"):
        result = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--worker", mode],
                                check=True, capture_output=True, text=True, encoding="utf-8")
        cases.append(json.loads(result.stdout))
    report = {"recorded_at": datetime.now(timezone.utc).isoformat(),
              "python": sys.version, "platform": platform.platform(),
              "origin": "Research-built known-defect fixture; not upstream code or a Hermes/LLM evaluation.",
              "method": "Separate subprocesses; 800 unique keys for unbounded/bounded comparison, 800 repetitions of one key as a control; 64 KiB payload; gc.collect at each checkpoint; tracemalloc snapshot differences.",
              "metric": "Incremental Python-traced live allocations, not process RSS or native heap.",
              "fixture": "assets/memory-demo/cache_fixture.py",
              "fixture_sha256": sha256(FIXTURE.read_bytes()).hexdigest(),
              "upstream_method_reference": "skills/prism-scan/references/optimize.md",
              "model_invoked": False, "cases": cases[:2], "controls": {"repeated_key": cases[2]}}
    body = json.dumps(report, ensure_ascii=False, indent=2)
    (ROOT / "web/assets/memory-reproduction.json").write_text(body + "\n", encoding="utf-8")
    (ROOT / "web/memory-data.js").write_text("window.MEMORY_CASE = " + body + ";\n", encoding="utf-8")
    for case in cases:
        sample = case["samples"][-1]
        print(f"{case['mode']}: {sample['entries']} entries, {sample['traced_growth_bytes'] / 1048576:.3f} MiB; "
              f"fixture growth after clear: {case['fixture_growth_bytes_after_clear']} bytes")
    print("PASS: known retention reproduced and bounded-cache alternative measured. No model was invoked.")


if __name__ == "__main__":
    main()
