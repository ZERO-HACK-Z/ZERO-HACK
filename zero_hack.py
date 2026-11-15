import os, re, sys
sys.stdin.reconfigure(encoding="utf-8", errors="replace")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import  json, time, hmac, socket, base64, hashlib, threading, subprocess, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

RED, GREEN, CYAN, YELLOW, WHITE, RESET = "\033[91m", "\033[92m", "\033[96m", "\033[93m", "\033[97m", "\033[0m"
LANG = {
    "ar": {
        "menu": "القائمة الرئيسية :", "o1": "غرفة سريعة مباشرة (رابط موحد مشفر)",
        "o2": "السيرفرات السحابية (غرف عامة وخاصة)", "o3": "تشغيل وضع السيرفر السحابي", "o4": "طريقة الاستخدام والمساعدة",
        "o4": "طريقة الاستخدام والمساعدة", "o0": "خروج", "ch": "اختر رقماً",
        "p2p": "\n [1] إنشاء غرفة  [2] دخول برابط  [0] رجوع: ",
        "key": "كلمة سر الغرفة (للتشفير): ", "wait": "[*] جاري إنشاء النفق وتوليد الرابط...",
        "share": "[+] انسخ الرابط وأرسله لصديقك:", "wpeer": "[*] في انتظار دخول صديقك...",
        "plink": "ألصق الرابط الموحد هنا: ", "blink": "[!] رابط غير صالح!",
        "conn": "[+] تم الاتصال! التشفير التام مفعل.", "help": "اكتب رسالتك | /file ملف | 0 رجوع | 00 خروج نهائي",
        "fpath": "مسار الملف: ", "fsent": "[+] تم تشفير وإرسال الملف!", "frecv": "[+] تم استلام ملف وحفظه: ",
        "curl": "رابط السيرفر السحابي (فارغ للمحلي): ", "rname": "اسم الغرفة: ",
        "rpass": "كلمة سر الغرفة (فارغ للعامة): ", "sstart": "[*] السيرفر يعمل على منفذ 5000..."
    },
    "en": {
        "menu": "MAIN MENU :", "o1": "Direct Fast Room (Encrypted Invite Link)",
        "o2": "Cloud Servers (Public & Private Rooms)", "o3": "Run Cloud Server Mode", "o4": "How to Use & Help",
        "o4": "How to Use & Help", "o0": "Exit", "ch": "Select option: ",
        "p2p": "\n [1] Host Room  [2] Join via Link  [0] Back: ",
        "key": "Room Secret Key: ", "wait": "[*] Creating tunnel & generating link...",
        "share": "[+] Copy and send this link:", "wpeer": "[*] Waiting for peer...",
        "plink": "Paste Invite Link: ", "blink": "[!] Invalid link!",
        "conn": "[+] Connected! E2E Encryption Active.", "help": "Type msg | /file to send file | /exit to quit",
        "fpath": "File path: ", "fsent": "[+] File sent!", "frecv": "[+] File saved as: ",
        "curl": "Cloud URL (Empty for localhost): ", "rname": "Room name: ",
        "rpass": "Room password (Empty for public): ", "sstart": "[*] Server running on port 5000..."
    }
}
lang, ROOMS = "ar", {}


class GoBack(Exception): pass

def ask(prompt_text):
    val = input(prompt_text).strip()
    if val == "0":
        raise GoBack()
    if val == "00":
        print(f"\n{RED}Goodbye! - Zero-Yuossf{RESET}")
        sys.exit()
    return val

