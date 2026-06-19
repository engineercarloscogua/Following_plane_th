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

# Let's inspect each parsed section text for terms like "cumplió", "100%", "avance", "no se", "pendiente", "en proceso", or specific numbers
for sec in sorted(sections.keys(), key=lambda x: [int(c) for c in x.split('.')]):
    t = " ".join(sections[sec]["text"]).strip()
    t = re.sub(r'\s+', ' ', t)
    
    # Check for keywords and percentages
    pcts = re.findall(r'(\d+(?:[\.,]\d+)?\s*%)', t)
    no_ejecutado = any(k in t.lower() for k in ["no se registra vinculación", "no se otorgaron", "no se registraron", "no se realizó", "en proceso de revisión", "en curso"])
    
    print(f"[{sec}] {sections[sec]['title']}")
    print(f"  Percentages found: {pcts}")
    print(f"  Suspicion of non-completion or process: {no_ejecutado}")
    # Print first 200 chars
    print(f"  Text: {t[:300]}...\n")
