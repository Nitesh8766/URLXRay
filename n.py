import socket
import urllib.parse
from datetime import datetime
import time
import requests
import ssl
import json
import os

# ───────── COLORS ─────────
try:
    from colorama import Fore, Style, init
    init(autoreset=True)

    R = Fore.RED
    G = Fore.GREEN
    Y = Fore.YELLOW
    C = Fore.CYAN
    W = Fore.WHITE
    M = Fore.MAGENTA
    B = Fore.BLUE
    E = Style.RESET_ALL
    BD = Style.BRIGHT

except:
    R=G=Y=C=W=M=B=E=BD=''

WIDTH = 60
HISTORY_FILE = "scan_history.json"

HOSTING_MAP = {
    "onrender.com": "Render",
    "vercel.app": "Vercel",
    "netlify.app": "Netlify",
    "github.io": "GitHub Pages",
    "herokuapp.com": "Heroku"
}

TRUSTED = ["instagram.com","google.com","facebook.com","apple.com"]

# ───────── HISTORY SYSTEM (RESTORED) ─────────
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(entry):
    data = load_history()
    data.append(entry)
    data = data[-50:]  # keep last 50
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def export_file(entry):
    name = "result_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".txt"
    with open(name, "w") as f:
        f.write("PHISHING SCAN REPORT\n")
        f.write("="*40 + "\n")
        f.write(f"URL: {entry['url']}\n")
        f.write(f"Score: {entry['score']}\n")
        f.write(f"Time: {entry['time']}\n")
    print(C + "  [+] Exported: " + name + E)

# ───────── UI ─────────
def show_commands():
    print("\n")
    print(M + "  ======================================================")
    print(M + "  ||" + W + BD + "   PHISHING URL DETECTOR PRO".center(WIDTH-4) + M + "||")
    print(M + "  ||" + C + "  Cybersecurity Analysis Tool v2.0".center(WIDTH-4) + M + "||")
    print(M + "  ======================================================\n")

    print(C + "  +------------------------------------------------------+")
    print(C + "  |   COMMANDS                                          |")
    print(C + "  +------------------------------------------------------+")
    print(C + "  |   scan <url>   → Analyze URL                       |")
    print(C + "  |   history      → View history                     |")
    print(C + "  |   stats        → View stats                       |")
    print(C + "  |   q            → Quit                              |")
    print(C + "  +------------------------------------------------------+")
    print(C + "  |   Tip: You can also paste a URL directly.         |")
    print(C + "  +------------------------------------------------------+\n")

def line():
    print(C + "  " + "=" * WIDTH + E)

def box(text, col=W):
    print(C + "| " + col + text.ljust(WIDTH-2)[:WIDTH-2] + E + C + " |" + E)

def header(title):
    line()
    print(M + BD + "  " + title.center(WIDTH) + E)
    line()

def animate():
    frames = ["[.         ]","[..        ]","[...       ]","[....      ]",
              "[.....     ]","[......    ]","[.......   ]","[........  ]"]

    print(C + "\n  Scanning URL..." + E)
    for f in frames:
        print("\r  " + Y + f + E, end="")
        time.sleep(0.04)
    print()

# ───────── HELPERS ─────────
def domain_ok(domain):
    try:
        ip = socket.gethostbyname(domain)
        if ip in ["0.0.0.0","127.0.0.1"]:
            return False, ip
        return True, ip
    except:
        return False, None

def ssl_ok(domain):
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain,443),timeout=3) as s:
            with ctx.wrap_socket(s,server_hostname=domain):
                return True
    except:
        return False

def hosting(domain):
    for k,v in HOSTING_MAP.items():
        if domain.endswith(k):
            return v
    return "Unknown"

def redirects(url):
    try:
        r = requests.get(url,timeout=5,allow_redirects=True)
        return len(r.history)
    except:
        return 0

def login(url):
    try:
        r = requests.get(url,timeout=5)
        return "<form" in r.text.lower()
    except:
        return False

# ───────── SCORING ─────────
def score(domain, https, sslv, host):
    s = 100
    if not https: s -= 25
    if not sslv: s -= 25
    if host == "Unknown": s -= 10
    if any(domain.endswith(t) for t in TRUSTED):
        s = 95
    return max(0,min(100,s))

# ───────── MAIN ─────────
def analyze(url):

    if not url.startswith("http"):
        url = "http://" + url

    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc.replace("www.","")

    print("\n")
    header("INPUT DETAILS")
    box("TARGET: " + url, Y)
    box("TIME  : " + str(datetime.now()), W)

    header("STAGE 1: BASIC VALIDATION")

    print(C + "  Checking DNS resolution..." + E)

    ok, ip = domain_ok(domain)

    if not ok:
        box("❌ DOMAIN NOT RESOLVING", R)
        return

    box("✔ Domain resolves via DNS lookup", G)
    box("✔ Resolved IP: " + str(ip), C)

    header("STAGE 2: SECURITY CHECKS")
    animate()

    https = url.startswith("https")
    sslv = ssl_ok(domain)
    host = hosting(domain)
    redir = redirects(url)
    loginf = login(url)

    box("HTTPS: " + ("✔ Enabled" if https else "✘ Missing"), G if https else R)
    box("SSL  : " + ("✔ Valid" if sslv else "⚠ Issue"), G if sslv else Y)
    box("Redirects: " + str(redir), C)
    box("Login form: " + ("Detected" if loginf else "Clean"), Y if loginf else G)

    header("STAGE 3: INTELLIGENCE LAYER")

    box("Hosting: " + host, G if host!="Unknown" else Y)

    rep = score(domain, https, sslv, host)

    header("FINAL RESULT")

    col = G if rep >= 80 else (Y if rep >= 50 else R)
    box(f"SCORE: {rep}/100", col + BD)

    verdict = "SAFE" if rep>=80 else ("SUSPICIOUS" if rep>=50 else "DANGEROUS")
    box(verdict, col + BD)

    # ───── SAVE HISTORY (RESTORED) ─────
    entry = {
        "url": url,
        "score": rep,
        "time": str(datetime.now()),
        "ip": ip,
        "hosting": host,
        "verdict": verdict
    }

    save_history(entry)

    ans = input("\nExport report file? (y/n): ")
    if ans.lower() == "y":
        export_file(entry)

# ───────── START ─────────
show_commands()

while True:
    cmd = input(C + "\n>> " + E).strip()
    if cmd == "q":
        break
    analyze(cmd)
