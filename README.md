# Beethoven Jam Session: Afro-Latin Rock Blues

A cinematic, YouTube-ready MP4 generator built in Python that creates a 60-second concept video inspired by Beethoven's Moonlight Sonata fused with Afro-Latin rock/blues energy.

This repository is designed as a reusable foundation for more videos to come. It generates a polished cinematic prototype locally with:

- high-resolution 1920x1080 output
- original synthesized music
- dramatic lighting and motion
- layered title cards and atmospheric visuals
- a reusable modular structure for future AI-assisted additions

## What this produces

A 1-minute MP4 concept video titled:

- `output/beethoven_jam_session.mp4`

It is intentionally a cinematic prototype that is ready for YouTube upload and easy to iterate.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Render the video

```bash
python generate_video.py
```

The output file will be created in the `output/` directory.

## Notes

This version focuses on a self-contained local workflow using Python and MoviePy. It is structured so you can later add:

- AI-generated frame sequences
- stock footage or image layers
- custom music stems
- voiceover or narration
- text scene transitions
- higher-end compositing passes

For a photoreal cinematic Beethoven scene, replace the procedural visual layer with AI-generated footage or image plates and keep the same export pipeline.
