import json
import pathlib

import fire
import tiktoken
from cachier import cachier

from mistral_common.protocol.instruct.messages import (
    AssistantMessage,
    UserMessage,
    ToolMessage
)
from mistral_common.tokens.tokenizers.mistral import MistralTokenizer
from mistral_common.protocol.instruct.tool_calls import Function, Tool, ToolCall, FunctionCall
from mistral_common.tokens.instruct.normalize import ChatCompletionRequest

GPT4_TOKENIZER = tiktoken.encoding_for_model("gpt-4")
def gpt4_tokenizer(text: list):
    return GPT4_TOKENIZER.encode_ordinary_batch(text)

MISTRAL_TOKENIZER = MistralTokenizer.v3()
def mistral_tokenizer(text: list):
    tokenized = []
    for text in text:
        cr =  ChatCompletionRequest(
            messages=[
                UserMessage(content=text),
            ],
            model="Mixtral-8x22b-instruct-v0.1",
        )
        tokenized = MISTRAL_TOKENIZER.encode_chat_completion(cr)

        tokens, text = tokenized.tokens, tokenized.text
        tokenized.append(tokens)
    return tokenized


TOKENIZER_PER_MODEL = {
    "claude-3-haiku-20240307": gpt4_tokenizer,
    "gpt-4-1106-preview": gpt4_tokenizer,
    "Mixtral-8x22B-Instruct-v0.1": mistral_tokenizer,
}

COST_PER_INPUT_PER_TOKEN = {
    "claude-3-haiku-20240307":  0.00000025,
    "gpt-4-1106-preview": 0.00001,
    "Mixtral-8x22B-Instruct-v0.1":  1.2 / 1_000_000,
}
COST_PER_OUTPUT_PER_TOKEN = {
    "claude-3-haiku-20240307":  0.00000125,
    "gpt-4-1106-preview":  0.00003,
    "Mixtral-8x22B-Instruct-v0.1":  1.2 / 1_000_000,
}


@cachier()
def cost_of_inference_file(
    file: str,
):
    with open(file) as f:
        results = f.readlines()
    all_inputs = []
    all_outputs = []
    total_cost = 0
    for res in results:
        res = json.loads(res)
        text_inputs = res["text"]
        text_outputs = res["full_output"]
        all_inputs.append(text_inputs)
        all_outputs.append(text_outputs)
        model = res["model_name_or_path"]
    tokenizer = TOKENIZER_PER_MODEL[model]
    text_inputs = tokenizer(all_inputs)
    text_outputs = tokenizer(all_outputs)
    total_cost += sum(len(x) for x in text_inputs) * COST_PER_INPUT_PER_TOKEN[model]
    total_cost += sum(len(x) for x in text_outputs) * COST_PER_OUTPUT_PER_TOKEN[model]
    return total_cost

def zsb():
    for file, name in (
        ( "inference_output/gpt-4-1106-preview__swt_bench_lite_aug1_bm25_diff_27k_cl100k__seed=0,temperature=0__test.jsonl", "GPT 4 \\zsb"),
        ( "inference_output/gpt-4-1106-preview__swt_bench_lite_aug1_bm25_27k_cl100k__seed=0,temperature=0__test.jsonl", "GPT 4 \\zsp"),
    ):
        cost = cost_of_inference_file(file)
        print(f"{name} & {cost:.2f} \\\\")

def paf_cost():
    libro_pattern = "inference_output/gpt-4-1106-preview__swt_bench_lite_aug1_bm25_27k_cl100k__seed=1,temperature=0.7__test.jsonl"
    total_sum = 0
    for i in range(1, 6):
        total_sum += cost_of_inference_file(libro_pattern.replace("seed=1", f"seed={i}"))
    return total_sum

def paf():
    total_sum = paf_cost()
    print(f"GPT 4 \\paf & {total_sum:.2f} \\\\")

def libro():
    total_sum = 0
    total_sum += cost_of_inference_file("inference_output/gpt-4-1106-preview__libro_gpt-4-1106-preview__swt_bench_lite_aug1__test__test.jsonl")
    total_sum += paf_cost()
    print(f"GPT 4 \\libro & {total_sum:.2f} \\\\")

def sweagent_cost(trajectory_dir: str):
    total_sum = 0
    max_total_sum = 0
    directory = pathlib.Path(trajectory_dir)
    for file in directory.glob("*.traj"):
        with open(file, "r") as f:
            trajectory = json.load(f)
        total_sum += trajectory["info"]["model_stats"]["instance_cost"]
        max_total_sum = max(trajectory["info"]["model_stats"]["total_cost"], max_total_sum)
    # assert abs(total_sum - max_total_sum) < 0.1, (total_sum, max_total_sum)
    return total_sum

def sweagent():
    for traj_dir, model in (
        ("../SWE-agent/trajectories/nmuendler/gpt4__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1", "GPT 4"),
        # ("../SWE-agent/trajectories/nmuendler/claude-3-haiku-20240307__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1", "Haiku"),
        # ( "../SWE-agent/trajectories/nmuendler/mixtral8x22b__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1", "Mixtral"),
        ("../SWE-agent/trajectories/nmuendler/gpt4__SWE-bench_Lite__default_test_demo4__t-0.00__p-0.95__c-3.00__install-1",
        "+"),
    ):
        total_sum = sweagent_cost(traj_dir)
        print(f"{model} \\swea & {total_sum:.2f} \\\\")

def acr_cost(output_dir: str):
    total_sum = 0
    directory = pathlib.Path(output_dir)
    for file in directory.glob("**/cost.json"):
        with open(file, "r") as f:
            cost_map = json.load(f)
        total_sum += cost_map["total_cost"]
    return total_sum

def acr():
    total_sum = acr_cost("../auto-code-rover/output_docker")
    print(f"\\acr & {total_sum:.2f} \\\\")

def main():
    zsb()
    paf()
    libro()
    acr()
    sweagent()

if __name__ == '__main__':
    fire.Fire(main)