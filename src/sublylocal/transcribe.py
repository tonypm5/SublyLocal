import shutil
import subprocess
from pathlib import Path

import numpy as np

from .models import Segment


def transcribe(
    media: Path,
    model_name: str = "small",
    source_language: str | None = None,
) -> tuple[list[Segment], str]:
    """Transcribe a media file with faster-whisper."""
    from faster_whisper import WhisperModel

    model = WhisperModel(model_name, device="auto", compute_type="auto")
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg was not found. Install it and retry.")
    decoded = subprocess.run(
        [
            ffmpeg,
            "-v",
            "error",
            "-i",
            str(media),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-f",
            "f32le",
            "pipe:1",
        ],
        check=True,
        capture_output=True,
    )
    audio = np.frombuffer(decoded.stdout, dtype=np.float32)
    raw_segments, info = model.transcribe(
        audio,
        language=source_language,
        vad_filter=True,
        beam_size=5,
    )
    segments = [
        Segment(float(item.start), float(item.end), item.text.strip())
        for item in raw_segments
        if item.text.strip()
    ]
    return segments, info.language
