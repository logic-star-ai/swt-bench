import os
import json
from src.exec_spec import ExecSpec


if __name__ == "__main__":
    root_path = "/Users/mark/Projects/SWEBench/SWE-bench/run_instance_logs/validate-gold-new-build/gold"
    build_path = "/Users/mark/Projects/SWEBench/SWE-bench/image_build_logs"

    for instance_id in os.listdir(root_path):
        repo_exec_response = {}
        with open(os.path.join(root_path,instance_id, "exec_spec.json"), "r") as f:
            exec_spec_dict = json.load(f)
            exec_spec = ExecSpec(**exec_spec_dict)

        with open(os.path.join(root_path, instance_id, "run_instance.log"), "r") as f:
            repo_exec_response["run_log"] = f.read()

        with open(os.path.join(root_path, instance_id, "test_output.txt"), "r") as f:
            repo_exec_response["test_output"] = f.read()

        base_img_path = os.path.join(build_path, "base", f"{exec_spec.base_image_key.replace(':','__')}")
        env_img_path = os.path.join(build_path, "env", f"{exec_spec.env_image_key.replace(':','__')}")
        inst_img_path = os.path.join(build_path, "instances", f"{exec_spec.instance_image_key.replace(':','__')}")

        with open(os.path.join(root_path, instance_id, base_img_path, "build_image.log"), "r") as f:
            repo_exec_response["build_base_log"] = f.read()

        with open(os.path.join(root_path, instance_id, env_img_path, "build_image.log"), "r") as f:
            repo_exec_response["build_env_log"] = f.read()

        with open(os.path.join(root_path, instance_id, inst_img_path, "build_image.log"), "r") as f:
            repo_exec_response["build_inst_log"] = f.read()

        with open(os.path.join(root_path, instance_id, "exec_resp.json"), "w") as f:
            json.dump(repo_exec_response, f)