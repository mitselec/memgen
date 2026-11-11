"""Built-in waveform and pattern generators.

All waveform generators produce normalized signed floats in ``[-1.0, 1.0]``
which are then scaled by ``scale`` and shifted by ``offset`` and rounded to
integers. Pass ``scale=None`` (the default) to use the memory's full scale.
"""

from __future__ import annotations

import math
import random
from typing import List, Optional, Sequence

__all__ = [
    "sine",
    "sawtooth",
    "triangle",
    "square",
    "constant",
    "rampl",
    "random_data",
    "expr",
]


def _finish(
    raw: Sequence[float], depth: int, scale: Optional[float], offset: float, full_scale: int
) -> List[int]:
    s = full_scale if scale is None else scale
    return [int(round(offset + v * s)) for v in raw]


def sine(
    depth: int,
    cycles: float = 1.0,
    scale: Optional[float] = None,
    offset: float = 0.0,
    phase: float = 0.0,
    full_scale: int = 127,
) -> List[int]:
    """Integer sinusoid sampled over ``depth`` points, ``cycles`` periods."""
    raw = [math.sin(2.0 * math.pi * cycles * i / depth + phase) for i in range(depth)]
    return _finish(raw, depth, scale, offset, full_scale)


def sawtooth(
    depth: int,
    cycles: float = 1.0,
    reverse: bool = False,
    scale: Optional[float] = None,
    offset: float = 0.0,
    full_scale: int = 127,
) -> List[int]:
    """Sawtooth ramp, rising (or falling if ``reverse``) ``cycles`` times."""
    sign = -1.0 if reverse else 1.0
    raw = [sign * (2.0 * ((cycles * i / depth) % 1.0) - 1.0) for i in range(depth)]
    return _finish(raw, depth, scale, offset, full_scale)


def triangle(
    depth: int,
    cycles: float = 1.0,
    scale: Optional[float] = None,
    offset: float = 0.0,
    full_scale: int = 127,
) -> List[int]:
    """Triangle wave, ``cycles`` periods over ``depth`` points."""
    raw = []
    for i in range(depth):
        p = (cycles * i / depth) % 1.0
        raw.append(4.0 * abs(p - 0.5) - 1.0)
    return _finish(raw, depth, scale, offset, full_scale)


def square(
    depth: int,
    cycles: float = 1.0,
    duty: float = 0.5,
    scale: Optional[float] = None,
    offset: float = 0.0,
    full_scale: int = 127,
) -> List[int]:
    """Square wave with the given duty cycle."""
    if not 0.0 < duty < 1.0:
        raise ValueError("duty must be in (0, 1)")
    raw = [1.0 if ((cycles * i / depth) % 1.0) < duty else -1.0 for i in range(depth)]
    return _finish(raw, depth, scale, offset, full_scale)


def constant(value: int, depth: int) -> List[int]:
    """A constant value repeated ``depth`` times."""
    return [value] * depth


def rampl(depth: int, start: int = 0, step: int = 1) -> List[int]:
    """A linear ramp (counter): ``start + i * step``."""
    return [start + i * step for i in range(depth)]


def random_data(depth: int, seed: int = 0, lo: int = 0, hi: int = 255) -> List[int]:
    """Deterministic pseudo-random data between ``lo`` and ``hi`` inclusive."""
    rng = random.Random(seed)
    return [rng.randint(lo, hi) for _ in range(depth)]


def _make_math_env(x: int) -> dict:
    env = {
        "x": x,
        "math": math,
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
    }
    for name in (
        "sin cos tan asin acos atan atan2 sqrt exp log log2 log10 pow "
        "floor ceil fabs hypot degrees radians"
    ).split():
        env[name] = getattr(math, name)
    env["abs"] = abs
    env["min"] = min
    env["max"] = max
    env["round"] = round
    return env


def expr(formula: str, depth: int) -> List[int]:
    """Evaluate ``formula`` for ``x`` in ``0..depth-1``.

    The expression has access to ``x`` and common ``math`` functions as bare
    names (``sin``, ``sqrt``, ``pi``, ...). Note: this uses ``eval`` and is
    intended for trusted, local use.
    """
    result: List[int] = []
    code = compile(formula, "<expr>", "eval")
    for i in range(depth):
        try:
            result.append(int(round(eval(code, {"__builtins__": {}}, _make_math_env(i)))))
        except Exception as exc:  # noqa: BLE001 - report a friendly message
            raise ValueError(f"expr failed for x={i}: {exc}") from None
    return result
