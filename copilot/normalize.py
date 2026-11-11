"""Нормализация текста и определение языка.

Игра работает в cp1251, поэтому на kz-серверах казахские буквы набраны похожими
символами. Таблица ниже проверена по частотам слов в train (сјлеметсіз, шаєым,
дјлелдеріѕіз, кґмек, сўраєыѕызды, їшін). Она отличается от таблицы в ТЗ для є, ґ, ј:
в данных є -> ғ, ґ -> ө, ј -> ә.
"""
import re
import unicodedata

# Однозначные замены: эти символы почти не встречаются вне "казахского cp1251"
KK_STRONG = {"ќ": "қ", "Ќ": "Қ", "ѕ": "ң", "Ѕ": "Ң", "ј": "ә", "Ј": "Ә", "ґ": "ө", "Ґ": "Ө"}
# Эти символы бывают и в украинском (є, ї) и узбекской кириллице (ў),
# поэтому заменяем их только если текст уже похож на казахский
KK_WEAK = {"є": "ғ", "Є": "Ғ", "ў": "ұ", "Ў": "Ұ", "ї": "ү", "Ї": "Ү"}

KK_LETTERS = set("әғқңөұүһіӘҒҚҢӨҰҮҺІ")
KK_WORDS = {
    "сәлеметсіз", "сәлем", "көмек", "көмектесіңіз", "рахмет", "маған", "менің", "мен", "ойын",
    "шағым", "жоқ", "қалай", "неге", "керек", "бар", "біз", "сіз", "ағай", "аға", "өтініш",
    "қайда", "үшін", "және", "бұл", "мына", "тұрып", "қалдым", "ойнап", "ақша",
    "шықпай", "түсіп", "кетті", "берші", "беріңіз", "болды", "жатыр", "емес", "білмеймін",
}
UZ_WORDS = {
    "yordam", "iltimos", "menga", "qanday", "nima", "salom", "assalomu", "alaykum", "bor", "yoq",
    "yo'q", "kerak", "mashina", "mashinam", "qoldi", "uchun", "emas", "bilan", "men", "meni",
    "sizlar", "aka", "qayerda", "qilib", "qilish", "bering", "beringlar", "rahmat", "haqorat",
    "so'kdi", "o'ldirdi", "ishlamayapti", "nega", "qachon", "qaysi", "kim", "chiqib", "ketdi",
    "qildi", "pul", "tushmadi", "akkaunt", "hamma", "joyda", "tiqilib", "yordamberinglar", "uje",
    "ham", "buni", "shu", "manga", "boshqa", "ber", "kuzat", "kotaring", "olib", "chiqing", "edi",
}
EN_WORDS = {"help", "please", "the", "my", "car", "stuck", "hello", "is", "are", "how", "where",
            "what", "can", "you", "me", "admin", "i", "im", "not", "player", "killed", "why"}
ES_WORDS = {"ayuda", "por", "favor", "estoy", "coche", "carro", "mi", "como", "donde", "que",
            "hola", "jugador", "no", "puedo", "tengo", "esta", "atascado", "ayudame", "una", "el"}
PT_WORDS = {"ajuda", "ajudem", "preciso", "não", "nao", "você", "voce", "obrigado", "carro", "meu",
            "estou", "preso", "como", "onde", "jogador", "olá", "ola", "pra", "uma", "tá", "ta"}
# Русский транслитом ("osk rod", "pomogite"): отвечаем по-русски
RU_TRANSLIT = {"osk", "rod", "pomogite", "pomogi", "pomoch", "menya", "mne", "ne", "chit", "chiter",
               "dm", "ubil", "pozhaluysta", "pojaluysta", "pls", "plz", "rodnyh", "rodni", "mat",
               "skam", "kinul", "zastryal", "zastral", "mashina", "admin", "igrok", "bez", "prichiny",
               "dayte", "help", "privet", "osk.", "oskorblenie", "oskorbil"}

SERVER_LANG_DEFAULT = {"kk": "kk", "uz": "uz", "ru": "ru"}


def fix_cp1251(text: str, force_kk: bool = False) -> str:
    """Возвращает текст с восстановленными казахскими буквами."""
    if not text:
        return ""
    has_strong = any(ch in KK_STRONG for ch in text)
    out = "".join(KK_STRONG.get(ch, ch) for ch in text)
    if has_strong or force_kk or _looks_kk(out):
        out = "".join(KK_WEAK.get(ch, ch) for ch in out)
    return out


def _looks_kk(text: str) -> bool:
    low = text.lower()
    if any(ch in KK_LETTERS for ch in low if ch != "і"):
        return True
    return len(set(re.findall(r"\w+", low)) & KK_WORDS) >= 2


def clean(text: str) -> str:
    text = unicodedata.normalize("NFC", text or "")
    text = text.replace("‘", "'").replace("’", "'").replace("ʻ", "'").replace("ʼ", "'").replace("`", "'")
    return re.sub(r"\s+", " ", text).strip()


def normalize(text: str, server_lang: str | None = None) -> str:
    return clean(fix_cp1251(text, force_kk=False))


def detect_lang(text: str, server_lang: str | None = None) -> str:
    """ru | kk | uz | en | es | pt. Пустые и неопределенные тексты берут язык сервера."""
    low = clean(text).lower()
    words = re.findall(r"[\w']+", low)
    letters = [ch for ch in low if ch.isalpha()]
    fallback = SERVER_LANG_DEFAULT.get(server_lang or "", "ru")
    if len(letters) < 2:
        return fallback
    cyr = sum(1 for ch in letters if "Ѐ" <= ch <= "ӿ")
    lat = sum(1 for ch in letters if "a" <= ch <= "z")
    wset = set(words)
    if cyr >= lat:
        kk_spec = sum(1 for ch in low if ch in "әғқңөұүһ")
        uz_cyr = sum(1 for ch in low if ch in "ўҳ")
        kk_words = len(wset & KK_WORDS)
        ukr = len(re.findall(r"\b(що|та|ти|мене|не\s*може|бути|цікав\w*|використ\w*|поможіть|переверніть|адмін\w*)\b", low))
        if (kk_spec >= 2 or (kk_spec and (kk_words or len(words) <= 4)) or kk_words >= 2 or ("і" in low and kk_words and not ukr)) \
                and not (ukr >= 2 and kk_spec <= 1):
            if uz_cyr > kk_spec:
                return "uz"
            return "kk"
        if uz_cyr and any(ch in low for ch in "қғ"):
            return "uz"
        return "ru"
    # латиница
    scores = {
        "uz": len(wset & UZ_WORDS) * 2 + len(re.findall(r"\b\w*(o'|g'|sh|ch)\w*\b", low)) * 0.3
              + len(re.findall(r"(ing|lar|dim|yapti|man|miz)\b", low)) * 0.7,
        "en": len(wset & EN_WORDS) * 1.5,
        "es": len(wset & ES_WORDS) * 1.5 + low.count("ñ") * 2,
        "pt": len(wset & PT_WORDS) * 1.5 + sum(low.count(c) for c in "ãõç") * 2,
        "ru": len(wset & RU_TRANSLIT) * 1.6,
    }
    if server_lang == "uz":
        scores["uz"] += 1.5
    best = max(scores, key=scores.get)
    if scores[best] < 1:
        return "uz" if server_lang == "uz" else ("ru" if server_lang in (None, "ru") else fallback)
    return best


NICK_RE = re.compile(r"\b([A-Z][a-z]+_[A-Z][a-z]+\d*)\b")


def find_nicks(text: str) -> list[str]:
    return NICK_RE.findall(text or "")
