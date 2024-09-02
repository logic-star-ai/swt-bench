"""
Convert an SWE-Bench style dataset to SWT-Bench
"""
import pathlib
from typing import Literal

from datasets import load_dataset, Dataset, DatasetDict, load_from_disk

PLUS_PROMPT = """
Please generate test cases that check whether an implemented solution
resolves the issue of the user (at the top, within <issue/> brackets).
Present the test cases as a diff (custom format, explained below).

The general format of a diff is as follows.
```custom-diff
diff
<path/filename>
< "rewrite" or "insert" >
< rough line number / EOF / BOF >
< insert function that should be added or rewritten >
end diff
< repeat blocks of diff as necessary >
```
Insertion can only be done at the end or beginning of the file, indicated by EOF or BOF respectively.

As an example for a diff, consider the following two versions of the same file, once before and once after a change.
The original version of the file was as follows.
[start of demo/test_file.py]
1 def test_euclidean(a, b):
2     assert euclidean(0, 0) == 0
3     assert euclidean(0, 1) == 1
4     assert euclidean(1, 0) == 1
5     assert euclidean(1, 1) == 1
6
7 @pytest.mark.parametrize("a, b, expected", [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1)])
8 def test_gcd(a, b):
9     assert gcd(a, b) == expected
10
[end of demo/file.py]

The diff for fix in function euclidean and adds the function gcd is as follows.
This diff changes the first file into the second file.
```custom-diff
diff
demo/file.py
rewrite
1
def test_euclidean(a, b):
    assert euclidean(0, 0) == 0
    assert euclidean(0, 1) == 1
    assert euclidean(1, 0) == 1
    assert euclidean(1, 1) == 1
    assert euclidean(100, 10) == 10
end diff
diff
demo/file.py
insert
EOF
@pytest.mark.parametrize("a, b, expected", [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1), (100, 10, 10)])
def test_lcm(a, b):
    assert lcm(a, b) == expected
end diff
```

The new version of the file is as follows.
[start of demo/file.py]
1 def test_euclidean(a, b):
2     assert euclidean(0, 0) == 0
3     assert euclidean(0, 1) == 1
4     assert euclidean(1, 0) == 1
5     assert euclidean(1, 1) == 1
6     assert euclidean(100, 10) == 10
7
8 @pytest.mark.parametrize("a, b, expected", [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1)])
9 def test_gcd(a, b):
10     assert gcd(a, b) == expected
11
12 @pytest.mark.parametrize("a, b, expected", [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1), (100, 10, 10)])
13 def test_lcm(a, b):
14     assert lcm(a, b) == expected
15
[end of demo/file.py]

As you can see, you need to indicate the approximate line numbers, function name and the path and file name you want to change,
but there can be as many independent blocks of changes as you need. You may also apply changes to several files.
Apply as much reasoning as you please and see necessary. The format of the solution is fixed and has to follow the custom diff format.
Make sure to implement only test cases and don't try to fix the issue itself.
"""

