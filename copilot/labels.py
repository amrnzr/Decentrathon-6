"""Правила для категорий, приоритета и слабой разметки train.

Категорий и приоритетов в данных нет. Мы размечаем train правилами по taxonomy.json:
текст игрока + пункт правил из формы + (только для разметки) нарушение из ответа админа.
На этой разметке учится классификатор, который на инференсе видит только текст игрока.
"""
import re

from .normalize import normalize

# ---------- словари ключевых слов (по основам, с опечатками и транслитом) ----------
KW = {
    "appeal": r"не\s*согл|несогл|не\s*соглас|nesogl|ne\s*sogl|rozi\s*emas|qo'?shilmayman|снимите|неверно\s*выдан|выдан\w*\s*(не\s*верно|неверно)|"
              r"выдал[аи]?\s*(мне\s*)?(мут|бан|варн|джайл|демор|наказ|warn|jail)|наказал[аи]?\s*(меня\s*)?(без|не\s*за|просто)|"
              r"(дали|дал)\s*(мне\s*)?(мут|бан|варн|джайл|деморган)|разбан|разбань|сними\s*(бан|мут)|ошибочно\s*наказ|"
              r"меня\s*(забанил|замутил|посадил)|наказание\s*(выдано\s*)?(не\s*верно|неверно|не\s*правильно)|"
              r"админ\w*\s*(выдал|дал|наказ|посадил|забанил|замутил)|unban|meni\s*(ban|mute)|пересмотр|рассмотреть\s*(данное\s*|это\s*)?решени|"
              r"^\W*за\s*что\W*$|дали\s*(мне\s*)?предупр|заблокировали\s*(меня|мне)?|мне\s*заблокир|ban\s*(berdi|yechil|olib)|yechib|yechila|"
              r"даже\s*не\s*убил|готов\s*сменить|прошу\s*разбан|почему\s*(мне\s*)?(бан|мут|варн|перевыдал)|перевыдал|үшін\s*бан|"
              r"в\s*каком\s*месте\s*я|я\s*(ничего|ничо|ни\s*чего)\s*не\s*нарушал|обжалов|апелляц|снять\s*наказ|"
              r"ban\s*berish|nohaq|noqonuniy|naqonuniy",
    "admin": r"превышен|должностн|полномоч|отвечает\s*на\s*репорт|rep\s*javob|suiste'?mol|lavozim|"
             r"(админ|адм|admin|хелпер|модер)\w*\s*(\w+\s*){0,3}(не\s*следит|ничего\s*не\s*дела|бездейств|злоупотреб|наруш|"
             r"неправильно|не\s*отвеча|hech\s*nima\s*qilmayapti|хамит|оскорб)|"
             r"(не\s*следит|бездейств)\w*\s*(\w+\s*){0,2}(админ|адм)",
    "insult": r"боқта|балағат|сөкті|қорла|\bоск|оскорб|осорб|окорб|маты?\b|матер|матюк|родн|родител|мамк|мама|мать|матер|семь|"
              r"\bтуп|дебил|дурак|урод|чмо|сука|токс|расизм|нацио|национ|религ|osk|rodn|rod\b|mat\b|haqorat|so'?k|"
              r"унижа|обозва|обзыва|хамит|хамств|insult|toxic|insulto",
    "cheat": r"чит|читак|читер|cheat|чiт|aim|аим|аимбот|\bwh\b|\bвх\b|воллхак|летает|летал|спидхак|speed\s*hack|"
             r"сторонн\w*\s*(по|программ|софт)|софт|бессмерт|godmode|телепортир\w*\s*сам|скрипт|макрос|автоклик|багоюз|баг\s*юз|"
             r"tp\s*hack|airbrake|аирбрейк|бегает\s*быстро|сквозь\s*стен|через\s*стен",
    "dm": r"\bдм\b|\bdm\b|дм\b|\bdm|дмит|дмя|убил|убива|убийств|стрел|шмаля|без\s*причин|просто\s*так\s*(убил|стрел|напал)|"
          r"\bзз\b|\bzz\b|\bgz\b|зел[её]н\w*\s*зон|спавн|\bдб\b|\bdb\b|драйв|\bsk\b|\bск\b|спавн\s*кил|\btk\b|\bтк\b|нонрп|non\s*rp|nonrp|"
          r"\bрп\b|\brp\b|урон|сбил|давит|задавил|таран|напал|избил|бьет|бил\s*меня|ударил|пг\b|\bpg\b|мг\b|\bmg\b|"
          r"o'?ldirdi|o'?ldir|otdi|urdi|kill|mato|mata|atropel|похит|ограб|связал|верёвк|веревк|мешок|уход\s*от\s*рп|выход\s*из\s*игры|посадил|посадили|в\s*тюрьм\w*\s*просто|qamadi|qamash|qamoq|\bгз\b",
    "scam": r"скам|scam|обман|обманул|кинул|кидал|развел|развёл|не\s*отдал|не\s*вернул|не\s*верн(ул|ет|ёт)|долг|вымога|aldad|aldov|"
            r"украл|своровал|мошен|забрал\s*(деньги|машин|скин|вещ)|взял\s*(деньги|машин)|golpe|estafa|fraud",
    "rmt": r"реал\b|за\s*реал|реальн\w*\s*деньг|рубл\w*\s*(за|на)|продает\s*акк|продаёт\s*акк|продажа\s*акк|тг\b|телег|telegram|"
           r"\bтгк\b|реклам|другой\s*сервер|другого\s*сервера|каспи|kaspi|сбер|qiwi|киви|\brmt\b|\bрмт\b|продаёт\s*вирт|продает\s*вирт|"
           r"покупает\s*вирт|сливает\s*вирт|реклама|discord\.gg",
    "other_viol": r"\bfw\b|\bfv\b|\bфв\b|ник\b|никнейм|является\s*администратор|я\s*админ|ивент|мероприят|мешает|номер\w*\s*(знак|машин)|номерн|флуд|микрофон|музык|войс|voice|"
                  r"назван\w*\s*сем|домога|аморал|наркот|пропаганд|выдает\s*себя\s*за\s*админ|представля\w*\s*админ",
    # репорты
    "payment": r"төлем|ақша\s*түспеді|donat\s*qil|\bdonat|донат|доннат|задонат|оплат|оплачив|пополн|платеж|платёж|списал|списали|чек\b|покупк\w*\s*(не|гк)|"
               r"\bгк\b.*(не\s*приш|не\s*зачисл|не\s*дош)|не\s*(пришл|зачисл|дошл)\w*\s*(гк|донат|рубин|коин)|"
               r"coins?\b.*not|to'?lov|pul\s*tushmadi|donat|pagamento|pago|compra|refund|возврат\s*(денег|средств)",
    "account": r"бұзып\s*алды|akkauntimni|buzib|взлом|взломал|ломанул|украли\s*акк|угнали\s*акк|пароль|парол|почт|аккаунт\w*\s*(украл|взлом|забрал|пропал)|"
               r"не\s*могу\s*(зайти|войти)|восстанов|обнулил|обнулили|пропал\w*\s*(машин|дом|деньг|имущ|бизнес|скин|вещ|акс|кейс|авто|все)|"
               r"исчез\w*|удалил\w*\s*(акк|перс)|hack|akkaunt|parol|o'?g'?irla|sumiu|robaron|роблокс\s*акк",
    "help": r"почин|достань|достаньте|из\s*воды|на\s*дорогу|следите\s*за\s*мной|за\s*мной\s*следи|суға|түсіп\s*кет|аударыл|тұрып\s*қал|шыға\s*алмай|көмектес|suvga|ag'?dar|tiqil|qolib\s*ketdim|chiqolmay|наручник|развяж|розв'яж|зав'язал|kishan|потерял|потірявся|измерени|застрял|застряла|застрял\w*|текстур|переверн|перевор|перевёр|под\s*вод|тону|тонет|упал|провалил|баг\b|багнул|"
            r"телепорт|тпни|\bтп\b|вытащ|выбрать|выбраться|не\s*могу\s*(выйти|выехать|сдвин|двиг)|слетел|эвакуатор|машин\w*\s*(в\s*вод|упал|застр|перев)|"
            r"подкин|довез|в\s*воде|в\s*текстур|kotar|tiqil|qoldi|chiqar|stuck|flipped|atascado|preso|travado|virou|"
            r"тюрьм|турм|тюрм|деморган|джайл|выпустите|освободите|разморозь|замороз",
    "report_complaint": r"\bспек|^\s*\d{1,4}\s*(дм|дб|чит|оск|db|dm|sk|ск|тк|tk|читак|читер)|\b\d{1,4}\s*(дм|дб|чит|оск|db|dm|читак|читер)\b|"
                        r"дмят|дмит|убива|читер|читак|оскорбля|оскорбил|мешает|стреляет|таранит|сбивает|нонрп|наруша|"
                        r"нарушител|haqorat|o'?ldir|урон",
    "question": r"\?|как\b|как\s|где\b|что\b|когда|почему|сколько|можно\s*ли|какой|какая|какие|зачем|подскажите|подскажи|"
                r"скажите|qanday|qayerda|qachon|nega|nima|qancha|how|where|what|when|why|como|onde|donde|cuando|quando|"
                r"қалай|қайда|неге|қашан|не\s*істеу",
    "rules_q": r"правил|можно\s*ли|разреш|запрещ|наказани\w*\s*за|бан\s*за|мут\s*за|за\s*что\s*(бан|мут|варн)|что\s*такое\s*(дм|рп|мг|пг|дб|sk|tk)",
    "threat_irl": r"сват|деанон|доксинг|найду\s*тебя|найду\s*где|твой\s*адрес|адрес\w*\s*(твой|его)|ддос|дудос|ddos|убью\s*в\s*реал|в\s*реале\s*найду|"
                  r"по\s*ip|айпи|личн\w*\s*данн|слив\w*\s*(фото|данн)",
    "mass_bug": r"у\s*всех|сервер\s*(упал|лежит|лагает)|массов|все\s*игроки|никто\s*не\s*может|hammada",
}
KWC = {k: re.compile(v, re.I) for k, v in KW.items()}