def ar(text):
    if not any("\u0600" <= c <= "\u06FF" for c in text):
        return text
    forms = {
        "ا":("ﺍ","ﺍ","ﺎ","ﺎ"),"أ":("ﺃ","ﺃ","ﺄ","ﺄ"),"إ":("ﺇ","ﺇ","ﺈ","ﺈ"),"آ":("ﺁ","ﺁ","ﺂ","ﺂ"),
        "ب":("ﺏ","ﺑ","ﺒ","ﺐ"),"ت":("ﺕ","ﺗ","ﺘ","ﺖ"),"ث":("ﺙ","ﺛ","ﺜ","ﺚ"),"ج":("ﺝ","ﺟ","ﺠ","ﺞ"),
        "ح":("ﺡ","ﺣ","ﺤ","ﺢ"),"خ":("ﺥ","ﺧ","ﺨ","ﺦ"),"د":("ﺩ","ﺩ","ﺪ","ﺪ"),"ذ":("ﺫ","ﺫ","ﺬ","ﺬ"),
        "ر":("ﺭ","ﺭ","ﺮ","ﺮ"),"ز":("ﺯ","ﺯ","ﺰ","ﺰ"),"س":("ﺱ","ﺳ","ﺴ","ﺲ"),"ش":("ﺵ","ﺷ","ﺸ","ﺶ"),
        "ص":("ﺹ","ﺻ","ﺼ","ﺺ"),"ض":("ﺽ","ﺿ","ﻀ","ﺾ"),"ط":("ﻁ","ﻃ","ﻄ","ﻂ"),"ظ":("ﻅ","ﻇ","ﻈ","ﻆ"),
        "ع":("ﻉ","ﻋ","ﻌ","ﻊ"),"غ":("ﻍ","ﻏ","ﻐ","ﻎ"),"ف":("ﻑ","ﻓ","ﻔ","ﻒ"),"ق":("ﻕ","ﻗ","ﻘ","ﻖ"),
        "ك":("ﻙ","ﻛ","ﻜ","ﻚ"),"ل":("ﻝ","ﻟ","ﻠ","ﻞ"),"م":("ﻡ","ﻣ","ﻤ","ﻢ"),"ن":("ﻥ","ﻧ","ﻨ","ﻦ"),
        "ه":("ﻩ","ﻫ","ﻬ","ﻪ"),"ة":("ﺓ","ﺓ","ﺔ","ﺔ"),"و":("ﻭ","ﻭ","ﻮ","ﻮ"),"ؤ":("ﺅ","ﺅ","ﺆ","ﺆ"),
        "ي":("ﻱ","ﻳ","ﻴ","ﻲ"),"ى":("ﻯ","ﻯ","ﻰ","ﻰ"),"ئ":("ﺉ","ﺋ","ﺌ","ﺊ"),"ء":("ﺀ","ﺀ","ﺀ","ﺀ")
    }
    no_next = set("اأإآدذرزوؤةىء")
    res, n = [], len(text)
    for i, ch in enumerate(text):
        if ch not in forms:
            res.append(ch); continue
        prev_c = i > 0 and text[i-1] in forms and text[i-1] not in no_next
        next_c = i + 1 < n and text[i+1] in forms
        idx = 2 if (prev_c and next_c) else (1 if next_c else (3 if prev_c else 0))
        res.append(forms[ch][idx])
    shaped = "".join(res).replace("(", "\x01").replace(")", "\x02")
    parts = re.split(r"([\u0600-\u06FF\uFE70-\uFEFF\s\x01\x02]+)", shaped)
    out = []
    for part in parts:
        if any("\u0600" <= c <= "\u06FF" or "\uFE70" <= c <= "\uFEFF" for c in part):
            p_rev = part[::-1].replace("\x01", ")").replace("\x02", "(")
            out.append(p_rev)
        else:
            out.append(part.replace("\x01", "(").replace("\x02", ")"))
    return "".join(out[::-1])


def type_line(text, delay=0.04, prefix=""):
    clean = re.sub(r"\033\[[0-9;]*m", "", text)
    if prefix:
        sys.stdout.write(prefix)
        sys.stdout.flush()
        time.sleep(delay * 2)
    if lang == "ar" and any("\u0600" <= c <= "\u06FF" or "\uFE70" <= c <= "\uFEFF" for c in clean):
        m = re.match(r"^(\033\[[0-9;]*m)(.*)(\033\[0m)$", text)
        c_start, body, c_end = m.groups() if m else ("", text, "")
        for i in range(1, len(body) + 1):
            sys.stdout.write("\r" + prefix + " " * (len(body) - i) + c_start + body[-i:] + c_end)
            sys.stdout.flush()
            time.sleep(delay)
        print()
    else:
        for ch in text:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(delay)
        print()

