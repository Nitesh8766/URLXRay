import json
import matplotlib.pyplot as plt

file = "scan_history.json"

with open(file, "r") as f:
    data = json.load(f)

urls = []
scores = []

for item in data:
    urls.append(item["url"])
    scores.append(item["risk_score"])

plt.bar(urls, scores)

plt.xlabel("URLs")
plt.ylabel("Risk Score")
plt.title("URL Risk Score Analysis")

plt.xticks(rotation=45)
plt.tight_layout()

plt.show()