OFFTOPIC_RE = re.compile(
    r"^\s*(помогите|помоги|помогите\s*пж|помогите\s*пожалуйста|пж|плиз|ау+|алло|привет|здравствуйте|салам|салем|сәлем|"
    r"hello|hi|help|yordam|ayuda|ajuda|admin|админ|админы|\+|\.|\?|!|ок|ok|хелп|помогите\s*срочно|срочно|"
    r"слежу|ауу|эй|прив|ку|qq|салам\s*алейкум|ассалому\s*алейкум|assalomu\s*alaykum|"
    r"pomogite|памагите|памагітє|помагите|yordam\s*bering|yordam\s*beringlar)\s*[!.?)]*\s*$",
    re.I,
)
SPAM_RE = re.compile(r"^\W*$|^(\w)\1{2,}$|^[\W\d]{0,4}$")

# Нарушение из ответа админа -> категория (только для слабой разметки train)
VIOL_MAP = [
    (r"2\.[146]\b|оскорб|оск\b", "complaint.insult"),
    (r"5\.2\b|чит|сторон|cheat", "complaint.cheat"),
    (r"\bdm\b|\bдм\b|gz|гз|\bзз\b|\bzz\b|5\.[34]\b|\bdb\b|\bдб\b|\bsk\b|\btk\b|\bрп\b|\brp\b|non\s*rp|нонрп", "complaint.dm"),
    (r"4\.[12]\b|обман|мошен|скам", "complaint.scam"),
    (r"2\.3\b|4\.4\b|реклам", "complaint.rmt_ads"),
    (r"\bfw\b|\bfv\b|\bфв\b|1\.6\b|2\.2\b|2\.5\b|5\.[5-9]\b|warn|1\.2\b", "complaint.other"),
]


