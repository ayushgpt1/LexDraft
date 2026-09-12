# -*- coding: utf-8 -*-
"""Analyze the /generate API result."""

import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

r = json.load(
    open("outputs/generate_result.json", encoding="utf-8")
)

d = r["deterministic_score"]

print(
    "DETERMINISTIC:",
    d["score"],
    f"({d['passed_checks']}/{d['total_checks']})",
)

for v in r["validation_results"]:
    print("[PASS]" if v["passed"] else "[FAIL]", v["check"])
    if not v["passed"]:
        print("    issues:", v["issues"])

e = r["evaluation_report"]

print("LLM OVERALL:", e["overall_score"])

for c in [
    "entity_accuracy",
    "completeness",
    "semantic_faithfulness",
    "hallucination",
    "template_fidelity",
]:
    print(" ", c, "=", e[c]["score"])
    for i in e[c]["issues"]:
        print("     -", i)

print("OVERALL ISSUES:", e["overall_issues"])

cd = r["case_data"]

print("answering_respondent_number =", cd["answering_respondent_number"])
print("deponent =", cd["deponent"])
print(
    "advocate_firm =",
    cd["advocate_firm"],
    "| advocate_for =",
    cd["advocate_for"],
)

paras = r["generated_paragraphs"]["paragraphs"]

print("num generated paragraphs =", len(paras))
print("closing number =", paras[-1]["paragraph_number"])
