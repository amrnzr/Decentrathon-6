"""Оценка классификации на ручной разметке тикетов валидации.

python scripts/eval_gold.py [reports/gold_holdout_70.json] [--verbose]
gold_manual_120 использовалась для настройки правил, gold_holdout_70 размечена после и не подкручивалась.
"""
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import accuracy_score, f1_score

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from copilot.classifier import Classifier, features  # noqa: E402
from copilot.labels import (accused_text, complaint_category, has_evidence, player_text,  # noqa: E402
                            priority, report_category)

verbose = "--verbose" in sys.argv
gold_path = next((a for a in sys.argv[1:] if a.endswith(".json")), "reports/gold_manual_120.json")
clf = Classifier.load("models/classifier.pkl")
rows = [json.loads(line) for line in open("data/tickets_valid.jsonl", encoding="utf-8")]
gold = json.load(open(gold_path))
yr, ym, yh, yg, pg, pp = [], [], [], [], [], []
for i, g in gold.items():
    r = rows[int(i)]
    t = player_text(r)
    rr = r.get("rule_refs_raw") or ""
    rule = report_category(t) if r["kind"] == "report" else complaint_category(t, rr)
    d = features(r["kind"], t, rr, bool(accused_text(r)))
    pr = clf.predict_proba([d])[0]
    cl = clf.clf.classes_
    m = np.array([c.startswith(r["kind"] + ".") for c in cl])
    model = cl[(pr * m).argmax()]
    hyb, conf, src = clf.predict(r["kind"], d, t, rr)
    yr.append(rule); ym.append(model); yh.append(hyb); yg.append(g["category"])
    pg.append(g["priority"]); pp.append(priority(hyb, t, has_evidence(r, t)))
    if verbose and hyb != g["category"]:
        print(i, "gold", g["category"], "| pred", hyb, src, round(conf, 2), "|", t[:90])
res = {
    "n": len(yg),
    "category_accuracy_rules": round(accuracy_score(yg, yr), 3),
    "category_accuracy_model": round(accuracy_score(yg, ym), 3),
    "category_accuracy_hybrid": round(accuracy_score(yg, yh), 3),
    "priority_macro_f1": round(f1_score(pg, pp, average="macro"), 3),
    "priority_accuracy": round(accuracy_score(pg, pp), 3),
}
print(json.dumps(res, ensure_ascii=False, indent=1))
Path(gold_path.replace("gold_", "metrics_gold_")).write_text(json.dumps(res, ensure_ascii=False, indent=1))
