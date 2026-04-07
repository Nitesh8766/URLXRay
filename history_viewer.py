import json

file = "scan_history.json"

try:
    with open(file, "r") as f:
        data = json.load(f)

    print("\n==== URL Scan History ====\n")

    for item in data:
        print("URL:", item.get("url"))
        print("Risk Score:", item.get("risk_score"))
        print("Verdict:", item.get("verdict"))
        print("------------------------")

except FileNotFoundError:
    print("No scan history found.")
