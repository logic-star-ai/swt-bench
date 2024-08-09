import subprocess
import sys


def test_no_trace():
    print("not shown in trace!")


if len(sys.argv) > 1:
    test_no_trace()
else:
    subprocess.run([sys.executable, __file__, "--arg"])
