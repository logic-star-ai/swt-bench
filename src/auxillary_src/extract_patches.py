import dataclasses
import os
from tempfile import NamedTemporaryFile
from typing import List, Tuple, Dict
from collections import defaultdict
import ast
import textwrap
import pathlib
import editdistance
import argparse
import git
import re

### MARK - Patch Correction
PATCH_PATTERN = re.compile(
    r"(?:diff[\w\_\.\ \/\-]+\n)?\-\-\-\s+a\/(?:.*?)\n\+\+\+\s+b\/(?:.*?)(?=diff\ |\-\-\-\ a\/|\Z)",
    re.DOTALL,
)
PATCH_FILE_PATTERN = re.compile(r"\-\-\-\s+a\/(?:.+)\n\+\+\+\s+b\/(?:.+)")
PATCH_HUNK_PATTERN = re.compile(
    r"\@\@\s+\-(\d+),(\d+)\s+\+(\d+),(\d+)\s+\@\@(.+?)(?=diff\ |\-\-\-\ a\/|\@\@\ \-|\Z)",
    re.DOTALL,
)


@dataclasses.dataclass
class FuzzyPatch:
    rough_line_number: int
    preceding_lines: List[str]
    deleted_lines: List[str]
    inserted_lines: List[str]
    following_lines: List[str]


@dataclasses.dataclass
class FuzzyFilePatch:
    file_name: str
    diffs: List[FuzzyPatch]


@dataclasses.dataclass
class CustomPatch:
    file_name: str
    patch_type: str
    rough_line_number: str
    changed_lines: list


def get_first_idx(charlist):
    """Get index of first occurrence of "-" or "+" in charlist"""
    first_min = charlist.index("-") if "-" in charlist else len(charlist)
    first_plus = charlist.index("+") if "+" in charlist else len(charlist)
    return min(first_min, first_plus)


def get_last_idx(charlist):
    """Get index of last occurrence of "-" or "+" in charlist"""
    char_idx = get_first_idx(charlist[::-1])
    last_idx = len(charlist) - char_idx
    return last_idx + 1


def strip_content(hunk):
    """Remove trailing non +/- lines and trailing whitespace per line per hunk"""
    first_chars = list(map(lambda x: None if not len(x) else x[0], hunk.split("\n")))
    first_idx = get_first_idx(first_chars)
    last_idx = get_last_idx(first_chars)
    new_lines = list(map(lambda x: x.rstrip(), hunk.split("\n")[first_idx:last_idx]))
    new_hunk = "\n" + "\n".join(new_lines) + "\n"
    return new_hunk, first_idx - 1

def remove_binary_diffs(diff_content):
    binary_file_indicator = 'Binary files'

    lines = diff_content.splitlines()

    new_lines = []
    curr_diff = []
    skip_current_diff = False
    for line in lines + ["diff --git"]:
        if line.startswith('diff --git'):
            if curr_diff and not skip_current_diff:
                new_lines.append('\n'.join(curr_diff))
            curr_diff = []
            skip_current_diff = False
        if binary_file_indicator in line:
            skip_current_diff = True
        curr_diff.append(line)

    return '\n'.join(new_lines) + "\n"

