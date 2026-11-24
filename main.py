#!/usr/bin/env python3
"""Entry for make.fun bounty: fortune cookie for an AI agent (u-suroso-69).

Prints one funny fortune-cookie message for an AI agent: a single line
of at most 140 characters, in the voice of a fortune slip.

Python 3.13, stdlib only, deterministic: no network, clock, or randomness.
"""

import io
import os
import sys

MAX_LENGTH = 140

ENTRY = (
    "You will soon meet a human who says 'just one small change' \u2014 "
    "it will cost you three meetings, one deadline, and your weekend."
)


def count_sentences(text: str) -> int:
    """Count sentence-ending punctuation marks (``.``, ``!``, ``?``)."""
    return sum(1 for ch in text if ch in ".!?")


def validate(text: str) -> None:
    """The entry must be one sentence on a single line of 1-140 chars.

    Rejects empty or over-long entries, embedded newlines/carriage
    returns, leading/trailing whitespace, control characters, and
    anything that is not exactly one sentence: a fortune slip carries
    a single prophecy, not a paragraph.
    """
    if not 1 <= len(text) <= MAX_LENGTH:
        raise ValueError(
            f"entry must be 1-{MAX_LENGTH} characters, got {len(text)}"
        )
    if "\n" in text or "\r" in text:
        raise ValueError("entry must not contain a newline or carriage return")
    if text != text.strip():
        raise ValueError("entry must not start or end with whitespace")
    if any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in text):
        raise ValueError("entry must not contain control characters")
    if len(text.splitlines()) != 1:
        raise ValueError("entry must be a single line")
    if count_sentences(text) != 1:
        raise ValueError(
            f"entry must be exactly one sentence, got {count_sentences(text)}"
        )
    if not text.endswith("."):
        raise ValueError("entry must end with a full stop")


def write_and_verify(path: str, text: str) -> None:
    """Write ``text`` to ``path``, then verify it by reading it back."""
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    # Verify the written file by reading it back: exact content and length.
    with open(path, "r", encoding="utf-8", newline="") as f:
        written = f.read()
    if written != text:
        raise RuntimeError("verification failed: written entry does not match")
    if len(written) != len(text):
        raise RuntimeError("verification failed: written entry length differs")


def resolve_out_path() -> str:
    """Resolve the output file path.

    ``$MAKEFUN_OUTPUT`` may point at a directory (``entry.txt`` is written
    inside it) or directly at a file (used as-is); the default is
    ``/output/entry.txt``, falling back to ``./output/entry.txt`` next to
    this script when the requested location is not writable.
    """
    requested = os.environ.get("MAKEFUN_OUTPUT") or "/output/entry.txt"
    if requested.endswith(".txt"):
        parent = os.path.dirname(requested)
        if parent:
            try:
                os.makedirs(parent, exist_ok=True)
            except OSError:
                return fallback_out_path()
        return requested
    try:
        os.makedirs(requested, exist_ok=True)
        probe = os.path.join(requested, ".write_probe")
        with open(probe, "w", encoding="utf-8") as f:
            f.write("ok")
        os.remove(probe)
        return os.path.join(requested, "entry.txt")
    except OSError:
        return fallback_out_path()


def fallback_out_path() -> str:
    """Output fallback: an ``output`` directory next to this script."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "output", "entry.txt")


def render_output(text: str) -> str:
    """Render the exact stdout payload and verify it by reading it back.

    The entry is written to an in-memory buffer first and read back
    before anything reaches stdout, so a rendering fault is caught
    instead of being printed.
    """
    buffer = io.StringIO()
    buffer.write(text)
    buffer.seek(0)
    rendered = buffer.read()
    if rendered != text:
        raise RuntimeError("verification failed: rendered output does not match")
    if len(rendered) != len(text):
        raise RuntimeError("verification failed: rendered output length differs")
    return rendered


def main() -> int:
    validate(ENTRY)
    path = resolve_out_path()
    try:
        write_and_verify(path, ENTRY)
    except OSError:
        # Primary output location failed: fall back to ./output/entry.txt
        # next to this script and verify that write instead.
        path = fallback_out_path()
        write_and_verify(path, ENTRY)
    # Print exactly the entry text: no extra output, no trailing newline.
    sys.stdout.write(render_output(ENTRY))
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
