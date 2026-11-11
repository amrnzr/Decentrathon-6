"""Метрики на валидации: python scripts/evaluate.py --pred out/pred_valid.jsonl --data data/tickets_valid.jsonl

Категорий в валидации нет, поэтому классификация оценивается отдельно на ручной разметке
(scripts/eval_gold.py). Здесь считаем то, что можно проверить по реальным ответам админов:
совпадает ли тип черновика с вердиктом админа, цитаты, долю needs_human, латентность.
"""
import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from copilot.rules import RulesIndex  # noqa: E402

# какому вердикту админа соответствует тип черновика
EXPECTED = {
    "approve": {"approved", "punished"},
    "need_video": {"need_evidence"},
    "invalid_empty": {"invalid_format", "rejected"},
    "invalid_not_complaint": {"invalid_format", "rejected"},
    "invalid_toxic": {"invalid_format", "rejected"},
    "duplicate": {"duplicate"},
    "appeal": {"appeal_rejected", "appeal_approved"},
    "appeal_extra": {"appeal_rejected", "appeal_approved"},
}


def admin_outcome(r):
    v = r.get("verdict")
    if v == "other" and r.get("punishment"):
        return "punished"
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", default="out/pred_valid.jsonl")
    ap.add_argument("--data", default="data/tickets_valid.jsonl")
    ap.add_argument("--out", default="reports")
    args = ap.parse_args()
    rules = RulesIndex(Path(__file__).resolve().parent.parent / "data" / "rules.json")
    P = [json.loads(x) for x in open(args.pred, encoding="utf-8")]
    R = {r["ticket_id"]: r for r in (json.loads(x) for x in open(args.data, encoding="utf-8"))}
    n = len(P)
    tpl_stats = defaultdict(lambda: [0, 0])
    tpl_count = Counter()
    cited_total = cited_ok = 0
    no_cite_need = 0
    for p in P:
        r = R[p["ticket_id"]]
        tpl = p.get("template", "?")
        tpl_count[tpl] += 1
        for c in p["draft_reply"]["cited"]:
            cited_total += 1
            cited_ok += rules.exists(c)
        if not p["draft_reply"]["cited"] and p["category"] not in ("report.offtopic", "report.question", "report.help",
                                                                    "report.payment", "complaint.admin"):
            no_cite_need += 1
        if tpl in EXPECTED and r["kind"] == "complaint":
            tpl_stats[tpl][0] += 1
            tpl_stats[tpl][1] += admin_outcome(r) in EXPECTED[tpl]
    lat = sorted(p["latency_ms"] for p in P)
    by_lang = Counter(p["lang"] for p in P)
    human_by_kind = defaultdict(lambda: [0, 0])
    for p in P:
        k = R[p["ticket_id"]]["kind"]
        human_by_kind[k][0] += 1
        human_by_kind[k][1] += p["needs_human"]
    agree_n = sum(v[0] for v in tpl_stats.values())
    agree_ok = sum(v[1] for v in tpl_stats.values())
    gold = {}
    for name, f in (("tuning_set_120", "metrics_gold_manual_120.json"), ("holdout_70", "metrics_gold_holdout_70.json")):
        gp = Path(args.out) / f
        if gp.exists():
            gold[name] = json.loads(gp.read_text())
    metrics = {
        "tickets": n,
        "classification_on_manual_gold": gold,
        "draft_type_vs_admin_verdict": {
            "overall_agreement": round(agree_ok / max(1, agree_n), 3),
            "n_comparable": agree_n,
            "by_template": {k: {"n": v[0], "agree": round(v[1] / max(1, v[0]), 3)} for k, v in sorted(tpl_stats.items())},
        },
        "citations": {"total": cited_total, "existing_in_rules_json": cited_ok,
                      "share_valid": round(cited_ok / max(1, cited_total), 3),
                      "drafts_without_citation_in_rule_categories": no_cite_need},
        "needs_human_share": round(sum(p["needs_human"] for p in P) / n, 3),
        "needs_human_by_kind": {k: round(v[1] / v[0], 3) for k, v in human_by_kind.items()},
        "auto_answer_share": round(1 - sum(p["needs_human"] for p in P) / n, 3),
        "spam_or_duplicate_share": round(sum(p["is_spam_or_duplicate"] for p in P) / n, 3),
        "draft_lang": dict(by_lang),
        "categories": dict(Counter(p["category"] for p in P).most_common()),
        "priorities": dict(sorted(Counter(p["priority"] for p in P).items())),
        "templates": dict(tpl_count.most_common()),
        "latency_ms": {"p50": lat[n // 2], "p95": lat[int(0.95 * (n - 1))], "max": lat[-1]},
        "cost_per_ticket_usd": 0.0,
    }
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=1))

    # Примеры черновиков рядом с реальным ответом (содержат данные кейса: в публичный репозиторий не класть)
    random.seed(0)
    lines = ["# Примеры черновиков (валидация)\n", "Файл содержит тексты из данных Grand Mobile, не публиковать.\n"]
    picked = []
    for lang in ("ru", "kk", "uz", "en", "pt"):
        pool = [p for p in P if p["lang"] == lang]
        picked += random.sample(pool, min(len(pool), 8 if lang == "ru" else 4))
    for p in picked:
        r = R[p["ticket_id"]]
        player = " / ".join(m["text"] for m in r["messages"] if m["role"] == "player")
        real = " / ".join(m["text"] for m in r["messages"] if m["role"] == "admin")
        lines += [f"## {r['kind']} · {p['lang']} · {p['category']} · {p['priority']} · needs_human={p['needs_human']}\n",
                  f"**Игрок:** {player}\n", f"**Черновик:** {p['draft_reply']['text']}\n",
                  f"**Цитаты:** {p['draft_reply']['cited']}\n", f"**Реальный ответ админа:** {real}\n",
                  f"**Причины:** {'; '.join(p['reasons'])}\n"]
    (out / "examples.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
