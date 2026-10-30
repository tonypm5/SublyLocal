import shutil
import subprocess
from pathlib import Path

DEFAULT_STYLE = (
    "FontName=DejaVu Sans,FontSize=18,Bold=1,PrimaryColour=&H00FFFFFF,"
    "OutlineColour=&H00000000,BackColour=&H90000000,BorderStyle=3,"
    "Outline=1,Shadow=0,Alignment=2,MarginL=24,MarginR=24,MarginV=70"
)


def require_ffmpeg() -> str:
    executable = shutil.which("ffmpeg")
    if not executable:
        raise RuntimeError("ffmpeg was not found. Install it and retry.")
    return executable


def burn_subtitles(video: Path, srt: Path, output: Path, style: str = DEFAULT_STYLE) -> None:
    ffmpeg = require_ffmpeg()
    escaped = str(srt.resolve()).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(video),
            "-vf",
            f"subtitles='{escaped}':force_style='{style}'",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "20",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-movflags",
            "+faststart",
            str(output),
        ],
        check=True,
    )
