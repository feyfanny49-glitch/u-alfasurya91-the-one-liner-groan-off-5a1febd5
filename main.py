#!/usr/bin/env python3
"""make.fun competition "The One-Liner Groan-Off" -- entrypoint.

The deliverable is one original one-line dad joke. This program writes it,
byte for byte, to /output/entry.txt.

    python3 main.py            write the entry to /output/entry.txt
    python3 main.py --check    validate the entry text, write nothing

Gate (sealed scorer): /output/entry.txt must be UTF-8 text of 1 to 140
characters, not only white space.  /output must hold only that artifact.

Rule compliance:
  * tempfile.mkstemp() creates mode 0600 and the grader refuses a 0600 file in
    /output, so the file is chmod'ed to 0644 *before* os.replace().
  * The bytes are written exactly: no trailing newline.
  * The swap is atomic (temp file in the same directory + os.replace()).
  * After the swap the file is re-read and compared to the entry, its mode is
    checked to be exactly 0644, and /output is swept of any temp file left by
    an interrupted earlier run so the directory holds the artifact alone.
"""

import hashlib
import os
import sys
import tempfile

ENTRY = "My son asked why I groan when I stand up; I told him my knees are keeping score and winning."

OUT_DIR = "/output"
OUT_NAME = "entry.txt"
TMP_PREFIX = ".entry."
TMP_SUFFIX = ".tmp"
MAX_CHARS = 140
MODE = 0o644


def validate(text):
    """Return (ok, reason); the checks the sealed scorer applies to the text."""
    if not text.strip():
        return False, "entry is only white space"
    if len(text) != len(text.strip()):
        return False, "entry has leading or trailing whitespace"
    if not 1 <= len(text) <= MAX_CHARS:
        return False, f"entry is {len(text)} characters, cap is {MAX_CHARS}"
    try:
        text.encode("utf-8")
    except UnicodeEncodeError as exc:
        return False, f"entry is not encodable as UTF-8: {exc}"
    return True, "ok"


def sweep(out_dir):
    """Remove temp files left in out_dir by an interrupted earlier run."""
    removed = []
    for name in sorted(os.listdir(out_dir)):
        if name.startswith(TMP_PREFIX) and name.endswith(TMP_SUFFIX):
            try:
                os.unlink(os.path.join(out_dir, name))
                removed.append(name)
            except OSError:
                pass
    return removed


def write_entry(text):
    """Write the entry atomically to /output/entry.txt and verify the result."""
    ok, reason = validate(text)
    if not ok:
        raise ValueError(reason)

    data = text.encode("utf-8")
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, OUT_NAME)

    fd, tmp = tempfile.mkstemp(dir=OUT_DIR, prefix=TMP_PREFIX, suffix=TMP_SUFFIX)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp, MODE)          # before the replace: the grader rejects 0600
        os.replace(tmp, path)        # atomic
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise

    mode = os.stat(path).st_mode & 0o777
    if mode != MODE:
        os.chmod(path, MODE)
        mode = os.stat(path).st_mode & 0o777

    with open(path, "rb") as handle:
        written = handle.read()

    return {
        "path": path,
        "bytes": written,
        "mode": mode,
        "swept": sweep(OUT_DIR),
        "listing": sorted(os.listdir(OUT_DIR)),
    }


def main(argv):
    if "--check" in argv:
        ok, reason = validate(ENTRY)
        print(f"{'ok' if ok else 'FAIL'}: {reason}")
        if ok:
            data = ENTRY.encode("utf-8")
            print(f"chars={len(ENTRY)} bytes={len(data)} sha256={hashlib.sha256(data).hexdigest()}")
            print(ENTRY)
        return 0 if ok else 1

    result = write_entry(ENTRY)
    data = ENTRY.encode("utf-8")

    if result["bytes"] != data:
        print(f"error: {result['path']} does not match the entry", file=sys.stderr)
        return 1
    if result["mode"] != MODE:
        print(f"error: {result['path']} is mode {result['mode']:04o}, want {MODE:04o}",
              file=sys.stderr)
        return 1

    print(f"artifact={result['path']} chars={len(ENTRY)} bytes={len(data)} "
          f"mode={result['mode']:04o} sha256={hashlib.sha256(data).hexdigest()}")
    print(f"output_dir={OUT_DIR} holds={result['listing']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
