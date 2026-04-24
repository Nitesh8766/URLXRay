🔎 URLXRayy

<p align="center">"Python" (https://img.shields.io/badge/Python-3.x-blue?logo=python)
"Security Tool" (https://img.shields.io/badge/Tool-CyberSecurity-red)
"Status" (https://img.shields.io/badge/Status-Active-success)
"Stars" (https://img.shields.io/github/stars/Nitesh8766/URLXRay?style=social)

</p>---

🧑‍💻 URLXRay – Phishing URL Detection Tool

██╗   ██╗██████╗ ██╗     ██╗  ██╗██████╗  █████╗ ██╗   ██╗
██║   ██║██╔══██╗██║     ██║  ██║██╔══██╗██╔══██╗╚██╗ ██╔╝
██║   ██║██████╔╝██║     ███████║██████╔╝███████║ ╚████╔╝
██║   ██║██╔══██╗██║     ██╔══██║██╔══██╗██╔══██║  ╚██╔╝
╚██████╔╝██║  ██║███████╗██║  ██║██║  ██║██║  ██║   ██║
 ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝

           URLXRay - Phishing URL Analyzer

A lightweight cybersecurity tool that analyzes URLs and detects potential phishing or malicious patterns using heuristic analysis.

---

🚀 Features

🚀 Features
✔ Detect suspicious keywords in URLs
✔ Identify phishing patterns and brand impersonation
✔ Detect open redirect parameters
✔ Check HTTPS security status
✔ Domain structure analysis (subdomains, TLD, encoding tricks)
✔ DNS resolution validation
✔ SSL/TLS connectivity check
✔ Hosting platform detection (Render, Vercel, Netlify, etc.)
✔ Multi-stage security scanning (Basic → Security → Intelligence)
✔ Real-time CLI scan animation
✔ Risk-based reputation scoring system (0–100)
✔ Site classification engine:
--Phishing / Malicious
--Dev / Hosted Applications
--Pentest / Security Lab
--Legit / Unknown Trust
✔ Scan history storage (JSON-based persistence)
✔ Export scan reports to text files
✔ Colorful CLI interface with structured UI output
✔ Redirect analysis and login form detection
---

📥 Installation

Clone the repository:

git clone https://github.com/Nitesh8766/URLXRay.git

Move into the directory:

cd URLXRay

Run the tool:

python url.py

---

🖥 CLI Usage

Example:

python url.py https://example.com/login

Example Output:

[PASS] HTTPS secure connection
[FAIL] Suspicious keyword detected: login
[PASS] Domain resolves to real server

Risk Score : 30/100
Verdict    : LIKELY SAFE

---

📂 Project Structure

URLXRay
 ├── url.py
 ├── scan_history.json
 └── README.md

---

⚠ Disclaimer

This tool is for educational and cybersecurity research purposes only.
It may not detect every malicious URL.

---

👨‍💻 Author

Nitesh Chavan
BSc Cyber Security Student
