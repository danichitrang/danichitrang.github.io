from scholarly import scholarly
from pathlib import Path


# Use only the Google Scholar user ID, not "&hl"
SCHOLAR_ID = "XzHP3wkAAAAJ"

# This image should exist at:
# assets/img/publication_preview/default_paper.png
DEFAULT_PREVIEW = "default_paper.png"


def bib_escape(value: str) -> str:
    if value is None:
        return ""
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("{", "\\{")
        .replace("}", "\\}")
    )


def make_key(pub: dict, i: int) -> str:
    bib = pub.get("bib", {})
    year = bib.get("pub_year", "nodate")
    title = bib.get("title", f"paper{i}")
    first_word = title.split()[0].lower() if title else f"paper{i}"

    # keep key simple and stable-ish
    first_word = "".join(ch for ch in first_word if ch.isalnum())
    return f"paper{year}{first_word or i}"


def doi_to_url(doi: str) -> str:
    doi = (doi or "").strip()
    if not doi:
        return ""
    return f"https://doi.org/{doi}"


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

    # Prefer Scholar/publication URL; if missing, fall back to DOI URL
    pub_url = filled.get("pub_url") or ""
    if not pub_url and doi:
        pub_url = doi_to_url(doi)
    pub_url = bib_escape(pub_url)

    key = make_key(filled, i)

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
    if pub_url:
        fields.append(f"  url = {{{pub_url}}}")
        fields.append(f"  html = {{{pub_url}}}")

    # Add the same default preview image to every paper
    fields.append(f"  preview = {{{DEFAULT_PREVIEW}}}")

    # Optional but useful in al-folio
    fields.append("  bibtex_show = {true}")

    entry = "@article{" + key + ",\n" + ",\n".join(fields) + "\n}\n"
    entries.append(entry)

out = Path("_bibliography/papers.bib")
out.write_text("\n".join(entries), encoding="utf-8")
print(f"Wrote {len(entries)} entries to {out}")