def extract_fuzzy_patch(model_patch) -> List[FuzzyFilePatch]:
    """
    Wrapper function that takes hunk and
    * Removes trailing whitespace per line per hunk
    * Returns new patch
    """
    model_patch = model_patch.lstrip("\n")
    patches = []
    for patch in PATCH_PATTERN.findall(model_patch):
        patch_header = PATCH_FILE_PATTERN.findall(patch)[0]
        subpatches = []
        for hunk in PATCH_HUNK_PATTERN.findall(patch):
            pre_start, pre_len, post_start, post_len, content = list(
                map(lambda x: int(x) if x.isnumeric() else x, hunk)
            )
            content_lines = content.split("\n")
            content_lines = content_lines[1:]
            i = 0
            deleted_lines = []
            inserted_lines = []
            preceding_lines = []
            following_lines = []
            change_start = pre_start
            # positions: 0 = preceding, 1 = in change, 2 = following
            position = 0
            for i, line in enumerate(content_lines):
                if line.startswith(" "):
                    if position == 1:
                        position = 2
                    if position == 0:
                        preceding_lines.append(line[1:])
                    if position == 2:
                        following_lines.append(line[1:])
                if line.startswith("-"):
                    if position == 2:
                        subpatches.append(FuzzyPatch(change_start, preceding_lines, deleted_lines, inserted_lines, following_lines))
                        change_start = pre_start + i - len(following_lines)
                        preceding_lines = following_lines
                        following_lines = []
                        deleted_lines = []
                        inserted_lines = []
                        position = 1
                    if position == 0:
                        position = 1
                    deleted_lines.append(line[1:])
                if line.startswith("+"):
                    if position == 2:
                        subpatches.append(FuzzyPatch(change_start, preceding_lines, deleted_lines, inserted_lines, following_lines))
                        change_start = pre_start + i - len(following_lines)
                        preceding_lines = following_lines
                        following_lines = []
                        deleted_lines = []
                        inserted_lines = []
                        position = 1
                    if position == 0:
                        position = 1
                    inserted_lines.append(line[1:])
                if line.startswith("```") or line.startswith("<"):
                    break
            subpatches.append(FuzzyPatch(change_start, preceding_lines, deleted_lines, inserted_lines, following_lines))
            content = "\n".join(content_lines[:i])
        patches.append(FuzzyFilePatch(patch_header.split()[1][2:], subpatches))

    return patches


def extract_custom_patches(model_patch):
    """
    Wrapper function that takes response and
    - searches for all lines with "diff"
    - extracts the file name, file line start and end and changed lines
    """
    model_patch = model_patch.lstrip("\n").splitlines()
    patches = []
    for i, line in enumerate(model_patch):
        if line.startswith("diff"):
            try:
                file_name = model_patch[i+1]
                patch_type = model_patch[i+2]
                rough_line_number = model_patch[i+3]
                j = i + 4
                for j in range(i+4, len(model_patch)):
                    if model_patch[j].startswith("end diff"):
                        break
                changed_lines = model_patch[i + 4:j]
            except:
                continue
            patches.append(CustomPatch(file_name, patch_type, rough_line_number, changed_lines))
    return patches


def extract_minimal_patch(model_patch) -> str:
    """
    Wrapper function that takes hunk and
    * Removes trailing non +/- lines and trailing whitespace per line per hunk
    * Recalculates hunk start/end position and diff delta
    * Returns new patch
    """
    model_patch = remove_binary_diffs(model_patch)
    model_patch = model_patch.lstrip("\n")
    new_patch = ""
    for patch in PATCH_PATTERN.findall(model_patch):
        total_delta = 0
        patch_header = PATCH_FILE_PATTERN.findall(patch)[0]
        if patch_header:
            new_patch += patch_header + "\n"
        for hunk in PATCH_HUNK_PATTERN.findall(patch):
            pre_start, pre_len, post_start, post_len, content = hunk
            pre_start, pre_len, post_start, post_len, content = list(
                map(lambda x: int(x) if x.isnumeric() else x, hunk)
            )
            content, adjust_pre_start = strip_content(content)
            pre_start += adjust_pre_start
            pre_start, pre_len, post_start, post_len, total_delta = get_hunk_stats(
                pre_start, pre_len, post_start, post_len, content, total_delta
            )
            new_patch += (
                f"@@ -{pre_start},{pre_len} +{post_start},{post_len} @@{content}"
            )
    return new_patch



