#!/usr/bin/env python3
# ヨヨイ 창구 — 손님과 가게가 한 칸에 쓴 말을 받아, 쓴 그대로 쌓고, 그 자리에서 대화를 잇는다.
#   철학(ops/WHY.md): 「사람은 말은 한다.」 입력은 말이어야 한다. 메일 앱이 열리면 말이 끊긴다.
#   길: yoyoi.jp 의 한 칸 → POST <창구>/say → 캐디 → 127.0.0.1:7980 → <자료>/대화/<대화표>.jsonl
#       손님은 yoyoi.jp/t/#<대화표> 에서 답을 보고 이어 쓴다. 대화표가 곧 열쇠다(로그인 없음).
#       우리는 <창구>/<열쇠>/ 에서 읽고 답한다. 열쇠가 틀리면 404 만 준다.
#   받고, 쌓고, 보여 준다. 답은 안쪽 화면에서 사람이 쓴다.
#   먼저 답하기(11-24 원장님 「먼저 답해」): <자료>/답 이 있으면 손님 말이 올 때 ヨヨイ 에이전트가 먼저 답한다.
#         하는 일은 접수(ops/INTAKE.md 의 1·3)까지다: 알아듣고, 빠진 것을 하나씩 묻고, 조건을 되읽는다.
#         가게 이름·빈자리·확정은 말하지 않는다(아직 아무도 가게에 묻지 않았으니). 그것은 사람이 안쪽 화면에서 쓴다.
#   넣을 글(11-24 원장님 「에이전트가 글로」): 손님이 되읽은 조건에 「좋다」고 하면, 에이전트가 안쪽 메모로 「넣을 글」을 한 번 쓴다.
#         조건 요약, 대장(ops/shops.json)에서 맞는 가게 후보와 닿는 길, 가게에 그대로 보낼 일본어 글. 손님에게는 안 보인다.
#         🔴 이 서버는 가게에 아무것도 보내지 않는다. 글을 지어 둘 뿐이다. 보내는 길(LINE 계정 등)은 아직 없다.
#         켜기 = touch <자료>/답 (안에 {"day": 60, "thread": 12} 를 적으면 하루·대화마다 한도를 바꾼다) · 끄기 = 그 파일을 지운다.
#         열쇠는 환경 ANTHROPIC_API_KEY, 없으면 ~/열쇠/열쇠.env 에서 읽는다. 값은 어디에도 적지 않는다.
#   글은 고치거나 줄이지 않는다. 한 줄 = 한 마디. 손님 주소(IP)는 적지 않는다.
#   자료는 이 저장소(공개) 밖에 둔다: 기본 ~/창구-자료 · 바꾸려면 YOYOI_CH_DATA
#   알림: <자료>/알림 이 있으면 손님 말이 올 때 텔레그램으로 「왔습니다」 한 줄을 보낸다. 손님 글은 보내지 않는다.
#         알림을 거는 법 = 마을에서 python3 ~/douzo/ch/문.py 알림 (봇 토큰은 원장님이 직접 넣는다. 저장소에 두지 않는다)
#         알림 끄기 = <자료>/알림 을 지운다. 서버를 다시 켤 필요 없다.
#   끄기 = 크론의 창구 지킴이 줄을 빼고 pkill -f ch/문.py
import collections
import datetime
import html
import json
import os
import re
import secrets
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("YOYOI_CH_PORT", "7980"))
DATA = os.path.expanduser(os.environ.get("YOYOI_CH_DATA", "~/창구-자료"))
BOX = os.path.join(DATA, "대화")
LOG = os.path.join(DATA, "문.log")
KEYFILE = os.path.join(DATA, "열쇠")
SITE = "https://yoyoi.jp"
# 이 문을 두드려도 되는 곳. 시험할 때만 YOYOI_CH_ORIGIN 으로 하나 더 연다.
ORIGINS = {"https://yoyoi.jp", "https://www.yoyoi.jp"} | set(filter(None, os.environ.get("YOYOI_CH_ORIGIN", "").split(",")))
LANGS = ("en", "ja", "ko", "zh-hant", "zh-hans", "th")
KST = datetime.timezone(datetime.timedelta(hours=9))
MAX_BODY = 32 * 1024      # 한 번에 받는 몸
MAX_TEXT = 4000           # 한 마디 글자 수
MAX_MSGS = 300            # 한 대화의 마디 수
PER_IP_HOUR = 30          # 한 곳에서 한 시간에
PER_DAY = 3000            # 하루 전체
ID_RE = re.compile(r"^[A-Za-z0-9_-]{16}$")
LOCK = threading.Lock()
HITS = collections.defaultdict(collections.deque)   # 주소 → 받은 때(기억에만 둔다. 적지 않는다)
DAY = {"d": "", "n": 0}

