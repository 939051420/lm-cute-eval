import os, json

from .human_eval.evaluation import evaluate_functional_correctness

def match_answer_humaneval(infer_result:dict, round_idx:int, args):
    sample_fn = os.path.join(args.save_path, args.temp_file_path, f"humaneval_sample_round{round_idx}.jsonl")
    problem_fn = os.path.join(args.save_path, args.temp_file_path, f"humaneval_limit_data.jsonl")
    problem_keys = ["task_id", "prompt", "test", "entry_point"]
    with open(sample_fn, "w") as sample_file, open(problem_fn, "w") as problem_file:
        for item in infer_result["humaneval"]:
            text = item[f"infer_round{round_idx}"]
            function_prefix = "def " + item["entry_point"]
            # find the first python block  ```python ```
            try:
                function_text = text[text.find("```python\n"):text.find("\n```")]
                completion = function_prefix + function_text.split(function_prefix)[1]
            except:
                completion = "failed to extract answer"
            print(json.dumps({
                "task_id": item["task_id"],
                "completion": completion,
            }), file=sample_file)
            print(json.dumps({
                **{key: item[key] for key in problem_keys}
            }), file=problem_file)
    result = evaluate_functional_correctness(
        sample_file=sample_fn,
        n_workers=4,
        timeout=0.5,
        problem_file=problem_fn,
    )
    return {
        "humaneval": {
            "acc": result["pass@1"]
        }
    }
