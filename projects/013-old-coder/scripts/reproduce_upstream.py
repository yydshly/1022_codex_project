"""Run explicitly selected upstream checks on Windows without altering sources.

This is a partial reproduction, never a claim that gauntlet.sh completed.
"""
from __future__ import annotations
import json
from pathlib import Path
import platform
import subprocess
import sys
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "upstream/demo-rate-limiter"
PYTHON = ROOT / (".venv/Scripts/python.exe" if sys.platform == "win32" else ".venv/bin/python")
commands = [
    ("tests-and-coverage", [str(PYTHON), "-m", "pytest", "tests/test_ratelimiter.py", "tests/test_properties.py", "-q", "--cov=ratelimiter", "--cov-branch", "--cov-report=term-missing", "--cov-fail-under=100", "--randomly-seed=42"]),
    ("types", [str(PYTHON), "-m", "mypy", "src", "tests", "examples", "tools"]),
    ("lint", [str(PYTHON), "-m", "ruff", "check", "."]),
    ("format", [str(PYTHON), "-m", "ruff", "format", "--check", "."]),
    ("real-execution", [str(PYTHON), "examples/demo.py"]),
    ("dependency-audit", [str(PYTHON), "-m", "pip_audit", "-r", "requirements-dev.txt"]),
]


def main() -> None:
    results = []
    for name, command in commands:
        print(f"Running {name}", flush=True)
        try:
            process = subprocess.run(command, cwd=DEMO, capture_output=True, text=True,
                                     encoding="utf-8", errors="replace", timeout=120)
            result = {"name": name, "command": " ".join(command).replace(str(ROOT), "<project>"),
                      "returncode": process.returncode, "status": "pass" if process.returncode == 0 else "fail",
                      "stdout": process.stdout.replace(str(ROOT), "<project>"),
                      "stderr": process.stderr.replace(str(ROOT), "<project>")}
        except subprocess.TimeoutExpired:
            result = {"name": name, "status": "unverified", "reason": "command exceeded 120 seconds"}
        results.append(result)
        print(f"{name}: {result['status']}", flush=True)
    freeze = subprocess.run([str(PYTHON), "-m", "pip", "freeze"], capture_output=True, text=True, check=True).stdout
    (ROOT / "results/environment-freeze.txt").write_text(freeze.replace(str(ROOT), "<project>"), encoding="utf-8")
    report = {"kind": "partial upstream reproduction", "date": datetime.now(timezone(timedelta(hours=8))).isoformat(),
              "upstreamCommit": "a0eb529d393a1cb3ccc564e32b2104e7e75c7a29", "platform": platform.platform(),
              "python": subprocess.check_output([str(PYTHON), "--version"], text=True).strip(),
              "results": results, "notRun": [
                  "Original POSIX gauntlet.sh and its orchestration/source-binding/shell checker self-tests",
                  "Original POSIX-dependent mutation runner (hardcodes .venv/bin/pytest)",
                  "Nine source-state tests requiring POSIX script execution and source checkout semantics",
                  "Ten repeated randomized suite runs", "Independent fresh-context verifier protocol"],
              "scope": "Unmodified upstream application and property tests; no claims about the original complete gauntlet."}
    target = ROOT / "results/upstream-reproduction.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "web/assets/upstream-reproduction.json").write_bytes(target.read_bytes())
    print(f"Saved {len(results)} results. Full gauntlet not run.")


if __name__ == "__main__":
    main()
