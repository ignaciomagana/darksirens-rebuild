# Fable D-ladder parity precondition: the six n4096+full M5b soft1 specs with max_variance 10 (soft@10).
import json
src = json.load(open("/media/volume/tbs/darksirens_benchmark/benchmarks/gate1/m5b/specs/m5b.json"))
out = []
for s in src:
    if not (s["pe_label"] == "bbh259_n4096" and s["record_id"].endswith("_soft1")):
        continue
    t = dict(s)
    t["record_id"] = s["record_id"][:-len("_soft1")] + "_soft10"
    t["max_variance"] = 10.0
    t["flags"] = {"guard_variant": "soft10", "decision": "D-ladder parity precondition"}
    t["compare_to"] = [c[:-len("_soft1")] + "_soft10" for c in s["compare_to"]]
    out.append(t)
assert len(out) == 6, len(out)
json.dump(out, open("/media/volume/tbs/darksirens_benchmark/benchmarks/gate1/m5b/soft10/specs/m5b_soft10.json", "w"), indent=1)
for t in out: print(t["record_id"], t["guard"], t["max_variance"], t["compare_to"])
