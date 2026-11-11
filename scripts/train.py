"""Слабая разметка train, обучение классификатора, сборка базы знаний.

python scripts/train.py --train data/tickets_train.jsonl.gz --out models/
"""
import argparse
import gzip
import json
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from copilot.classifier import Classifier, features  # noqa: E402
from copilot.kb import KB, clean_answer  # noqa: E402
from copilot.labels import accused_text, player_text, weak_label  # noqa: E402


def read_jsonl(path):
    op = gzip.open if str(path).endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", default="data/tickets_train.jsonl.gz")
    ap.add_argument("--out", default="models")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    rows = list(read_jsonl(args.train))
    docs, labels, kb_q, kb_a = [], [], [], []
    for r in rows:
        text = player_text(r)
        lab = weak_label(r)
        docs.append(features(r["kind"], text, r.get("rule_refs_raw") or "", bool(accused_text(r))))
        labels.append(lab)
        if r["kind"] == "report" and lab in ("report.question", "report.help") and len(text) >= 8:
            admin = [m["text"] for m in r["messages"] if m["role"] == "admin"]
            if admin:
                a = clean_answer(admin[-1])
                if a:
                    kb_q.append(text.lower())
                    kb_a.append(a)
    print("weak labels:", Counter(labels).most_common(), flush=True)

    clf = Classifier().fit(docs, labels)
    clf.save(out / "classifier.pkl")
    print(f"classifier trained on {len(docs)} tickets, {time.time() - t0:.0f}s", flush=True)

    kb = KB(kb_q, kb_a)
    kb.save(out / "kb.pkl")
    print(f"KB: {len(kb_q)} question-answer pairs", flush=True)


if __name__ == "__main__":
    main()
