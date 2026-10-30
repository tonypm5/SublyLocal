# SublyLocal

Local-first video transcription, subtitle translation, and readable caption burning—for humans and AI agents.

SublyLocal turns a video into a synchronized `.srt` file and, optionally, an MP4 with captions burned in. Speech recognition runs locally with faster-whisper. Translation can run locally with Ollama or through an optional OpenAI-compatible API.

## One-command usage

```bash
sublylocal video.mp4 --target fr --burn
```

Outputs:

```text
sublylocal-output/video.fr.srt
sublylocal-output/video.fr.captioned.mp4
```

## Install

### Requirements

- Python 3.10+
- FFmpeg
- Ollama for private local translation, or an optional API key

macOS:

```bash
brew install ffmpeg ollama uv
ollama pull qwen2.5:7b
uv tool install .
```

Ubuntu/Debian:

```bash
sudo apt update && sudo apt install -y ffmpeg pipx
pipx install .
ollama pull qwen2.5:7b
```

Check the installation:

```bash
sublylocal --doctor
```

## Local translation with Ollama

```bash
ollama serve
sublylocal interview.mp4 \
  --target fr \
  --provider ollama \
  --translation-model qwen2.5:7b \
  --burn
```

## Optional OpenAI translation

```bash
export OPENAI_API_KEY="your-key"
sublylocal interview.mp4 \
  --target fr \
  --provider openai \
  --translation-model gpt-4.1-mini \
  --burn
```

Never commit API keys. SublyLocal reads them only from the environment.

## Commands for AI agents

Give an agent this task:

```text
Install ffmpeg, Ollama, and SublyLocal. Pull qwen2.5:7b. Then run:
sublylocal INPUT.mp4 --target fr --provider ollama --translation-model qwen2.5:7b --burn
Return the SRT and captioned MP4 from sublylocal-output/.
```

Or let the agent inspect [`AGENTS.md`](AGENTS.md).

## Privacy model

- Transcription is local.
- Ollama translation is local.
- API translation is opt-in.
- Media is not uploaded by SublyLocal unless an explicitly selected provider requires it. The current API provider receives subtitle text, not the video.

## Current scope

Version 0.1 focuses on a dependable command-line workflow. It does not yet select viral moments, track moving speakers, remove filler words, or provide a graphical editor.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
ruff check .
```

## License

MIT. See [`LICENSE`](LICENSE).
