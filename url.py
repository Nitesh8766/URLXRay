import re
import sys
import socket
import json
import os
import time
import urllib.parse
from datetime import datetime

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    R  = Fore.RED
    G  = Fore.GREEN
    Y  = Fore.YELLOW
    C  = Fore.CYAN
    W  = Fore.WHITE
    M  = Fore.MAGENTA
    B  = Fore.BLUE
    E  = Style.RESET_ALL
    BD = Style.BRIGHT
except ImportError:
    R = G = Y = C = W = M = B = E = BD = ''

HISTORY_FILE = 'scan_history.json'

SUSPICIOUS_TLDS = [
    '.xyz', '.tk', '.pw', '.ru', '.cn', '.top', '.click',
    '.gq', '.ml', '.cf', '.ga', '.icu', '.live', '.work',
    '.online', '.site', '.website', '.space', '.fun', '.zip'
]
SUSPICIOUS_KEYWORDS = [
    'login', 'signin', 'verify', 'verification', 'secure',
    'account', 'update', 'confirm', 'banking', 'paypal',
    'apple', 'amazon', 'microsoft', 'google', 'facebook',
    'instagram', 'netflix', 'support', 'helpdesk', 'password',
    'credential', 'validate', 'webscr', 'cmd', 'suspend',
    'unlock', 'restore', 'alert', 'billing', 'invoice',
    'claim', 'winner', 'prize', 'free', 'urgent', 'expire'
]
SHORTENER_DOMAINS = [
    'bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'ow.ly',
    'is.gd', 'buff.ly', 'adf.ly', 'short.io', 'rb.gy', 'tiny.cc'
]
BRAND_NAMES = [
    'paypal', 'apple', 'amazon', 'microsoft', 'google',
    'facebook', 'instagram', 'netflix', 'ebay', 'yahoo',
    'linkedin', 'twitter', 'dropbox', 'whatsapp', 'bank',
    'chase', 'wellsfargo', 'citibank', 'coinbase', 'binance',
    'metamask', 'blockchain', 'trustwallet'
]

findings_log = []
WIDTH = 54


def line(char='='):
    return C + '  ' + char * WIDTH + E


def box_top():
    print(C + '  +' + '-' * WIDTH + '+' + E)


def box_row(text='', col='', align='left'):
    visible = len(text)
    pad = WIDTH - 2 - visible
    if align == 'center':
        lpad = pad // 2
        rpad = pad - lpad
        content = ' ' * lpad + text + ' ' * rpad
    else:
        content = ' ' + text + ' ' * (WIDTH - 2 - visible)
    print(C + '  |' + E + col + content + E + C + '|' + E)


def box_div():
    print(C + '  +' + '-' * WIDTH + '+' + E)


def box_bot():
    print(C + '  +' + '-' * WIDTH + '+' + E)


def banner():
    print()
    print(C + BD + '  ' + '=' * WIDTH + E)
    print(C + BD + '  ||' + E + M + BD + ' PHISHING URL DETECTOR '.center(WIDTH - 4) + E + C + BD + '||' + E)
    print(C + BD + '  ||' + E + W + ' Cybersecurity Analysis Tool v2.0'.center(WIDTH - 4) + E + C + BD + '||' + E)
    print(C + BD + '  ' + '=' * WIDTH + E)
    print()


def mini_banner():
    print()
    print(C + '  ' + '=' * WIDTH + E)
    print(C + '  |' + E + BD + W + ' PHISHING URL DETECTOR  '.center(WIDTH) + E + C + '|' + E)
    print(C + '  ' + '=' * WIDTH + E)


def show_menu():
    print()
    box_top()
    box_row('  COMMANDS', BD + W)
    box_div()
    box_row('  scan              Analyze a URL')
    box_row('  file <path>       Scan a list of URLs from .txt file')
    box_row('  history           View previous scan results')
    box_row('  stats             View overall statistics')
    box_row('  help              Show this menu')
    box_row('  q                 Quit')
    box_div()
    box_row('  Tip: You can also paste a URL directly.')
    box_bot()
    print()