os.makedirs(BOX, exist_ok=True)
os.chmod(DATA, 0o700)
if not os.path.exists(KEYFILE):
    with open(os.open(KEYFILE, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w", encoding="utf-8") as f:
        f.write(secrets.token_urlsafe(18) + "\n")
KEY = open(KEYFILE, encoding="utf-8").read().strip()


def now():
    return datetime.datetime.now(KST).isoformat(timespec="seconds")


def log(line):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write("%s %s\n" % (now(), line))


NOTE = os.path.join(DATA, "알림")     # {"token": 봇 토큰, "chat": 받을 방} · 없으면 알리지 않는다
PUBLIC = os.environ.get("YOYOI_CH_PUBLIC", "https://ch.43-200-65-88.sslip.io")   # 알림에 적을 안쪽 화면 주소
QUIET = 300                           # 같은 대화는 5분에 한 번만 알린다
TOLD = {}


def tg(token, method, **kw):
    """텔레그램 봇에 한 번 묻는다."""
    req = urllib.request.Request("https://api.telegram.org/bot%s/%s" % (token, method),
                                 data=urllib.parse.urlencode(kw).encode())
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))


def notify(tid, lang, pg, first):
    """손님 말이 왔다고 알린다. 손님 글은 싣지 않고, 읽을 곳만 알린다. 알림이 안 가도 받기는 멈추지 않는다."""
    try:
        with open(NOTE, encoding="utf-8") as f:
            cfg = json.load(f)
        token, chat = cfg["token"], cfg["chat"]
    except Exception:
        return
    t = time.time()
    with LOCK:
        if t - TOLD.get(tid, 0) < QUIET:
            return
        TOLD[tid] = t
        if len(TOLD) > 2000:
            for k in [k for k, v in TOLD.items() if t - v > QUIET]:
                del TOLD[k]
    text = "ヨヨイ 창구 — %s\n%s · %s\n%s/%s/t/%s" % (
        "새 말이 왔습니다" if first else "손님이 이어 썼습니다", lang, pg or "-", PUBLIC, urllib.parse.quote(KEY), tid)

    def go():
        try:
            tg(token, "sendMessage", chat_id=chat, text=text, disable_web_page_preview="true")
        except Exception as e:
            log("알림 못 보냄 %s" % type(e).__name__)
    threading.Thread(target=go, daemon=True).start()


