#!/usr/bin/env python3
# ヨヨイ 창구 — 손님과 가게가 한 칸에 쓴 말을 받아, 쓴 그대로 쌓고, 그 자리에서 대화를 잇는다.
#   철학(ops/WHY.md): 「사람은 말은 한다.」 입력은 말이어야 한다. 메일 앱이 열리면 말이 끊긴다.
#   길: yoyoi.jp 의 한 칸 → POST <창구>/say → 캐디 → 127.0.0.1:7980 → <자료>/대화/<대화표>.jsonl
#       손님은 yoyoi.jp/t/#<대화표> 에서 답을 보고 이어 쓴다. 대화표가 곧 열쇠다(로그인 없음).
#       우리는 <창구>/<열쇠>/ 에서 읽고 답한다. 열쇠가 틀리면 404 만 준다.
#   v1 원칙 그대로: 자동으로 답하지 않는다. 받고, 쌓고, 보여 준다. 답은 사람(미치)이 쓴다.
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
        out.append(dict(t=tid, first=msgs[0], last=last, n=len(said), waiting=last.get("who") == "guest"))
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
               '<span class="tag">답 기다림</span>' if x["waiting"] else "",
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
                   % (w if w in WHO else "guest", WHO.get(w, w),
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
