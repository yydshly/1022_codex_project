"""Preserve an actual completed Skill-directed video and package its review.

Never submits a generation request. The installed ChatArt CLI must finish first.
FFmpeg extracts review frames and validates media; the original MP4 is unchanged.
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
ASSETS = PROJECT / "assets" / "skill-film"
FRAMES = ((2, "frame-02.jpg"), (5, "frame-05.jpg"), (9, "frame-09.jpg"))


def read(name: str) -> dict:
    return json.loads((ASSETS / name).read_text(encoding="utf-8"))


def write(name: str, value: object) -> None:
    (ASSETS / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ingest(work: Path) -> None:
    brief, request = read("brief.json"), read("request.json")
    assert brief["authorization"]["confirmed"], "This new film needs its own approval"
    assert read_private(work / "attempt.json")["attempts"] == 1
    assert read_private(work / "execution-status.json")["exit_code"] == 0
    log = (work / "run.log").read_text(encoding="utf-8-sig")
    task = re.search(r"Task submitted\. taskId:\s*(\d+)", log)
    completed = re.search(r"status:\s*1\s+cost:\s*(\d+(?:\.\d+)?)\s+credits", log)
    url = re.search(r"video_url:(https?://\S+)", log)
    assert task and completed and url, "A completed actual provider result is required"
    prompt = (ASSETS / "prompt.txt").read_bytes().decode("utf-8")
    assert request["body"]["prompt"] == prompt and sha(ASSETS / "prompt.txt") == brief["prompt_sha256"]
    assert request["type"] == "i2v" and request["body"]["function_mode"] == "omni_reference"
    assert len(request["body"]["image_url"]) == len(brief["inputs"]) == 2
    for row in brief["inputs"]:
        assert sha((ASSETS / row["file"]).resolve(strict=True)) == row["sha256"]
    originals = list((work / "provider-original").glob("*.mp4"))
    assert len(originals) == 1, "Expected one provider-original video"
    source, output = originals[0], ASSETS / "original.mp4"
    if output.exists():
        assert output.read_bytes() == source.read_bytes(), "Do not replace a different original"
    else:
        shutil.copyfile(source, output)
    assert sha(output) == sha(source)
    raw = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(output)]))
    video = next(row for row in raw["streams"] if row["codec_type"] == "video")
    audios = [row for row in raw["streams"] if row["codec_type"] == "audio"]
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(output), "-f", "null", "-"], check=True)
    actual = {"file": output.name, "provider_filename": source.name, "width": video["width"], "height": video["height"],
        "duration_seconds": float(raw["format"]["duration"]), "video_codec": video["codec_name"], "fps": video["r_frame_rate"],
        "has_audio": bool(audios), "bytes": output.stat().st_size, "sha256": sha(output), "unmodified_provider_output": True,
        "audio": [{key: row.get(key) for key in ("codec_name", "sample_rate", "channels", "duration")} for row in audios]}
    for seconds, filename in FRAMES:
        assert seconds < actual["duration_seconds"]
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", str(seconds), "-i", str(output),
            "-frames:v", "1", "-update", "1", "-q:v", "2", str(ASSETS / filename)], check=True)
    cost = float(completed.group(1))
    provider = {"provider": "ChatArt", "task_id": task.group(1), "date": "2026-10-22", "status": "completed",
        "source_url": url.group(1), "estimated_cost_credits": brief["parameters"]["estimated_credits"], "actual_cost_credits": cost,
        "cost_difference_credits": cost - brief["parameters"]["estimated_credits"], "video_model_calls": 1,
        "record_source": "Exact completed output of the installed skill CLI; provider raw JSON was not requested; credentials excluded."}
    request["task_id"] = task.group(1)
    write("request.json", request)
    write("media.json", actual)
    write("provider-result.json", provider)
    brief.update(status="awaiting_review", generated=True, actual_result=actual, task_id=task.group(1), generation_attempts=1)
    write("brief.json", brief)
    write("skill-use.json", {"skill": brief["skill"], "read_files": brief["skill_snapshot"],
        "intent": brief["intent"], "fixed_style": brief["style"], "planned_stages": brief["planned_stages"],
        "roles": brief["inputs"], "interpretation": [
            "从安心档案提取可靠支撑与可停留的目标，转译为主动拉出座位、来者回应并实际入座。",
            "视频模板要求情绪起点、转机、结尾余味、动作、摄影连续性和声音；相应写入四段时间计划。",
            "旧视频案例只迁移邀请与回应的关系组织，未复用共伞情节；主机位改为可看清椅脚接触的固定中远景。",
            "本次选择写实影像规则，主体身份参考与光色材料参考分开，不将中性椅子图当首帧。"],
        "generation_tool": "ChatArt Skill / Seedance 2.0", "prompt_file": "prompt.txt", "request_file": "request.json",
        "skill_files_modified": False, "independent_evaluation": False})
    print(json.dumps({"task": task.group(1), "actual": actual, "actual_credits": cost}, ensure_ascii=False))


def read_private(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def finalize() -> None:
    brief, media, review, provider, request = read("brief.json"), read("media.json"), read("review.json"), read("provider-result.json"), read("request.json")
    assert brief["generated"] and brief["authorization"]["confirmed"] and provider["status"] == "completed"
    assert review["observations"] and review["deviations"] and len(review["frames"]) == 3
    assert request["body"]["prompt"] == (ASSETS / "prompt.txt").read_bytes().decode("utf-8")
    assert media["sha256"] == sha(ASSETS / media["file"])
    for row, (seconds, filename) in zip(review["frames"], FRAMES):
        assert row["file"] == filename and row["seconds"] == seconds and (ASSETS / filename).is_file()
    brief["status"] = "completed"
    write("brief.json", brief)
    study = {"version": 1, "id": brief["id"], "title": brief["title"], "date": brief["date"], "status": "completed", "generated": True,
        "actual": media, "request": brief["parameters"], "task_id": provider["task_id"], "actual_cost_credits": provider["actual_cost_credits"],
        "inputs": brief["inputs"], "skill": brief["skill"], "skill_snapshot": brief["skill_snapshot"], "intent": brief["intent"],
        "style": brief["style"], "planned_stages": brief["planned_stages"], "frames": review["frames"],
        "observations": review["observations"], "deviations": review["deviations"], "review_method": review["method"],
        "audio_reviewed": review["audio_reviewed"], "independent_audience_evaluation": False,
        "production": {"video_model_calls": 1, "type": "i2v", "input_mode": "omni_reference", "image_inputs": brief["inputs"],
            "code_animation_used": False, "original_video_modified": False, "extra_music_or_voice_added": False,
            "prompt_file": "prompt.txt", "exact_request_file": "request.json", "skill_evidence_file": "skill-use.json"}}
    write("study.json", study)
    names = ["brief.json", "prompt.txt", "request.json", "provider-result.json", "media.json", "skill-use.json", "review.json", "study.json", "original.mp4"] + [f for _, f in FRAMES]
    write("manifest.json", {"date": brief["date"], "provider": "ChatArt", "requested_model": brief["parameters"]["model"],
        "task_id": provider["task_id"], "generation_calls": 1, "actual_cost_credits": provider["actual_cost_credits"],
        "source_url": provider["source_url"], "original_video_sha256": media["sha256"], "input_roles": brief["inputs"],
        "model_weights_version": None, "seed": None, "original_video_modified": False,
        "files": [{"file": n, "bytes": (ASSETS / n).stat().st_size, "sha256": sha(ASSETS / n)} for n in names]})
    print("Saved 13 actual media, prompt, Skill evidence and review assets.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ingest", type=Path, help="Private official-CLI run folder, after completed download")
    parser.add_argument("--finalize", action="store_true", help="After actual review.json has been written")
    args = parser.parse_args()
    if args.ingest:
        ingest(args.ingest.resolve(strict=True))
    elif args.finalize:
        finalize()
    else:
        parser.error("Use --ingest or --finalize")