def banner(anim=False):
    logo = [
        "   ███████╗███████╗██████╗  ██████╗ ",
        "   ╚══███╔╝██╔════╝██╔══██╗██╔═══██╗",
        "     ███╔╝ █████╗  ██████╔╝██║   ██║",
        "    ███╔╝  ██╔══╝  ██╔══██╗██║   ██║",
        "   ███████╗███████╗██║  ██║╚██████╔╝",
        "   ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ",
        "   ██╗  ██╗ █████╗  ██████╗██╗  ██╗ ",
        "   ██║  ██║██╔══██╗██╔════╝██║ ██╔╝ ",
        "   ███████║███████║██║     █████╔╝  ",
        "   ██╔══██║██╔══██║██║     ██╔═██╗  ",
        "   ██║  ██║██║  ██║╚██████╗██║  ██╗ ",
        "   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ "
    ]
    if anim:
        os.system("clear")
        w = len(logo[0])
        seq = list(range(w - 1, -1, -1)) + list(range(0, w))
        for pos in seq:
            sys.stdout.write("\033[H\n")
            for row in logo:
                line_str = ""
                for idx, ch in enumerate(row):
                    if abs(idx - pos) <= 2:
                        line_str += f"{WHITE}{ch}"
                    else:
                        line_str += f"{RED}{ch}"
                sys.stdout.write(line_str + RESET + "\n")
            sys.stdout.write(f"\n{WHITE}   Dev: {RED}Zero-Yuossf{WHITE} | P2P & Cloud Encrypted{RESET}\n")
            sys.stdout.flush()
            time.sleep(0.045)
    os.system("clear")
    print()
    for row in logo:
        print(f"{RED}{row}{RESET}")
    print(f"\n{WHITE}   Dev: {RED}Zero-Yuossf{WHITE} | P2P & Cloud Encrypted")
    print(f"{RED} ============================================{RESET}")

def _stream(k, iv, n):
    out, c = bytearray(), 0
    while len(out) < n:
        out.extend(hashlib.sha256(k + iv + c.to_bytes(4, "big")).digest()); c += 1
    return bytes(out[:n])

def enc_msg(pw, txt):
    k = hashlib.sha256((pw or "ZERO_HACK_PUB").encode()).digest()
    iv, raw = os.urandom(16), txt.encode()
    ct = bytes(a ^ b for a, b in zip(raw, _stream(k, iv, len(raw))))
    sig = hmac.new(k, iv + ct, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(iv + sig + ct).decode()

def dec_msg(pw, tok):
    k = hashlib.sha256((pw or "ZERO_HACK_PUB").encode()).digest()
    b = base64.urlsafe_b64decode(tok.encode())
    iv, sig, ct = b[:16], b[16:48], b[48:]
    if not hmac.compare_digest(sig, hmac.new(k, iv + ct, hashlib.sha256).digest()): raise ValueError()
    return bytes(a ^ b for a, b in zip(ct, _stream(k, iv, len(ct)))).decode()

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_POST(self):
        if self.path == "/send":
            d = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))).decode())
            ROOMS.setdefault(d.get("room", "general"), []).append(d)
            self.send_response(200); self.end_headers(); self.wfile.write(b"{}")
    def do_GET(self):
        if self.path.startswith("/get/"):
            p = self.path.split("/")
            m = ROOMS.get(p[2], [])
            self.send_response(200); self.end_headers()
            self.wfile.write(json.dumps({"messages": m[int(p[3]):], "total": len(m)}).encode())


def show_help():
    banner()
    if lang == "ar":
        print(f"\n{WHITE}  {ar('دليل استخدام أداة ZERO-HACK :')}{RESET}")
        print(f"{RED}  ────────────────────────────{RESET}\n")
        print(f"  {GREEN} {ar('الغرفة السريعة المباشرة (P2P) :')}{RESET}")
        print(f"      {WHITE}{ar('ينشئ المضيف غرفة ويحصل على رابط موحد مشفر،')}{RESET}")
        print(f"      {WHITE}{ar('ويرسله لصديقه ليلصقه ويدخل معه فوراً.')}{RESET}\n")
        print(f"  {CYAN} {ar('السيرفرات السحابية (Cloud) :')}{RESET}")
        print(f"      {WHITE}{ar('اكتب اسم الغرفة وكلمة السر للتواصل المشفر،')}{RESET}")
        print(f"      {WHITE}{ar('أو اترك كلمة السر فارغة لدخول غرفة عامة.')}{RESET}\n")
        print(f"  {YELLOW} {ar('تشغيل السيرفر السحابي :')}{RESET}")
        print(f"      {WHITE}{ar('يحول جهازك إلى سيرفر لاستقبال المستخدمين.')}{RESET}\n")
        print(f"  {RED}[*] {ar('أوامر سريعة داخل الأداة :')}{RESET}")
        print(f"      {WHITE}/file : {ar('إرسال ملف مشفر')} | 0 : {ar('رجوع')} | 00 : {ar('خروج')}{RESET}\n")
    else:
        print(f"\n{WHITE}  ZERO-HACK User Guide :{RESET}")
        print(f"{RED}  ────────────────────{RESET}\n")
        print(f"  {GREEN} Direct Fast Room (P2P) :{RESET}")
        print(f"      {WHITE}Host creates a room to get an encrypted invite link,{RESET}")
        print(f"      {WHITE}friend pastes the link to connect instantly.{RESET}\n")
        print(f"  {CYAN} Cloud Servers :{RESET}")
        print(f"      {WHITE}Enter room name & password for E2E encrypted chat,{RESET}")
        print(f"      {WHITE}or leave password empty for an open public room.{RESET}\n")
        print(f"  {YELLOW} Run Cloud Server :{RESET}")
        print(f"      {WHITE}Turns your device or host into a cloud relay server.{RESET}\n")
        print(f"  {RED}[*] Quick Commands :{RESET}")
        print(f"      {WHITE}/file : Send encrypted file | 0 : Back | 00 : Exit{RESET}\n")
    ask(f"  {CYAN}{ar('اكتب 0 للرجوع للقائمة الرئيسية :') if lang == 'ar' else 'Enter 0 to go back :'} {WHITE}")

