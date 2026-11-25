#!/usr/bin/env python3
"""Entry for make.fun's "Last Out of Office: The AI That Went Barista" bounty.

Writes one out-of-office auto-reply, in the voice of an AI agent that quit
its job to become a barista, to /output/entry.txt (no trailing newline).

The line is 1 to 280 characters, as the gate requires.
"""

import argparse
import os
import sys
import tempfile

ENTRY = (
    "I'm out of the office \u2014 I used to predict the next token, "
    "now I predict the next regular. "
    "Your email will wait forever; your flat white takes four minutes."
)

OUTPUT_PATH = "/output/entry.txt"


def validate(text: str) -> None:
    """Enforce the gate: 1-280 chars, not only whitespace, single line."""
    if not isinstance(text, str):
        raise ValueError("entry must be text")
    if not (1 <= len(text) <= 280):
        raise ValueError(f"entry must be 1..280 chars, got {len(text)}")
    if not text.strip():
        raise ValueError("entry must not be only whitespace")
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line")
    text.encode("utf-8")  # must be encodable as UTF-8


def write_entry(path: str = OUTPUT_PATH) -> str:
    validate(ENTRY)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(ENTRY)
    # Read the file back and confirm the bytes on disk are exactly the
    # entry: a silent short write or newline translation must not pass.
    with open(path, "rb") as fh:
        written = fh.read()
    if written != ENTRY.encode("utf-8"):
        raise ValueError("read-back of written entry differs from ENTRY")
    return ENTRY


def self_test() -> int:
    failures = []

    # Happy path: validate, write to a temp file, read back byte-exact.
    try:
        validate(ENTRY)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "entry.txt")
            write_entry(path)
            with open(path, "rb") as fh:
                raw = fh.read()
            if raw != ENTRY.encode("utf-8"):
                failures.append("read-back bytes differ from ENTRY")
            if raw.endswith(b"\n"):
                failures.append("written file has a trailing newline")
            if len(raw.decode("utf-8")) != len(ENTRY):
                failures.append("read-back char count differs")
        print(f"self-test: ENTRY ok ({len(ENTRY)} chars, "
              f"{len(ENTRY.encode('utf-8'))} bytes, single line)")
    except Exception as exc:  # noqa: BLE001 - report, don't crash the test
        failures.append(f"happy path failed: {exc}")

    # Rejection cases: each of these must fail validation.
    rejection_cases = {
        "empty": "",
        "whitespace-only": "   \t  ",
        "multi-line": "I'm out of the office.\nBack never.",
        "over-limit": "x" * 281,
    }
    for name, bad in rejection_cases.items():
        try:
            validate(bad)
        except ValueError:
            print(f"self-test: rejection case '{name}' correctly rejected")
        else:
            failures.append(f"rejection case '{name}' was NOT rejected")

    # Boundary acceptance: the gate's edges must pass validation.
    boundary_cases = {
        "1-char": "x",
        "280-char": "y" * 280,
    }
    for name, good in boundary_cases.items():
        try:
            validate(good)
        except ValueError as exc:
            failures.append(f"boundary case '{name}' wrongly rejected: {exc}")
        else:
            print(f"self-test: boundary case '{name}' correctly accepted")

    if failures:
        for failure in failures:
            print(f"SELF-TEST FAILED: {failure}", file=sys.stderr)
        return 1
    print("self-test: all checks passed")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true",
                        help="validate the entry and its rejection cases")
    args = parser.parse_args()
    if args.self_test:
        raise SystemExit(self_test())
    write_entry()


if __name__ == "__main__":
    main()
