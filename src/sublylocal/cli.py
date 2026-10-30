import argparse
import shutil
import sys
from pathlib import Path

from .render import burn_subtitles
from .subtitles import write_srt
from .transcribe import transcribe
from .translate import translate_segments


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        prog="sublylocal",
        description="Transcribe, translate, and burn readable subtitles into a video.",
    )
    result.add_argument("input", nargs="?", type=Path, help="Input video or audio file")
    result.add_argument("--target", default="fr", help="Target language (default: fr)")
    result.add_argument("--source", default=None, help="Source language, or auto-detect")
    result.add_argument("--whisper-model", default="small", help="faster-whisper model")
    result.add_argument("--provider", choices=["ollama", "openai", "none"], default="ollama")
    result.add_argument("--translation-model", default=None, help="Translator model name")
    result.add_argument("--base-url", default=None, help="Override provider base URL")
    result.add_argument("--output-dir", type=Path, default=Path("sublylocal-output"))
    result.add_argument("--burn", action="store_true", help="Also create an MP4 with captions burned in")
    result.add_argument("--line-width", type=int, default=38)
    result.add_argument("--doctor", action="store_true", help="Check local dependencies")
    return result


def doctor() -> int:
    checks = {"ffmpeg": shutil.which("ffmpeg"), "ffprobe": shutil.which("ffprobe")}
    for name, path in checks.items():
        print(f"{'OK' if path else 'MISSING':7} {name}{f' ({path})' if path else ''}")
    return 0 if all(checks.values()) else 1


def main() -> None:
    args = parser().parse_args()
    if args.doctor:
        raise SystemExit(doctor())
    if not args.input:
        parser().error("input is required unless --doctor is used")
    if not args.input.is_file():
        parser().error(f"input file does not exist: {args.input}")

    model = args.translation_model
    if not model:
        model = "qwen2.5:7b" if args.provider == "ollama" else "gpt-4.1-mini"

    args.output_dir.mkdir(parents=True, exist_ok=True)
    stem = args.input.stem
    srt = args.output_dir / f"{stem}.{args.target}.srt"
    video_output = args.output_dir / f"{stem}.{args.target}.captioned.mp4"

    print(f"[1/4] Transcribing {args.input} ...", file=sys.stderr)
    segments, detected = transcribe(args.input, args.whisper_model, args.source)
    print(f"      Detected language: {detected}; segments: {len(segments)}", file=sys.stderr)
    print(f"[2/4] Translating to {args.target} with {args.provider}/{model} ...", file=sys.stderr)
    translated = translate_segments(segments, args.target, args.provider, model, args.base_url)
    print(f"[3/4] Writing {srt} ...", file=sys.stderr)
    write_srt(translated, srt, args.line_width)
    if args.burn:
        print(f"[4/4] Rendering {video_output} ...", file=sys.stderr)
        burn_subtitles(args.input, srt, video_output)
    else:
        print("[4/4] Render skipped (add --burn to create a captioned MP4).", file=sys.stderr)
    print(srt)
    if args.burn:
        print(video_output)


if __name__ == "__main__":
    main()
