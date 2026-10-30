# Instructions for AI coding agents

## Goal

Install and use SublyLocal to create translated SRT subtitles and an optionally captioned MP4.

## Safe default workflow

1. Confirm the input media path exists.
2. Run `sublylocal --doctor`.
3. Prefer local translation with Ollama unless the user explicitly requests an API provider.
4. Never print, copy, or commit credentials.
5. Run the command below and return both output paths.

```bash
sublylocal INPUT.mp4 --target fr --provider ollama --translation-model qwen2.5:7b --burn
```

## Development checks

After code changes, run:

```bash
pytest
ruff check .
```

Do not modify generated media or user input files in place.