def player_text(ticket: dict) -> str:
    """Текст игрока (без ответа админа: на инференсе его нет)."""
    parts = []
    for m in ticket.get("messages", []):
        if m.get("role") == "player":
            parts.append(m.get("text") or "")
    return normalize(" ".join(parts), ticket.get("server_lang"))


def accused_text(ticket: dict) -> str:
    return normalize(" ".join(m.get("text") or "" for m in ticket.get("messages", [])
                              if m.get("role") == "reported_player"))


def has_evidence(ticket: dict, text: str) -> bool:
    att = ticket.get("images_count")
    if att is None:
        att = sum(int(m.get("attachments") or 0) for m in ticket.get("messages", []) if m.get("role") == "player")
    return bool(att) or "<url>" in text or bool(re.search(r"https?://|youtu|imgur|yapx|disk\.yandex", text, re.I))


def is_spam(text: str) -> bool:
    t = text.strip()
    letters = sum(ch.isalpha() for ch in t)
    return letters < 2 or bool(SPAM_RE.match(t))


def complaint_category(text: str, rule_refs_raw: str = "", violation: str | None = None,
                       verdict: str | None = None) -> str:
    raw = (rule_refs_raw or "")
    both = f"{text} {raw}".lower()
    if verdict in ("appeal_approved", "appeal_rejected"):
        return "complaint.admin"
    if KWC["appeal"].search(both) or KWC["admin"].search(text) or re.search(r"\bадм|админ|admin", raw.lower()):
        return "complaint.admin"
    # явный контент в тексте игрока (в порядке "тяжести")
    order = [("rmt", "complaint.rmt_ads"), ("scam", "complaint.scam"), ("cheat", "complaint.cheat"),
             ("insult", "complaint.insult"), ("dm", "complaint.dm"), ("other_viol", "complaint.other")]
    for key, cat in order:
        if KWC[key].search(text):
            return cat
    # пункт правил из формы или нарушение из ответа админа
    for src in (raw, text, violation or ""):
        s = src.lower()
        for pat, cat in VIOL_MAP:
            if re.search(pat, s):
                return cat
        for key, cat in order:
            if KWC[key].search(s):
                return cat
    if verdict in ("invalid_format", "duplicate") or re.search(r"компенсац|kompensats", text.lower()):
        return "complaint.invalid"
    letters = sum(ch.isalpha() for ch in text)
    if letters < 3 or KWC["question"].search(text) and not violation:
        return "complaint.invalid"
    if violation:
        return "complaint.other"
    return "complaint.invalid" if letters < 15 else "complaint.other"