def run_srv():
    print(f"{GREEN}{ar(LANG[lang]['sstart'])}{RESET}")
    try:
        print(f"{YELLOW}  [CTRL+C] {ar('للرجوع للقائمة الرئيسية')}{RESET}")
        ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", 5000))), Handler).serve_forever()
    except KeyboardInterrupt:
        pass
def cloud_cli():
    t = LANG[lang]
    url = ask(f"{CYAN}{ar(t['curl'])}{RESET}").strip() or "http://127.0.0.1:5000"
    if not url.startswith("http"): url = "http://" + url
    rm = ask(f"{CYAN}{ar(t['rname'])}{RESET}").strip() or "general"
    pw = ask(f"{CYAN}{ar(t['rpass'])}{RESET}").strip()
    usr = ask(f"{CYAN}Username / الاسم: {RESET}").strip() or "User"
    print(f"\n{GREEN}{ar(t['conn'])}{RESET}\n{YELLOW}{ar(t['help'])}{RESET}\n")
    lid, run = 0, True
    def poll():
        nonlocal lid
        while run:
            try:
                res = json.loads(urllib.request.urlopen(f"{url}/get/{rm}/{lid}", timeout=5).read().decode())
                for m in res.get("messages", []):
                    try:
                        dec = dec_msg(pw, m["payload"])
                        if dec.startswith("FILE::"):
                            _, fn, fd = dec.split("::", 2)
                            sn = "recv_" + os.path.basename(fn)
                            open(sn, "wb").write(base64.b64decode(fd))
                            print(f"\n{GREEN}{ar(t['frecv'])} {sn}{RESET}")
                        elif m["sender"] != usr: print(f"\n{CYAN}[{m['sender']}]: {WHITE}{ar(dec)}{RESET}")
                    except: pass
                lid = res.get("total", lid)
            except: pass
            time.sleep(1.5)
    threading.Thread(target=poll, daemon=True).start()
    while run:
        try:
            txt = input()
            if txt.strip() in ["/exit", "00"]: print(f"\n{RED}Goodbye! - Zero-Yuossf{RESET}"); sys.exit()
            elif txt.strip() in ["/back", "0"]: run = False; break
            elif txt.strip() == "/file":
                fp = ask(f"{YELLOW}{ar(t['fpath'])}{RESET}").strip()
                if os.path.exists(fp):
                    b64 = base64.b64encode(open(fp, "rb").read()).decode()
                    d = json.dumps({"room": rm, "sender": usr, "payload": enc_msg(pw, f"FILE::{os.path.basename(fp)}::{b64}")}).encode()
                    urllib.request.urlopen(urllib.request.Request(f"{url}/send", data=d)); print(f"{GREEN}{ar(t['fsent'])}{RESET}")
            elif txt.strip():
                d = json.dumps({"room": rm, "sender": usr, "payload": enc_msg(pw, txt)}).encode()
                urllib.request.urlopen(urllib.request.Request(f"{url}/send", data=d))
        except: run = False; break

