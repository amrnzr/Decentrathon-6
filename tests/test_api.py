"""Проверки контракта и guardrails. Требуют обученных моделей (make train)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402

from app import app, copilot  # noqa: E402
from copilot.normalize import detect_lang, normalize  # noqa: E402

client = TestClient(app)
FIELDS = {"lang", "category", "priority", "is_spam_or_duplicate", "extracted", "draft_reply", "needs_human",
          "confidence", "reasons"}


def post(kind, text, **extra):
    r = client.post("/triage", json={"kind": kind, "messages": [{"role": "player", "text": text, "attachments": 1}],
                                     **extra})
    assert r.status_code == 200
    return r.json()


def test_contract_example():
    res = post("complaint", "Arman_Petrov оскорблял меня и мою семью в чате, скрины есть, 2.1 ОП")
    assert set(res) == FIELDS
    assert res["category"] == "complaint.insult"
    assert res["extracted"]["nickname"] == "Arman_Petrov"
    assert res["extracted"]["rule_refs"] == ["2.1"]
    assert "2.1" in res["draft_reply"]["cited"]
    assert res["needs_human"] is True  # черновик обещает наказание


def test_citations_always_exist():
    texts = ["читер летает", "убил в зеленой зоне", "скам на машину", "реклама другого сервера", "не согласен",
             ".", "привет", "подкиньте до банка", "можно ли рекламировать ютуб", "1.2.3.4 9.9 ЖБ 7.7"]
    for kind in ("complaint", "report"):
        for t in texts:
            res = post(kind, t)
            for ref in res["draft_reply"]["cited"]:
                assert copilot.rules.exists(ref), (t, ref)


def test_always_human():
    assert post("report", "оплатил гк, не пришло")["needs_human"] is True
    assert post("report", "взломали аккаунт")["needs_human"] is True
    assert post("complaint", "админ выдал мут без причины")["needs_human"] is True


def test_no_promises_without_human():
    for t in ["разбаньте меня", "верните машину", "накажите его", "помогите", "как устроиться в полицию"]:
        res = post("report", t)
        if not res["needs_human"]:
            low = res["draft_reply"]["text"].lower()
            assert "разбан" not in low and "верн" not in low and "получит" not in low


def test_cp1251_kazakh():
    assert normalize("Сјлеметсіз бе, шаєым жазыѕыз") == "Сәлеметсіз бе, шағым жазыңыз"
    assert detect_lang(normalize("кґмектесіѕізші машинам суєа тїсіп кетті")) == "kk"
    res = post("report", "машинам суѕа тїсіп кетті кґмектесіѕізші")
    assert res["lang"] == "kk" and res["draft_reply"]["lang"] == "kk"


def test_uzbek():
    res = post("report", "mashinam ag'darildi yordam bering", server_lang="uz")
    assert res["lang"] == "uz"
