"""База знаний из ответов администраторов на вопросы в репортах (train).

Для вопроса игрока ищем похожие вопросы и голосуем за ответ: берем ответ, который
админы давали чаще всего среди ближайших соседей. Так случайный неудачный ответ
одного админа не попадает в черновик.
"""
import pickle
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

GENERIC = re.compile(
    r"слежу|уточните|лечу|спешу|работаю|на\s*помощь|ожидайте|приятной\s*игры|помогу|сейчас\s*помо|"
    r"постара|попробу|помочь|нет\s*информац|не\s*знаю|не\s*подсказываем|kuzat|yordamga|aniqlashtir|<url>|<digits>|<email>|<handle>|разбан|верн[её]м|компенс|получит\s*(бан|мут)|наказан",
    re.I,
)
GREET = re.compile(r"^\s*(приветствую|здравствуйте|добрый\s*(день|вечер)|привет|салам\w*|assalomu\s*alaykum|salom)"
                   r"[\s,!.]*(уважаемый\s*игрок[,!.]?)?\s*", re.I)
NICK = re.compile(r"\b[A-Z][a-z]+_[A-Z][a-z]+\d*\b")


def clean_answer(ans: str) -> str | None:
    a = re.sub(r"\s+", " ", ans).strip()
    a = GREET.sub("", a)
    a = NICK.sub("", a).strip(" ,.")
    if len(a) < 12 or GENERIC.search(a):
        return None
    a = a[0].upper() + a[1:]
    if not a.endswith((".", "!", "?")):
        a += "."
    return a


class KB:
    def __init__(self, questions: list[str], answers: list[str]):
        self.answers = answers
        self.vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), min_df=2, sublinear_tf=True)
        self.X = self.vec.fit_transform(questions)

    def lookup(self, question: str, k: int = 15) -> tuple[str | None, float]:
        q = self.vec.transform([question.lower()])
        sims = (self.X @ q.T).toarray().ravel()
        if sims.max() <= 0:
            return None, 0.0
        idx = np.argpartition(-sims, min(k, len(sims) - 1))[:k]
        votes: dict[str, float] = defaultdict(float)
        best_sim: dict[str, float] = defaultdict(float)
        for i in idx:
            key = self.answers[i].lower().strip(" .")
            votes[key] += float(sims[i])
            best_sim[key] = max(best_sim[key], float(sims[i]))
        key = max(votes, key=votes.get)
        ans = next(self.answers[i] for i in idx if self.answers[i].lower().strip(" .") == key)
        # уверенность: похожесть ближайшего вопроса с этим ответом * доля голосов
        share = votes[key] / sum(votes.values())
        return ans, best_sim[key] * (0.5 + 0.5 * share)

    def save(self, path):
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path) -> "KB":
        with open(path, "rb") as f:
            return pickle.load(f)
