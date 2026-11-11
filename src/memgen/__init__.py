"""memgen - generate memory initialization files for FPGA synthesis tools.

Supported formats:

* ``.coe`` - Xilinx Vivado / ISE coefficient files (Block RAM init)
* ``.mem`` - Verilog ``$readmemh`` / ``$readmemb`` files (Xilinx style)
* ``.mif`` - Intel Quartus / Altera memory initialization files

Example::

    from memgen import generate
    text = generate("coe", sine(16), width=16, radix=16)
"""

from memgen.core import Memory, normalize_values
from memgen.generators import (
    constant,
    expr,
    rampl,
    random_data,
    sine,
    sawtooth,
    square,
    triangle,
)
from memgen.formats import format_coe, format_mem, format_mif, generate

__version__ = "1.0.0"

__all__ = [
    "Memory",
    "normalize_values",
    "constant",
    "expr",
    "rampl",
    "random_data",
    "sine",
    "sawtooth",
    "square",
    "triangle",
    "format_coe",
    "format_mem",
    "format_mif",
    "generate",
    "__version__",
]