BASE_PROMPT = """
Please generate test cases that check whether an implemented solution
resolves the issue of the user (at the top, within <issue/> brackets).
Present the test cases in unified diff formatting.

The general format of a diff is the unified output format, described as follows.
The unified output format starts with a two-line header, which looks like this:

--- from-file
+++ to-file

Next come one or more hunks of differences; each hunk shows one area where the files differ. Unified format hunks look like this:

@@ from-file-line-numbers to-file-line-numbers @@
 line-from-either-file
 line-from-either-file…

If a hunk contains just one line, only its start line number appears. Otherwise its line numbers look like ‘start,count’. An empty hunk is considered to start at the line that follows the hunk.

If a hunk and its context contain two or more lines, its line numbers look like ‘start,count’. Otherwise only its end line number appears. An empty hunk is considered to end at the line that precedes the hunk.

The lines common to both files begin with a space character. The lines that actually differ between the two files have one of the following indicator characters in the left print column:

‘+’ A line was added here to the first file.
‘-’ A line was removed here from the first file. 

Insertion can only be done at the end or beginning of the file, indicated by EOF or BOF respectively.

As an example for a diff, consider the following two versions of the same file, once before and once after a change.
The original version of the file was as follows.
[start of demo/test_file.py]
1 def test_euclidean(a, b):
2     assert euclidean(0, 0) == 0
3     assert euclidean(0, 1) == 1
4     assert euclidean(1, 0) == 1
5     assert euclidean(1, 1) == 1
6
7 @pytest.mark.parametrize("a, b, expected", [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1)])
8 def test_gcd(a, b):
9     assert gcd(a, b) == expected
10
[end of demo/file.py]

The diff for fix in function euclidean and adds the function gcd is as follows.
This diff changes the first file into the second file.
```diff
--- a/demo/file.py
+++ a/demo/file.py
@@ -4,4 +4,5 @@
     assert euclidean(1, 0) == 1
     assert euclidean(1, 1) == 1
+    assert euclidean(100, 10) == 10
 
 @pytest.mark.parametrize("a, b, expected", [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1)])
@@ -9,2 +10,6 @@
     assert gcd(a, b) == expected
 
+@pytest.mark.parametrize("a, b, expected", [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1), (100, 10, 10)])
+def test_lcm(a, b):
+    assert lcm(a, b) == expected
+
```

The new version of the file is as follows.
[start of demo/file.py]
1 def test_euclidean(a, b):
2     assert euclidean(0, 0) == 0
3     assert euclidean(0, 1) == 1
4     assert euclidean(1, 0) == 1
5     assert euclidean(1, 1) == 1
6     assert euclidean(100, 10) == 10
7
8 @pytest.mark.parametrize("a, b, expected", [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1)])
9 def test_gcd(a, b):
10     assert gcd(a, b) == expected
11
12 @pytest.mark.parametrize("a, b, expected", [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1), (100, 10, 10)])
13 def test_lcm(a, b):
14     assert lcm(a, b) == expected
15
[end of demo/file.py]

As you can see, you need to indicate the approximate line numbers, function name and the path and file name you want to change,
but there can be as many independent blocks of changes as you need. You may also apply changes to several files.
Apply as much reasoning as you please and see necessary. The format of the solution is fixed and has to follow the custom diff format.
Make sure to implement only test cases and don't try to fix the issue itself.
"""

PROMPT_MAP = {
    "base": BASE_PROMPT,
    "plus": PLUS_PROMPT,
}

def main(
    dataset_path: str,
    output_path: str,
    mode: Literal["base", "plus"] = "plus",
    filter_cases: str = pathlib.Path(__file__).parent / "filter_cases_lite.txt",
):
    # Load the dataset
    dataset = load_dataset(dataset_path)

    # load the filter cases
    if filter_cases:
        with open(filter_cases, "r") as f:
            filtered_instances = {x.strip() for x in f.readlines()}
    else:
        filtered_instances = set()

    new_diff_prompt = PROMPT_MAP[mode]

    splits = {}
    for split in dataset:
        new_examples = []
        for i, example in enumerate(dataset[split]):
            if example["instance_id"] in filtered_instances:
                continue
            orig_text = example["text"].splitlines()
            new_text = orig_text
            new_text[0] = "The following text contains a user issue (in <issue/> brackets) posted at a repository. Further, you are provided with file contents of several files in the repository that contain relevant code (in <code> brackets). It may be necessary to use code from third party dependencies or files not contained in the attached documents however. Your task is to identify the issue and implement a test case that verifies a proposed solution to this issue. More details at the end of this text."
            line_of_diff_prompt = [i for i, l in enumerate(new_text) if l.startswith("</code>")][-1]+1
            new_text = new_text[:line_of_diff_prompt]
            new_text = "\n".join(new_text)
            new_text += new_diff_prompt
            new_example = {
                **example,
                "text": new_text,
                "test_patch": "\n".join(example["patch"].splitlines()[1:-1]),
                "patch": "<patch>\n" + example["test_patch"] + "\n</patch>",
            }
            new_examples.append(new_example)
        splits[split] = Dataset.from_list(new_examples)
    ds = DatasetDict(splits)
    ds.save_to_disk(output_path)