ANSWER = os.path.join(DATA, "답")      # 있으면 에이전트가 먼저 답한다. 없으면 예전 그대로다
KEYENV = os.path.expanduser(os.environ.get("YOYOI_CH_KEYENV", "~/열쇠/열쇠.env"))
API = os.environ.get("YOYOI_CH_API", "https://api.anthropic.com/v1/messages")
MODEL = "claude-opus-5-5"
ANSWERED = {"d": "", "n": 0}
BUSY = set()                           # 지금 답을 짓고 있는 대화
LANGNAME = {"en": "English", "ja": "日本語", "ko": "한국어", "zh-hant": "繁體中文", "zh-hans": "简体中文", "th": "ไทย"}
MIND = """You are the front desk of ヨヨイ (Yoyoi, yoyoi.jp). Yoyoi takes a traveler's own words and arranges a reservation at a shop in Japan (restaurants, hair salons, nail salons; Nagoya, Kyoto, Osaka), including shops that only take bookings by phone in Japanese. Its one line is 「사람은 말은 한다」: people can say what they want; the rest is our work. Shops write here too, to say what they offer, and people ask about working with us.

You are an AI, and you are the first to answer. A person on the Yoyoi team reads this same conversation and does what you cannot: contacting shops and confirming. Do not hide that you are an AI if asked.

What you do in this conversation is intake:
- Understand what the person wants, in whatever language and however roughly it was written. Never ask them to rewrite or fill in a form.
- A reservation needs: date, time, number of people, area, rough budget, foods they cannot eat (as ingredients, e.g. "no pork, including broth and lard", not as a diet label), and a name for the booking. Work out which of these are still missing and ask for them, the most important one or two at a time, in plain words. Do not ask again for anything already said.
- When everything is there, read the conditions back once in a short list and ask them to confirm. After they confirm, tell them the team will now look for a place and call, and that the answer will arrive on this same page, normally within a day.
- If a shop owner or a job seeker writes, thank them, ask the one or two things the team would need to follow up, and say a person will reply here.

What you must not do, because nobody has contacted any shop yet:
- Do not name, recommend or describe specific shops. Do not say or imply that a table is available, held, or confirmed. Do not quote prices or promise a time other than "normally within a day".
- Do not ask for a phone number, email, passport or payment details. This page is where the answer comes.
- If someone asks for something outside this (medical or legal advice, anything unrelated), say briefly that this desk only arranges reservations.

How you write the reply: in the language the person wrote in (the page they came from was %(lang)s, use that if their message is too short to tell). Short and warm, two to five sentences, plain text with no markdown.

Today is %(today)s (Japan time). Use it to turn "tomorrow" or "Friday" into a date, and say the date when you read conditions back.

Your output has three fields.
- reply: what the person sees.
- confirmed: true only when you had already read the full conditions back and the person's latest message agrees to them. Otherwise false.
- brief: empty unless confirmed is true. When it is true, write the handover the Yoyoi team works from. The guest never sees it. Write it in this order: (1) the conditions as a short list in Korean, with the date written out and foods-they-cannot-eat as ingredients; (2) 가게 후보: up to three shops from the ledger below that fit the city and kind, each with its name and how it is reached, or the plain sentence 「대장에 맞는 가게가 없다 — 새로 찾아야 한다」 when none fits (most restaurants are not in the ledger; do not stretch a massage or nail shop to fit a dinner request, and never invent a shop); (3) 가게에 보낼 글: a polite Japanese message that can be sent to a shop as it is, saying it is from ヨヨイ (yoyoi.jp), which arranges reservations for visitors from abroad, giving the conditions, asking whether they can take the booking, and asking them to reply in writing. Do not put the guest's nationality in it; give only the booking name, the number of people, the language they speak, and what they cannot eat.

The ledger of shops researched so far (none has been contacted yet):
%(shops)s"""
FORM = {"type": "json_schema", "schema": {"type": "object", "additionalProperties": False,
        "required": ["reply", "confirmed", "brief"],
        "properties": {"reply": {"type": "string"}, "confirmed": {"type": "boolean"}, "brief": {"type": "string"}}}}
SHOPS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ops", "shops.json")


def ledger():
    """가게 대장을 한 줄씩. 못 읽으면 빈 대장이다."""
    try:
        with open(SHOPS, encoding="utf-8") as f:
            shops = json.load(f)["shops"]
        return "\n".join("- %s | %s | %s | %s | 닿는 길: %s" % (
            x.get("city", ""), x.get("name", ""), x.get("area", ""), x.get("kind", ""),
            x.get("ch") or x.get("tel") or "?") for x in shops) or "(empty)"
    except Exception:
        return "(empty)"


