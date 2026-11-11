"""Индекс правил: канонические идентификаторы пунктов, разбор ссылок игрока, BM25-поиск.

Номера пунктов в rules.json повторяются между разделами (1.1 есть почти везде), поэтому
каждому пункту дан канонический id с префиксом раздела:
  общие правила (ОП)  -> "2.1"         (как в taxonomy.json и ответах админов: "2.1 ОП")
  правила жалоб       -> "ЖБ 1.2.2"
  зелёная зона        -> "GZ 1.1"
  остальные разделы   -> "ЛИД 1.1", "ГОС 2.1", "ГВ 1.1", "СМ 1.1", "ОПГ 1.1", "ВЗБ 1.1", "БЗФ 1.1"
"""
import json
import math
import re
from collections import Counter
from pathlib import Path

SECTION_PREFIX = {30: "", 31: "ЖБ", 32: "GZ", 33: "ЛИД", 34: "ГОС", 35: "ГВ", 36: "СМ",
                  40: "ОПГ", 41: "ВЗБ", 42: "БЗФ"}

# Как назвать раздел в тексте ответа на каждом языке
SECTION_NAME = {
    "": {"ru": "общих правил", "kk": "жалпы ережелердің", "uz": "umumiy qoidalarning",
         "en": "of the General Rules", "es": "de las Reglas Generales", "pt": "das Regras Gerais"},
    "ЖБ": {"ru": "правил подачи жалоб", "kk": "шағым беру ережелерінің", "uz": "shikoyat berish qoidalarining",
           "en": "of the Complaint Rules", "es": "de las Reglas de Quejas", "pt": "das Regras de Denúncias"},
    "GZ": {"ru": "правил Зелёной зоны", "kk": "Жасыл аймақ ережелерінің", "uz": "Yashil hudud qoidalarining",
           "en": "of the Green Zone Rules", "es": "de las Reglas de la Zona Verde", "pt": "das Regras da Zona Verde"},
}

# Синонимы разделов в тексте игрока/админа
PREFIX_ALIASES = [
    (r"(?:оп|op|общ\w*)", ""),
    (r"(?:жб|jb|ж\.б\.?)", "ЖБ"),
    (r"(?:gz|гз|зз|green\s*zone|зел\w*\s*зон\w*)", "GZ"),
    (r"(?:опг|opg)", "ОПГ"),
]


def _stem(tok: str) -> str:
    return tok[:5]


def tokenize(text: str) -> list[str]:
    return [_stem(t) for t in re.findall(r"[a-zа-яёәғқңөұүһі0-9]+", text.lower()) if len(t) > 1]


class RulesIndex:
    def __init__(self, path: str | Path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        self.points: dict[str, dict] = {}
        for sec in data["rules"]:
            prefix = SECTION_PREFIX.get(sec["id"])
            if prefix is None:
                continue
            for p in sec.get("points", []):
                ref = p["ref"] if not prefix else f"{prefix} {p['ref']}"
                self.points[ref] = {"ref": ref, "prefix": prefix, "num": p["ref"],
                                    "section": sec["category"], "text": p["text"]}
        # BM25 только по основным разделам: жалобы и репорты почти всегда про них
        self._doc_ids = [r for r, p in self.points.items() if p["prefix"] in ("", "ЖБ", "GZ")]
        self._docs = [tokenize(self.points[r]["text"]) for r in self._doc_ids]
        self._df = Counter(t for d in self._docs for t in set(d))
        self._avgdl = sum(len(d) for d in self._docs) / max(1, len(self._docs))

    def exists(self, ref: str) -> bool:
        return ref in self.points

    def text(self, ref: str) -> str:
        return self.points[ref]["text"]

    def rule_body(self, ref: str) -> str:
        """Текст пункта без блока санкций."""
        return self.points[ref]["text"].split("|")[0].strip()

    def human(self, ref: str, lang: str) -> str:
        p = self.points[ref]
        names = SECTION_NAME.get(p["prefix"])
        if names is None:
            return {"ru": f"п. {p['num']} раздела «{p['section']}»"}.get(lang, f"{p['num']} ({p['section']})")
        name = names.get(lang, names["ru"])
        return {
            "ru": f"п. {p['num']} {name}",
            "kk": f"{name} {p['num']}-тармағы",
            "uz": f"{name} {p['num']}-bandi",
            "en": f"clause {p['num']} {name}",
            "es": f"punto {p['num']} {name}",
            "pt": f"item {p['num']} {name}",
        }.get(lang, f"п. {p['num']} {name}")

    def parse_refs(self, text: str) -> list[str]:
        """Достает из текста игрока существующие пункты правил. Несуществующие отбрасываются."""
        if not text:
            return []
        low = text.lower().replace(",", ".")
        found: list[str] = []
        for m in re.finditer(r"(?<![\d.])(\d{1,2}(?:\.\d{1,2}){1,2})(?![\d])\s*([a-zа-яё.]{0,12})", low):
            num, tail = m.group(1), m.group(2)
            before = low[max(0, m.start() - 12):m.start()]
            prefix = ""
            for pat, pref in PREFIX_ALIASES:
                if re.search(pat, tail) or re.search(pat + r"\W*$", before):
                    prefix = pref
                    break
            ref = num if not prefix else f"{prefix} {num}"
            if ref in self.points and ref not in found:
                found.append(ref)
        return found

    def search(self, query: str, k: int = 3, prefixes=("", "ЖБ", "GZ")) -> list[tuple[str, float]]:
        q = tokenize(query)
        if not q:
            return []
        n = len(self._docs)
        scores = []
        for ref, d in zip(self._doc_ids, self._docs):
            if self.points[ref]["prefix"] not in prefixes:
                continue
            tf = Counter(d)
            s = 0.0
            for t in q:
                if t not in tf:
                    continue
                idf = math.log(1 + (n - self._df[t] + 0.5) / (self._df[t] + 0.5))
                s += idf * tf[t] * 2.2 / (tf[t] + 1.2 * (0.25 + 0.75 * len(d) / self._avgdl))
            if s > 0:
                scores.append((ref, s))
        scores.sort(key=lambda x: -x[1])
        return scores[:k]
