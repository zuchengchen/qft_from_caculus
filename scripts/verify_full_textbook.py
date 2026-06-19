#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MANUSCRIPT_GLOBS = [
    "main.tex",
    "qftcalc.sty",
    "frontmatter/*.tex",
    "chaptersfull/*.tex",
    "appendicesfull/*.tex",
]

PLACEHOLDER_PATTERNS = [
    r"\bTODO\b",
    r"\bTBD\b",
    r"lorem ipsum",
    r"\bplaceholder\b",
    r"\bunfinished\b",
    r"insert later",
    r"to be written",
    r"\bAI\b",
    r"\bChatGPT\b",
    r"\bOpenAI\b",
    r"artificial intelligence",
    r"delve into",
    r"it is important to note",
    r"comprehensive guide",
    r"specific form used for",
    r"narrow question inside",
    r"without importing a finished formalism",
    r"reader who writes that warning",
    r"particular calculation in this section",
]

REQUIRED_TOC_TERMS = [
    "Calculus",
    "Fourier",
    "Distribution",
    "Green",
    "Variational",
    "Classical Field",
    "Relativity",
    "Quantum",
    "Free Quantum Field",
    "Path Integrals",
    "Perturbative",
    "LSZ",
    "Renormalization",
    "Effective Field",
    "Spinors",
    "Abelian Gauge",
    "Non-Abelian",
    "Higgs",
    "Anomalies",
    "Nonperturbative",
    "Standard Model",
]


def files() -> list[Path]:
    seen: set[Path] = set()
    result: list[Path] = []
    for pattern in MANUSCRIPT_GLOBS:
        for path in ROOT.glob(pattern):
            if path.is_file() and path not in seen:
                seen.add(path)
                result.append(path)
    return sorted(result)


def strip_tex(text: str) -> str:
    text = re.sub(r"%.*", " ", text)
    text = re.sub(r"\\begin\{[^}]+\}|\\end\{[^}]+\}", " ", text)
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})?", " ", text)
    text = re.sub(r"[{}\\_^$&#]", " ", text)
    return text


def count_words(paths: list[Path]) -> int:
    words = 0
    for path in paths:
        text = strip_tex(path.read_text(encoding="utf-8", errors="ignore"))
        words += len(re.findall(r"[A-Za-z][A-Za-z'-]*", text))
    return words


def count_regex(paths: list[Path], pattern: str) -> int:
    rx = re.compile(pattern)
    total = 0
    for path in paths:
        total += len(rx.findall(path.read_text(encoding="utf-8", errors="ignore")))
    return total


def page_count() -> int | None:
    pdf = ROOT / "main.pdf"
    if not pdf.exists():
        return None
    try:
        out = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
    except Exception:
        return None
    for line in out.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    return None


def placeholder_hits(paths: list[Path]) -> list[dict[str, str | int]]:
    hits = []
    compiled = [(p, re.compile(p, re.IGNORECASE)) for p in PLACEHOLDER_PATTERNS]
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for lineno, line in enumerate(text.splitlines(), start=1):
            for label, rx in compiled:
                if rx.search(line):
                    hits.append({"file": str(path.relative_to(ROOT)), "line": lineno, "pattern": label, "text": line.strip()})
    return hits


def repeated_paragraphs(paths: list[Path]) -> list[dict[str, object]]:
    seen: dict[str, list[str]] = {}
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="ignore")
        paragraphs = [re.sub(r"\s+", " ", p.strip()) for p in re.split(r"\n\s*\n", text)]
        for para in paragraphs:
            if len(para.split()) >= 35:
                seen.setdefault(para, []).append(str(path.relative_to(ROOT)))
    repeated = []
    for para, locations in seen.items():
        if len(locations) > 1:
            repeated.append({"count": len(locations), "locations": locations[:5], "text": para[:220]})
    return repeated[:50]


def repeated_paragraph_summary(paths: list[Path]) -> dict[str, int]:
    seen: dict[str, set[str]] = {}
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="ignore")
        paragraphs = [re.sub(r"\s+", " ", p.strip()) for p in re.split(r"\n\s*\n", text)]
        for para in paragraphs:
            if len(para.split()) >= 35:
                seen.setdefault(para, set()).add(str(path.relative_to(ROOT)))
    exact_repeats = {para: locs for para, locs in seen.items() if len(locs) > 1}
    return {
        "exact_repeated_paragraphs": len(exact_repeats),
        "max_repeat_locations": max((len(locs) for locs in exact_repeats.values()), default=0),
    }


def toc_missing() -> list[str]:
    toc = ROOT / "main.toc"
    if not toc.exists():
        return REQUIRED_TOC_TERMS
    text = toc.read_text(encoding="utf-8", errors="ignore")
    lower = text.lower()
    return [term for term in REQUIRED_TOC_TERMS if term.lower() not in lower]


def main() -> None:
    paths = files()
    report = {
        "files": [str(p.relative_to(ROOT)) for p in paths],
        "word_count": count_words(paths),
        "exercise_count": count_regex(paths, r"\\begin\{exercise\}"),
        "example_count": count_regex(paths, r"\\begin\{example\}"),
        "derivation_mentions": count_regex(paths, r"Step-by-step derivation|\\derivation"),
        "page_count": page_count(),
        "placeholder_hits": placeholder_hits(paths),
        "repeated_paragraphs": repeated_paragraphs(paths),
        "repeated_paragraph_summary": repeated_paragraph_summary(paths),
        "toc_missing_terms": toc_missing(),
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