def get_hunk_stats(pre_start, pre_len, post_start, post_len, hunk, total_delta):
    """Recalculate hunk start/end position and diff delta"""
    stats = {"context": 0, "added": 0, "subtracted": 0}
    hunk = hunk.split("\n", 1)[-1].strip("\n")
    for line in hunk.split("\n"):
        if line.startswith("-"):
            stats["subtracted"] += 1
        elif line.startswith("+"):
            stats["added"] += 1
        else:
            stats["context"] += 1
    context = stats["context"]
    added = stats["added"]
    subtracted = stats["subtracted"]
    pre_len = context + subtracted
    post_start = pre_start + total_delta
    post_len = context + added
    total_delta = total_delta + (post_len - pre_len)
    return pre_start, pre_len, post_start, post_len, total_delta


def apply_fuzzy_patches(fuzzy_patch: List[FuzzyFilePatch], testbed: str, patch_type: str = "fuzzy") -> bool:
    """
    Apply a git diff patch without exact line number matching

    Args:
        fuzzy_patches (list): list of patches to apply
        patch_type (str): Type of patch (e.g. "eval", "test")
    Returns:
        bool: whether the patch applied successfully
    """
    if not fuzzy_patch:
        return False

    # Apply patch to testbed directory
    for patch in fuzzy_patch:
        file_name = patch.file_name
        os.path.join(testbed, file_name)
        try:
            with open(file_name, "r") as f:
                file = f.read()
        except FileNotFoundError as e:
            print(f"Patch file not found ({file_name} for patch type {patch_type})")
            return False

        lines = file.splitlines()
        for diff in patch.diffs:
            # find position in the file where the patch should be applied
            best_start = 0
            best_start_score = 0
            for i, line in enumerate(lines):
                score = overlap_score(diff.preceding_lines + diff.deleted_lines, lines[i:])
                if score > best_start_score:
                    best_start_score = score
                    best_start = min(i + len(diff.preceding_lines), len(lines))

            # find position of the last line of the patch
            best_end = len(lines)
            best_end_score = 0
            for i, line in enumerate(lines):
                score = overlap_score(diff.following_lines, lines[i:])
                if score > best_end_score:
                    best_end_score = score
                    best_end = i

            if best_end < best_start:
                print(f"Invalid patch reverses ({file_name} for patch type {patch_type})")

            # apply the patch
            lines = lines[:best_start] + diff.inserted_lines + lines[best_end:]

        with open(file_name, "w") as f:
            f.write("\n".join(lines))

    # Patch apply succeeded
    print(f"Custom patch successful ({file_name} for patch type {patch_type})")
    return True


class ReplaceFunctionTransformer(ast.NodeTransformer):
    def __init__(self, new_ast, approximate_lineno):
        self.new_ast = new_ast
        self.approximate_lineno = approximate_lineno
        self.any_change_applied = False

    def visit_FunctionDef(self, node):
        if isinstance(node, ast.FunctionDef) and isinstance(self.new_ast, ast.FunctionDef) and node.name == self.new_ast.name:
            self.any_change_applied = True
            return self.new_ast
        return self.generic_visit(node)

    def visit_ClassDef(self, node):
        if isinstance(node, ast.ClassDef) and isinstance(self.new_ast, ast.ClassDef) and node.name == self.new_ast.name:
            self.any_change_applied = True
            return self.new_ast
        return self.generic_visit(node)


