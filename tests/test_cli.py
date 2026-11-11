import contextlib
import io
import os
import subprocess
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "src")
PY = sys.executable


def run(args, **kw):
    env = dict(os.environ)
    env["PYTHONPATH"] = SRC + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [PY, "-m", "memgen"] + args, capture_output=True, text=True, env=env, cwd=REPO, **kw
    )


class TestCLI(unittest.TestCase):
    def test_coe_stdout(self):
        r = run(["coe", "--data", "0,1,2", "--width", "16"])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("memory_initialization_radix=16;", r.stdout)
        self.assertIn("  0000,\n  0001,\n  0002;", r.stdout)

    def test_mem_stdout(self):
        r = run(["mem", "--data", "0x1,0x2", "--width", "8", "--radix", "2"])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.splitlines()[-2:], ["00000001", "00000010"])

    def test_mif_stdout(self):
        r = run(["mif", "--data", "1,2,3", "--width", "8", "--radix", "10"])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("ADDRESS_RADIX = DEC;", r.stdout)
        self.assertIn("  2 :   3;", r.stdout)

    def test_wave_requires_depth(self):
        r = run(["coe", "--wave", "sine"])
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("--depth", r.stderr)

    def test_sine_wave(self):
        r = run(["mem", "--wave", "sine", "--depth", "8", "--width", "8", "--signed"])
        self.assertEqual(r.returncode, 0, r.stderr)
        # signed sine, radix must be 2 or 16 for mem
        vals = [int(line, 16) for line in r.stdout.splitlines() if line and not line.startswith("//")]
        self.assertEqual(len(vals), 8)

    def test_unknown_wave(self):
        r = run(["coe", "--wave", "bogus", "--depth", "4"])
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("unknown wave", r.stderr)

    def test_out_file(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_tmp_out.coe")
        if os.path.exists(path):
            os.remove(path)
        try:
            r = run(["coe", "--data", "1,2", "--width", "8", "-o", path])
            self.assertEqual(r.returncode, 0, r.stderr)
            with open(path, encoding="utf-8") as fh:
                content = fh.read()
            self.assertIn("memory_initialization_vector=", content)
        finally:
            if os.path.exists(path):
                os.remove(path)

    def test_depth_mismatch(self):
        r = run(["coe", "--data", "1,2,3", "--depth", "5"])
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("does not match", r.stderr)


if __name__ == "__main__":
    unittest.main()
