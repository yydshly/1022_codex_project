"""Package an actually completed ChatArt video, its exact request and human review.

Does not submit tasks, call a video API or synthesize/alter the original video.
The provider's CLI must have completed first. FFmpeg only extracts review frames.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

PROJECT = Path(__file__).resolve().parents[1]
ASSETS = PROJECT / "assets" / "ai-film"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(name: str, data: dict) -> None:
    (ASSETS / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", required=True)
    args = parser.parse_args()
    log = Path(args.log).read_text(encoding="utf-8-sig")
    plan, request, review = read(ASSETS / "plan.json"), read(ASSETS / "request.json"), read(ASSETS / "review.json")
    assert plan["authorization"]["confirmed"] and plan["generation_attempts"] == 1
    task = re.search(r"Task submitted\. taskId:\s*(\d+)", log)
    result = re.search(r"status:\s*1\s+cost:\s*([^\s]+)\s+credits", log)
    url = re.search(r"video_url:(https?://\S+)", log)
    if not task or not result or not url or task.group(1) != request["task_id"]:
        parser.error("A completed provider task and final video URL are required")
    assert request["body"]["prompt"] == (ASSETS / "shared-space-prompt.txt").read_text(encoding="utf-8")
    assert review["observations"] and review["deviations"] and len(review["frames"]) == 3
    sources = list((ASSETS / "provider-original").glob("*.mp4"))
    if len(sources) != 1:
        parser.error("Expected exactly one original provider MP4")
    source = sources[0]
    info = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(source)]))
    stream = next(row for row in info["streams"] if row["codec_type"] == "video")
    audios = [row for row in info["streams"] if row["codec_type"] == "audio"]
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(source), "-f", "null", "-"], check=True)
    output = ASSETS / "shared-space-original.mp4"
    shutil.copyfile(source, output)
    original_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    assert hashlib.sha256(output.read_bytes()).hexdigest() == original_hash
    actual = {"file": output.name, "provider_filename": source.name, "width": stream["width"], "height": stream["height"],
              "duration_seconds": float(info["format"]["duration"]), "video_codec": stream["codec_name"],
              "fps": stream["r_frame_rate"], "has_audio": bool(audios), "sha256": original_hash,
              "bytes": output.stat().st_size, "unmodified_provider_output": True,
              "audio": [{key: row.get(key) for key in ["codec_name", "sample_rate", "channels", "duration"]} for row in audios]}
    for frame in review["frames"]:
        assert 0 <= frame["seconds"] < actual["duration_seconds"]
        assert Path(frame["file"]).name == frame["file"]
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", str(frame["seconds"]),
                        "-i", str(output), "-frames:v", "1", "-update", "1", "-q:v", "2", str(ASSETS / frame["file"])], check=True)
    cost = float(result.group(1)) if result.group(1).replace(".", "", 1).isdigit() else None
    provider = {"provider": "ChatArt", "task_id": task.group(1), "status": "completed", "source_url": url.group(1),
                "estimated_cost_credits": plan["parameters"]["estimated_credits"],
                "actual_cost_credits": cost, "cost_difference_credits": cost - plan["parameters"]["estimated_credits"] if cost is not None else None,
                "date": "2026-10-22", "video_model_calls": 1,
                "note": "Recorded from the skill CLI's completed result; credentials are excluded."}
    write("provider-result.json", provider)
    plan["status"], plan["generated"], plan["actual_result"] = "completed", True, actual
    plan["observations"] = review["observations"]
    write("plan.json", plan)
    study = {"version": 1, "id": plan["id"], "title": plan["title"], "status": "completed", "generated": True,
             "date": "2026-10-22", "request": plan["parameters"], "task_id": task.group(1), "actual": actual,
             "actual_cost_credits": cost, "intent": plan["intent"], "visual_language": plan["visual_language"],
             "planned_stages": plan["planned_stages"], "frames": review["frames"], "observations": review["observations"],
             "deviations": review["deviations"], "review_method": review["method"], "independent_audience_evaluation": False,
             "production": {"video_model_calls": 1, "image_inputs": [], "code_animation_used": False,
                            "extra_music_or_voice_added": False, "original_video_modified": False,
                            "prompt_file": "shared-space-prompt.txt", "exact_request_file": "request.json"}}
    write("study.json", study)
    names = ["shared-space-prompt.txt", "request.json", "plan.json", "provider-result.json", "review.json", "study.json", output.name] + [f["file"] for f in review["frames"]]
    records = [{"file": name, "bytes": (ASSETS / name).stat().st_size,
                "sha256": hashlib.sha256((ASSETS / name).read_bytes()).hexdigest()} for name in names]
    write("manifest.json", {"date": "2026-10-22", "provider": "ChatArt", "requested_model": "Seedance 2.0",
                             "task_id": task.group(1), "generation_calls": 1, "source_url": url.group(1),
                             "actual_cost_credits": cost, "original_file_sha256": original_hash, "files": records,
                             "model_weights_version": None, "seed": None})
    print(json.dumps({"task": task.group(1), "actual": actual, "cost": cost, "packaged_files": len(records) + 1}, ensure_ascii=False))


if __name__ == "__main__":
    main()
