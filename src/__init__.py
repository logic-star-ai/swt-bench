__version__ = "2.0.2"

from src.constants import (
    KEY_INSTANCE_ID,
    KEY_MODEL,
    KEY_PREDICTION,
    MAP_REPO_TO_TEST_FRAMEWORK,
    MAP_VERSION_TO_INSTALL,
)

from src.docker_build import (
    build_image,
    build_base_images,
    build_env_images,
    build_instance_images,
    build_instance_image,
    close_logger,
    setup_logger,
)

from src.docker_utils import (
    cleanup_container,
    remove_image,
    copy_to_container,
    exec_run_with_timeout,
    list_images,
)

from src.grading import (
    compute_fail_to_pass,
    compute_pass_to_pass,
    get_logs_eval,
    get_eval_report,
    get_pred_report,
    get_resolution_success,
    ResolvedStatus,
    TestStatus,
)

from src.log_parsers import (
    MAP_REPO_TO_PARSER,
)

from src.main import (
    run,
)

from src.utils import (
    get_environment_yml,
    get_requirements,
)