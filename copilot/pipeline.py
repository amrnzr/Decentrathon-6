"""Триаж одного обращения: язык, категория, приоритет, факты, черновик, needs_human."""
import re
import time
from collections import deque
from datetime import datetime
from pathlib import Path

from . import templates as TP
from .classifier import Classifier, features
from .kb import KB
from .labels import (KWC, OFFTOPIC_RE, accused_text, has_evidence, is_spam, player_text,
                     priority as calc_priority)
from .normalize import detect_lang, find_nicks
from .rules import RulesIndex

ROOT = Path(__file__).resolve().parent.parent

# Обещания, которые черновик не может давать сам: такие тикеты идут человеку
PROMISE_RE = re.compile(
    r"(?<!не\s)разбан|(?<!не\s)сним\w*\s*(бан|мут|наказ)|наказание\s*будет\s*снято|верн[её]м|возврат|компенсир|компенсац|"
    r"получит\s|будет\s*наказан|жаза:|jazo:|will\s*receive|recibirá|receberá|unban|refund",
    re.I,
)
ALWAYS_HUMAN = {"report.account", "report.payment", "complaint.admin"}

GZ_CUE = re.compile(r"\bgz\b|\bгз\b|\bзз\b|\bzz\b|зел[её]н\w*\s*зон|green\s*zone|больниц|банк[еау]?\b|вокзал|автосалон|"
                    r"автошкол|мэри|правительств|стоянк|yashil", re.I)
HOUSE_CUE = re.compile(r"\bдом[аеу]?\b|квартир|у\s*входа|uy\s*oldida|uyim", re.I)
RP_LEAVE_CUE = re.compile(r"вышел\s*из\s*игр|ливнул|лив\b|афк|\bafk\b|уход\w*\s*от\s*рп|ушел\s*от\s*рп|ушёл\s*от\s*рп", re.I)
FAMILY_CUE = re.compile(r"mother|mom\b|father|family|mãe|madre|familia|família|анам|анаң|анасы|\bана\b|әке|туған|родн|родит|мам|мать|матер[иь]|сем[ьи]|бабушк|отц|отец|папа|rodn|rod\b|onasi|onam|ona\b|"
                        r"oilasi|туыс|анас", re.I)
MENTION_CUE = re.compile(r"упом|упомин|eslat", re.I)
RACISM_CUE = re.compile(r"расизм|расист|нацио|национ|религ|xenofob|ксенофоб|\b2\.4\b", re.I)
EXTORT_CUE = re.compile(r"вымога|угрожа\w*\s*(забрать|отдать)|tovlam|\b4\.2\b", re.I)
ADS_CUE = re.compile(r"реклам|другой\s*сервер|другого\s*сервера|discord\.gg|\b2\.3\b|reklama", re.I)
TELEPORT_CUE = re.compile(r"телепорт|\bтп\b|тпни|тпшни|подкин|довез|отвез|метк|teleport|\btp\b", re.I)
VEHICLE_CUE = re.compile(r"машин|авто|транспорт|мото|матоц|мопед|байк|велик|грузов|фур|vehicle|car\b|carro|coche|"
                         r"mashina|moshin|көлік", re.I)
VEHICLE_PROBLEM = re.compile(r"из\s*воды|суға|түсіп|аударыл|тұрып\s*қал|suvga|ag'?dar|перевер|перевор|перевёр|застр|в\s*вод|под\s*вод|упал|слетел|flipped|stuck|virou|"
                             r"atascad|preso|travad|tiqil|ag'darildi|qoldi", re.I)
