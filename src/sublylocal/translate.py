import json
import os
from collections.abc import Sequence

import httpx

from .models import Segment

SYSTEM_PROMPT = """You are a professional audiovisual subtitle translator.
Translate naturally into the requested language. Preserve tone, slang, names, and intent.
Keep every subtitle concise, readable, and no longer than two short lines.
Return only a JSON array of objects with the original integer id and translated text.
Do not merge, remove, reorder, or add items."""


def _payload(segments: Sequence[Segment], target_language: str) -> str:
    rows = [{"id": i, "text": segment.text} for i, segment in enumerate(segments)]
    return f"Target language: {target_language}\nSubtitles:\n{json.dumps(rows, ensure_ascii=False)}"


def _parse_response(content: str, count: int) -> list[str]:
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1].rsplit("```", 1)[0]
    rows = json.loads(content)
    if not isinstance(rows, list) or len(rows) != count:
        raise ValueError("The translator returned an unexpected number of subtitles")
    by_id = {int(row["id"]): str(row["text"]).strip() for row in rows}
    if set(by_id) != set(range(count)):
        raise ValueError("The translator changed subtitle identifiers")
    return [by_id[i] for i in range(count)]


def translate_ollama(
    segments: Sequence[Segment],
    target_language: str,
    model: str,
    base_url: str = "http://localhost:11434",
) -> list[Segment]:
    response = httpx.post(
        f"{base_url.rstrip('/')}/api/chat",
        json={
            "model": model,
            "stream": False,
            "format": "json",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _payload(segments, target_language)},
            ],
        },
        timeout=300,
    )
    response.raise_for_status()
    translated = _parse_response(response.json()["message"]["content"], len(segments))
    return [Segment(s.start, s.end, text) for s, text in zip(segments, translated)]


def translate_openai(
    segments: Sequence[Segment],
    target_language: str,
    model: str,
    base_url: str = "https://api.openai.com/v1",
) -> list[Segment]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required when provider=openai")
    response = httpx.post(
        f"{base_url.rstrip('/')}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": _payload(segments, target_language)
                    + "\nWrap the array in an object with the key subtitles.",
                },
            ],
        },
        timeout=300,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    parsed = json.loads(content)
    rows = parsed["subtitles"]
    translated = _parse_response(json.dumps(rows, ensure_ascii=False), len(segments))
    return [Segment(s.start, s.end, text) for s, text in zip(segments, translated)]


def translate_segments(
    segments: Sequence[Segment],
    target_language: str,
    provider: str,
    model: str,
    base_url: str | None = None,
) -> list[Segment]:
    if provider == "none":
        return list(segments)
    if provider == "ollama":
        return translate_ollama(
            segments,
            target_language,
            model,
            base_url or "http://localhost:11434",
        )
    if provider == "openai":
        return translate_openai(
            segments,
            target_language,
            model,
            base_url or "https://api.openai.com/v1",
        )
    raise ValueError(f"Unsupported translation provider: {provider}")