def report_category(text: str) -> str:
    t = text.strip()
    if KWC["payment"].search(t):
        return "report.payment"
    if KWC["account"].search(t):
        return "report.account"
    if is_spam(t) or OFFTOPIC_RE.match(t):
        return "report.offtopic"
    if KWC["report_complaint"].search(t):
        return "report.complaint"
    if KWC["help"].search(t):
        return "report.help"
    if KWC["question"].search(t) and len(t) >= 8:
        return "report.question"
    if KWC["cheat"].search(t) or KWC["insult"].search(t) or KWC["dm"].search(t) or KWC["scam"].search(t):
        return "report.complaint"
    words = re.findall(r"\w+", t)
    if len(words) <= 2:
        return "report.offtopic"
    return "report.question"


def weak_label(ticket: dict) -> str:
    text = player_text(ticket)
    if ticket.get("kind") == "report":
        return report_category(text)
    return complaint_category(text, ticket.get("rule_refs_raw") or "", ticket.get("violation"),
                              ticket.get("verdict"))


def priority(category: str, text: str, evidence: bool) -> str:
    if KWC["threat_irl"].search(text) or (KWC["mass_bug"].search(text) and category.startswith("report")):
        return "p0"
    if category in ("report.account", "report.payment"):
        return "p0"
    if category in ("complaint.cheat", "complaint.scam", "complaint.rmt_ads", "complaint.admin"):
        return "p1"
    if category == "report.complaint" and (KWC["cheat"].search(text) or KWC["rmt"].search(text)):
        return "p1"
    if category in ("complaint.insult", "complaint.dm", "complaint.other", "report.complaint", "report.help"):
        return "p2" if evidence or category.startswith("report") else "p3"
    if category == "report.question" and KWC["rules_q"].search(text):
        return "p2"
    return "p3"