JAIL_CUE = re.compile(r"тюрьм|тюрм|турм|деморган|джайл|выпустите|освободите|qamoq|түрме|prison|jail|cárcel|prisão", re.I)
PROPERTY_LOSS = re.compile(r"пропал|исчез|украл|обнул|потерял|забрал|sumiu|perdí|yo'qoldi|o'g'irla", re.I)
MAT_RE = re.compile(r"ху[йеёияю]|пизд|\bеба|\bъеба|ебан|ебат|ебал|\bбля|сука|суки|шлюх|уеб|мудак|гандон|долбо[её]б|залуп", re.I)
# Грамматика шаблона approve, когда ник нарушителя неизвестен
NO_NICK = {
    "kk": [(" ойыншысының", " Аталған ойыншының"), (" ойыншысына", " Аталған ойыншыға")],
    "uz": [(" o'yinchisining", " Ushbu o'yinchining"), (" o'yinchisiga", " Ushbu o'yinchiga")],
    "en": [("Player  violated", "The player violated"), ("Player  will", "The player will")],
}

# Темы вопросов о правилах -> пункт. Точнее, чем BM25 без морфологии
RULE_TOPICS = [(re.compile(p, re.I), r) for p, r in [
    (r"зел[её]н\w*\s*зон|\bgz\b|\bзз\b", "GZ 1.1"),
    (r"реклам", "2.3"),
    (r"реал\w*\s*деньг|за\s*реал|продать\s*акк|продава\w*\s*акк|купить\s*акк", "4.4"),
    (r"бизнес\w*", "4.3"),
    (r"чит|сторонн|софт|макрос|автоклик|сборк", "5.2"),
    (r"оскорб|мат\b|материт|родн", "2.1"),
    (r"репорт", "3.1"),
    (r"\bник\w*|никнейм", "1.6"),
    (r"удал\w*\s*акк", "1.7"),
    (r"полити|национ|религ|расизм", "2.4"),
    (r"передать\s*(деньг|имущ|валют)|подар", "4.5"),
    (r"между\s*сервер|на\s*друг\w*\s*сервер", "4.7"),
    (r"тви?нк|втор\w*\s*акк|друг\w*\s*персонаж|своими\s*персонаж", "4.6"),
    (r"у\s*дома|в\s*доме|квартир", "5.4"),
    (r"выйти\s*из\s*игры|ливнуть|уйти\s*от\s*рп", "5.3"),
]]
SERVER_RE = re.compile(r"(?:сервер\w*|server\w*|серв)\s*№?\s*(\d{1,3})", re.I)


