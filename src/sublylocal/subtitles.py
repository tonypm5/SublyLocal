import re
from pathlib import Path
from textwrap import wrap

from .models import Segment


def timestamp(seconds: float) -> str:
    milliseconds = round(max(0.0, seconds) * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    secs, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def readable_lines(text: str, width: int = 38) -> str:
    clean = re.sub(r"\s+", " ", text).strip()
    lines = wrap(clean, width=width, break_long_words=False, break_on_hyphens=False)
    if len(lines) <= 2:
        return "\n".join(lines)
    midpoint = max(1, len(clean) // 2)
    split = clean.rfind(" ", 0, midpoint + 1)
    if split < width // 2:
        split = clean.find(" ", midpoint)
    return clean if split < 0 else clean[:split] + "\n" + clean[split + 1 :]


def write_srt(segments: list[Segment], destination: Path, width: int = 38) -> None:
    blocks = []
    for index, segment in enumerate(segments, 1):
        blocks.append(
            f"{index}\n{timestamp(segment.start)} --> {timestamp(segment.end)}\n"
            f"{readable_lines(segment.text, width)}"
        )
    destination.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
