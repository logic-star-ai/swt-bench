<div align="center">
    <h1><img height="150px" src="./docs/static/images/color_circle.png" alt="SWT-Bench 🔍🦙"><br>SWT-Bench</h1>

[![Build & Test](https://github.com/logic-star-ai/swt-bench/actions/workflows/build.yml/badge.svg)](https://github.com/logic-star-ai/swt-bench/actions/workflows/build.yml)
   <a href="https://www.python.org/">
        <img alt="Build" src="https://img.shields.io/badge/Python-3.9+-1f425f.svg?color=blue">
    </a>
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>


## 👋 Overview

SWT-Bench is a benchmark for evaluating large language models on testing generation for real world software issues collected from GitHub.
Given a *codebase* and an *issue*, a language model is tasked with generating a *reproducing test* that fails in the original state of the code base and passes after a patch resolving the issue has been applied.

> Check out our Paper for more details: [SWT-Bench: Testing and Validating Real-World Bug-Fixes with Code Agents](https://openreview.net/pdf?id=9Y8zUO11EQ)

## 🚀 Set Up
SWT-Bench uses Docker for reproducible evaluations.
Follow the instructions in the [Docker setup guide](https://docs.docker.com/engine/install/) to install Docker on your machine.
If you're setting up on Linux, we recommend seeing the [post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/) as well.

Finally, to build SWT-Bench, follow these steps:
```bash
git clone git@github.com:eth-sri/swt-bench.git
cd swt-bench
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Test your installation by running:
```bash
python -m src.main \
    --predictions_path gold \
    --max_workers 1 \
    --instance_ids sympy__sympy-20590 \
    --run_id validate-gold
```

## 💽 Usage

## Running Evaluation

> [!WARNING]
> Running fast evaluations on SWT-Bench can be resource intensive
> We recommend running the evaluation harness on an `x86_64` machine with at least 120GB of free storage, 16GB of RAM, and 8 CPU cores.
> You may need to experiment with the `--max_workers` argument to find the optimal number of workers for your machine, but we recommend using fewer than `min(0.75 * os.cpu_count(), 24)`.
>
> If running with docker desktop, make sure to increase your virtual disk space to have ~120 free GB available, and set max_workers to be consistent with the above for the CPUs available to docker.
>
> Support for `arm64` machines is experimental.

Evaluate model predictions on SWT-Bench Lite using the evaluation harness with the following command:
```bash
python -m src.main \
    --dataset_name princeton-nlp/SWE-bench_Lite \
    --predictions_path <path_to_predictions> \
    --max_workers <num_workers> \
    --run_id <run_id>
    # use --predictions_path 'gold' to verify the gold patches
    # use --run_id to name the evaluation run
```

This command will generate docker build logs (`image_build_logs`) and evaluation logs (`run_instance_swt_logs`) in the current directory.

The final evaluation results will be stored in the `evaluation_results` directory.

## Reporting results

To assess the result of a single run, we provide a simple script to assess a single evaluation run.
Pass it the path to your evaluation, including run_id and model to get a simple tabellaric overview.
For example, to reproduce the results for SWE-Agent from Table 2 and 3 of the paper, run the following command:

```bash
python -m src.report run_instance_swt_logs/swea__gpt-4-1106-preview/gpt4__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1 --dataset lite
# |------------------------------------|--------------------------|
# | Method                             | swea__gpt-4-1106-preview |
# | Applicability (W)                  | 87.31884057971014        |
# | Success Rate (S)                   | 15.942028985507246       |
# | F->X                               | 48.18840579710145        |
# | F->P                               | 16.666666666666668       |
# | P->P                               | 9.782608695652174        |
# | Coverage Delta (Δᵃˡˡ)              | 26.488815129800212       |
# | Coverage Delta Resolved (Δᔆ)       | 64.69774543638181        |
# | Coverage Delta Unresolved (Δⁿᵒᵗ ᔆ) | 19.14736127176707        |
```

In order to see a coverage delta reported, you need to have the gold evaluation included in the same evaluation path, i.e. download the golden results into `run_instance_swt_logs` from the downloads section below.

### Submitting Results to the Leaderboard

We list top performing methods for SWT-Bench Lite and Verified on our [leaderboard](https://swtbench.com). If you want to have your results included, please [send us an email to submit@swebench.com](mailto:submit@swtbench.com?subject=SWT-Bench%20Submission&body=Hi%20there%2C%0A%0ASWT-Bench%20is%20great%21%20We%20want%20to%20submit%20our%20agent%20evaluation%20to%20the%20leaderboard.%0A%0APlease%20find%20attached%201%29%20the%20predictions%20of%20our%20cool%20agent%20as%20jsonl%20zip%2C%202%29%20the%20resulting%20evaluation%20report%2C%20and%203%29%20a%20link%20to%20the%20project%20and%20inference%20traces%3A) containing

- The name of your method
- The inference results from your method as the JSONL used to run the evaluation. The JSONL should contain a prediction for each instance in SWT-Bench Lite or Verified per line, each with the following fields
  - `instance_id` The name of the instance in SWT-Bench Lite or Verified
  - `model_name_or_path` The name of your model/approach
  - `model_patch` The git patch to apply to the repository
  - `full_output` _(optional)_ The complete output of your model for the given task
- Your locally determined performance
- A link to your projects homepage and traces of your method (to verify that the predictions are legitimate)
- A description on how to reproduce your runs if you want to have your results independently verified through us

We will independently run your predictions in our dockerized environment to verify your score, contact you to confirm your results and to coordinate the publication. To ensure the accessibility of traces, we reserve the right to host your predictions on a server of ours.

> The inclusion in the leaderboard will be performed on a best effort basis, but we can not guarantee inclusion or timely processing of your requests.



## ⬇️ Downloads

### Datasets

The SWT-Bench, SWT-Bench-Lite and SWT-Bench Verified datasets are published publicly accessible on huggingface and can be accessed using the following links. They already contain the 27k token capped context retrieved via BM25 in the prompt.

| Prompt Format | SWT-Bench                                                                     | SWT-Bench Lite                                                                     | SWT-Bench Verified                                                                     |
|---------------|-------------------------------------------------------------------------------|------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------|
| ZeroShotBase  | [Download](https://huggingface.co/datasets/nmuendler/SWT-Bench_bm25_27k_zsb/) | [Download](https://huggingface.co/datasets/nmuendler/SWT-Bench_Lite_bm25_27k_zsb/) | [Download](https://huggingface.co/datasets/nmuendler/SWT-Bench_Verified_bm25_27k_zsb/) |             
| ZeroShotPlus  | [Download](https://huggingface.co/datasets/nmuendler/SWT-Bench_bm25_27k_zsp/) | [Download](https://huggingface.co/datasets/nmuendler/SWT-Bench_Lite_bm25_27k_zsp/) | [Download](https://huggingface.co/datasets/nmuendler/SWT-Bench_Verified_bm25_27k_zsp/) |             

### Evaluation Results

We provide the full traces of run code agents, the predicted patches by each method and setting and the logs of the evaluation harness.

| Artifact          | Single Files                                                            | ZIP                                                                                |
|-------------------|---------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| Agent Traces      | [Download](https://files.sri.inf.ethz.ch/swt-bench/agent_traces//) | [Download](https://files.sri.inf.ethz.ch/swt-bench/agent_traces/) |             
| Predicted Patches | [Download](https://files.sri.inf.ethz.ch/swt-bench/inference_output/) | [Download](https://files.sri.inf.ethz.ch/swt-bench/inference_output.zip) |
| Evaluation Harness Logs | [Download](https://files.sri.inf.ethz.ch/swt-bench/run_instance_swt_logs) | [Download](https://files.sri.inf.ethz.ch/swt-bench/run_instance_swt_logs.zip) |

The full list of resolved instances per approach can be found [here](https://files.sri.inf.ethz.ch/swt-bench/resolved_per_approach.json).

For our evaluation of OpenHands, we automatically discard all top-level files to remove stale reproduction scripts generated by the agent.
Moreover, for the evaluation of the agent in the correct environment, we discard changes to `setup.py`, `pyproject.toml` and `requirements.txt` files, as they are changed by the test setup and conflict with the repeated evaluation.
To find the exact setup used for OpenHands, check out the branch [`feat/CI`](https://github.com/logic-star-ai/swt-bench/tree/feat/CI).

## 🏗 Building SWT-Bench and Zero-Shot inference

To recreate the SWT-Bench dataset or create one with your own flavoring
and to run the zero-shot approaches from the paper on this dataset, follow these steps.
In order to avoid duplication, we re-use some of the SWE-Bench tooling.
First, create an SWE-Bench style dataset, i.e. by using the [SWE-Bench dataset collection scripts](https://github.com/princeton-nlp/SWE-bench/tree/main/swebench/collect).
If you want to add BM-25 retrieved documents, you can use the [SWE-Bench BM-25 retrieval script `bm25_retrieval.py`](https://github.com/princeton-nlp/SWE-bench/tree/main/swebench/inference/make_datasets) - make sure to set [`include_tests` to `True`](https://github.com/princeton-nlp/SWE-bench/blob/d99c1c45880375bdca90b2ffd2627576c886a1b2/swebench/inference/make_datasets/bm25_retrieval.py#L188C42-L188C55) to ensure that test files are included in the results.

Finally, run [dataset/swt_bench.py](dataset/swt_bench.py) to convert the SWE-Bench style dataset into an SWT-Bench dataset.
For example, with your SWE-Bench dataset in `datasets/swe_bench`, run the following commands.

```bash
python3 dataset/swt_bench.py --dataset_path datasets/swe_bench --output_path dataset/swt_bench_zsb --mode base
python3 dataset/swt_bench.py --dataset_path datasets/swe_bench --output_path dataset/swt_bench_zsp --mode plus
```

These commands will create the datasets for the approaches Zero-Shot Base and Zero-Shot Plus from the paper.
You can then use the [SWE-Bench inference tooling](https://github.com/princeton-nlp/SWE-Bench/tree/main/swebench/inference) to generate
the model inference files.

## 💫 Contributions
We would love to hear from the broader NLP, Machine Learning, and Software Engineering research communities, and we welcome any contributions, pull requests, or issues!
To do so, please either file a new pull request or issue. We'll be sure to follow up shortly!

Contact person: [Niels Mündler](https://www.sri.inf.ethz.ch/people/niels) and [Mark Niklas Müller](https://www.sri.inf.ethz.ch/people/mark) (Email: {niels.muendler, mark.mueller}@inf.ethz.ch).

This repo is based on the [SWE-Bench evaluation harness](https://github.com/princeton-nlp/SWE-Bench) and we want to thank all their contributors. 

## ✍️ Citation
If you find our work helpful, please use the following citations.
```bib
@inproceedings{
  mundler2024swtbench,
  title={{SWT}-Bench: Testing and Validating Real-World Bug-Fixes with Code Agents},
  author={Niels M{\"u}ndler and Mark Niklas Mueller and Jingxuan He and Martin Vechev},
  booktitle={The Thirty-eighth Annual Conference on Neural Information Processing Systems},
  year={2024},
  url={https://openreview.net/forum?id=9Y8zUO11EQ}
}
```

Please also consider citing SWE-bench which inspired our work and forms the basis of this code-base.
```bib
@inproceedings{
    jimenez2024swebench,
    title={{SWE}-bench: Can Language Models Resolve Real-world Github Issues?},
    author={Carlos E Jimenez and John Yang and Alexander Wettig and Shunyu Yao and Kexin Pei and Ofir Press and Karthik R Narasimhan},
    booktitle={The Twelfth International Conference on Learning Representations},
    year={2024},
    url={https://openreview.net/forum?id=VTF8yNQM66}
}
```

## 🪪 License
MIT. Check `LICENSE.md`.
