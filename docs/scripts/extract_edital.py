from pdfminer.high_level import extract_text
from pathlib import Path

IN_PATH = Path(r"c:\Users\claud\CascadeProjects\Techdengue_MT\docs\edital\Preg. 014 - Dengue - Cincop-MT - Com TR.pdf")
OUT_PATH = Path(r"c:\Users\claud\CascadeProjects\Techdengue_MT\docs\edital\edital.txt")

if not IN_PATH.exists():
    raise SystemExit(f"Input PDF not found: {IN_PATH}")

text = extract_text(str(IN_PATH))
OUT_PATH.write_text(text, encoding="utf-8")
print(f"OK: wrote {OUT_PATH}")
