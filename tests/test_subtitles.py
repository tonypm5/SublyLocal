from pathlib import Path

from sublylocal.models import Segment
from sublylocal.subtitles import readable_lines, timestamp, write_srt


def test_timestamp_rounding() -> None:
    assert timestamp(64.481) == "00:01:04,481"
    assert timestamp(0) == "00:00:00,000"


def test_readable_lines_has_at_most_two_lines() -> None:
    result = readable_lines("This is a subtitle that should be split into readable lines", width=25)
    assert result.count("\n") <= 1


def test_write_srt(tmp_path: Path) -> None:
    output = tmp_path / "sample.srt"
    write_srt([Segment(0.0, 1.25, "Bonjour tout le monde")], output)
    assert "00:00:00,000 --> 00:00:01,250" in output.read_text(encoding="utf-8")
