# Legacy

This folder preserves the original 2017 snippet this project grew out of —
kept for history's sake, not for use.

## `blockram_template.py`

The original script, as committed in 2017. It emitted an empty Xilinx
`.coe` template for a Block Memory Generator with radix 16 and width 16,
leaving a comment placeholder where the user was supposed to insert their
own function to fill in values, and then truncated the trailing comma and
replaced it with `;`.

**Note:** it never actually ran as written. Known defects:

* `os.SEEK_END` is used, but the `os` module is never imported.
* The body of the `with open(...)` block (lines 26–28) is not indented,
  which is a `SyntaxError`.
* `fo.close` is missing the call parentheses in both places, so the file
  was never explicitly closed (CPython usually closed it at exit).
* It writes no actual data vector, so the resulting `.coe` would be invalid.

The blog post that accompanied it lives at:
<https://mitselec.wordpress.com/2017/08/01/coe-file-creation-in-python/>

## Replacement

Everything this snippet attempted (and much more — `.mem` and `.mif`
output, waveform generators, signed data, arbitrary widths) is now handled
by the `memgen` tool documented in the [README](../README.md).
