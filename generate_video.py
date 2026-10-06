import math
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from moviepy.editor import AudioClip, CompositeVideoClip, TextClip, VideoClip

FPS = 30
WIDTH = 1920
HEIGHT = 1080
DURATION = 60.0
OUTPUT_DIR = Path("output")
OUTPUT_FILE = OUTPUT_DIR / "beethoven_jam_session.mp4"


def build_background_frame(t: float) -> np.ndarray:
    frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.float32)

    # atmospheric blue-black gradient
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = 5 + ratio * 50
        g = 10 + ratio * 30
        b = 25 + ratio * 80
        frame[y, :, 0] = r
        frame[y, :, 1] = g
        frame[y, :, 2] = b

    # moving moonlight spotlight
    cx = WIDTH * (0.5 + 0.12 * math.sin(t / 7.0))
    cy = HEIGHT * (0.38 + 0.04 * math.sin(t / 11.0))
    for y in range(HEIGHT):
        for x in range(WIDTH):
            dx = x - cx
            dy = y - cy
            dist = dx * dx + dy * dy
            glow = math.exp(-dist / (700000 + 50000 * math.sin(t / 9.0)))
            frame[y, x, 0] += 120 * glow
            frame[y, x, 1] += 150 * glow
            frame[y, x, 2] += 210 * glow

    # subtle cinematic lens flare streak
    beam_center = WIDTH * (0.18 + 0.1 * math.sin(t / 4.0))
    for x in range(WIDTH):
        light = max(0.0, 1.0 - abs(x - beam_center) / (WIDTH * 0.62))
        light = light ** 2
        frame[:, x, 0] += 10 * light
        frame[:, x, 1] += 16 * light
        frame[:, x, 2] += 24 * light

    return np.clip(frame, 0, 255).astype(np.uint8)


def build_piano_layer(t: float) -> np.ndarray:
    img = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    # piano perch / silhouette stage area
    stage_top = int(HEIGHT * 0.68)
    stage_bottom = HEIGHT
    draw.rounded_rectangle(
        [int(WIDTH * 0.12), stage_top, int(WIDTH * 0.88), stage_bottom],
        radius=28,
        fill=(8, 10, 16),
    )

    # piano keys
    key_count = 26
    start_x = WIDTH * 0.18
    key_width = (WIDTH * 0.64) / key_count
    for i in range(key_count):
        x0 = start_x + i * key_width
        x1 = x0 + key_width * 0.82
        y0 = stage_top + 20 + 18 * math.sin(t * 2.6 + i * 0.7)
        y1 = HEIGHT - 18
        fill = (16, 18, 22) if i % 2 == 0 else (30, 32, 38)
        draw.rounded_rectangle([x0, y0, x1, y1], radius=6, fill=fill)

    # player silhouette
    center_x = WIDTH * (0.58 + 0.04 * math.sin(t / 5.5))
    center_y = HEIGHT * 0.48
    draw.ellipse([center_x - 32, center_y - 70, center_x + 32, center_y + 10], fill=(12, 12, 18))
    draw.rectangle([center_x - 22, center_y + 10, center_x + 22, center_y + 160], fill=(22, 22, 28))
    draw.line((center_x - 16, center_y + 35, center_x - 60, center_y + 110), fill=(18, 18, 24), width=14)
    draw.line((center_x + 16, center_y + 35, center_x + 72, center_y + 100), fill=(18, 18, 24), width=14)
    draw.line((center_x, center_y + 155, center_x - 18, center_y + 240), fill=(18, 18, 24), width=12)
    draw.line((center_x, center_y + 155, center_x + 24, center_y + 240), fill=(18, 18, 24), width=12)

    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    return np.array(img)


def build_visuals(t: float) -> np.ndarray:
    frame = build_background_frame(t).copy()
    piano_layer = build_piano_layer(t)
    alpha = 0.78
    frame = frame.astype(np.float32)
    piano_layer = piano_layer.astype(np.float32)
    frame = frame * (1.0 - alpha) + piano_layer * alpha
    return np.clip(frame, 0, 255).astype(np.uint8)


def make_audio_frame(t: float) -> np.ndarray:
    # Beethoven-inspired harmonic motion in a dark, rumbling blues/rock groove
    note_sequence = [
        196.0, 220.0, 246.94, 220.0, 174.61, 146.83, 174.61, 196.0,
        164.81, 196.0, 220.0, 196.0, 174.61, 164.81, 146.83, 174.61,
    ]
    idx = int((t * 2.0) % len(note_sequence))
    freq = note_sequence[idx]
    beat = 0.7 * np.sin(2 * math.pi * freq * t)
    bass = 0.35 * np.sin(2 * math.pi * (freq / 2.0) * t)
    over = 0.12 * np.sin(2 * math.pi * (freq * 2.0) * t + 0.8)
    pulse = 0.03 * np.sin(2 * math.pi * 2.4 * t)
    return np.clip(beat + bass + over + pulse, -1.0, 1.0)


def make_audio(duration: float):
    sample_rate = 44100

    def audio_frame(t):
        t = np.asarray(t)
        values = np.zeros_like(t, dtype=np.float32)
        for i, tt in enumerate(t):
            values[i] = make_audio_frame(float(tt))
        return values

    return AudioClip(audio_frame, duration=duration, fps=sample_rate)


def make_title_clips(duration: float):
    title = (
        TextClip(
            "BEETHOVEN JAM",
            font="DejaVu-Sans-Bold",
            fontsize=82,
            color="white",
            stroke_color="black",
            stroke_width=2,
        )
        .set_position(("center", 0.12))
        .set_duration(duration)
    )
    subtitle = (
        TextClip(
            "AFRO-LATIN ROCK BLUES • MOONLIGHT SONATA",
            font="DejaVu-Sans-Bold",
            fontsize=34,
            color="#dfe7ff",
            stroke_color="black",
            stroke_width=1,
        )
        .set_position(("center", 0.22))
        .set_duration(duration)
    )
    return title, subtitle


def build_video():
    video_clip = VideoClip(build_visuals, duration=DURATION)
    video_clip = video_clip.set_fps(FPS)

    title, subtitle = make_title_clips(DURATION)
    audio = make_audio(DURATION)

    final = CompositeVideoClip(
        [video_clip, title, subtitle],
        size=(WIDTH, HEIGHT),
        bg_color=(10, 12, 20),
    ).set_audio(audio)

    OUTPUT_DIR.mkdir(exist_ok=True)
    final.write_videofile(
        str(OUTPUT_FILE),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        bitrate="10M",
        preset="medium",
        threads=4,
    )


if __name__ == "__main__":
    build_video()
    print(f"Rendered video: {OUTPUT_FILE.resolve()}")
