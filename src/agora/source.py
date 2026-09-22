"""Bounded, revision-pinned UTF-8 file reads. No models or external stores."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat

MAX_SOURCE_BYTES = 16 * 1024 * 1024
MAX_ENVELOPE_BYTES = 8 * 1024 * 1024
MAX_UNITS = 16384


class SourceError(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode_record(record):
    """Exact wire encoding used for the envelope budget, including newline."""
    return (json.dumps(record, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def integer(value, minimum, maximum, diagnostic):
    if type(value) is not int or not minimum <= value <= maximum:
        raise SourceError(diagnostic)
    return value


def bounded(record, budget):
    integer(budget, 1, MAX_ENVELOPE_BYTES, "invalid_envelope_budget")
    if len(encode_record(record)) > budget:
        raise SourceError("envelope_budget_exceeded")
    return record


class FileSourceAdapter:
    """Read current bytes only if they match the caller's pinned revision.

    The hash identifies received bytes, not authenticity or historical availability.
    Every operation reads a bounded full copy locally. Returned records are detached.
    """
    def __init__(self, path, source_id, max_source_bytes=MAX_SOURCE_BYTES):
        if type(source_id) is not str or not source_id.strip() or len(source_id) > 200:
            raise SourceError("invalid_source_id")
        try:
            source_id.encode("utf-8")
        except UnicodeError as exc:
            raise SourceError("invalid_source_id") from exc
        self.path = Path(path)
        self.source_id = source_id
        self.max_source_bytes = integer(max_source_bytes, 1, MAX_SOURCE_BYTES,
                                        "invalid_source_budget")

    def _read(self, revision):
        if type(revision) is not str or re.fullmatch(r"[0-9a-f]{64}", revision) is None:
            raise SourceError("invalid_revision")
        # Nonblocking open prevents a pipe masquerading as a file from hanging.
        fd = os.open(self.path, os.O_RDONLY | os.O_NONBLOCK)
        with os.fdopen(fd, "rb") as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode):
                raise SourceError("not_regular_file")
            if before.st_size > self.max_source_bytes:
                raise SourceError("source_budget_exceeded")
            data = stream.read(self.max_source_bytes + 1)
            after = os.fstat(stream.fileno())
        if len(data) > self.max_source_bytes:
            raise SourceError("source_budget_exceeded")
        if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
                after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise SourceError("source_changed_during_read")
        if digest(data) != revision:
            raise SourceError("source_revision_mismatch")
        try:
            data.decode("utf-8")
        except UnicodeError as exc:
            raise SourceError("invalid_utf8") from exc
        if not data:
            raise SourceError("empty_source")
        return data

    def _identity(self, revision, size):
        return {"source_id": self.source_id, "revision": revision,
                "revision_kind": "sha256", "source_bytes": size,
                "media_type": "text/plain; charset=utf-8",
                "provenance": {"adapter": "file", "identity": "caller_declared"}}

    def inventory(self, revision, unit_bytes=4096, envelope_budget=MAX_ENVELOPE_BYTES):
        integer(unit_bytes, 4, 65536, "invalid_unit_size")
        data = self._read(revision)
        units = []
        start = 0
        while start < len(data):
            if len(units) == MAX_UNITS:
                raise SourceError("unit_limit_exceeded")
            end = min(start + unit_bytes, len(data))
            while end < len(data) and data[end] & 0xC0 == 0x80:
                end -= 1
            units.append({"start_byte": start, "end_byte": end,
                          "sha256": digest(data[start:end])})
            start = end
        return bounded({"schema": "agora/source-inventory/v0.1",
                        "source": self._identity(revision, len(data)),
                        "unit_kind": "utf8_byte_ranges", "units": units,
                        "inventory_complete": True, "content_delivered": False,
                        "evidence_sufficiency": "unknown"}, envelope_budget)

    def fetch(self, revision, ranges, content_budget=65536,
              envelope_budget=MAX_ENVELOPE_BYTES):
        integer(content_budget, 1, MAX_SOURCE_BYTES, "invalid_content_budget")
        if type(ranges) is not list or not 1 <= len(ranges) <= 256:
            raise SourceError("invalid_ranges")
        data = self._read(revision)
        previous = 0
        count = 0
        spans = []
        for pair in ranges:
            if type(pair) not in (tuple, list) or len(pair) != 2:
                raise SourceError("invalid_range")
            start, end = pair
            integer(start, 0, len(data) - 1, "invalid_range")
            integer(end, start + 1, len(data), "invalid_range")
            if start < previous:
                raise SourceError("ranges_overlap_or_unsorted")
            previous = end
            count += end - start
            if count > content_budget:
                raise SourceError("content_budget_exceeded")
            raw = data[start:end]
            try:
                text = raw.decode("utf-8")
            except UnicodeError as exc:
                raise SourceError("range_splits_utf8") from exc
            spans.append({"start_byte": start, "end_byte": end,
                          "sha256": digest(raw), "text": text})
        return bounded({"schema": "agora/source-envelope/v0.1",
                        "source": self._identity(revision, len(data)), "spans": spans,
                        "delivered_bytes": count, "integrity": "matches_requested_revision",
                        "coverage": "full" if count == len(data) else "partial",
                        "truncated": False, "redacted": False,
                        "evidence_sufficiency": "unknown"}, envelope_budget)


def parse_range(value):
    try:
        start, end = value.split(":")
        return (int(start), int(end))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("range must be START:END in UTF-8 bytes") from exc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("inventory", "fetch"))
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--max-source-bytes", type=int, default=MAX_SOURCE_BYTES)
    parser.add_argument("--envelope-budget", type=int, default=MAX_ENVELOPE_BYTES)
    parser.add_argument("--unit-bytes", type=int)
    parser.add_argument("--range", type=parse_range, action="append")
    parser.add_argument("--content-budget", type=int)
    args = parser.parse_args()
    if args.action == "inventory" and (args.range is not None or args.content_budget is not None):
        parser.error("inventory accepts unit-bytes, not ranges/content-budget")
    if args.action == "fetch" and (not args.range or args.unit_bytes is not None):
        parser.error("fetch requires ranges and does not accept unit-bytes")
    try:
        adapter = FileSourceAdapter(args.source, args.source_id, args.max_source_bytes)
        if args.action == "inventory":
            result = adapter.inventory(args.sha256, args.unit_bytes if args.unit_bytes is not None else 4096,
                                       args.envelope_budget)
        else:
            result = adapter.fetch(args.sha256, args.range,
                                   args.content_budget if args.content_budget is not None else 65536,
                                   args.envelope_budget)
        with args.out.open("xb") as stream:
            stream.write(encode_record(result))
    except (OSError, SourceError) as exc:
        parser.exit(2, "Source operation failed: " +
                    (str(exc) if isinstance(exc, SourceError) else type(exc).__name__) + "\n")
    print(json.dumps({"status": "complete", "action": args.action,
                      "model_calls": 0, "memory_writes": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
