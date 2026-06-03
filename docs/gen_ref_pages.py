"""mkdocs-gen-files generator: one API-reference page per public module.

Run by the gen-files plugin at build time; writes ``reference/<path>.md`` (each an
mkdocstrings autodoc directive) plus ``reference/SUMMARY.md`` for literate-nav. The
output is virtual and not committed. Private modules (``_dates``, ``_numbers``) are
intentionally absent.
"""

from pathlib import Path

import mkdocs_gen_files

PUBLIC_MODULES = [
    "kaloricketabulky.sdk.client",
    "kaloricketabulky.sdk.auth",
    "kaloricketabulky.sdk.errors",
    "kaloricketabulky.sdk.models.common",
    "kaloricketabulky.sdk.models.diary",
    "kaloricketabulky.sdk.models.snapshot",
    "kaloricketabulky.sdk.models.summary",
    "kaloricketabulky.sdk.models.tips",
    "kaloricketabulky.config",
]

nav = mkdocs_gen_files.Nav()

for dotted in PUBLIC_MODULES:
    parts = dotted.split(".")
    rel = Path(*parts[1:])  # drop the leading "kaloricketabulky"
    doc_path = Path("reference", rel).with_suffix(".md")
    nav[tuple(parts[1:])] = doc_path.relative_to("reference").as_posix()
    with mkdocs_gen_files.open(doc_path, "w") as fd:
        fd.write(f"# `{dotted}`\n\n::: {dotted}\n")

with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as fd:
    fd.writelines(nav.build_literate_nav())
