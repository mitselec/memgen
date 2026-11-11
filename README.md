# memgen

Generate memory initialization files for FPGA synthesis tools — a modernized
version of the old [BlockRam_COE](https://github.com/mitselec/BlockRam_COE)
snippet for creating Xilinx Block RAM coefficient files in Python. The
original 2017 script is preserved in [`legacy/`](legacy/).

Supported output formats:

| Format | Tool                          | Use                                       |
| ------ | ----------------------------- | ----------------------------------------- |
| `.coe` | Xilinx Vivado / ISE           | Block Memory Generator / Block RAM init   |
| `.mem` | Any Verilog simulator         | `$readmemh` / `$readmemb`                 |
| `.mif` | Intel Quartus / Altera        | RAM: 1-PORT / ROM memory init             |

## Install

Using a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows (source .venv/bin/activate on Linux/macOS)
pip install -e .
```

Python 3.8+, no dependencies.

## CLI usage

```
memgen <coe|mem|mif> [data source] [options]
```

Common options:

* `-w, --width N` — word width in bits (default: 16)
* `--radix 2|8|10|16` — value radix (default: 16)
* `--signed` — treat data as signed two's complement
* `-o, --out FILE` — write to a file (default: stdout)

Data sources (mutually exclusive):

* `--data "0x10, 20, -3"` — explicit values (accepts `0x`/`0b`/`0o` prefixes)
* `--input FILE` — read values from a text file (`#` and `//` comments allowed)
* `--wave NAME` — generate a waveform (requires `-n/--depth`)

Waveforms: `sine`, `saw`, `triangle`, `square`, `constant`, `ramp`, `random`, `expr`

Waveform options: `-n/--depth N`, `--cycles F`, `--scale F`, `--offset F`,
`--phase F` (sine), `--reverse` (saw), `--duty F` (square), `--value N`
(constant), `--start/--step` (ramp), `--seed/--min/--max` (random),
`--expr "x*x"` (expr).

### Examples

A 1024×16 sine LUT for a Vivado Block RAM:

```bash
memgen coe --wave sine --depth 1024 --width 16 --cycles 4 --out sine_lut.coe
```

A 256×8 signed triangle wave as a Verilog `.mem` file:

```bash
memgen mem --wave triangle --depth 256 --width 8 --signed -o tri.mem
```

Read values from a file and emit a Quartus `.mif`:

```bash
memgen mif --input coefficients.txt --width 12 -o rom.mif
```

Custom expression (square root LUT):

```bash
memgen coe --wave expr --expr "round(sqrt(x)*255)" --depth 64 --width 8
```

Random test data (deterministic, seeded):

```bash
memgen mem --wave random --seed 42 --min 0 --max 65535 --depth 512
```

## Library usage

```python
from memgen import sine, generate

values = sine(256, cycles=2)
print(generate("coe", values, width=16))
```

```python
from memgen import format_mem, format_mif, format_coe

format_coe(values, width=16, radix=16, comment="my sine LUT")
format_mem(values, width=8, radix=2)    # for $readmemb
format_mif(values, width=12, radix=10)  # for Quartus
```

Signed data is emitted as two's complement in non-decimal radices and as
negative numbers in decimal radix. Values outside the word width are masked
(wrapped) rather than rejected, matching how the hardware would store them.

## Notes

* `.mem` files only support radix 2 (`$readmemb`) or 16 (`$readmemh`).
* The `expr` wave evaluates a Python expression in `x` with common `math`
  functions available (`sin`, `sqrt`, `pi`, ...). It uses `eval` — only use it
  with trusted, local input.

## Tests

```bash
.venv\Scripts\python -m unittest discover -s tests
```

## License

Apache License 2.0 — see [LICENSE](LICENSE).