def animate_scan():
    frames = ['[.         ]', '[..        ]', '[...       ]', '[....      ]',
              '[.....     ]', '[......    ]', '[.......   ]', '[........  ]',
              '[......... ]', '[..........]']
    print()
    sys.stdout.write('  ' + C + 'Scanning  ' + E)
    for f in frames:
        sys.stdout.write('\r  ' + C + 'Scanning  ' + Y + f + E)
        sys.stdout.flush()
        time.sleep(0.06)
    sys.stdout.write('\r  ' + G + 'Scan complete!' + ' ' * 20 + E + '\n')


def score_bar(score):
    filled = score // 5
    empty = 20 - filled
    if score >= 70:
        col = R
    elif score >= 40:
        col = Y
    else:
        col = G
    bar = col + '[' + '#' * filled + '-' * empty + ']' + E
    return bar


def risk_label(score):
    if score >= 70:
        return R + BD + 'LIKELY PHISHING' + E
    elif score >= 40:
        return Y + BD + 'SUSPICIOUS' + E
    else:
        return G + BD + 'LIKELY SAFE' + E


def score_col(score):
    if score >= 70:
        return R
    elif score >= 40:
        return Y
    else:
        return G


def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_history(entry):
    history = load_history()
    history.append(entry)
    history = history[-50:]
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def show_history():
    history = load_history()
    print()
    box_top()
    box_row('  SCAN HISTORY', BD + W)
    box_div()
    if not history:
        box_row('  No scans recorded yet.')
    else:
        for i, h in enumerate(reversed(history), 1):
            s = h['score']
            col = score_col(s)
            label = 'PHISHING' if s >= 70 else ('SUSPECT' if s >= 40 else 'SAFE   ')
            url_cut = h['url'][:30] + ('...' if len(h['url']) > 30 else '')
            row = str(i).rjust(2) + '. ' + col + label + ' ' + str(s).rjust(3) + '/100' + E + '  ' + url_cut
            box_row('  ' + row)
    box_bot()
    print()


def show_stats():
    history = load_history()
    print()
    box_top()
    box_row('  STATISTICS', BD + W)
    box_div()
    if not history:
        box_row('  No scan data yet.')
    else:
        scores = [h['score'] for h in history]
        avg = sum(scores) // len(scores)
        ph = sum(1 for s in scores if s >= 70)
        su = sum(1 for s in scores if 40 <= s < 70)
        sa = sum(1 for s in scores if s < 40)
        box_row('  Total scans      :  ' + W + str(len(scores)) + E)
        box_row('  Average score    :  ' + Y + str(avg) + '/100' + E)
        box_row('  Likely phishing  :  ' + R + str(ph) + E)
        box_row('  Suspicious       :  ' + Y + str(su) + E)
        box_row('  Likely safe      :  ' + G + str(sa) + E)
    box_bot()
    print()


def export_results(entry):
    fname = 'result_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.txt'
    with open(fname, 'w') as f:
        f.write('PHISHING URL DETECTOR - Scan Result\n')
        f.write('=' * 50 + '\n')
        f.write('URL     : ' + entry['url'] + '\n')
        f.write('Score   : ' + str(entry['score']) + '/100\n')
        f.write('Verdict : ' + entry['verdict'] + '\n')
        f.write('Time    : ' + entry['time'] + '\n')
        f.write('=' * 50 + '\n')
        for r in entry['findings']:
            f.write(r + '\n')
    print(G + '  [+] Exported to: ' + fname + E)