def p2p():
    t = LANG[lang]
    ch = ask(f"{CYAN}{ar(t['p2p'])}{RESET}").strip()
    def chat(conn, pw):
        print(f"\n{GREEN}{ar(t['conn'])}{RESET}\n{YELLOW}{ar(t['help'])}{RESET}\n")
        def rloop():
            while True:
                try:
                    data = conn.recv(10485760)
                    if not data: break
                    dec = dec_msg(pw, data.decode())
                    if dec.startswith("FILE::"):
                        _, fn, fd = dec.split("::", 2)
                        sn = "recv_" + os.path.basename(fn)
                        open(sn, "wb").write(base64.b64decode(fd))
                        print(f"\n{GREEN}{ar(t['frecv'])} {sn}{RESET}")
                    else: print(f"\n{CYAN}[Peer]: {WHITE}{ar(dec)}{RESET}")
                except: break
        threading.Thread(target=rloop, daemon=True).start()
        while True:
            txt = input()
            if txt.strip() in ["/exit", "00"]: print(f"\n{RED}Goodbye! - Zero-Yuossf{RESET}"); sys.exit()
            elif txt.strip() in ["/back", "0"]: conn.close(); break
            elif txt.strip() == "/file":
                fp = ask(f"{YELLOW}{ar(t['fpath'])}{RESET}").strip()
                if os.path.exists(fp):
                    b64 = base64.b64encode(open(fp, "rb").read()).decode()
                    conn.sendall(enc_msg(pw, f"FILE::{os.path.basename(fp)}::{b64}").encode()); print(f"{GREEN}{ar(t['fsent'])}{RESET}")
            elif txt.strip(): conn.sendall(enc_msg(pw, txt).encode())
    if ch == "1":
        pw = ask(f"{CYAN}{ar(t['key'])}{RESET}").strip()
        srv = socket.socket(); srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("0.0.0.0", 4444)); srv.listen(1)
        print(f"{YELLOW}{ar(t['wait'])}{RESET}")
        proc = subprocess.Popen(["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ServerAliveInterval=30", "-R", "0:localhost:4444", "serveo.net"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            m = re.search(r"serveo\.net:(\d+)", line)
            if m:
                ep = base64.urlsafe_b64encode(pw.encode()).decode()
                print(f"\n{GREEN}{ar(t['share'])}{RESET}\n{WHITE}  zerohack://serveo.net:{m.group(1)}#{ep}{RESET}\n\n{YELLOW}{ar(t['wpeer'])}{RESET}")
                break
        conn, _ = srv.accept(); chat(conn, pw); proc.terminate()
    elif ch == "2":
        lk = ask(f"{CYAN}{ar(t['plink'])}{RESET}").strip()
        try:
            ap, ep = lk.replace("zerohack://", "").split("#", 1)
            h, p = ap.split(":", 1)
            pw = base64.urlsafe_b64decode(ep.encode()).decode()
            cli = socket.socket(); cli.connect((h, int(p))); chat(cli, pw)
        except: print(f"{RED}{ar(t['blink'])}{RESET}"); time.sleep(2)
banner()
print(f"\n{WHITE}  Choose Language / {ar('اختر اللغة')}{RESET}\n\n  {GREEN}1. {ar('العربية')}{RESET}\n  {CYAN}2. English{RESET}\n")
lc = input(f"{YELLOW}  [1/2]: {RESET}").strip()
lang = "en" if lc == "2" else "ar"

while True:
    banner(); t = LANG[lang]
    print()
    type_line(f"{WHITE}{ar(t['menu'])}{RESET}", 0.045, "  ")
    print(f"{RED}  ────────────────────{RESET}\n")
    type_line(f"{GREEN}{ar(t['o1'])}{RESET}", 0.038, f"  {WHITE}[{GREEN}1{WHITE}] ")
    type_line(f"{CYAN}{ar(t['o2'])}{RESET}", 0.038, f"  {WHITE}[{CYAN}2{WHITE}] ")
    type_line(f"{YELLOW}{ar(t['o3'])}{RESET}", 0.038, f"  {WHITE}[{YELLOW}3{WHITE}] ")
    type_line(f"{WHITE}{ar(t['o4'])}{RESET}", 0.038, f"  {WHITE}[{CYAN}4{WHITE}] ")
    type_line(f"{RED}{ar(t['o0'])}{RESET}", 0.045, f"  {WHITE}[{RED}0{WHITE}] ")
    print(f"\n  {CYAN}{ar(t['ch'])}{RESET}")
    c = input(f"  {RED}>>> {WHITE}").strip()
    try:
        if c == "1": p2p()
        elif c == "2": cloud_cli()
        elif c == "3": run_srv()
        elif c == "4": show_help()
        elif c in ["0", "00"]:
            print(f"\n{RED}Goodbye! - Zero-Yuossf{RESET}")
            sys.exit()
    except (GoBack, KeyboardInterrupt):
        pass
