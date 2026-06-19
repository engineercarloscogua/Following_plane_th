import re

with open("scratch/informe_2025_extracted.txt", "r", encoding="utf-8") as f:
    text = f.read()

lines = text.split("\n")
sections = {}
current_sec = None

# Match sections
sec_pattern = re.compile(r'^(2\.\d+\.\d+|3\.\d+)\.?\s+(.*)')

for line in lines:
    m = sec_pattern.match(line.strip())
    if m:
        current_sec = m.group(1)
        sections[current_sec] = {
            "title": m.group(2),
            "text": []
        }
    elif current_sec:
        if line.strip().startswith("--- PAGE"):
            continue
        sections[current_sec]["text"].append(line)

# Let's print the first half (2.1.1 to 2.2.6)
for sec in sorted(sections.keys(), key=lambda x: [int(c) for c in x.split('.')]):
    if sec.startswith("2.1.") or (sec.startswith("2.2.") and int(sec.split('.')[2]) <= 6):
        t = " ".join(sections[sec]["text"]).strip()
        t = re.sub(r'\s+', ' ', t)
        print(f"[{sec}] {sections[sec]['title']}")
        print(f"  Text: {t[:400]}...\n")
