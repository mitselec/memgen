"""memgen command line interface."""

from __future__ import annotations

import argparse
import sys

from memgen import __version__
from memgen.core import MemoryError, parse_file, parse_values
from memgen.formats import generate


def _add_common(p: argparse.ArgumentParser) -> None:
    p.add_argument("-w", "--width", type=int, default=16, help="memory word width in bits (default: 16)")
    p.add_argument("--radix", type=int, default=16, choices=(2, 8, 10, 16), help="value radix (default: 16)")
    p.add_argument("--signed", action="store_true", help="treat data as signed (two's complement)")
    p.add_argument("-o", "--out", default=None, help="output file (default: stdout)")


def _add_source(p: argparse.ArgumentParser) -> None:
    g = p.add_argument_group("data source").add_mutually_exclusive_group(required=True)
    g.add_argument("--data", help="explicit values, comma/space separated (accepts 0x prefixes)")
    g.add_argument("--input", help="text file of values ('#' and '//' comments allowed)")
    g.add_argument("--wave", help="built-in generator: sine, saw, triangle, square, constant, ramp, random, expr")


def _add_wave_opts(p: argparse.ArgumentParser) -> None:
    g = p.add_argument_group("generator options")
    g.add_argument("-n", "--depth", type=int, default=None, help="number of values to generate")
    g.add_argument("--cycles", type=float, default=1.0, help="wave periods across the memory (default: 1)")
    g.add_argument("--scale", type=float, default=None, help="amplitude scale (default: full scale, centered for unsigned)")
    g.add_argument("--offset", type=float, default=None, help="offset added after scaling (default: centered for unsigned, 0 for signed)")
    g.add_argument("--phase", type=float, default=0.0, help="sine phase in radians")
    g.add_argument("--reverse", action="store_true", help="falling sawtooth instead of rising")
    g.add_argument("--duty", type=float, default=0.5, help="square wave duty cycle (default: 0.5)")
    g.add_argument("--value", type=int, default=0, help="constant wave value (default: 0)")
    g.add_argument("--start", type=int, default=0, help="ramp start value (default: 0)")
    g.add_argument("--step", type=int, default=1, help="ramp step (default: 1)")
    g.add_argument("--seed", type=int, default=0, help="random seed (default: 0)")
    g.add_argument("--min", dest="lo", type=int, default=0, help="random minimum (default: 0)")
    g.add_argument("--max", dest="hi", type=int, default=255, help="random maximum (default: 255)")
    g.add_argument("--expr", dest="formula", default="x", help="expression in x for the 'expr' wave")


def _resolve_values(args: argparse.Namespace):
    if args.data is not None:
        values = parse_values(args.data)
        if args.depth is not None and args.depth != len(values):
            raise MemoryError(
                f"--depth {args.depth} does not match the {len(values)} provided values"
            )
        return values
    if args.input is not None:
        values = parse_file(args.input)
        if args.depth is not None and args.depth != len(values):
            raise MemoryError(
                f"--depth {args.depth} does not match the {len(values)} values in {args.input}"
            )
        return values

    depth = args.depth
    if depth is None:
        raise MemoryError("--depth is required when generating a wave")
    if depth < 1:
        raise MemoryError("--depth must be >= 1")
    from memgen import generators as G

    name = args.wave.strip().lower()
    full_scale = (1 << (args.width - 1)) - 1 if args.signed else (1 << args.width) - 1
    # Default scaling: signed -> span [-full, +full]; unsigned -> centered on mid-scale
    if args.signed:
        default_scale, default_offset = float(full_scale), 0.0
    else:
        default_scale, default_offset = full_scale / 2.0, full_scale / 2.0
    wave_kwargs = {
        "cycles": args.cycles,
        "scale": args.scale if args.scale is not None else default_scale,
        "offset": args.offset if args.offset is not None else default_offset,
        "full_scale": full_scale,
    }
    if name in ("sine", "sin"):
        return G.sine(depth, **wave_kwargs, phase=args.phase)
    if name in ("saw", "sawtooth"):
        return G.sawtooth(depth, **wave_kwargs, reverse=args.reverse)
    if name in ("tri", "triangle"):
        return G.triangle(depth, **wave_kwargs)
    if name in ("square", "sq"):
        return G.square(depth, **wave_kwargs, duty=args.duty)
    if name == "constant":
        return G.constant(args.value, depth)
    if name == "ramp":
        return G.rampl(depth, start=args.start, step=args.step)
    if name == "random":
        return G.random_data(depth, seed=args.seed, lo=args.lo, hi=args.hi)
    if name == "expr":
        return G.expr(args.formula, depth)
    raise MemoryError(f"unknown wave {args.wave!r}: " + "sine, saw, triangle, square, constant, ramp, random, expr")


def _run(args: argparse.Namespace) -> int:
    values = _resolve_values(args)
    text = generate(args.format, values, width=args.width, radix=args.radix, signed=args.signed)
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print(f"wrote {args.out} ({len(values)} words x {args.width} bits)", file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="memgen",
        description="Generate FPGA memory initialization files (.coe, .mem, .mif).",
        epilog="examples: memgen coe --wave sine --depth 256 --width 16 --out sine.coe",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="format", metavar="FORMAT", required=True)

    for fmt in ("coe", "mem", "mif"):
        p = sub.add_parser(fmt, help=f"generate a {fmt.upper() if fmt != 'mem' else '.mem'} file")
        _add_common(p)
        _add_source(p)
        _add_wave_opts(p)
        p.set_defaults(func=_run)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except MemoryError as exc:
        parser.error(str(exc))
    return 2  # pragma: no cover - parser.error exits


if __name__ == "__main__":
    sys.exit(main())
