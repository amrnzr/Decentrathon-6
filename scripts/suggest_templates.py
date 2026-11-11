"""Бонус: предложение новых шаблонов ответов по кластерам похожих обращений.

python scripts/suggest_templates.py --train data/tickets_train.jsonl.gz --out reports/template_suggestions.md

Как работает:
1. Тексты игроков (без ответа админа) кластеризуются: TF-IDF по словам + MiniBatchKMeans.
2. Для каждого кластера смотрим, как на эти обращения отвечали админы: самый частый
   нормализованный ответ и его доля.
3. Прогоняем обращения кластера через текущий сервис и смотрим, каким шаблоном он отвечает.
4. Если админы в кластере отвечают одинаково (доля ответа >= 20%), а черновик сервиса
   в большинстве случаев с этим ответом не совпадает, кластер становится кандидатом
   в новый шаблон: ответ админа предлагается как текст шаблона.

Выход содержит тексты из данных кейса: файл в .gitignore, не публиковать.
"""
import argparse
import gzip
import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.cluster import MiniBatchKMeans
from sklearn.feature_extraction.text import TfidfVectorizer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from copilot.labels import player_text  # noqa: E402
from copilot.pipeline import Copilot  # noqa: E402

NICK = re.compile(r"\b[A-Z][a-z]+_[A-Z][a-z]+\d*(\[\d+\])?")
GREET = re.compile(r"^\s*(приветствую|здравствуйте|уважаемый\s+игрок|добрый\s+(день|вечер)|assalomu\s+alaykum|salom)"
                   r"[\s,!.]*", re.I)


def norm_answer(a: str) -> str:
    a = NICK.sub("<ник>", a.strip())
    a = re.sub(r"\s+", " ", a)
    a = GREET.sub("", a).strip(" .!,")
    return a[:1].upper() + a[1:] if a else a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", default="data/tickets_train.jsonl.gz")
    ap.add_argument("--out", default="reports/template_suggestions.md")
    ap.add_argument("--kind", default="report", choices=["report", "complaint"])
    ap.add_argument("--k", type=int, default=60)
    ap.add_argument("--sample", type=int, default=30000)
    args = ap.parse_args()

    rng = np.random.default_rng(0)
    rows = []
    with gzip.open(args.train, "rt", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r["kind"] != args.kind:
                continue
            admin = [m["text"] for m in r["messages"] if m["role"] == "admin"]
            text = player_text(r)
            if admin and len(text) >= 4:
                rows.append((r, text, norm_answer(admin[-1])))
    if len(rows) > args.sample:
        idx = rng.choice(len(rows), args.sample, replace=False)
        rows = [rows[i] for i in idx]
    texts = [t.lower() for _, t, _ in rows]

    vec = TfidfVectorizer(analyzer="word", token_pattern=r"(?u)\b[\w']{2,}\b", min_df=5, max_df=0.3,
                          sublinear_tf=True)
    X = vec.fit_transform(texts)
    km = MiniBatchKMeans(n_clusters=args.k, random_state=0, n_init=3, batch_size=4096).fit(X)
    terms = np.array(vec.get_feature_names_out())

    cp = Copilot()
    used, drafts = [], []
    for r, _, _ in rows:
        t = {k: v for k, v in r.items() if k not in ("verdict", "punishment", "violation")}
        t["messages"] = [m for m in r["messages"] if m["role"] != "admin"]
        t.pop("reporter_hash", None)  # без дедупликации
        res = cp.triage(t)
        used.append(res["template"])
        drafts.append(norm_answer(res["draft_reply"]["text"]))

    clusters = []
    for c in range(args.k):
        members = np.where(km.labels_ == c)[0]
        if len(members) < 50:
            continue
        answers = Counter(rows[i][2] for i in members)
        top_answer, top_n = answers.most_common(1)[0]
        share = top_n / len(members)
        tpl = Counter(used[i] for i in members)
        our_tpl, our_n = tpl.most_common(1)[0]
        # совпадает ли наш черновик с самым частым ответом админа (без приветствия, без регистра)
        key = top_answer.lower().replace("<ник>", "").strip(" .")
        same = sum(drafts[i].lower().strip(" .").startswith(key) for i in members) / len(members)
        center = km.cluster_centers_[c]
        order = np.argsort(-center)[:6]
        keywords = [terms[j] for j in order if center[j] > 0.01]
        examples = [rows[i][1][:70] for i in members[:3]]
        candidate = share >= 0.2 and len(top_answer) >= 5 and same < 0.5
        clusters.append(dict(c=c, size=len(members), keywords=keywords, top_answer=top_answer, share=share,
                             our_tpl=our_tpl, our_share=our_n / len(members), same=same,
                             examples=examples, candidate=candidate))
    clusters.sort(key=lambda x: (-x["candidate"], -x["size"] * x["share"]))

    lines = [f"# Предложения новых шаблонов ({args.kind})\n",
             "Файл содержит тексты из данных кейса, не публиковать.\n",
             f"Кластеров: {len(clusters)}, обращений в выборке: {len(rows)}. Кандидат = админы отвечают "
             "одинаково (>= 20% одним ответом), а черновик сервиса в большинстве случаев с этим ответом не совпадает.\n",
             "| # | Размер | Ключевые слова | Частый ответ админа | Доля | Шаблон сервиса | Черновик совпадает | Кандидат |",
             "|---|---|---|---|---|---|---|---|"]
    for x in clusters:
        lines.append(f"| {x['c']} | {x['size']} | {', '.join(x['keywords'])} | {x['top_answer'][:90]} | "
                     f"{x['share']:.0%} | {x['our_tpl']} ({x['our_share']:.0%}) | {x['same']:.0%} | {'да' if x['candidate'] else ''} |")
    lines.append("\n## Кандидаты подробно\n")
    for x in clusters:
        if not x["candidate"]:
            continue
        lines += [f"### Кластер {x['c']} · {x['size']} обращений",
                  f"Ключевые слова: {', '.join(x['keywords'])}",
                  f"Примеры: {' / '.join(x['examples'])}",
                  f"Предлагаемый шаблон: «{x['top_answer']}» (так отвечали в {x['share']:.0%} случаев)",
                  f"Сейчас сервис отвечает: {x['our_tpl']}\n"]
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text("\n".join(lines), encoding="utf-8")
    n_cand = sum(x["candidate"] for x in clusters)
    covered = sum(x["same"] * x["size"] for x in clusters) / max(1, sum(x["size"] for x in clusters))
    lines.insert(3, f"Черновик сервиса совпадает с самым частым ответом админа своего кластера в {covered:.0%} обращений.\n")
    Path(args.out).write_text("\n".join(lines), encoding="utf-8")
    print(f"совпадение черновика с типовым ответом кластера: {covered:.0%}")
    print(f"{n_cand} кандидатов из {len(clusters)} кластеров -> {args.out}")


if __name__ == "__main__":
    main()
