"""Core data model and value normalization."""

from __future__ import annotations

import math
from typing import Iterable, List, Sequence


class MemoryError_(ValueError):
    """Raised for invalid memory configurations."""


# Kept name simple for imports
MemoryError = MemoryError_  # noqa: N816


class Memory:
    """A memory image: a list of integers plus a bit width and radix."""

    def __init__(self, values: Sequence[int], width: int, radix: int = 16, signed: bool = False):
        if width < 1:
            raise MemoryError_("width must be >= 1")
        if radix not in (2, 8, 10, 16):
            raise MemoryError_("radix must be one of 2, 8, 10, 16")
        if not values:
            raise MemoryError_("memory must contain at least one value")
        self.values = list(values)
        self.width = width
        self.radix = radix
        self.signed = signed
        self.depth = len(self.values)

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return (
            f"Memory(depth={self.depth}, width={self.width}, "
            f"radix={self.radix}, signed={self.signed})"
        )


def parse_value(text: str) -> int:
    """Parse a single integer literal, accepting ``0x``, ``0b``, ``0o`` prefixes."""
    try:
        return int(text.strip(), 0)
    except ValueError:
        raise MemoryError_(f"invalid integer literal: {text!r}") from None


def parse_values(text: str) -> List[int]:
    """Parse a comma- and/or whitespace-separated list of integers."""
    parts = [p for p in text.replace(",", " ").split() if p]
    if not parts:
        raise MemoryError_("no values found in input")
    return [parse_value(p) for p in parts]


def parse_file(path: str) -> List[int]:
    """Parse a text file of integer values (one or more per line, '#' comments)."""
    values: List[int] = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.split("#", 1)[0].split("//", 1)[0]
            line = line.split(";", 1)[0]
            parts = [p for p in line.replace(",", " ").split() if p]
            values.extend(parse_value(p) for p in parts)
    if not values:
        raise MemoryError_(f"no values found in {path}")
    return values


def normalize_values(
    values: Iterable[int], width: int, signed: bool = False
) -> List[int]:
    """Normalize raw integers into representable values for the given width.

    * Unsigned: values are masked to ``width`` bits (high bits dropped).
    * Signed: values are wrapped into the two's-complement range
      ``[-2**(width-1), 2**(width-1) - 1]``.
    """
    half = 1 << (width - 1)
    result: List[int] = []
    for v in values:
        v = int(v)
        if signed:
            result.append((v + half) % (half * 2) - half)
        else:
            result.append(v & ((1 << width) - 1))
    return result


def format_value(value: int, width: int, radix: int) -> str:
    """Format a single already-normalized value in the given radix."""
    if radix == 2:
        return f"{value:0{width}b}"
    if radix == 8:
        digits = math.ceil(width / 3)
        return f"{value:0{digits}o}"
    if radix == 16:
        digits = math.ceil(width / 4)
        return f"{value:0{digits}X}"
    # radix 10 may be negative for signed memories
    return str(value)


RADIX_NAMES = {2: "BIN", 8: "OCT", 10: "DEC", 16: "HEX"}
