"""HTTP-сервис: POST /triage по контракту ТЗ.

uvicorn app:app --host 0.0.0.0 --port 8000
"""
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict

from copilot.pipeline import Copilot

app = FastAPI(title="Grand Mobile Support Copilot", version="1.0")
copilot = Copilot()


class Message(BaseModel):
    model_config = ConfigDict(extra="allow")
    role: str = "player"
    text: str = ""
    attachments: int | None = None


class TriageRequest(BaseModel):
    """Обязательны kind и messages. Остальные поля из выгрузки (server_lang, rule_refs_raw,
    reported_nick, reporter_hash, reported_hash, created_at, images_count) необязательны,
    но улучшают язык по умолчанию, факты и дедупликацию."""
    model_config = ConfigDict(extra="allow")
    kind: str
    messages: list[Message]


@app.post("/triage")
def triage(req: TriageRequest) -> dict[str, Any]:
    t = req.model_dump()
    t["messages"] = [m for m in t["messages"] if m.get("role") != "admin"]
    if t.get("images_count") is None:
        t["images_count"] = sum(int(m.get("attachments") or 0) for m in t["messages"] if m.get("role") == "player")
    res = copilot.triage(t)
    res.pop("latency_ms", None)
    res.pop("template", None)
    return res


@app.get("/health")
def health():
    return {"status": "ok"}
