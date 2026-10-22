"""Render the original Night Signal motion study (AI still + authored motion/audio).

Requires Python 3.10+, Pillow, NumPy and FFmpeg/FFprobe on PATH.
This is a deterministic film compositor, not an AI video-generation client.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJECT = Path(__file__).resolve().parents[1]
ASSETS = PROJECT / "assets" / "motion"
WIDTH, HEIGHT, FPS, DURATION = 1280, 720, 24, 15


def smooth(start: float, end: float, value: float) -> float:
    t = float(np.clip((value - start) / (end - start), 0, 1))
    return t * t * (3 - 2 * t)


def envelope(t: float, start: float, end: float, fade: float = .7) -> float:
    return smooth(start, start + fade, t) * (1 - smooth(end - fade, end, t))


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def audio(path: Path) -> None:
    """Original synthesized sound: airy low space, then three warm harmonic notes."""
    rate = 48000
    t = np.arange(rate * DURATION, dtype=np.float64) / rate
    rng = np.random.default_rng(20261021)
    drift = np.interp(t, np.arange(0, DURATION + 1, .03), rng.normal(0, 1, 534))
    space = .012 * drift + .014 * np.sin(2 * np.pi * 55 * t)
    space += .008 * np.sin(2 * np.pi * 82.4069 * t + .18 * np.sin(t))
    left, right = space.copy(), space.copy()
    for onset, freq, pan in [(6.6, 261.6256, -.35), (8.9, 329.6276, .3),
                             (10.8, 391.9954, -.15), (12.1, 523.2511, .22)]:
        tau = np.maximum(t - onset, 0)
        env = (1 - np.exp(-tau * 3)) * np.exp(-tau * .65) * (t >= onset)
        tone = sum(np.sin(2 * np.pi * freq * h * tau) / (h * h)
                   for h in [1, 2, 3, 4]) * env * .045
        left += tone * (1 - pan) / 2
        right += tone * (1 + pan) / 2
        echo_tau = np.maximum(t - onset - .43, 0)
        echo = np.sin(2 * np.pi * freq * echo_tau) * np.exp(-echo_tau * .9)
        echo *= (1 - np.exp(-echo_tau * 4)) * (t >= onset + .43) * .009
        left += echo * .6
        right += echo
    fade = np.minimum(t / .6, 1) * np.minimum((DURATION - t) / 1.4, 1)
    stereo = np.stack([left, right], axis=1) * fade[:, None] * 4
    assert np.max(np.abs(stereo)) < 1
    with wave.open(str(path), "wb") as stream:
        stream.setnchannels(2)
        stream.setsampwidth(2)
        stream.setframerate(rate)
        stream.writeframes((stereo * 32767).astype("<i2").tobytes())


def render(args: argparse.Namespace) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("FFmpeg is required on PATH")
    work = Path(args.work_dir).resolve()
    work.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    source = ASSETS / "night-signal-keyframe.png"
    original = Image.open(source).convert("RGB")
    # Fit the generated landscape to the film aperture, keeping its composition.
    ratio = max(WIDTH / original.width, HEIGHT / original.height)
    fit = original.resize((round(original.width * ratio), round(original.height * ratio)), Image.Resampling.LANCZOS)
    fit = fit.crop(((fit.width - WIDTH) // 2, (fit.height - HEIGHT) // 2,
                    (fit.width + WIDTH) // 2, (fit.height + HEIGHT) // 2))
    base = np.asarray(fit, dtype=np.float32)
    luminance = np.sum(base * np.array([.2126, .7152, .0722], dtype=np.float32), axis=2)
    cold = luminance[:, :, None] * np.array([.76, .9, 1.12], dtype=np.float32)
    amber = np.clip((base[:, :, 0] - base[:, :, 2] - 3) / 55, 0, 1)[:, :, None]
    cold_delta = (cold - base) * amber * np.float32(.88)
    del cold, amber, luminance
    yy = np.arange(HEIGHT, dtype=np.float32)[:, None]
    xx = np.arange(WIDTH, dtype=np.float32)[None, :]
    glow = np.exp(-(((xx / WIDTH - .96) / .29) ** 2 + ((yy / HEIGHT - .59) / .43) ** 2))
    title_font = font(args.chinese_font, 94)
    body_font = font(args.chinese_font, 27)
    small_font = font(args.chinese_font, 17)
    mono_font = font(args.latin_font, 13)
    title = Image.new("RGBA", (290, 145))
    title_draw = ImageDraw.Draw(title)
    title_draw.text((0, 0), "夜香", font=title_font, fill=(231, 232, 219, 255), stroke_width=1)
    # A few modular cuts retain the poster family's editorial/data relationship.
    for gx, gy in [(23, 20), (61, 47), (84, 76), (136, 22), (172, 65), (189, 89)]:
        title_draw.rectangle((gx, gy, gx + 3, gy + 3), fill=(0, 0, 0, 0))
    for gx, gy in [(219, 25), (224, 30), (231, 37), (238, 48)]:
        title_draw.rectangle((gx, gy, gx + 2, gy + 2), fill=(211, 174, 110, 175))

    def frame(time: float) -> Image.Image:
        warmth = .1 + .9 * smooth(5.1, 11.9, time)
        image = base + cold_delta * np.float32(1 - warmth)
        image *= np.array([.86 + .14 * warmth, .94 + .06 * warmth, 1.0], dtype=np.float32)
        image += glow[:, :, None] * np.array([15, 8, 1], dtype=np.float32) * smooth(5, 12.3, time)
        image = Image.fromarray(np.uint8(np.clip(image, 0, 255)))
        z = 1 + .052 * smooth(0, 15, time)
        # A real slow push, with the bottle as the optical anchor.
        crop_w, crop_h = WIDTH / z, HEIGHT / z
        left, top = (WIDTH - crop_w) * .65, (HEIGHT - crop_h) * .55
        image = image.transform((WIDTH, HEIGHT), Image.Transform.EXTENT,
                                (left, top, left + crop_w, top + crop_h), Image.Resampling.BICUBIC).convert("RGBA")

        def point(px: float, py: float) -> tuple[float, float]:
            return ((px * WIDTH - left) * z, (py * HEIGHT - top) * z)

        overlay = Image.new("RGBA", image.size)
        draw = ImageDraw.Draw(overlay)
        trace = [( .583, .747), (.724, .747), (.74, .724), (.74, .402), (.728, .374)]
        # Animate a single semantic signal along the contact edge and glass contour.
        progress = smooth(5.7, 10.8, time)
        pts = [np.array(point(*p)) for p in trace]
        lengths = np.array([np.linalg.norm(b - a) for a, b in zip(pts, pts[1:])])
        travelled = progress * lengths.sum()
        at = pts[0]
        for a, b, length in zip(pts, pts[1:], lengths):
            if travelled <= 0:
                break
            end = a + (b - a) * min(travelled / length, 1)
            draw.line([tuple(a), tuple(end)], fill=(247, 198, 117, round(140 * progress)), width=1)
            at = end
            travelled -= length
        if .01 < progress < 1:
            x, y = at
            draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(255, 222, 170, 210))
        for index, py in enumerate([.45, .49, .53, .57, .61]):
            amount = smooth(7 + index * .32, 9.8 + index * .32, time)
            x, y = point(.747, py)
            draw.line([(x + 6, y), (x + 6 + 18 * amount, y)], fill=(223, 185, 124, round(100 * amount)), width=1)
            if amount > .1:
                draw.rectangle((x + 28, y - 1, x + 30, y + 1), fill=(223, 185, 124, round(100 * amount)))
        bloom = overlay.filter(ImageFilter.GaussianBlur(5))
        image = Image.alpha_composite(image, bloom)
        image = Image.alpha_composite(image, overlay)
        lettering = Image.new("RGBA", image.size)
        text_draw = ImageDraw.Draw(lettering)
        header_alpha = round(165 * smooth(.3, 1.4, time))
        text_draw.text((124, 92), "NIGHT SIGNAL  /  001", font=mono_font, fill=(200, 212, 216, header_alpha))
        first = envelope(time, .6, 5.1)
        second = envelope(time, 5.6, 10.6)
        if first > 0:
            text_draw.text((123, 315), "世界很安静。", font=body_font, fill=(214, 222, 225, round(230 * first)))
        if second > 0:
            text_draw.text((123, 315), "直到，一点回应。", font=body_font, fill=(231, 223, 204, round(230 * second)))
        last = smooth(10.5, 11.7, time)
        final_title = title.copy()
        final_title.putalpha(title.getchannel("A").point(lambda a: round(a * last)))
        lettering.alpha_composite(final_title, (118, 239))
        text_draw = ImageDraw.Draw(lettering)
        text_draw.text((124, 382), "独处，也有微光回应。", font=small_font, fill=(214, 201, 174, round(220 * last)))
        text_draw.text((124, 627), "ART DIRECTION STUDY  /  15 SECONDS", font=mono_font, fill=(173, 189, 200, header_alpha))
        image = Image.alpha_composite(image, lettering).convert("RGB")
        fade = smooth(0, .6, time) * (1 - .18 * smooth(14.5, 15, time))
        return Image.fromarray((np.asarray(image, dtype=np.float32) * fade).astype(np.uint8))

    samples = {2 * FPS: "night-signal-02.jpg", int(7.5 * FPS): "night-signal-07.jpg",
               int(12.5 * FPS): "night-signal-12.jpg"}
    if args.stills_only:
        for number, name in samples.items():
            frame(number / FPS).save(ASSETS / name, quality=95)
        print("Rendered three film stills.")
        return
    sound = work / "night-signal-sound.wav"
    audio(sound)
    silent = work / "night-signal-silent.mp4"
    command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264",
               "-preset", "medium", "-crf", "18", "-threads", "2", "-pix_fmt", "yuv420p", str(silent)]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    try:
        for number in range(FPS * DURATION):
            image = frame(number / FPS)
            process.stdin.write(image.tobytes())
            if number in samples:
                image.save(ASSETS / samples[number], quality=95)
            if number % (FPS * 5) == 0:
                print(f"Rendered {number // FPS}/{DURATION}s", flush=True)
    finally:
        process.stdin.close()
    if process.wait() != 0:
        raise SystemExit("Film encoding failed")
    output = ASSETS / "night-signal.mp4"
    subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(silent), "-i", str(sound),
                    "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                    "-movflags", "+faststart", "-t", str(DURATION), str(output)], check=True)
    # Keep the published storyboard grounded in the encoded, final film.
    for number, name in samples.items():
        subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-threads", "1",
                        "-ss", str(number / FPS), "-i", str(output), "-frames:v", "1",
                        "-threads", "1", "-q:v", "2", str(ASSETS / name)], check=True)
    info = json.loads(subprocess.check_output([shutil.which("ffprobe"), "-v", "error", "-show_streams",
                                               "-show_format", "-of", "json", str(output)]))
    report = {"file": str(output), "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
              "bytes": output.stat().st_size, "streams": [{k: s.get(k) for k in
              ["codec_name", "codec_type", "width", "height", "r_frame_rate", "duration", "sample_rate", "channels"]}
              for s in info["streams"]], "duration": info["format"]["duration"]}
    (work / "render-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", default="_site/poster-motion-render-20261021")
    parser.add_argument("--chinese-font", default="C:/Windows/Fonts/msyh.ttc")
    parser.add_argument("--latin-font", default="C:/Windows/Fonts/consola.ttf")
    parser.add_argument("--stills-only", action="store_true")
    render(parser.parse_args())
