## 👋 Overview
SWT-bench is a benchmark for evaluating large language models on testing generation for real world software issues collected from GitHub.
Given a *codebase* and an *issue*, a language model is tasked with generating a *reproducing test* that fails in the original state of the code base and passes after a patch resolving the issue has been applied.


## 🚀 Set Up
SWT-bench uses Docker for reproducible evaluations.
Follow the instructions in the [Docker setup guide](https://docs.docker.com/engine/install/) to install Docker on your machine.
If you're setting up on Linux, we recommend seeing the [post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/) as well.

Finally, to build SWT-bench, follow these steps:
```bash
git clone git@github.com:eth-sri/swt-bench.git
cd swt-bench
python -m venv .venv
soruce .venv/bin/activate
pip install -e .
```

Test your installation by running:
```bash
python -m src.run_evaluation \
    --predictions_path gold \
    --max_workers 1 \
    --instance_ids sympy__sympy-20590 \
    --run_id validate-gold
```

## 💽 Usage
> [!WARNING]
> Running fast evaluations on SWT-bench can be resource intensive
> We recommend running the evaluation harness on an `x86_64` machine with at least 120GB of free storage, 16GB of RAM, and 8 CPU cores.
> You may need to experiment with the `--max_workers` argument to find the optimal number of workers for your machine, but we recommend using fewer than `min(0.75 * os.cpu_count(), 24)`.
>
> If running with docker desktop, make sure to increase your virtual disk space to have ~120 free GB available, and set max_workers to be consistent with the above for the CPUs available to docker.
>
> Support for `arm64` machines is experimental.

Evaluate model predictions on SWT-bench Lite using the evaluation harness with the following command:
```bash
python -m src.run_evaluation \
    --dataset_name princeton-nlp/SWE-bench_Lite \
    --predictions_path <path_to_predictions> \
    --max_workers <num_workers> \
    --run_id <run_id>
    # use --predictions_path 'gold' to verify the gold patches
    # use --run_id to name the evaluation run
```

This command will generate docker build logs (`image_build_logs`) and evaluation logs (`run_instance_swt_logs`) in the current directory.

The final evaluation results will be stored in the `evaluation_results` directory.



## ⬇️ Downloads
| Datasets | Models |
| - | - |


## 💫 Contributions
We would love to hear from the broader NLP, Machine Learning, and Software Engineering research communities, and we welcome any contributions, pull requests, or issues!
To do so, please either file a new pull request or issue. We'll be sure to follow up shortly!

Contact person: [Niels Mündler](https://www.sri.inf.ethz.ch/people/niels) and [Mark Niklas Müller](https://www.sri.inf.ethz.ch/people/mark) (Email: {niels.muendler, mark.mueller}@inf.ethz.ch).

This repo is based on the [SWE-Bench evaluation harness](https://github.com/princeton-nlp/SWE-bench) and we want to thank all their contributors. 

## ✍️ Citation
If you find our work helpful, please use the following citations.
```
@misc{mündler2024codeagentsstateart,
      title={Code Agents are State of the Art Software Testers}, 
      author={Niels Mündler and Mark Niklas Müller and Jingxuan He and Martin Vechev},
      year={2024},
      eprint={2406.12952},
      archivePrefix={arXiv},
      primaryClass={cs.SE},
      url={https://arxiv.org/abs/2406.12952}, 
}
```

Please also consider citing SWE-Bench which inspired our work and forms the basis of this code-base.
```
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