class Copilot:
    def __init__(self, models_dir: str | Path = ROOT / "models", rules_path: str | Path = ROOT / "data" / "rules.json"):
        self.rules = RulesIndex(rules_path)
        self.clf = Classifier.load(Path(models_dir) / "classifier.pkl")
        self.kb = KB.load(Path(models_dir) / "kb.pkl")
        # история для дедупликации в рамках процесса: (ts, reporter, reported, text)
        self.history: deque = deque(maxlen=50_000)

    # --------------------------------------------------------------- helpers
    def _ref(self, ref: str, lang: str) -> str:
        return self.rules.human(ref, lang)

    def _is_duplicate(self, t: dict, text: str) -> bool:
        reporter = t.get("reporter_hash")
        if not reporter:
            return False
        ts = _parse_ts(t.get("created_at"))
        reported = t.get("reported_hash")
        key_text = re.sub(r"\W+", " ", text.lower()).strip()
        dup = False
        for (ts0, rep0, red0, txt0, kind0) in reversed(self.history):
            if ts is not None and ts0 is not None and abs((ts - ts0).total_seconds()) > 3600:
                continue
            if rep0 != reporter or kind0 != t.get("kind"):
                continue
            if t.get("kind") == "complaint" and reported and red0 == reported:
                dup = True
                break
            if t.get("kind") == "report" and len(key_text) > 6 and txt0 == key_text:
                dup = True
                break
        self.history.append((ts, reporter, reported, key_text, t.get("kind")))
        return dup

    # ------------------------------------------------------------------ main
    def triage(self, t: dict) -> dict:
        t0 = time.perf_counter()
        TP.USED.clear()
        kind = t.get("kind") or "report"
        if kind not in ("complaint", "report"):
            kind = "report"
        text = player_text(t)
        rr = t.get("rule_refs_raw") or ""
        server_lang = t.get("server_lang")
        lang = detect_lang(text, server_lang)
        evidence = has_evidence(t, text)
        doc = features(kind, text, rr, bool(accused_text(t)))
        # модель училась в основном на русском и узбекском; для kk/en/es/pt решают правила
        category, cat_conf, cat_src = self.clf.predict(kind, doc, text, rr, trust_model=lang in ("ru", "uz"))
        prio = calc_priority(category, text, evidence)
        nicks = find_nicks(text)
        nickname = t.get("reported_nick") or (nicks[0] if nicks else None)
        refs = self.rules.parse_refs(f"{text} {rr}")
        m_server = SERVER_RE.search(text)
        extracted = {"nickname": nickname, "rule_refs": refs, "has_evidence": evidence,
                     "server": m_server.group(1) if m_server else None}

        duplicate = self._is_duplicate(t, text)
        spam = kind == "report" and category == "report.offtopic" and (is_spam(text) or not re.search(
            r"помог|помож|помаг|помгит|памаг|хелп|help|\bсос\b|\bsos\b|yordam|ayud|ajud|көмек|следи", text, re.I))

        if duplicate and kind == "complaint":
            body, cited, human, sit_conf, reasons = self._duplicate(lang)
        elif kind == "complaint":
            body, cited, human, sit_conf, reasons = self._complaint(category, text, rr, refs, evidence, lang, nickname)
        else:
            body, cited, human, sit_conf, reasons = self._report(category, text, lang, spam)
            if duplicate:
                reasons.append("повтор того же репорта за последний час")

        draft_text = TP.wrap(body, lang, kind)
        # ---------- guardrails
        cited = [c for c in dict.fromkeys(cited) if self.rules.exists(c)]
        if category in ALWAYS_HUMAN:
            human = True
            reasons.append("категория всегда идет человеку (аккаунт, платежи, жалобы на администрацию)")
        if PROMISE_RE.search(draft_text):
            if not human:
                reasons.append("черновик содержит обещание действия, нужна проверка администратора")
            human = True
        if KWC["threat_irl"].search(text):
            human = True
            reasons.append("возможна угроза вне игры, приоритет p0")
        confidence = round(max(0.05, min(0.99, 0.5 * cat_conf + 0.5 * sit_conf)), 2)
        if confidence < 0.45 and not human:
            human = True
            reasons.append("низкая уверенность классификации")
        return {
            "lang": lang,
            "category": category,
            "priority": prio,
            "is_spam_or_duplicate": bool(duplicate or spam),
            "extracted": extracted,
            "draft_reply": {"lang": lang, "text": draft_text, "cited": cited},
            "needs_human": bool(human),
            "confidence": confidence,
            "reasons": list(dict.fromkeys(reasons)),
            "template": TP.USED[0] if TP.USED else "kb_answer",
            "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
        }

    # ------------------------------------------------------------ complaints
    def _duplicate(self, lang):
        r1 = "ЖБ 1.2.9"
        body = TP.get("duplicate", lang).format(r1=self._ref(r1, lang))
        return body, [r1], False, 0.8, ["дубликат: тот же заявитель и тот же обвиняемый в течение часа"]

    def _violation(self, category: str, text: str, rr: str):
        """(ref, desc_key, punishment_key, needs_video) или None, если пункт не определить надежно."""
        both = f"{text} {rr}"
        if category == "complaint.insult":
            if RACISM_CUE.search(both):
                return "2.4", "racism", "mute60", False
            if FAMILY_CUE.search(both):
                if MENTION_CUE.search(both):
                    return "2.1", "insult_family", "mute90", False
                return "2.1", "insult_family", "ban7", False
            return "2.1", "insult", "mute30", False
        if category == "complaint.cheat":
            return "5.2", "cheat", "ban31", True
        if category == "complaint.dm":
            if GZ_CUE.search(both):
                return "GZ 1.1", "dm_gz", "demorgan60", True
            if HOUSE_CUE.search(both):
                return "5.4", "dm_house", "demorgan120", True
            if RP_LEAVE_CUE.search(both):
                return "5.3", "dm_rp", "demorgan60", True
            return None, None, None, True
        if category == "complaint.scam":
            if EXTORT_CUE.search(both):
                return "4.2", "extortion", "ban7", True
            return "4.1", "scam", "ban31", True
        if category == "complaint.rmt_ads":
            if ADS_CUE.search(both):
                return "2.3", "ads", "mute60", False
            return "4.4", "rmt", "ban31", False
        if category == "complaint.other":
            low = both.lower()
            if re.search(r"\b1\.6\b|ник\b|никнейм|nick", low):
                return "1.6", "nick", "verbal", False
            if re.search(r"\b1\.2\b.*оп|является\s*администратор|я\s*админ|выдает\s*себя", low):
                return "1.2", "impersonation", "ban7", False
            if re.search(r"\b5\.9\b|ивент|мероприят", low):
                return "5.9", "event", "warn", False
        return None, None, None, False

    def _complaint(self, category, text, rr, refs, evidence, lang, nick):
        reasons = []
        has_video = bool(re.search(r"<url>|https?://|youtu|rutube|imgur|disk", text, re.I))
        if category == "complaint.admin":
            if KWC["appeal"].search(f"{text} {rr}") or not KWC["admin"].search(text):
                r1, r2 = "ЖБ 1.3.1", "ЖБ 1.3.4"
                extra = ""
                cited = []
                if len(text) < 60:
                    extra = TP.get("appeal_extra", lang).format(r1=self._ref(r1, lang), r2=self._ref(r2, lang))
                    cited = [r1, r2]
                body = TP.get("appeal", lang).format(extra=extra)
                return body, cited, True, 0.7, ["апелляция на наказание: решение принимает старшая администрация"]
            r1 = "3.4"
            body = TP.get("admin_misconduct", lang).format(r1=self._ref(r1, lang))
            return body, [r1], True, 0.7, ["жалоба на администратора"]

        if category == "complaint.invalid":
            if KWC["question"].search(text) and len(text) > 10:
                r1 = "ЖБ 1.1.2"
                body = TP.get("invalid_not_complaint", lang).format(r1=self._ref(r1, lang))
                return body, [r1], False, 0.6, ["похоже на вопрос, а не на жалобу"]
            r1, r2 = "ЖБ 1.2.3", "ЖБ 1.3.1"
            body = TP.get("invalid_empty", lang).format(r1=self._ref(r1, lang), r2=self._ref(r2, lang))
            reasons.append("в жалобе нет описания нарушения")
            human = evidence  # скриншоты мы не видим: пусть админ глянет, вдруг нарушение на них очевидно
            if human:
                reasons.append("есть вложения, которые сервис не видит")
            return body, [r1, r2], human, 0.55, reasons

        if len(MAT_RE.findall(text)) >= 2:
            r1 = "ЖБ 1.2.7"
            body = TP.get("invalid_toxic", lang).format(r1=self._ref(r1, lang))
            return body, [r1], True, 0.6, ["текст жалобы содержит ненормативную лексику (возможна цитата обвиняемого)"]
        ref, desc_key, pun_key, needs_video = self._violation(category, text, rr)
        if needs_video and not has_video:
            r1, r2 = "ЖБ 1.2.2", "ЖБ 1.2.1"
            body = TP.get("need_video", lang).format(r1=self._ref(r1, lang), r2=self._ref(r2, lang))
            return body, [r1, r2], False, 0.6, ["для этого типа нарушения админы обычно требуют видео"]
        if ref and self.rules.exists(ref):
            body = TP.get("approve", lang).format(
                nick=nick or "", rule=self._ref(ref, lang), desc=TP.VIOLATION_DESC[desc_key].get(lang, TP.VIOLATION_DESC[desc_key]["ru"]),
                punishment=TP.PUNISHMENT[pun_key].get(lang, TP.PUNISHMENT[pun_key]["ru"]))
            if not nick:
                for old, new in NO_NICK.get(lang, []):
                    body = body.replace(old, new)
            return body, [ref], True, 0.75, [
                "решение о наказании подтверждает администратор после просмотра доказательств",
                "факты из текста жалобы не проверены: скриншотов у сервиса нет"]
        r1 = "ЖБ 1.1.1"
        body = TP.get("complaint_review", lang).format(r1=self._ref(r1, lang))
        return body, [r1], True, 0.5, ["пункт нарушения не удалось определить надежно"]

    # --------------------------------------------------------------- reports
    def _report(self, category, text, lang, spam):
        if category == "report.payment":
            return TP.get("payment", lang), [], True, 0.8, ["платеж: всегда человек"]
        if category == "report.account":
            extra, cited = "", []
            if PROPERTY_LOSS.search(text) or KWC["account"].search(text):
                r1 = "1.4"
                extra = TP.get("account_extra", lang).format(r1=self._ref(r1, lang))
                cited = [r1]
            return TP.get("account", lang).format(extra=extra), cited, True, 0.8, ["аккаунт: всегда человек"]
        if category == "report.offtopic":
            if spam:
                r1 = "3.1"
                return TP.get("spam", lang).format(r1=self._ref(r1, lang)), [r1], False, 0.75, ["пустое сообщение или оффтоп"]
            # «помогите» без деталей: админы почти всегда отвечают «слежу за вами» и смотрят сами
            return TP.get("help_admin", lang), [], True, 0.7, ["просьба о помощи без деталей: администратору нужно посмотреть"]
        if category == "report.help":
            if TELEPORT_CUE.search(text) and not VEHICLE_PROBLEM.search(text):
                r1 = "3.1"
                return TP.get("no_teleport", lang).format(r1=self._ref(r1, lang)), [r1], False, 0.65, ["просьба о телепорте"]
            if VEHICLE_CUE.search(text) and VEHICLE_PROBLEM.search(text):
                return TP.get("help_vehicle", lang), [], False, 0.65, ["типовая проблема с транспортом"]
            if JAIL_CUE.search(text):
                return TP.get("jail", lang), [], False, 0.6, ["просьба освободить из тюрьмы"]
            return TP.get("help_admin", lang), [], True, 0.7, ["нужна помощь администратора в игре (телепорт, освобождение)"]
        if category == "report.complaint":
            return TP.get("report_complaint", lang), [], True, 0.7, [
                "жалоба через репорт: администратору нужно проверить игрока"]
        # report.question
        if KWC["rules_q"].search(text):
            ref = next((r for pat, r in RULE_TOPICS if pat.search(text)), None)
            if ref and self.rules.exists(ref):
                body_ru = re.split(r"(?<=[.!?])\s", self.rules.rule_body(ref))[0]
                body = TP.get("rules_answer", lang).format(rule=self._ref(ref, lang), body=body_ru)
                return body, [ref], False, 0.7, ["вопрос по правилам: пункт выбран по теме вопроса"]
            hits = self.rules.search(text, k=1, prefixes=("", "GZ"))
            if hits and hits[0][1] >= 9:  # BM25 без морфологии ненадежен: цитируем только при сильном совпадении
                ref = hits[0][0]
                body_ru = re.split(r"(?<=[.!?])\s", self.rules.rule_body(ref))[0]
                body = TP.get("rules_answer", lang).format(rule=self._ref(ref, lang), body=body_ru)
                return body, [ref], True, 0.55, ["ответ по правилам найден поиском, проверьте релевантность пункта"]
        if lang in ("ru",):
            ans, score = self.kb.lookup(text)
            if ans and score >= 0.45:
                return ans, [], False, min(0.9, 0.4 + score), ["ответ из базы ответов администраторов"]
            if ans and score >= 0.25:
                return ans, [], True, 0.4 + score / 2, ["похожий ответ из базы найден, но уверенность низкая"]
        return TP.get("question_forward", lang), [], True, 0.5, ["ответа в базе знаний нет"]


def _parse_ts(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s)[:19])
    except ValueError:
        return None