def scan_file(filepath):
    if not os.path.exists(filepath):
        print(R + '  [!] File not found: ' + filepath + E)
        return
    with open(filepath, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    print(C + '\n  [*] Scanning ' + str(len(urls)) + ' URLs from file...' + E)
    for url in urls:
        analyze(url, silent=True)


def do_check(label, passed, reason, weight):
    if passed:
        findings_log.append('[PASS] ' + label)
        status = G + ' OK ' + E
    else:
        findings_log.append('[FAIL] ' + label + ' -> ' + reason)
        status = R + 'FAIL' + E
    print('  ' + C + '|' + E + ' [' + status + C + ']' + E + '  ' + label)
    if not passed:
        pad = ' ' * (WIDTH - len(reason) - 3)
        print('  ' + C + '|' + E + '        ' + Y + '> ' + reason + E)
    return 0 if passed else weight


def analyze(raw, silent=False):
    global findings_log
    findings_log = []

    if not raw.startswith(('http://', 'https://')):
        raw = 'http://' + raw

    try:
        parsed = urllib.parse.urlparse(raw)
    except Exception:
        print(R + '  [!] Cannot parse this URL.' + E)
        return

    domain = parsed.netloc.lower().replace('www.', '')
    path = parsed.path.lower()
    query = parsed.query.lower()
    full = raw.lower()
    score = 0

    animate_scan()

    print()
    print(C + '  +' + '-' * WIDTH + '+' + E)
    url_display = raw if len(raw) <= WIDTH - 4 else raw[:WIDTH - 7] + '...'
    box_row('  TARGET: ' + W + url_display + E)
    box_row('  TIME  : ' + W + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + E)
    print(C + '  +' + '=' * WIDTH + '+' + E)
    box_row('  SECURITY CHECKS', BD + W)
    print(C + '  +' + '-' * WIDTH + '+' + E)

    # Check 1
    score += do_check(
        'HTTPS secure connection',
        raw.startswith('https://'),
        'Uses HTTP only. Phishing sites often skip encryption.',
        15
    )

    # Check 2
    ip_match = re.match(r'^\d{1,3}(\.\d{1,3}){3}(:\d+)?$', domain)
    score += do_check(
        'Domain name used (not raw IP)',
        ip_match is None,
        'Raw IP address hides the real host identity.',
        25
    )

    # Check 3
    score += do_check(
        'URL length under 100 characters',
        len(raw) <= 100,
        'URL is ' + str(len(raw)) + ' chars. Malicious paths are buried in long URLs.',
        10
    )

    # Check 4
    score += do_check(
        'No @ symbol in URL',
        '@' not in raw,
        '@ tricks browsers into ignoring the real domain.',
        20
    )

    # Check 5
    tld_found = None
    for t in SUSPICIOUS_TLDS:
        if domain.endswith(t):
            tld_found = t
            break
    score += do_check(
        'Trusted top-level domain (TLD)',
        tld_found is None,
        'TLD "' + str(tld_found) + '" is heavily abused in phishing.',
        15
    )

    # Check 6
    sub_count = domain.count('.')
    score += do_check(
        'Normal subdomain depth (max 2)',
        sub_count <= 2,
        str(sub_count) + ' subdomain levels detected. Stacked to fake legitimacy.',
        15
    )

    # Check 7
    hyphen_count = domain.count('-')
    score += do_check(
        'Minimal hyphens in domain (max 2)',
        hyphen_count <= 2,
        str(hyphen_count) + ' hyphens found. Fakes use "paypal-secure-login.com".',
        10
    )

    # Check 8
    is_short = any(s in domain for s in SHORTENER_DOMAINS)
    score += do_check(
        'Not a URL shortener service',
        not is_short,
        'Shorteners mask the true destination URL.',
        20
    )

    # Check 9
    hits = [k for k in SUSPICIOUS_KEYWORDS if k in full]
    score += do_check(
        'No phishing keywords in URL',
        len(hits) == 0,
        'Keywords found: ' + ', '.join(hits),
        15
    )

    # Check 10
    brands = []
    for b in BRAND_NAMES:
        official = [b + '.com', b + '.net', b + '.org', b + '.co']
        if b in domain and domain not in official:
            brands.append(b)
    bm = '"' + brands[0] + '" in domain but not the official site.' if brands else ''
    score += do_check(
        'No brand name impersonation',
        len(brands) == 0,
        bm,
        25
    )

    # Check 11
    score += do_check(
        'No double slashes in path',
        '//' not in path,
        'Double slashes in path can trigger malicious redirects.',
        10
    )

    # Check 12
    encoded_matches = re.findall(r'%[0-9a-fA-F][0-9a-fA-F]', raw)
    enc_count = len(encoded_matches)
    score += do_check(
        'Minimal URL encoding (no obfuscation)',
        enc_count <= 3,
        str(enc_count) + ' encoded chars found. Used to conceal malicious content.',
        15
    )

    # Check 13
    score += do_check(
        'No IDN homograph attack',
        'xn--' not in domain,
        'Punycode in domain. Lookalike letters used to fake real domains.',
        30
    )

    # Check 14
    sus_params = ['redirect', 'url', 'return', 'next', 'continue', 'goto', 'link', 'dest']
    param_found = None
    for p in sus_params:
        if p in query:
            param_found = p
            break
    score += do_check(
        'No open redirect parameters',
        param_found is None,
        'Parameter "' + str(param_found) + '" found. Common in redirect attacks.',
        15
    )

    # Check 15
    score += do_check(
        'Not a data URI scheme',
        not raw.startswith('data:'),
        'data: URIs embed malicious HTML directly in the URL.',
        30
    )

    # Check 16 - Domain resolution
    resolved_ip = None
    try:
        clean_host = domain.split(':')[0]
        resolved_ip = socket.gethostbyname(clean_host)
        resolves = True
    except Exception:
        resolves = False

    do_check(
        'Domain resolves to a real server',
        resolves,
        'Domain does not resolve. May be fake or already removed.',
        0
    )

    score = min(score, 100)
    col = score_col(score)

    print(C + '  +' + '=' * WIDTH + '+' + E)
    box_row('  RESULT', BD + W)
    print(C + '  +' + '-' * WIDTH + '+' + E)

    if resolved_ip:
        box_row('  Resolved IP  : ' + W + resolved_ip + E)

    bar = score_bar(score)
    bar_text = '  Risk Meter   : ' + bar + '  ' + col + str(score) + '%' + E
    print('  ' + C + '|' + E + bar_text + C + '|' + E)

    box_row('  Risk Score   : ' + col + BD + str(score) + '/100' + E)
    box_row('  Verdict      : ' + risk_label(score))

    print(C + '  +' + '-' * WIDTH + '+' + E)

    if score >= 70:
        msg = '  [!] Do NOT visit. This URL is likely a phishing site.'
        msg_col = R
    elif score >= 40:
        msg = '  [~] Proceed carefully. Verify before entering credentials.'
        msg_col = Y
    else:
        msg = '  [+] Appears safe. Stay alert — no tool is 100% accurate.'
        msg_col = G

    box_row(msg, msg_col + BD)
    box_bot()
    print()

    entry = {
        'url': raw,
        'score': score,
        'verdict': ('LIKELY PHISHING' if score >= 70 else ('SUSPICIOUS' if score >= 40 else 'LIKELY SAFE')),
        'time': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'findings': findings_log
    }
    save_history(entry)

    if not silent:
        ans = input('  Export result to file? (y/n): ').strip().lower()
        if ans == 'y':
            export_results(entry)
    print()


# ── STARTUP ───────────────────────────────────────────────────
banner()
show_menu()

while True:
    try:
        cmd = input(C + '  >> ' + E).strip()
        if not cmd:
            continue
        low = cmd.lower()
        if low in ('q', 'quit', 'exit'):
            print(W + '\n  Stay safe out there. Goodbye!\n' + E)
            break
        elif low in ('help', 'h', '?', 'menu'):
            show_menu()
        elif low == 'history':
            show_history()
        elif low == 'stats':
            show_stats()
        elif low.startswith('file '):
            scan_file(cmd[5:].strip())
        elif low == 'scan':
            url = input(C + '  Enter URL: ' + E).strip()
            if url:
                analyze(url)
        else:
            analyze(cmd)
    except KeyboardInterrupt:
        print(W + '\n\n  Goodbye!\n' + E)
        break
