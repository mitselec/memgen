# Legacy

This folder preserves the original 2017 snippet this project grew out of —
kept for history's sake, not for use.

## `blockram_template.py`

The original template script, as committed in 2017. It was a starting
point, not a standalone program: the intended workflow was to copy the
file, insert your own function where the placeholder comment says
*("Insert a function of your choice to fill line after line the designated
value with a comma and a newline in the end")*, and adapt the remaining
pieces as needed. It generates a Xilinx `.coe` template for a Block Memory
Generator with radix 16 and width 16, then truncates the trailing comma
and replaces it with `;`.

Things you were expected to change while filling it in:

* Import the `os` module (used for `os.SEEK_END` in the trailer logic).
* Fix the indentation of the `with open(...)` block (flattened when the
  snippet was committed, most likely during copy-paste from the blog post).
* Replace the `"wb"` mode with `"w"` if you write text instead of bytes.
* Point the two `open()` calls at the same filename, whatever you choose.
* Add `parentheses` to the `fo.close` calls, or rely on `with` closing it.

The blog post that accompanied it lives at:
<https://mitselec.wordpress.com/2017/08/01/coe-file-creation-in-python/>

## Replacement

Everything this template did by hand (and much more — `.mem` and `.mif`
output, waveform generators, signed data, arbitrary widths) is now
automated by the `memgen` tool documented in the [README](../README.md).
