#!/usr/bin/env python3
import argparse
import base64
import os
from pathlib import Path
from typing import Optional

import subprocess
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
    audio_format: str = "ogg",
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

    pcm_data = bytearray()
    for chunk in completion:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        audio = getattr(delta, "audio", None)
        if not audio:
            continue
        pcm_bytes = base64.b64decode(audio["data"])
        pcm_data.extend(pcm_bytes)

    if not pcm_data:
        raise RuntimeError("No audio chunks received from stream")

    command = [
        "ffmpeg",
        "-y",
        "-f", "s16le",
        "-ar", "24000",
        "-ac", "1",
        "-i", "-",
        "-f", audio_format,
        output,
    ]
    try:
        subprocess.run(
            command,
            input=pcm_data,
            check=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg encoding failed:\n{e.stderr.decode('utf-8', errors='replace')}")


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
    parser.add_argument(
        "--format",
        default="ogg",
        choices=["wav", "ogg", "mp3"],
        help="Output audio format (default: ogg)",
    )
    parser.add_argument("--output", default=None, help="Output file path (default: stream_output.<format>)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.style and args.styles:
        raise ValueError("Use either --style or --styles, not both")

    if args.text_file:
        text = Path(args.text_file).read_text(encoding="utf-8")
    else:
        text = args.text

    output_path = args.output
    if not output_path:
        output_path = f"stream_output.{args.format}"
        audio_format = args.format
    else:
        ext = Path(output_path).suffix.lstrip(".").lower()
        audio_format = ext if ext else args.format

    synthesize_stream(
        text=text,
        voice=args.voice,
        output=output_path,
        style=args.style,
        styles=args.styles,
        audio_format=audio_format,
    )
    print(f"Saved streaming audio to {output_path}")


if __name__ == "__main__":
    main()
