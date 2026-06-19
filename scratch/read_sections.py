import re

with open("scratch/informe_2025_extracted.txt", "r", encoding="utf-8") as f:
    text = f.read()

lines = text.split("\n")
sections = {}
current_sec = None

# Match sections like 2.1.1, 2.1.21, 2.2.8, 2.3.12, 3.1, 3.2
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
        # Check if we hit page indicator or other section headers
        if line.strip().startswith("--- PAGE"):
            continue
        sections[current_sec]["text"].append(line)

print(f"Parsed {len(sections)} sections.")
# Let's print out the first 3 lines of each section text to understand them
for sec in sorted(sections.keys(), key=lambda x: [int(c) for c in x.split('.')]):
    t = " ".join(sections[sec]["text"]).strip()
    # clean multiple spaces
    t = re.sub(r'\s+', ' ', t)
    preview = t[:250] + "..." if len(t) > 250 else t
    print(f"{sec}: {sections[sec]['title']}")
    print(f"  PREVIEW: {preview}\n")
