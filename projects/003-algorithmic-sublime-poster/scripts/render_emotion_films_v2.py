"""V2 motion revision. Keeps every V1 film/source unchanged; no model call.

Reuses the two original ImageGen plates, improves figure scale/registration,
distance-driven gait, settling, contact shadows, rain occlusion and footstep sync.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from render_emotion_films import ASSETS as SOURCE, Scene, W, H, FPS, SECONDS, ease, pulse

OUT = SOURCE / "v2"
START, FINISH = -.06, .662
ACCEL_END, BRAKE_START, STOP = .8, 6.8, 8.2
VELOCITY = (FINISH - START) / (ACCEL_END / 2 + BRAKE_START - ACCEL_END + (STOP - BRAKE_START) / 2)


def arrival(t: float) -> tuple[float, float, float]:
    """Analytic integral of a trapezoid speed profile: x, speed, travelled px."""
    if t <= 0:
        distance, speed = 0., 0.
    elif t < ACCEL_END:
        distance = VELOCITY * t * t / (2 * ACCEL_END)
        speed = VELOCITY * t / ACCEL_END
    elif t < BRAKE_START:
        distance = VELOCITY * (t - ACCEL_END / 2)
        speed = VELOCITY
    elif t < STOP:
        age = t - BRAKE_START
        brake = STOP - BRAKE_START
        distance = VELOCITY * (BRAKE_START - ACCEL_END / 2 + age - age * age / (2 * brake))
        speed = VELOCITY * (1 - age / brake)
    else:
        distance, speed = FINISH - START, 0.
    return START + distance, speed, distance * W


class RevisedScene(Scene):
    def __init__(self) -> None:
        super().__init__()
        sheet = Image.open(SOURCE / "walker-sprites.png").convert("RGBA")
        self.registered = []
        # Register by upper-body alpha centroid instead of each crop's width.
        # This reduces side-to-side torso jumps when leg silhouettes change.
        for number in range(4):
            slot = sheet.crop((round(number * sheet.width / 4), 0, round((number + 1) * sheet.width / 4), sheet.height))
            box = slot.getchannel("A").getbbox()
            slot = slot.crop(box)
            alpha = np.asarray(slot.getchannel("A"), dtype=np.float32)
            head = alpha[:round(slot.height * .22)]
            anchor = float((head.sum(axis=0) * np.arange(slot.width)).sum() / head.sum())
            canvas = Image.new("RGBA", (360, 760))
            ratio = 720 / slot.height
            slot = slot.resize((round(slot.width * ratio), 720), Image.Resampling.LANCZOS)
            canvas.alpha_composite(slot, (round(180 - anchor * ratio), 40))
            self.registered.append(canvas)
        self.actor_cache = {}

    def sprite(self, phase: float, moving: float, newcomer: bool) -> Image.Image:
        height = 134 if newcomer else 144
        factor = max(0., min(1., moving))
        position = phase % 4
        index = int(position)
        fraction = position - index
        # Keep each pose through most of its interval, then interpolate the cut.
        mix = ease(.72, 1., fraction)
        if factor < .03:
            index, mix = 1, 0.
        key = (index, round(mix * 10), round(factor * 8), newcomer)
        if key in self.actor_cache:
            return self.actor_cache[key]
        image = Image.blend(self.registered[index], self.registered[(index + 1) % 4], mix)
        image = Image.blend(self.registered[1], image, factor)
        if newcomer:
            # An authored coat grade, not a newly generated identity.
            pixels = np.asarray(image, dtype=np.float32).copy()
            pixels[:, :, :3] *= np.array([1.24, 1.09, .91], dtype=np.float32)
            image = Image.fromarray(np.uint8(np.clip(pixels, 0, 255)))
        else:
            image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        image = image.resize((round(360 * height / 720), round(760 * height / 720)), Image.Resampling.LANCZOS)
        self.actor_cache[key] = image
        return image

    def frame(self, direction: str, t: float) -> Image.Image:
        response = ease(4, 10, t)
        if direction == "solitude":
            light = pulse(t, 6, .9) * .85
            beam_x = .12 + .98 * ease(4.4, 7.6, t)
            zoom, wind, travel = 1.075 - .070 * ease(0, 12, t), .4, .34 * t
        elif direction == "unease":
            light = sum(pulse(t, at, width) * amount for at, width, amount in [(3.8, .65, .55), (6.3, .5, .75), (8.2, .45, .85)])
            beam_x = .76 + .18 * math.sin(t * 1.7)
            zoom = 1.02 + .04 * min(t, 10) / 12 + (.055 if t >= 4 else 0) + (.065 if t >= 7.5 else 0)
            wind, travel = 1.15, .40 * t + .34 * t * t / 24
        else:
            light = .24 * ease(5.5, 9, t)
            beam_x = .72
            zoom, wind = 1.01 + .045 * ease(0, 9, t), .3
            # Continuous integral, unlike multiplying elapsed time by changing speed.
            travel = .36 * t - .13 * max(t - 4, 0) ** 2 / 16 if t < 12 else .36 * 12 - .52
        glow = np.exp(-((self.x - beam_x) / .20) ** 2 - ((self.y - .81) / .19) ** 2)
        delta = glow[:, :, None] * np.array([38, 32, 22], dtype=np.float32) * light
        image = Image.fromarray(np.uint8(np.clip(self.base + delta, 0, 255))).convert("RGBA")
        weather = Image.new("RGBA", (W, H))
        draw = ImageDraw.Draw(weather)
        for dx, dy, depth, length, alpha in self.drops:
            px = (dx - .035 * travel * wind + 1) % 1 * W
            py = (dy + travel * (.6 + depth)) % 1 * H
            cover = .18 if .64 * W < px < .87 * W and .32 * H < py < .62 * H and depth < .72 else 1.
            draw.line([(px, py), (px - (1.5 + depth * 3.5) * wind, py + 6 + length * 10)],
                      fill=(161, 188, 201, round((15 + 30 * alpha) * cover)), width=1)
        for rx, ry, cycle, offset in self.ripples:
            progress = ((t * (1.3 if direction == "unease" else .8) + offset * 3) % (1.4 + cycle)) / (1.4 + cycle)
            cx, cy, radius = rx * W, (.67 + ry * .31) * H, progress * (10 + ry * 20)
            draw.ellipse((cx - radius, cy - radius * .17, cx + radius, cy + radius * .17),
                         outline=(150, 180, 188, round((1 - progress) * (13 + ry * 10))), width=1)
        figures = Image.new("RGBA", (W, H))
        main_x = .705 - (.016 * ease(7, 9, t) if direction == "unease" else 0)
        retreat = direction == "unease" and 7 < t < 9
        people = [(main_x, .623, ease(7, 9, t) * 3 if retreat else 1., .50 * math.sin(math.pi * ease(7, 9, t)) if retreat else 0., False)]
        if direction == "hope":
            px, speed, distance = arrival(t)
            # One four-pose cycle per 78px travelled, and soften into the rest pose.
            people.append((px, .623, distance / 78 * 4, min(1., speed / VELOCITY * 1.35), True))
        shadows = Image.new("RGBA", (W, H))
        shadow_draw = ImageDraw.Draw(shadows)
        for px, gy, phase, moving, newcomer in people:
            sprite = self.sprite(phase, moving, newcomer)
            x, y = round(px * W - sprite.width / 2), round(gy * H - sprite.height)
            figures.alpha_composite(sprite, (x, y))
            shadow_draw.ellipse((px * W - 13, gy * H - 2, px * W + 13, gy * H + 5), fill=(0, 8, 12, 130))
        image = Image.alpha_composite(image, shadows.filter(ImageFilter.GaussianBlur(2)))
        ground = round(.623 * H)
        reflection = figures.crop((0, ground - 160, W, ground)).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        reflection = reflection.resize((W, 160), Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(1.8))
        pixels = np.asarray(reflection).copy()
        pixels[:, :, 3] = (pixels[:, :, 3] * (np.linspace(.32, .01, 160)[:, None])).astype(np.uint8)
        for row in range(160):
            pixels[row] = np.roll(pixels[row], round(math.sin(row * .27 + t * 1.4) * row / 70), axis=0)
        image.alpha_composite(Image.fromarray(pixels), (0, ground))
        image = Image.alpha_composite(image, figures)
        image = Image.alpha_composite(image, weather)
        signal = Image.new("RGBA", (W, H))
        draw = ImageDraw.Draw(signal)
        y = .631 * H
        if direction == "hope":
            progress = ease(8, 9.4, t)
            x0, x1 = FINISH * W, .705 * W
            draw.line([(x0, y), (x0 + (x1 - x0) * progress, y)], fill=(219, 183, 123, round(190 * progress)), width=1)
            for x in [x0, x1]:
                draw.rectangle((x - 1, y - 1, x + 1, y + 1), fill=(235, 201, 143, round(180 * progress)))
        else:
            for number in range(5):
                amount = max(0., math.sin(t * (1.2 if direction == "solitude" else 2.4) - number * .7))
                amount *= (1 - ease(8, 11, t)) if direction == "solitude" else .9
                jitter = math.sin(t * 4 + number) * 2 if direction == "unease" else 0
                x = main_x * W + number * 6 + jitter
                draw.line([(x, y), (x + 3, y)], fill=(160, 190, 202, round(110 * amount)), width=1)
        image = Image.alpha_composite(image, signal)
        aperture_w, aperture_h = W / zoom, H / zoom
        left, top = (W - aperture_w) * .65, (H - aperture_h) * .52
        if direction == "unease":
            left += math.sin(t * 9) * .55 * response
            top += math.sin(t * 13) * .30 * response
        return image.transform((W, H), Image.Transform.EXTENT,
                               (left, top, left + aperture_w, top + aperture_h), Image.Resampling.BICUBIC).convert("RGB")


def audio(path: Path, direction: str) -> dict:
    rate = 48000
    t = np.arange(rate * SECONDS, dtype=np.float32) / rate
    rng = np.random.default_rng(20261022)
    noise = rng.normal(0, 1, t.shape).astype(np.float32)
    soft = np.convolve(noise, np.ones(13, dtype=np.float32) / 13, mode="same")
    rain = .021 * noise + .043 * soft
    room = .013 * np.sin(math.tau * 55 * t) + .007 * np.sin(math.tau * 82.4069 * t)
    left, right = rain + room, np.roll(rain, 197) + room
    step_times = []

    def note(at: float, frequency: float, level: float, decay: float = .7) -> None:
        age = np.maximum(t - at, 0)
        envelope = (1 - np.exp(-age * 9)) * np.exp(-age * decay) * (t >= at)
        sound = level * envelope * (np.sin(math.tau * frequency * age) + .15 * np.sin(math.tau * frequency * 2 * age))
        left[:] += sound * .56
        right[:] += sound * .44

    if direction == "solitude":
        note(5.7, 261.6256, .070, .85)
    elif direction == "unease":
        beat = np.maximum(np.sin(math.tau * (.65 * t + .065 * t * t)), 0) ** 9
        tension = (.018 + .045 * t / 12) * beat * np.sin(math.tau * 47 * t)
        tension += .011 * t / 12 * (np.sin(math.tau * 146.83 * t) + np.sin(math.tau * 155.56 * t))
        left += tension
        right += np.roll(tension, 211)
    else:
        for at, hz in [(5.9, 261.6256), (7.1, 329.6276), (8.4, 391.9954)]:
            note(at, hz, .065, .38)
        times = np.arange(0, STOP, 1 / 240)
        distances = np.array([arrival(float(at))[2] for at in times])
        step_numbers = np.floor(distances / 39).astype(int)
        for index in np.flatnonzero(np.diff(step_numbers) > 0) + 1:
            at = float(times[index])
            px, speed, _ = arrival(at)
            if not .01 < px < .67 or speed < VELOCITY * .08:
                continue
            step_times.append(round(at, 4))
            age = np.maximum(t - at, 0)
            sound = .024 * soft * np.exp(-age * 34) * (t >= at)
            left += sound * .65
            right += sound
    fade = np.minimum(t / .35, 1) * np.minimum((SECONDS - t) / .65, 1)
    stereo = np.stack([left, right], axis=1) * fade[:, None]
    # Equal RMS target reduces overall loudness as an accidental comparison cue.
    stereo *= .032 / np.sqrt(np.mean(stereo ** 2))
    assert np.isfinite(stereo).all() and np.max(np.abs(stereo)) < .98
    with wave.open(str(path), "wb") as stream:
        stream.setnchannels(2); stream.setsampwidth(2); stream.setframerate(rate)
        stream.writeframes((stereo * 32767).astype("<i2").tobytes())
    return {"rms": round(float(np.sqrt(np.mean(stereo ** 2))), 4),
            "peak": round(float(np.abs(stereo).max()), 4), "footstep_times": step_times}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", default="_site/emotion-films-v2-work-20261022")
    args = parser.parse_args()
    work = Path(args.work_dir).resolve(); work.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        parser.error("FFmpeg is required")
    study = copy.deepcopy(json.loads((SOURCE / "study.json").read_text(encoding="utf-8")))
    study.update(version=2, edition="v2", title="候光 / 动态编排优化版", image_calls_this_revision=0,
                 fixed="与首版共享两张AI原素材、场景、三种故事、12秒时长与计算隐喻。",
                 limitation="二维四姿态素材动画，人物仍来自同一源图；调色与身高差不是独立角色生成。没有视频模型调用、真实三维运动或独立观众评测。",
                 improvements=["人物高度从约90px调整为144/134px，按头部对齐姿态，减少切帧横跳。",
                               "步态按走过的距离推进；末段减速并混入站姿，脚步声跟随相同距离标记。",
                               "补充接触阴影与衰减水面反射；亭内后层雨线减弱，前层雨保留。",
                               "保持原配色和情绪走向；三组原合成音频RMS统一为0.032，避免仅靠整体音量区分。"])
    for film in study["films"]:
        film["edition"] = "v2"
        if film["id"] == "hope":
            film["action"] = "第二人从左侧持续走来，6.8秒开始减速，8.2秒停在等候者旁；以身高与衣色区分。"
            film["weather"] = "同一雨夜，雨速平滑减缓，亭内后层雨线减少；没有突然放晴。"
            film["sound"] = "脚步按同一行走距离排布；5.9/7.1/8.4秒进入三个音符，结尾停留在协和。"
        if film["id"] == "unease":
            film["weather"] = "斜雨加速；人物7至9秒退让并落稳，光影间隔缩短。"
    (OUT / "study.json").write_text(json.dumps(study, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for film in study["films"]:
        direction = film["id"]
        text = (SOURCE / (direction + "-video-direction.txt")).read_text(encoding="utf-8")
        text += "\n【V2针对动作与时间的补充 / 视频模型尚未执行】\n" + "\n".join(study["improvements"]) + "\n"
        text += "本片人物与声音：" + film["action"] + film["sound"] + "\n"
        (OUT / (direction + "-video-direction.txt")).write_text(text, encoding="utf-8")
    scene = RevisedScene()
    metrics = {"kind": "authored-motion-parameters", "emotion_scores": False, "arrival_stop_seconds": STOP,
               "source_figure_height_v1": 91, "figure_heights_v2": [144, 134], "audio": {},
               "trajectory": [{"seconds": at, "x_ratio": arrival(at)[0], "speed_ratio_per_second": arrival(at)[1], "travel_px": arrival(at)[2]} for at in [0, .8, 2, 4, 6, 6.8, 8, 8.2, 10, 12]]}
    for film in study["films"]:
        direction = film["id"]
        sound = work / (direction + ".wav")
        metrics["audio"][direction] = audio(sound, direction)
        output = OUT / (direction + ".mp4")
        command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-threads", "2", "-f", "rawvideo", "-pix_fmt", "rgb24",
                   "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(sound), "-c:v", "libx264", "-threads", "2",
                   "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-t", str(SECONDS), "-movflags", "+faststart", str(output)]
        process = subprocess.Popen(command, stdin=subprocess.PIPE)
        try:
            for number in range(FPS * SECONDS):
                process.stdin.write(scene.frame(direction, number / FPS).tobytes())
                if number % (FPS * 4) == 0:
                    print(f"v2/{direction}: {number // FPS}/{SECONDS}s", flush=True)
        finally:
            process.stdin.close()
        if process.wait() != 0:
            raise RuntimeError("Encoding failed: " + direction)
        subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-ss", "8.8", "-i", str(output),
                        "-frames:v", "1", "-update", "1", "-q:v", "2", str(OUT / (direction + "-poster.jpg"))], check=True)
        print(direction + " encoded: " + str(output.stat().st_size), flush=True)
    (OUT / "motion-metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    records = [{"file": f.name, "bytes": f.stat().st_size, "sha256": hashlib.sha256(f.read_bytes()).hexdigest()}
               for f in sorted(OUT.iterdir()) if f.name != "manifest.json"]
    manifest = {"date": "2026-10-22", "edition": "v2", "image_calls_this_revision": 0, "video_model_calls": 0,
                "source_manifest": "../manifest.json", "renderer": "scripts/render_emotion_films_v2.py", "files": records}
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
