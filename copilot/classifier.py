"""TF-IDF + логистическая регрессия поверх слабой разметки + правила как страховка."""
import pickle
from pathlib import Path

import numpy as np
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from .labels import complaint_category, report_category


def features(kind: str, text: str, rule_refs_raw: str, has_reply: bool) -> str:
    return f"[{kind}] {text} [rr] {rule_refs_raw or ''} {'[acc]' if has_reply else ''}".lower()


class Classifier:
    def __init__(self):
        self.char = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=3, max_features=300_000,
                                    sublinear_tf=True)
        self.word = TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=2, max_features=200_000,
                                    sublinear_tf=True, token_pattern=r"(?u)[\w.']+")
        self.clf = LogisticRegression(max_iter=300, C=4.0)

    def _X(self, docs, fit=False):
        if fit:
            return hstack([self.char.fit_transform(docs), self.word.fit_transform(docs)]).tocsr()
        return hstack([self.char.transform(docs), self.word.transform(docs)]).tocsr()

    def fit(self, docs, labels):
        X = self._X(docs, fit=True)
        self.clf.fit(X, labels)
        return self

    def predict_proba(self, docs):
        return self.clf.predict_proba(self._X(docs))

    def predict(self, kind: str, doc: str, text: str, rule_refs_raw: str,
                trust_model: bool = True) -> tuple[str, float, str]:
        """Возвращает (категория, уверенность, источник). Категория всегда согласована с kind.

        Логика: правило и модель голосуют. Если модель уверена (>0.6, порог подобран по 190 размеченным тикетам) и не согласна с правилом,
        берем модель. Иначе правило. Уверенность = вероятность выбранного класса по модели.
        """
        proba = self.predict_proba([doc])[0]
        classes = self.clf.classes_
        mask = np.array([c.startswith(kind + ".") for c in classes])
        p = np.where(mask, proba, 0.0)
        p = p / p.sum() if p.sum() > 0 else p
        best = classes[int(p.argmax())]
        rule = report_category(text) if kind == "report" else complaint_category(text, rule_refs_raw)
        p_rule = float(p[list(classes).index(rule)]) if rule in classes else 0.0
        # редкие, но критичные категории из правил модель не перебивает
        if rule in ("report.payment", "report.account"):
            return rule, max(p_rule, 0.8), "rule"
        if trust_model and best != rule and p.max() > 0.6:
            return best, float(p.max()), "model"
        return rule, max(p_rule, 0.35), "rule"

    def save(self, path: str | Path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path: str | Path) -> "Classifier":
        with open(path, "rb") as f:
            return pickle.load(f)
