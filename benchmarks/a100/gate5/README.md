# Gate 5 run tools (js2a100, `$ROOT/benchmarks/gate5`)

Copies of the scripts that produced the Gate 5 ladder records (paths are the remote campaign paths):

* `run_gate5_soft1_original.sh`: the original matrix at soft guard 1.0 (stopped during its first run, Fable D-ladder).
* `run_gate5_dladder_v1.sh`: D-ladder (soft guard cap 10; budgets 2e6 evaluations / 7200 s). Ran phase a1 (rung-1 TinyNS pair) and the start of a2.
* `run_gate5_dladder_v2.sh`: D-ladder2 (300,000 evaluations; 3600 s sampling wall as a safety; core-main dynesty rung 1 at 20,000). Ran rungs 2-5 and legacy 5b; stopped during the core-main 5b run to switch to v3.
* `run_gate5_dladder_v3.sh`: v2 plus the Fable exception (core-main dynesty rung 1 wall 7200 s) and phase c5b; ran phases b, c5b, c, d.
* `m5b_soft10_make_spec.py`, `m5b_soft10_spec.json`: the soft@10 fixed-coordinate parity precondition (campaign_run.py, outdir `$ROOT/benchmarks/gate1/m5b/soft10`).
* `gate5_table.py [GATE5_DIR]`: `gate5_matrix.csv` and `gate5_facts.json` from `runs/*/record.json`, `compare/*` and the smi windows.
* `gate5_report_tables.py [GATE5_DIR]`: Markdown tables for the Gate 5 report.
* `gate5_manifest_append.py`: one `$ROOT/state/manifest.json` run entry per ladder record.
* `gate5_status.sh`: compact driver status (polling helper).
