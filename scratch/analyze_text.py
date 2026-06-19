import re

with open("scratch/informe_2025_extracted.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Let's find sections like "2.1.1", "2.1.2", "2.2.1", "2.3.1", "3.1", "3.2" etc.
# We want to see the text that follows these headers.
lines = text.split("\n")
current_sec = None
sec_content = {}

# Patterns: e.g. "2.1.1. Realizar el Plan Anual..."
sec_pattern = re.compile(r'^(2\.\d+\.\d+|3\.\d+)\.?\s+(.*)')

for line in lines:
    m = sec_pattern.match(line.strip())
    if m:
        current_sec = m.group(1)
        title = m.group(2)
        sec_content[current_sec] = {"title": title, "lines": []}
    elif current_sec and line.strip().startswith("--- PAGE"):
        # Don't add page boundary to lines, but stop adding if we hit another main section
        pass
    elif current_sec:
        # If it's a new main section in the text (like "2.2 Policy..." or "3. Plan...") we can stop or ignore.
        # But actually, the matching is fine. Let's just collect lines.
        sec_content[current_sec]["lines"].append(line)

print(f"Found {len(sec_content)} sections.")
for sec, data in sorted(sec_content.items(), key=lambda x: [int(c) for c in x[0].split('.')]):
    content = "\n".join(data["lines"][:6]) # first 6 lines
    print(f"\n================ SECTION {sec} ================")
    print(f"TITLE: {data['title']}")
    print(f"CONTENT PREVIEW:\n{content}")
