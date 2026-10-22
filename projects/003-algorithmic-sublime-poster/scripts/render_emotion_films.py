"""Three authored motion studies from one AI plate; no video model is called.

Python 3.10+, Pillow, NumPy, FFmpeg. Writes H.264/AAC with original synthesized
sound. People use an AI-generated four-pose transparent sprite sheet; its playback,
rain, ripples, signal paths and camera motion are authored in code.
The AI background stays unmodified as a separate source file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PROJECT = Path(__file__).resolve().parents[1]
ASSETS = PROJECT / "assets" / "motion-emotions"
W, H, FPS, SECONDS = 1280, 720, 24, 12
TAU = math.tau

FILMS = [
    {
        "id": "solitude", "title": "孤独 · 没有停下的光", "label": "01 / SOLITUDE",
        "goal": "让人感到等待没有得到回应；避免把孤独等同于悲伤滤镜。",
        "arc": "等候 → 一次可能的回应 → 继续独处",
        "camera": "12秒连续慢拉远；人物越发小，最后3秒继续停留。",
        "action": "一个人始终独处。6秒附近的路面光经过后离开；没有第二个人到来。",
        "weather": "细雨匀速落下，稀疏水波重复，空间不被填满。",
        "sound": "远雨和低声底噪；一次稀疏音符，没有和声解决。",
        "signal": "脚边短线偶尔亮起，但没有连接对象，最后自行熄灭。",
        "avoid": "不要加悲伤字幕、哭脸、密集粒子或煽情旋律。",
        "check": "遮住标题后，是否读到等待落空？还是只像安静的海边？",
        "stages": [
            {"start": 0, "end": 4, "name": "等待", "detail": "人物静候；慢拉远；只有雨声和空间底噪。"},
            {"start": 4, "end": 8, "name": "光经过", "detail": "6秒左右路面亮光经过又离开，人物没有获得回应。"},
            {"start": 8, "end": 12, "name": "继续独处", "detail": "光退去，短线熄灭；镜头继续远离人物并停留。"},
        ],
    },
    {
        "id": "unease", "title": "不安 · 越来越近的动静", "label": "02 / UNEASE",
        "goal": "让人感到未知动静逐步逼近；避免直接演成恐怖或频闪。",
        "arc": "察觉 → 干扰加密 → 未解决的悬停",
        "camera": "先缓推；4秒、7.5秒两次硬切到更近画幅，末段极轻位移。",
        "action": "同一个人仍独处，在7至9秒退半步；光影经过的间隔缩短。",
        "weather": "斜雨加速，风向与剪影衣摆轻摆；不靠暴雨遮住主体。",
        "sound": "逐渐加快的低频脉冲、低强度不协和音；末段留悬念。",
        "signal": "同一区域的短线出现分段和错位，不增加成满屏HUD。",
        "avoid": "不要惊吓闪白、血腥、灾难、警报字幕或震耳声音。",
        "check": "是否能察觉逼近和退让？不要把镜头变大直接当成恐惧命中。",
        "stages": [
            {"start": 0, "end": 4, "name": "察觉", "detail": "小幅推进；低频脉冲开始，人物仍站定。"},
            {"start": 4, "end": 8, "name": "干扰加密", "detail": "两次画幅切换，雨速提高，光影间隔缩短。"},
            {"start": 8, "end": 12, "name": "未解决", "detail": "人物退半步，脉冲加密；结尾保留不协和与空间压力。"},
        ],
    },
    {
        "id": "hope", "title": "希望 · 等到了一个同行者", "label": "03 / HOPE",
        "goal": "让人感到等待有了回应，仍然克制；避免只把希望翻译成金色。",
        "arc": "独处 → 有人走近 → 共同停留",
        "camera": "连续缓推，始终保留空间；8秒后镜头运动逐渐停住。",
        "action": "第二个人从左侧走来，在8秒附近与等候者并肩站定，人物距离缩短。",
        "weather": "同样的雨夜；后半雨速减缓，水波仍在，不突然变成晴天。",
        "sound": "脚步与雨声之后，6秒起三音逐次进入；9秒形成柔和协和，留余音。",
        "signal": "一条稀疏短线从两人脚下逐渐接通，作为回应的隐喻。",
        "avoid": "不要胜利式高潮、突然日出、爱心图标或直接写希望。",
        "check": "是否因为人物关系发生变化而感到回应？还是只被和弦提示？",
        "stages": [
            {"start": 0, "end": 4, "name": "独处", "detail": "一人等候；第二个剪影从远侧缓缓走入。"},
            {"start": 4, "end": 8, "name": "走近", "detail": "人物逐渐靠近；脚步和三个音符依次出现。"},
            {"start": 8, "end": 12, "name": "共同停留", "detail": "两人并肩，脚边短线接通；和弦与镜头一起稳定。"},
        ],
    },
]


def ease(a: float, b: float, t: float) -> float:
    v = max(0., min(1., (t - a) / (b - a)))
    return v * v * (3 - 2 * v)


def pulse(t: float, at: float, width: float) -> float:
    return math.exp(-((t - at) / width) ** 2)


def make_audio(path: Path, direction: str) -> dict:
    rate = 48000
    time = np.arange(rate * SECONDS, dtype=np.float32) / rate
    rng = np.random.default_rng(20261022)
    noise = rng.normal(0, 1, time.shape).astype(np.float32)
    # The same original rain recording substitute in all three films.
    rain = (noise - np.roll(noise, 1) * .6) * .020
    low = .020 * np.sin(TAU * 55 * time) + .009 * np.sin(TAU * 82.4069 * time)
    left = rain + low
    right = np.roll(rain, 187) + low

    def note(at: float, hz: float, level: float, decay: float = 1., pan: float = 0.) -> None:
        nonlocal left, right
        age = np.maximum(time - at, 0)
        env = (1 - np.exp(-age * 10)) * np.exp(-age * decay) * (time >= at)
        tone = (np.sin(TAU * hz * age) + .22 * np.sin(TAU * 2 * hz * age)) * env * level
        left += tone * (1 - pan) * .5
        right += tone * (1 + pan) * .5

    if direction == "solitude":
        note(5.7, 261.6256, .11, .9, -.25)
        swell = np.exp(-((time - 6.) / .8) ** 2) * .018 * noise
        left += swell
        right += np.roll(swell, 180)
    elif direction == "unease":
        phase = TAU * (.65 * time + .065 * time * time)
        beats = np.maximum(np.sin(phase), 0) ** 9
        rumble = (.017 + .045 * time / SECONDS) * beats * np.sin(TAU * 47 * time)
        dissonance = .012 * (time / SECONDS) * (np.sin(TAU * 146.83 * time) + np.sin(TAU * 155.56 * time))
        left += rumble + dissonance
        right += rumble + np.roll(dissonance, 291)
    else:
        for at, hz, pan in [(5.9, 261.6256, -.3), (7.1, 329.6276, .3), (8.4, 391.9954, -.1)]:
            note(at, hz, .095, .38, pan)
        for at in np.arange(1.7, 7.9, .43):
            age = np.maximum(time - at, 0)
            step = .018 * noise * np.exp(-age * 40) * (time >= at)
            left += step * .7
            right += step
    fade = np.minimum(time / .4, 1) * np.minimum((SECONDS - time) / .7, 1)
    stereo = np.stack([left, right], axis=1) * fade[:, None]
    assert np.isfinite(stereo).all() and np.max(np.abs(stereo)) < .98
    with wave.open(str(path), "wb") as stream:
        stream.setnchannels(2)
        stream.setsampwidth(2)
        stream.setframerate(rate)
        stream.writeframes((stereo * 32767).astype("<i2").tobytes())
    return {"peak": round(float(np.abs(stereo).max()), 4), "rms": round(float(np.sqrt(np.mean(stereo ** 2))), 4)}


class Scene:
    def __init__(self) -> None:
        source = Image.open(ASSETS / "rain-shelter-plate.png").convert("RGB")
        # Fit, not a destructive edit of the stored original.
        source = source.resize((W, H), Image.Resampling.LANCZOS)
        self.base = np.asarray(source, dtype=np.float32)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        self.x, self.y = xx / W, yy / H
        self.floor = np.clip((self.y - .59) / .25, 0, 1)
        self.rng = np.random.default_rng(1729)
        sheet = Image.open(ASSETS / "walker-sprites.png").convert("RGBA")
        self.poses = []
        for index in range(4):
            slot = sheet.crop((round(index * sheet.width / 4), 0, round((index + 1) * sheet.width / 4), sheet.height))
            slot = slot.crop(slot.getchannel("A").getbbox())
            slot = slot.resize((round(slot.width * (.126 * H) / slot.height), round(.126 * H)), Image.Resampling.LANCZOS)
            self.poses.append(slot)
        self.drops = self.rng.random((380, 5))
        self.ripples = self.rng.random((34, 4))

    def frame(self, direction: str, t: float) -> Image.Image:
        response = ease(4, 10, t)
        if direction == "solitude":
            illumination = pulse(t, 6., .9) * .6
            zoom = 1.055 - .05 * ease(0, 12, t)
            speed, wind = .34, .4
        elif direction == "unease":
            illumination = sum(pulse(t, at, width) * strength for at, width, strength in [(3.8, .65, .5), (6.3, .5, .7), (8.2, .45, .8)])
            zoom = 1.02 + .04 * t / 12 + (.055 if t >= 4 else 0) + (.065 if t >= 7.5 else 0)
            speed, wind = .40 + .34 * t / 12, 1.3
        else:
            illumination = .26 * ease(5, 9, t)
            zoom = 1.015 + .04 * ease(0, 9, t)
            speed, wind = .36 - .13 * response, .25
        beam_x = .20 + .78 * ease(4.5, 7.8, t) if direction == "solitude" else .66
        glow = np.exp(-((self.x - beam_x) / .26) ** 2 - ((self.y - .82) / .20) ** 2)
        delta = glow[:, :, None] * np.array([33, 28, 18], dtype=np.float32) * illumination
        image = Image.fromarray(np.uint8(np.clip(self.base + delta, 0, 255))).convert("RGBA")
        layer = Image.new("RGBA", (W, H))
        draw = ImageDraw.Draw(layer)
        for dx, dy, depth, length, alpha in self.drops:
            # Increasing cumulative travel gives continuous accelerating rain.
            travel = (.40 * t + .34 * t * t / 24) if direction == "unease" else (.34 * t if direction == "solitude" else .36 * t - .13 * max(0, t - 4) * response)
            px = (dx - .035 * travel * wind + 1) % 1 * W
            py = (dy + travel * (.6 + depth)) % 1 * H
            end_x = px - (1.5 + depth * 3.5) * wind
            end_y = py + (4 + length * 9) * (1 + speed)
            draw.line([(px, py), (end_x, end_y)], fill=(162, 187, 201, round(15 + 32 * alpha)), width=1)
        for rx, ry, cycle, offset in self.ripples:
            age = (t * (.8 if direction != "unease" else 1.3) + offset * 3) % (1.4 + cycle)
            progress = age / (1.4 + cycle)
            cx, cy = rx * W, (.67 + ry * .31) * H
            radius = progress * (10 + ry * 20)
            opacity = round((1 - progress) * (13 + ry * 10))
            draw.ellipse((cx - radius, cy - radius * .17, cx + radius, cy + radius * .17), outline=(150, 180, 188, opacity), width=1)

        main_x = .705 - (.014 * ease(7, 9, t) if direction == "unease" else 0)
        people = [(main_x, .623, .126, t * 1.8, .35 if direction == "unease" and 7 < t < 9 else 0., False)]
        if direction == "hope":
            walk = ease(0, 8.2, t)
            people.append((-.08 + .74 * walk, .623, .123, t * 7.3,
                           1 - ease(7.6, 8.2, t), True))
        # Grounded reflections have the same displacement and articulated legs.
        figures = Image.new("RGBA", (W, H))
        for px, gy, height, phase, moving, warm in people:
            pose_index = int(t * 9) % 4 if moving > .2 else 1
            sprite = self.poses[pose_index]
            if not warm:
                sprite = sprite.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            bob = round(math.sin(t * 2.2) * .5) if moving < .2 else 0
            figures.alpha_composite(sprite, (round(px * W - sprite.width * .5), round(gy * H) - sprite.height + bob))
        ground = round(.623 * H)
        reflected = figures.crop((0, ground - 100, W, ground)).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        reflected = reflected.resize((W, 130), Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(2.4))
        reflected.putalpha(reflected.getchannel("A").point(lambda a: round(a * .23)))
        layer.alpha_composite(reflected, (0, ground))
        layer.alpha_composite(figures)
        draw = ImageDraw.Draw(layer)

        # A minimal spatial relationship, rather than particle confetti.
        if direction == "hope":
            progress = ease(7.4, 9.2, t)
            x0, x1 = .66 * W, .705 * W
            y = .629 * H
            draw.line([(x0, y), (x0 + (x1 - x0) * progress, y)], fill=(213, 178, 116, round(progress * 170)), width=1)
            for x in [x0, x1]:
                draw.rectangle((x - 1, y - 1, x + 1, y + 1), fill=(230, 194, 132, round(progress * 180)))
        else:
            for number in range(5):
                alpha = max(0, math.sin(t * (1.2 if direction == "solitude" else 2.4) - number * .7))
                alpha *= (1 - ease(8, 11, t)) if direction == "solitude" else .9
                jitter = math.sin(t * 4 + number) * 2 if direction == "unease" else 0
                px, py = main_x * W + number * 6 + jitter, .63 * H
                draw.line([(px, py), (px + 3, py)], fill=(160, 190, 202, round(110 * alpha)), width=1)
        image = Image.alpha_composite(image, layer)
        aperture_w, aperture_h = W / zoom, H / zoom
        left = (W - aperture_w) * .65
        top = (H - aperture_h) * .52
        if direction == "unease":
            left += math.sin(t * 9) * .7 * response
            top += math.sin(t * 13) * .35 * response
        image = image.transform((W, H), Image.Transform.EXTENT,
                                (left, top, left + aperture_w, top + aperture_h), Image.Resampling.BICUBIC)
        return image.convert("RGB")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", default="_site/emotion-films-work-20261022")
    parser.add_argument("--direction", choices=["all", "solitude", "unease", "hope"], default="all")
    parser.add_argument("--stills-only", action="store_true")
    args = parser.parse_args()
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        parser.error("FFmpeg is required")
    work = Path(args.work_dir).resolve()
    work.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    # This plan is written before any of the encoded films are produced.
    study = {"version": 1, "title": "候光 / 同一场景，三种时间表达", "seconds": SECONDS,
             "fps": FPS, "width": W, "height": H, "video_model_used": False,
             "method": "两张内置ImageGen素材（场景与透明四姿态人物）+ 人物逐帧动画、雨、水波、光、镜头、信号 + 原创合成声音 + FFmpeg编码。",
             "fixed": "共享原始场景、构图、主体类别、12秒时长、24fps、16:9、同一基础雨声与稀疏计算线。",
             "changed": "人物关系、行动、等待时长、拉远/推进/切镜、雨速、光影时间、声音节奏与和声一起变化。",
             "limitation": "这是人工情绪导演与动态编排的演示；不是三次AI视频生成，也不是单变量实验或观众情绪成功率测试。人物为同一张四姿态素材复用的二维动画，两人外观相同；步态与停步有限，背景没有真实景深重建或自然演员表演。",
             "films": FILMS}
    (ASSETS / "study.json").write_text(json.dumps(study, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for film in FILMS:
        lines = ["【可交给视频模型的导演指令 / 尚未执行】", "作品：候光 / " + film["title"],
                 "交付：12秒，16:9，24fps，有声；以提供的雨夜候车亭场景为视觉参考。",
                 "请通过事件、人物关系、镜头节奏与声音表达感受，不在影片中写出情绪名称。",
                 "目标：" + film["goal"], "情绪走向：" + film["arc"], "保持：" + study["fixed"]]
        for field, title in [("action", "人物行动"), ("camera", "镜头"), ("weather", "环境运动"),
                             ("sound", "声音"), ("signal", "计算隐喻"), ("avoid", "避免"), ("check", "审片问题")]:
            lines.append(title + "：" + film[field])
        for shot in film["stages"]:
            lines.append(f"{shot['start']}–{shot['end']}秒 / {shot['name']}：{shot['detail']}")
        lines += ["保持雨亭结构与环境材质一致，人物运动接地，不要复制粘贴滑行。",
                  "当前网页成片来自程序动画，不是执行以上指令的视频模型结果。"]
        (ASSETS / (film["id"] + "-video-direction.txt")).write_text("\n".join(lines) + "\n", encoding="utf-8")
    scene = Scene()
    for film in FILMS:
        direction = film["id"]
        if args.direction not in ("all", direction):
            continue
        if args.stills_only:
            scene.frame(direction, 8.8).save(ASSETS / (direction + "-poster.jpg"), quality=94)
            continue
        sound = work / (direction + ".wav")
        audio_metrics = make_audio(sound, direction)
        output = ASSETS / (direction + ".mp4")
        command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-threads", "2",
                   "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                   "-i", str(sound), "-c:v", "libx264", "-threads", "2", "-preset", "fast", "-crf", "20",
                   "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-t", str(SECONDS),
                   "-movflags", "+faststart", str(output)]
        process = subprocess.Popen(command, stdin=subprocess.PIPE)
        try:
            for number in range(FPS * SECONDS):
                frame = scene.frame(direction, number / FPS)
                process.stdin.write(frame.tobytes())
                if number % (FPS * 4) == 0:
                    print(f"{direction}: {number // FPS}/{SECONDS}s", flush=True)
        finally:
            process.stdin.close()
        if process.wait() != 0:
            raise RuntimeError("FFmpeg encoding failed: " + direction)
        # Poster is extracted from the final MP4, not a separate invented frame.
        subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-ss", "8.8", "-i", str(output),
                        "-frames:v", "1", "-update", "1", "-q:v", "2", str(ASSETS / (direction + "-poster.jpg"))], check=True)
        print(json.dumps({"film": direction, "bytes": output.stat().st_size, "audio": audio_metrics}), flush=True)
    if not args.stills_only and all((ASSETS / (film["id"] + ".mp4")).is_file() for film in FILMS):
        records = []
        for file in sorted(ASSETS.iterdir()):
            if file.name == "manifest.json" or not file.is_file():
                continue
            records.append({"file": file.name, "bytes": file.stat().st_size,
                            "sha256": hashlib.sha256(file.read_bytes()).hexdigest()})
        manifest = {"date": "2026-10-22", "image_tool": "built-in ImageGen", "image_calls": 2,
                    "original_tool_files": ["exec-fe8a49f8-8de7-44e0-8efd-401a300c16af.png", "exec-c9e14961-3fb8-439b-a557-db9821fe0ed1.png"],
                    "original_size": [1672, 941], "model_version": None, "seed": None,
                    "video_model_calls": 0, "video_method": study["method"], "files": records}
        (ASSETS / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
