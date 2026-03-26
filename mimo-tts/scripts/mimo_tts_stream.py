#!/usr/bin/env python3
import argparse
import base64
import os
from pathlib import Path
from typing import Optional

import numpy as np
import soundfile as sf
from openai import OpenAI


BASE_URL = "https://api.xiaomimimo.com/v1"
MODEL = "mimo-v2-tts"


def build_text(text: str, style: Optional[str], styles: Optional[list[str]]) -> str:
    has_style_tag = "<style>" in text
    if has_style_tag and (style or styles):
        raise ValueError("Text already contains <style> tags; do not combine with --style/--styles")

    if styles:
        merged = " ".join(s for s in styles if s.strip())
        if merged:
            return f"<style>{merged}</style>{text}"
        return text

    if style:
        return f"<style>{style}</style>{text}"
    return text


def synthesize_stream(
    text: str,
    voice: str,
    output: str,
    style: Optional[str],
    styles: Optional[list[str]],
) -> None:
    api_key = os.environ.get("MIMO_API_KEY")
    if not api_key:
        raise RuntimeError("MIMO_API_KEY is not set")

    client = OpenAI(api_key=api_key, base_url=BASE_URL)

    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "assistant",
                "content": build_text(text, style, styles),
            }
        ],
        audio={
            "format": "pcm16",
            "voice": voice,
        },
        stream=True,
    )

    chunks = np.array([], dtype=np.float32)
    for chunk in completion:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        audio = getattr(delta, "audio", None)
        if not audio:
            continue
        pcm_bytes = base64.b64decode(audio["data"])
        np_pcm = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        chunks = np.concatenate((chunks, np_pcm))

    if chunks.size == 0:
        raise RuntimeError("No audio chunks received from stream")

    sf.write(output, chunks, samplerate=24000)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="MiMo TTS streaming client (pcm16)",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    text_group = parser.add_mutually_exclusive_group(required=True)
    text_group.add_argument("--text", help="Text to synthesize")
    text_group.add_argument("--text-file", help="Read UTF-8 text from file")
    parser.add_argument(
        "--voice",
        default="mimo_default",
        choices=["mimo_default", "default_zh", "default_en"],
        help="Voice name",
    )
    parser.add_argument("--style", default=None, help="Style tag value, e.g. 开心/粤语/唱歌")
    parser.add_argument(
        "--styles",
        nargs="+",
        default=None,
        help="Multiple style names in one <style> tag, e.g. --styles 开心 变快",
    )
    parser.add_argument("--output", default="stream_output.wav", help="Output WAV file path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.style and args.styles:
        raise ValueError("Use either --style or --styles, not both")

    if args.text_file:
        text = Path(args.text_file).read_text(encoding="utf-8")
    else:
        text = args.text

    synthesize_stream(
        text=text,
        voice=args.voice,
        output=args.output,
        style=args.style,
        styles=args.styles,
    )
    print(f"Saved streaming audio to {args.output}")


if __name__ == "__main__":
    main()
