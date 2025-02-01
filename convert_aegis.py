import json
import hashlib

import unidiff
from coverage.data import line_counts


def calculate_git_blob_hash(content):
    # Git blob hash is calculated as: "blob <len>\0<content>"
    header = f"blob {len(content)}\0".encode()
    store = header + content.encode()
    return hashlib.sha1(store).hexdigest()


def create_git_diff(file_path, file_content):
    # Calculate the SHA-1 hash for the new file content
    new_index = calculate_git_blob_hash(file_content)

    line_count = len(file_content.splitlines())
    # Construct the diff
    diff = [
        f"diff --git a/{file_path} b/{file_path}",
        "new file mode 100644",
        f"index 0000000..{new_index}",
        "--- /dev/null",
        f"+++ b/{file_path}",
        f"@@ -0,0 +1,{line_count} @@",
    ]

    # Add the file content, each line prefixed with '+'
    for line in file_content.splitlines():
        diff.append(f"+{line}")

    return "\n".join(diff)

aegis_preds = []
with open("inference_output/aegis_preds.json") as f:
    for line in f:
        aegis_preds.append(json.loads(line))

new_aegis_preds = []
for pred in aegis_preds:
    new_pred = pred.copy()
    new_pred["model_patch"] = create_git_diff("test_patch.py", pred["model_patch"])
    new_aegis_preds.append(new_pred)
with open("inference_output/aegis_preds_diff.jsonl", "w") as f:
    for pred in new_aegis_preds:
        f.write(json.dumps(pred) + "\n")
