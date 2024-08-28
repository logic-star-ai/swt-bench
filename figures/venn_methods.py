"""
Overlap between best methods
"""
import pathlib
from itertools import combinations

import fire

from figures.util import *
from tabulate import tabulate

venn_template = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Simple venn.js example</title>
<style>
body {
    font-family: "Helvetica Neue",Helvetica,Arial,sans-serif;
    font-size: 14px;
}
</style>
</head>

<body>
    <div id="venn"></div>
</body>

<script src="https://d3js.org/d3.v4.min.js"></script>
<script src="../node_modules/venn.js/venn.js"></script>
<script>
// define sets and set set intersections
var sets = %s;
var unique = %s;

var chart = venn.VennDiagram();
d3.select("#venn").datum(sets).call(chart);
for(child of document.getElementById("venn").childNodes[0].childNodes){
    let size = child.__data__.size;
    child.childNodes[1].textContent = size;
}

</script>
</html>
"""

# from venny4py
#get shared elements for each combination of sets
def get_shared(sets):
    IDs = sets.keys()
    combs = sum([list(map(list, combinations(IDs, i))) for i in range(1, len(IDs) + 1)], [])

    shared = {}
    for comb in combs:
        ID = tuple(comb)
        if len(comb) == 1:
            shared.update({ID: sets[comb[0]]})
        else:
            setlist = [sets[c] for c in comb]
            u = set.intersection(*setlist)
            shared.update({ID: u})
    return shared

#get unique elements for each combination of sets
def get_unique(shared):
    unique = {}
    for shar in shared:
        if shar == list(shared.keys())[-1]:
            s = shared[shar]
            unique.update({shar: s})
            continue
        count = len(shar)
        if count == 1:
            setlist = [shared[k] for k in shared.keys() if k != shar and len(k) == 1]
            s = shared[shar].difference(*setlist)
        else:
            setlist = [shared[k] for k in shared.keys() if k != shar and len(k) >= count]
            s = shared[shar].difference(*setlist)
        unique.update({shar: s})
    return(unique)




def main(instance_log_path: str = "./run_instance_swt_logs"):
    instance_log_path = Path(instance_log_path)
    if not instance_log_path.exists():
        raise FileNotFoundError(f"Instance log directory not found at {instance_log_path}")
    methods = [
        ("gpt-4-1106-preview", "libro_gpt-4-1106-preview__bm25_27k_cl100k__seed={seed},temperature=0.7.jsonl", "LIBRO", "libro", [1,2,3,4,5], Path("inference_output/gpt-4-1106-preview__libro__libro_gpt-4-1106-preview__bm25_27k_cl100k__seed={seed},temperature=0.7.jsonl__[1, 2, 3, 4, 5]__gpt-4-1106-preview__test__all__seed=0,temperature=0__test.jsonl")),
        ("gpt-4-1106-preview", "acr__gpt-4-1106-preview", r"AutoCodeRover"),
        ("aider--gpt-4-1106-preview", "aider_gpt-4-1106-preview", r"Aider"),
        ("gpt4__SWE-bench_Lite__default_test_demo4__t-0.00__p-0.95__c-3.00__install-1", "sweap__gpt-4-1106-preview", r"SWE-Agent+"),
    ]
    sets = {}
    for model, run_id, name, *args in methods:
        reports = collect_reports(model, run_id, instance_log_path, *args)
        resolved_reports, _ = filtered_by_resolved(reports)
        sets[name] = set(resolved_reports.keys())
    shared = get_shared(sets)
    unique = get_unique(shared)
    sets_list = [{"sets": set_names, "size": len(shared)} for set_names, shared in shared.items()]
    unique = [{"sets": set_names, "size": len(unique)} for set_names, unique in unique.items()]
    print(venn_template % (json.dumps(sets_list), json.dumps(unique)))



if __name__ == "__main__":
    fire.Fire(main)
