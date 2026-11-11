"""make predict IN=tickets.jsonl OUT=pred.jsonl

Обрабатывает тикеты в порядке created_at (нужно для дедупликации), пишет предсказания
в исходном порядке. Каждая строка выхода: ticket_id + ответ POST /triage.
"""
import argparse
import gzip
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from copilot.pipeline import Copilot  # noqa: E402


def read_jsonl(path):
    op = gzip.open if str(path).endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    cp = Copilot()
    rows = read_jsonl(args.inp)
    order = sorted(range(len(rows)), key=lambda i: rows[i].get("created_at") or "")
    preds = [None] * len(rows)
    lat = []
    t0 = time.time()
    for i in order:
        # не даем сервису подсмотреть ответ админа и разметку исхода
        r = {k: v for k, v in rows[i].items() if k not in ("verdict", "punishment", "violation", "category", "priority")}
        r["messages"] = [m for m in r.get("messages", []) if m.get("role") != "admin"]
        p = cp.triage(r)
        lat.append(p["latency_ms"])
        preds[i] = {"ticket_id": rows[i].get("ticket_id"), **p}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        for p in preds:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    lat.sort()
    p95 = lat[int(0.95 * (len(lat) - 1))] if lat else 0
    print(f"{len(rows)} tickets in {time.time() - t0:.1f}s, p50={lat[len(lat) // 2]:.1f}ms p95={p95:.1f}ms",
          file=sys.stderr)


if __name__ == "__main__":
    main()
