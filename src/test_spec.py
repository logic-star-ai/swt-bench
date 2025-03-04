from dataclasses import dataclass
from typing import Optional

from src.constants import (
    SWEbenchInstance,
)

from src.exec_spec import ExecSpec, make_exec_spec, ExecMode

DIFF_MODIFIED_FILE_REGEX = r"--- a/(.*)"


@dataclass
class TestSpec:
    """
    A dataclass that represents a test specification for a single instance of SWE-bench.
    """
    instance_id: str
    golden_code_patch: str
    golden_test_patch: str
    exec_spec: ExecSpec


def make_test_spec(
        instance: SWEbenchInstance,
        exec_mode: ExecMode = "unit_test",
        reproduction_script_name: Optional[str] = None,

) -> TestSpec:
    if isinstance(instance, TestSpec):
        return instance
    instance_id = instance["instance_id"]
    golden_code_patch = instance["golden_code_patch"]
    golden_test_patch = instance["golden_test_patch"]
    exec_spec = make_exec_spec(instance, exec_mode, reproduction_script_name)

    return TestSpec(
        instance_id=instance_id,
        golden_code_patch=golden_code_patch,
        golden_test_patch=golden_test_patch,
        exec_spec=exec_spec
    )
