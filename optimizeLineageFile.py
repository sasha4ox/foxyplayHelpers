import re
import json

with open("servers.txt", "r", encoding="utf-8") as f:
    raw = f.read()

pattern = re.compile(r"<option[^>]*>(.*?)</option>")

result = {}

for match in pattern.findall(raw):
    text = match.strip()
    if not text:
        continue

    parts = text.split()
    variant = parts[0]
    server = " ".join(parts[1:]).strip()

    if variant not in result:
        result[variant] = []

    if server:
        result[variant].append(server)

# dedupe + sort
for variant in result:
    result[variant] = sorted(set(result[variant]))

with open("foxyplayLinegaServers.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("Done")