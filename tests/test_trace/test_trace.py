import pathlib
import sys
import tempfile
import subprocess
import json
import unittest

TRACE_PATH = pathlib.Path(__file__).parent.parent.parent / "src" / "auxillary_src" / "trace.py"
FOO_PATH = pathlib.Path(__file__).parent / "foo.py"
FOO_SUBPROCESS_PATH = pathlib.Path(__file__).parent / "foo_subprocess.py"
FOO_MULTIPROCESS_PATH = pathlib.Path(__file__).parent / "foo_multiprocess.py"

def test_trace():
    with tempfile.NamedTemporaryFile(suffix=".jsonl") as f:
        subprocess.run([sys.executable, TRACE_PATH, "--count", "-C", f.name, "--include-pattern", ".*foo.py", FOO_PATH], check=True)
        found_line_3 = False
        foo_path = str(FOO_PATH.absolute())
        with open(f.name) as f:
            for line in f:
                line_dict = json.loads(line)
                if line_dict.get(foo_path, {}).get("3", 0) > 0:
                    found_line_3 = True
    assert found_line_3

def test_trace_subprocess():
    with tempfile.NamedTemporaryFile(suffix=".jsonl") as f:
        subprocess.run([sys.executable, TRACE_PATH, "--count", "-C", f.name, "--include-pattern", ".*foo_subprocess.py", FOO_SUBPROCESS_PATH], check=True)
        found_line_6 = False
        foo_path = str(FOO_SUBPROCESS_PATH.absolute())
        with open(f.name) as f:
            for line in f:
                line_dict = json.loads(line)
                if line_dict.get(foo_path, {}).get("6", 0) > 0:
                    found_line_6 = True
    assert found_line_6

@unittest.skip("Multiprocessing is not supported yet")
def test_trace_multiprocess():
    with tempfile.NamedTemporaryFile(suffix=".jsonl") as f:
        subprocess.run([sys.executable, TRACE_PATH, "--count", "-C", f.name, "--include-pattern", ".*foo.*.py", FOO_MULTIPROCESS_PATH], check=True)
        found_line_3 = False
        foo_path = str(FOO_PATH.absolute())
        with open(f.name) as f:
            for line in f:
                line_dict = json.loads(line)
                if line_dict.get(foo_path, {}).get("3", 0) > 0:
                    found_line_3 = True
    assert found_line_3