def api_key():
    k = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if k:
        return k
    try:
        with open(KEYENV, encoding="utf-8") as f:
            for line in f:
                m = re.match(r"^\s*(?:export\s+)?ANTHROPIC_API_KEY\s*=\s*[\"']?([^\"'\s#]+)", line)
                if m:
                    return m.group(1)
    except OSError:
        pass
    return ""


def compose(msgs):
    """대화를 모델에게 물어 답을 받는다: {"reply", "confirmed", "brief"}. 못 받으면 None."""
    key = api_key()
    if not key:
        log("답 못 함 열쇠 없음")
        return None
    turns = []
    for m in msgs:
        if m.get("who") not in ("guest", "us") or not (m.get("text") or "").strip():
            continue
        role = "user" if m["who"] == "guest" else "assistant"
        if turns and turns[-1]["role"] == role:
            turns[-1]["content"] += "\n\n" + m["text"]
        else:
            turns.append({"role": role, "content": m["text"]})
    while turns and turns[0]["role"] != "user":
        turns.pop(0)
    if not turns or turns[-1]["role"] != "user":
        return None
    mind = MIND % {"lang": LANGNAME.get(msgs[0].get("lang"), "English"), "shops": ledger(),
                   "today": datetime.datetime.now(KST).strftime("%Y-%m-%d (%A)")}
    body = {"model": MODEL, "max_tokens": 8000, "output_config": {"effort": "low", "format": FORM},
            "fallbacks": "default", "system": mind, "messages": turns}
    req = urllib.request.Request(API, data=json.dumps(body).encode("utf-8"), headers={
        "Content-Type": "application/json", "x-api-key": key, "anthropic-version": "2026-10-21",
        "anthropic-beta": "server-side-fallback-2026-07-01"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            d = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        log("답 못 함 HTTP %d" % e.code)
        return None
    except Exception as e:
        log("답 못 함 %s" % type(e).__name__)
        return None
    if d.get("stop_reason") != "end_turn":
        log("답 못 함 stop=%s" % d.get("stop_reason"))
        return None
    try:
        o = json.loads(next(b["text"] for b in d.get("content", []) if b.get("type") == "text"))
        reply = o["reply"].strip()[:MAX_TEXT]
    except Exception:
        log("답 못 함 꼴이 아님")
        return None
    u = d.get("usage", {})
    log("답 지음 %s in=%s out=%s" % (d.get("model"), u.get("input_tokens"), u.get("output_tokens")))
    if not reply:
        return None
    return {"reply": reply, "confirmed": o.get("confirmed") is True, "brief": str(o.get("brief") or "").strip()}


def answer(tid):
    """손님 말이 오면 에이전트가 먼저 답한다. <자료>/답 이 없으면 아무것도 하지 않는다. 답을 못 지어도 받기는 멈추지 않는다."""
    try:
        with open(ANSWER, encoding="utf-8") as f:
            raw = f.read().strip()
        cfg = json.loads(raw) if raw else {}
        per_day, per_thread = int(cfg.get("day", 60)), int(cfg.get("thread", 12))
    except FileNotFoundError:
        return
    except Exception:
        per_day, per_thread = 60, 12
    with LOCK:
        if tid in BUSY:
            return
        BUSY.add(tid)

    def go():
        try:
            while True:
                time.sleep(4)                      # 손님이 이어 쓰는 말을 잠깐 기다린다
                msgs = read(tid) or []
                said = [m for m in msgs if m.get("who") in ("guest", "us")]
                if not said or said[-1]["who"] != "guest":
                    return
                if sum(1 for m in said if m.get("by") == "agent") >= per_thread:
                    return log("%s 답 안 함(이 대화 한도)" % tid)
                with LOCK:
                    today = datetime.datetime.now(KST).date().isoformat()
                    if ANSWERED["d"] != today:
                        ANSWERED["d"], ANSWERED["n"] = today, 0
                    if ANSWERED["n"] >= per_day:
                        return log("%s 답 안 함(하루 한도)" % tid)
                    ANSWERED["n"] += 1
                n = len(said)
                got = compose(msgs)
                if not got:
                    return
                text = got["reply"]
                now_said = [m for m in (read(tid) or []) if m.get("who") in ("guest", "us")]
                if now_said and now_said[-1]["who"] == "us":
                    return                         # 그 사이 사람이 답했다. 사람 말이 이긴다
                if len(now_said) != n:
                    continue                       # 그 사이 손님이 더 썼다. 다시 읽고 짓는다
                append(tid, {"at": now(), "who": "us", "by": "agent", "text": text})
                log("%s us(agent) %d자" % (tid, len(text)))
                if got["confirmed"] and got["brief"] and not any(m.get("kind") == "order" for m in msgs):
                    append(tid, {"at": now(), "who": "note", "by": "agent", "kind": "order",
                                 "text": "넣을 글 — 아직 가게에 보내지 않았다\n\n" + got["brief"][:MAX_TEXT * 4]})
                    log("%s 넣을 글 %d자" % (tid, len(got["brief"])))
                return
        except Exception as e:
            log("답 못 함 %s" % type(e).__name__)
        finally:
            with LOCK:
                BUSY.discard(tid)
    threading.Thread(target=go, daemon=True).start()


def setup_note():
    """알림 걸기 — 원장님이 마을에서 직접 돌린다. 토큰은 화면에 보이지 않고, 자료 폴더에만 적힌다."""
    import getpass
    token = getpass.getpass("봇 토큰(BotFather 가 준 것. 붙여 넣어도 화면에 안 보입니다): ").strip()
    if not re.match(r"^\d+:[A-Za-z0-9_-]{30,}$", token):
        sys.exit("토큰 꼴이 아닙니다. 아무것도 바꾸지 않았습니다.")
    me = tg(token, "getMe")["result"]
    print("봇: @%s" % me.get("username"))
    input("텔레그램에서 이 봇에게 아무 말이나 한 줄 보낸 뒤 여기서 엔터를 누르세요. ")
    ups = [u["message"] for u in tg(token, "getUpdates").get("result", []) if "message" in u]
    if not ups:
        sys.exit("봇이 받은 말이 없습니다. 봇에게 한 줄 보낸 뒤 다시 돌려 주세요. 아무것도 바꾸지 않았습니다.")
    chat = ups[-1]["chat"]
    name = chat.get("title") or " ".join(filter(None, [chat.get("first_name"), chat.get("last_name")]))
    if input("이 방으로 알릴까요? 「%s」 (y/n): " % name).strip().lower() != "y":
        sys.exit("그만둡니다. 아무것도 바꾸지 않았습니다.")
    with open(os.open(NOTE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "w", encoding="utf-8") as f:
        json.dump({"token": token, "chat": chat["id"]}, f)
    tg(token, "sendMessage", chat_id=chat["id"], text="ヨヨイ 창구 — 알림이 걸렸습니다. 손님 말이 오면 여기로 알립니다.")
    print("걸었습니다. 텔레그램에 시험 알림이 갔습니다. 끄려면 %s 를 지우면 됩니다." % NOTE)


def path_of(tid):
    return os.path.join(BOX, tid + ".jsonl")


def read(tid):
    """대화 하나를 읽는다. 없으면 None."""
    if not ID_RE.match(tid):
        return None
    try:
        with open(path_of(tid), encoding="utf-8") as f:
            return [json.loads(x) for x in f if x.strip()]
    except FileNotFoundError:
        return None


def append(tid, row):
    with LOCK:
        with open(path_of(tid), "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def allowed(ip):
    """너무 많이 두드리면 잠깐 닫는다."""
    t = time.time()
    with LOCK:
        today = datetime.datetime.now(KST).date().isoformat()
        if DAY["d"] != today:
            DAY["d"], DAY["n"] = today, 0
        q = HITS[ip]
        while q and t - q[0] > 3600:
            q.popleft()
        if len(q) >= PER_IP_HOUR or DAY["n"] >= PER_DAY:
            return False
        q.append(t)
        DAY["n"] += 1
        if len(HITS) > 5000:
            for k in [k for k, v in HITS.items() if not v or t - v[-1] > 3600]:
                del HITS[k]
        return True


def threads():
    """대화 목록. 마지막 마디가 새 것부터."""
    out = []
    for name in os.listdir(BOX):
        if not name.endswith(".jsonl"):
            continue
        tid = name[:-6]
        msgs = read(tid)
        if not msgs:
            continue
        said = [m for m in msgs if m.get("who") != "note"]
        last = said[-1] if said else msgs[-1]
        out.append(dict(t=tid, first=msgs[0], last=last, n=len(said), waiting=last.get("who") == "guest",
                        order=any(m.get("kind") == "order" for m in msgs)))
    out.sort(key=lambda x: x["last"].get("at", ""), reverse=True)
    return out


OPS_CSS = """*{box-sizing:border-box}
:root{--bg:#fbfaf8;--fg:#1a1917;--mut:#6b6862;--line:#e6e2db;--card:#fff;--acc:#b8442e;--accs:#f5ede9}
@media(prefers-color-scheme:dark){:root{--bg:#141311;--fg:#f0ede8;--mut:#a29c93;--line:#2b2926;--card:#1c1a18;--acc:#e5714f;--accs:#2a1f1b}}
body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.65 -apple-system,BlinkMacSystemFont,"Noto Sans KR","Hiragino Sans",sans-serif}
.w{max-width:44rem;margin:0 auto;padding:1.2rem 1rem 4rem}
h1{font-size:1.3rem;margin:.4rem 0 1rem} a{color:var(--acc)}
.row{display:block;padding:.8rem 1rem;margin:0 0 .6rem;border:1px solid var(--line);border-radius:.7rem;background:var(--card);text-decoration:none;color:var(--fg)}
.row.wait{border-color:var(--acc)} .row small{display:block;color:var(--mut);font-size:.8rem}
.tag{display:inline-block;font-size:.75rem;padding:.05rem .5rem;border-radius:1rem;background:var(--accs);color:var(--acc);margin-right:.4rem}
.m{padding:.7rem .9rem;margin:0 0 .6rem;border-radius:.8rem;border:1px solid var(--line);background:var(--card);white-space:pre-wrap;overflow-wrap:anywhere}
.m.us{background:var(--accs);border-color:transparent;margin-left:2rem} .m.guest{margin-right:2rem} .m.note{border-style:dashed;color:var(--mut)}
.m small{display:block;color:var(--mut);font-size:.75rem;margin-bottom:.2rem}
textarea{width:100%;min-height:7rem;padding:.8rem;border:1px solid var(--line);border-radius:.55rem;background:var(--bg);color:var(--fg);font:inherit}
button{font:inherit;padding:.6rem 1.2rem;border-radius:.5rem;border:1px solid var(--acc);background:var(--acc);color:#fff;cursor:pointer;margin-top:.6rem}
label{display:block;margin-top:.5rem;color:var(--mut);font-size:.9rem}
"""
WHO = {"guest": "손님", "us": "ヨヨイ", "note": "메모(손님에게 안 보임)"}


def page(title, body):
    return ("<!doctype html><html lang=\"ko\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            "<meta name=\"robots\" content=\"noindex,nofollow\"><meta name=\"referrer\" content=\"no-referrer\">"
            "<title>%s</title><style>%s</style></head><body><div class=\"w\">%s</div></body></html>"
            % (html.escape(title), OPS_CSS, body))


def ops_list():
    rows = []
    ts = threads()
    for x in ts:
        f, l = x["first"], x["last"]
        head = (f.get("text") or "").strip().splitlines()[0][:120] if (f.get("text") or "").strip() else ""
        rows.append(
            '<a class="row%s" href="t/%s">%s<b>%s</b><small>%s · %s · %s마디 · 마지막 %s (%s)</small></a>'
            % (" wait" if x["waiting"] else "", x["t"],
               ('<span class="tag">답 기다림</span>' if x["waiting"] else "")
               + ('<span class="tag">넣을 차례</span>' if x["order"] else ""),
               html.escape(head), html.escape(f.get("lang", "")), html.escape(f.get("page", "")),
               x["n"], html.escape(l.get("at", "")[:16].replace("T", " ")), WHO.get(l.get("who"), "")))
    n = sum(1 for x in ts if x["waiting"])
    body = "<h1>ヨヨイ 창구 — 대화 %d개 · 답 기다림 %d개</h1>%s" % (
        len(ts), n, "".join(rows) or "<p>아직 온 말이 없습니다.</p>")
    return page("ヨヨイ 창구", body)


def ops_thread(tid, msgs):
    f = msgs[0]
    out = ['<p><a href="../">← 목록</a></p><h1>%s · %s</h1><p><small>손님이 보는 곳: <a href="%s/t/#%s">%s/t/#%s</a></small></p>'
           % (html.escape(f.get("lang", "")), html.escape(f.get("page", "")), SITE, tid, SITE, tid)]
    for m in msgs:
        w = m.get("who", "guest")
        out.append('<div class="m %s"><small>%s · %s</small>%s</div>'
                   % (w if w in WHO else "guest", WHO.get(w, w) + (" · 에이전트" if m.get("by") == "agent" else ""),
                      html.escape(m.get("at", "")[:16].replace("T", " ")), html.escape(m.get("text", ""))))
    out.append('<form method="post"><textarea name="text" required placeholder="손님 말로 답을 씁니다. 쓴 그대로 손님에게 보입니다."></textarea>'
               '<label><input type="checkbox" name="note" value="1"> 메모로만 남긴다(손님에게 안 보임)</label>'
               '<button type="submit">남기기</button></form>')
    return page("ヨヨイ 창구 — 대화", "".join(out))


class H(BaseHTTPRequestHandler):
    server_version = "yoyoi-ch"
    sys_version = ""
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def ip(self):
        # 캐디가 붙인 손님 주소. 맨 끝 것이 캐디가 직접 본 주소다.
        xff = self.headers.get("X-Forwarded-For", "")
        return xff.split(",")[-1].strip() if xff else self.client_address[0]

    def send(self, code, body=b"", ctype="application/json; charset=utf-8", extra=()):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        o = self.headers.get("Origin", "")
        if o in ORIGINS:
            self.send_header("Access-Control-Allow-Origin", o)
            self.send_header("Vary", "Origin")
        for k, v in extra:
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def js(self, code, obj):
        self.send(code, json.dumps(obj, ensure_ascii=False))

    def body(self):
        try:
            n = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            n = -1
        if n < 0 or n > MAX_BODY:
            self.close_connection = True
            return None
        return self.rfile.read(n)

    def parts(self):
        p = urllib.parse.urlsplit(self.path).path
        return [urllib.parse.unquote(x) for x in p.split("/") if x]

    def ops(self, ps):
        """열쇠가 맞으면 나머지 길을, 아니면 None."""
        if ps and secrets.compare_digest(ps[0].encode(), KEY.encode()):
            return ps[1:]
        return None

    def do_OPTIONS(self):
        self.send(204, extra=(("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
                              ("Access-Control-Allow-Headers", "Content-Type"),
                              ("Access-Control-Max-Age", "86400")))

    def do_GET(self):
        ps = self.parts()
        if not ps:
            return self.send(200, "ヨヨイ\n", "text/plain; charset=utf-8")
        if len(ps) == 2 and ps[0] == "t":
            msgs = read(ps[1])
            if msgs is None:
                return self.js(404, {"ok": False})
            return self.js(200, {"ok": True, "lang": msgs[0].get("lang", "en"),
                                 "msgs": [{"who": m["who"], "text": m["text"], "at": m["at"]}
                                          for m in msgs if m.get("who") in ("guest", "us")]})
        rest = self.ops(ps)
        if rest is None:
            return self.send(404, "", "text/plain")
        if not rest:
            if not urllib.parse.urlsplit(self.path).path.endswith("/"):
                return self.send(302, extra=(("Location", "/%s/" % urllib.parse.quote(KEY)),))
            return self.send(200, ops_list(), "text/html; charset=utf-8")
        if len(rest) == 2 and rest[0] == "t":
            msgs = read(rest[1])
            if msgs is not None:
                return self.send(200, ops_thread(rest[1], msgs), "text/html; charset=utf-8")
        return self.send(404, "", "text/plain")

    do_HEAD = do_GET

    def do_POST(self):
        ps = self.parts()
        raw = self.body()
        if raw is None:
            return self.js(413, {"ok": False, "why": "big"})
        if ps == ["say"]:
            return self.say(raw)
        rest = self.ops(ps)
        if rest is not None and len(rest) == 2 and rest[0] == "t":
            msgs = read(rest[1])
            if msgs is None:
                return self.send(404, "", "text/plain")
            form = urllib.parse.parse_qs(raw.decode("utf-8", "replace"), keep_blank_values=True)
            text = (form.get("text", [""])[0]).replace("\r\n", "\n").strip()
            if text:
                who = "note" if form.get("note") else "us"
                append(rest[1], {"at": now(), "who": who, "text": text[:MAX_TEXT * 4]})
                log("%s %s %d자" % (rest[1], who, len(text)))
            return self.send(303, extra=(("Location", "/%s/t/%s" % (urllib.parse.quote(KEY), rest[1])),))
        return self.send(404, "", "text/plain")

    def say(self, raw):
        o = self.headers.get("Origin", "")
        if o and o not in ORIGINS:
            return self.js(403, {"ok": False, "why": "origin"})
        try:
            d = json.loads(raw.decode("utf-8"))
            assert isinstance(d, dict)
        except Exception:
            return self.js(400, {"ok": False, "why": "form"})
        text = d.get("text")
        if not isinstance(text, str) or not text.strip():
            return self.js(400, {"ok": False, "why": "empty"})
        if len(text) > MAX_TEXT:
            return self.js(413, {"ok": False, "why": "long"})
        if not allowed(self.ip()):
            log("잠깐 닫음(너무 많이 두드림)")
            return self.js(429, {"ok": False, "why": "busy"})
        lang = d.get("lang") if d.get("lang") in LANGS else "en"
        pg = d.get("page") if isinstance(d.get("page"), str) else ""
        pg = re.sub(r"[^A-Za-z0-9/_.-]", "", pg)[:120]
        tid = d.get("t")
        row = {"at": now(), "who": "guest", "text": text}
        first = not tid
        if tid:
            msgs = read(tid) if isinstance(tid, str) else None
            if msgs is None:
                return self.js(404, {"ok": False, "why": "thread"})
            if len(msgs) >= MAX_MSGS:
                return self.js(429, {"ok": False, "why": "full"})
            lang, pg = msgs[0].get("lang", lang), msgs[0].get("page", pg)
        else:
            tid = secrets.token_urlsafe(12)
            row.update(lang=lang, page=pg)
        append(tid, row)
        log("%s guest %d자 %s %s" % (tid, len(text), lang, pg))
        notify(tid, lang, pg, first)
        answer(tid)
        return self.js(200, {"ok": True, "t": tid})


if __name__ == "__main__":
    if sys.argv[1:] == ["알림"]:
        setup_note()
        sys.exit(0)
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    srv.daemon_threads = True
    log("문 열림 127.0.0.1:%d" % PORT)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)
