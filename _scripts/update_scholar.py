# scripts/update_scholar.py
from scholarly import scholarly
from pathlib import Path
import html

# Replace with your Google Scholar user ID
SCHOLAR_ID = "YOUR_SCHOLAR_ID"

def bib_escape(s: str) -> str:
    if s is None:
        return ""
    return s.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")

def entry_key(pub, i):
    author = "paper"
    year = pub.get("bib", {}).get("pub_year", "nodate")
    title = pub.get("bib", {}).get("title", f"paper{i}")
    first = title.split()[0].lower() if title else f"paper{i}"
    return f"{author}{year}{first}"

author = scholarly.search_author_id(SCHOLAR_ID)
author = scholarly.fill(author, sections=["publications"])

entries = []
for i, pub in enumerate(author.get("publications", []), start=1):
    filled = scholarly.fill(pub)
    bib = filled.get("bib", {})

    title = bib_escape(bib.get("title", ""))
    authors = bib_escape(bib.get("author", ""))
    journal = bib_escape(bib.get("journal", "") or bib.get("venue", ""))
    year = bib_escape(str(bib.get("pub_year", "")))
    volume = bib_escape(str(bib.get("volume", "")))
    number = bib_escape(str(bib.get("number", "")))
    pages = bib_escape(str(bib.get("pages", "")))
    publisher = bib_escape(str(bib.get("publisher", "")))
    doi = bib_escape(str(bib.get("doi", "")))
    url = filled.get("pub_url") or ""
    url = bib_escape(url)

    key = entry_key(filled, i)

    fields = [
        f"  title = {{{title}}}",
        f"  author = {{{authors}}}",
    ]
    if journal:
        fields.append(f"  journal = {{{journal}}}")
    if year:
        fields.append(f"  year = {{{year}}}")
    if volume:
        fields.append(f"  volume = {{{volume}}}")
    if number:
        fields.append(f"  number = {{{number}}}")
    if pages:
        fields.append(f"  pages = {{{pages}}}")
    if publisher:
        fields.append(f"  publisher = {{{publisher}}}")
    if doi:
        fields.append(f"  doi = {{{doi}}}")
    if url:
        fields.append(f"  url = {{{url}}}")

    entry = "@article{" + key + ",\n" + ",\n".join(fields) + "\n}\n"
    entries.append(entry)

out = Path("_bibliography/papers.bib")
out.write_text("\n".join(entries), encoding="utf-8")
print(f"Wrote {len(entries)} entries to {out}")