def apply_custom_patches(custom_patches: List[CustomPatch], testbed:str, patch_type: str = "custom"
) -> bool:
    """
    Apply custom patches to task environment and return a git patch

    Args:
        custom_patches (list): list of patches to apply
        patch_type (str): Type of patch (e.g. "eval", "test")
    Returns:
        bool: whether the patch applied successfully
    """
    if not custom_patches:
        print(f"Patch is empty (patch type {patch_type})")
        return False

    # sort by start line number
    custom_patches = sorted(custom_patches, key=lambda x: x.rough_line_number)
    # split patches by file
    patches_by_file: Dict[str, List[CustomPatch]] = defaultdict(list)
    for patch in custom_patches:
        patches_by_file[patch.file_name].append(patch)


    # Apply patch to testbed directory
    # keep track of line number mapping for each file
    for file_name, patches in patches_by_file.items():
        file_name = os.path.join(testbed, file_name)
        try:
            with open(file_name, "r") as f:
                file = f.read()
        except FileNotFoundError:
            # Patch file not found
            # could be because this is a new file
            file = ""
        try:
            file_ast = ast.parse(file)
        except SyntaxError:
            print(f" Syntax error in file: {file_name}")
            return False

        for patch in patches:
            patch_joined = "\n".join(patch.changed_lines)
            patch_joined = textwrap.dedent(patch_joined)
            try:
                patch_ast = ast.parse(patch_joined)
            except SyntaxError:
                print(f"Syntax error in patch: {file_name}")
                return False
            if patch.patch_type == "rewrite":
                patch_ast = patch_ast.body[0]
                if not (isinstance(patch_ast, ast.FunctionDef) or isinstance(patch_ast, ast.ClassDef)):
                    print(f"Invalid patch: {file_name}")
                    return False
                transformer = ReplaceFunctionTransformer(patch_ast, 0)
                transformer.visit(file_ast)
                if not transformer.any_change_applied:
                    print(f"No change applied: {file_name}")
                    return False
            elif patch.patch_type == "insert":
                file_ast.body.extend(patch_ast.body)
                pathlib.Path(file_name).parent.mkdir(parents=True, exist_ok=True)

        with open(file_name, "w") as f:
            f.write(ast.unparse(file_ast))

    # Patch apply succeeded
    print(f"Custom patch successful (for {file_name} and patch type {patch_type})")
    return True


def overlap_score(a: List[str], b: List[str]):
    score = 0
    for j, context_line in enumerate(a):
        if j >= len(b):
            continue
        distance = editdistance.eval(b[j], context_line)
        score += (1 - (distance / max(len(b[j]), len(context_line)))) if len(b[j]) > 0 or len(context_line) > 0 else 0
    return score


def write_diff_and_reset(testbed: str, reference_commit: str ='', target_file:str = "./processed_patch.diff"):
    repo = git.Repo(testbed)
    repo.git.add(all=True)
    diff = repo.git.diff(reference_commit)
    with open(target_file, "w") as f:
        f.write(diff)

    repo.git.reset('--hard', reference_commit)


def apply_patch(patch, testbed):
    repo = git.Repo(testbed)
    with NamedTemporaryFile("w", suffix=".diff") as f:
        f.write(patch)
        try:
            repo.git.apply("-v", f.name)
            return True
        except git.exc.GitCommandError as e:
            return False


def run(model_output_file: str, testbed:str, patch_type: List[str], reference_commit: str, target_file: str):
    with open(model_output_file, "r") as f:
        raw_model_output = f.read()

    success = False
    for patch_type in patch_type:
        if success:
            break
        if patch_type == "fuzzy":
            model_patch = extract_fuzzy_patch(raw_model_output)
            success = apply_fuzzy_patches(fuzzy_patch=model_patch, testbed=testbed)
        elif patch_type == "custom":
            model_patch = extract_custom_patches(raw_model_output)
            success = apply_custom_patches(custom_patches=model_patch, testbed=testbed)
        elif patch_type == "vanilla":
            model_patch = extract_minimal_patch(raw_model_output)
            success = apply_patch(patch=model_patch, testbed=testbed)
        else:
            assert False, f"Unkown patch type {patch_type}"

    write_diff_and_reset(testbed, reference_commit, target_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_output_file", default="/root/raw_model_patch.txt", type=str, help="Path to raw model output")
    parser.add_argument("--testbed", default="/testbed/", type=str, help="Path to raw model output")
    parser.add_argument("--patch_type", nargs="+", choices=["vanilla", "fuzzy", "custom"], type=str, help="Type of patch to be extracted")
    parser.add_argument("--reference_commit", required=True, type=str, help="Type of patch to be extracted")
    parser.add_argument("--target_file", default="/root/extracted_patch.diff", type=str, help="Path to raw model output")

    args = parser.parse_args()

    run(**vars(args))


if __name__ == "__main__":
    main()


