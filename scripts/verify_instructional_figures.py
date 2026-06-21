#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "figures" / "instructional" / "manifest.json"
CHAPTER_GLOB = "chaptersfull/ch*.tex"
REVIEW_GLOB = "chaptersfull/partreview*.tex"

FIGURE_RE = re.compile(
    r"\\qftfigure\{(?P<path>[^}]+)\}\{(?P<caption>[^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\{(?P<label>[^}]+)\}",
    re.DOTALL,
)
BLOCK_RE = re.compile(r"% QFTFIGURE-BEGIN (?P<id>[^\n]+).*?% QFTFIGURE-END (?P=id)", re.DOTALL)


def included_files(pattern: str) -> list[Path]:
    main = (ROOT / "main.tex").read_text(encoding="utf-8")
    paths: list[Path] = []
    for path in sorted(ROOT.glob(pattern)):
        include_name = str(path.relative_to(ROOT))[:-4]
        if rf"\include{{{include_name}}}" in main:
            paths.append(path)
    return paths


def figure_refs(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    refs = []
    for match in FIGURE_RE.finditer(text):
        refs.append(
            {
                "path": match.group("path"),
                "caption": re.sub(r"\s+", " ", match.group("caption")).strip(),
                "label": match.group("label"),
            }
        )
    return refs


def block_ids(path: Path) -> set[str]:
    return {match.group("id") for match in BLOCK_RE.finditer(path.read_text(encoding="utf-8"))}


def load_manifest() -> dict[str, object]:
    if not MANIFEST.exists():
        return {"entries": []}
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def pdf_text(path: Path) -> str:
    result = subprocess.run(
        ["pdftotext", str(path), "-"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=20,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return re.sub(r"\s+", " ", result.stdout).strip().lower()


def main() -> int:
    chapters = included_files(CHAPTER_GLOB)
    reviews = included_files(REVIEW_GLOB)
    manifest = load_manifest()
    manifest_entries = manifest.get("entries", [])
    manifest_by_path = {entry.get("image_path"): entry for entry in manifest_entries if isinstance(entry, dict)}

    chapter_counts: dict[str, int] = {}
    review_counts: dict[str, int] = {}
    all_refs: list[dict[str, str]] = []
    missing_assets: list[str] = []
    weak_captions: list[dict[str, str]] = []
    missing_manifest_entries: list[str] = []
    non_instructional_refs: list[dict[str, str]] = []
    missing_blocks: list[str] = []
    missing_label_metadata: list[str] = []
    missing_label_text: list[dict[str, object]] = []
    weak_generation_priority: list[str] = []
    missing_intermediate_assets: list[str] = []

    for path in chapters + reviews:
        rel = str(path.relative_to(ROOT))
        refs = figure_refs(path)
        instructional_refs = [ref for ref in refs if ref["path"].startswith("figures/instructional/")]
        if path.name.startswith("partreview"):
            review_counts[rel] = len(instructional_refs)
        else:
            chapter_counts[rel] = len(instructional_refs)
        ids = block_ids(path)
        for ref in instructional_refs:
            ref = {**ref, "tex_file": rel}
            all_refs.append(ref)
            if not (ROOT / ref["path"]).exists():
                missing_assets.append(ref["path"])
            if len(ref["caption"].split()) < 12:
                weak_captions.append(ref)
            if ref["path"] not in manifest_by_path:
                missing_manifest_entries.append(ref["path"])
            label_id = ref["label"].removeprefix("fig:")
            if label_id not in ids:
                missing_blocks.append(ref["label"])
        for ref in refs:
            if ref["path"] != "figures/cover-image2.png" and not ref["path"].startswith("figures/instructional/"):
                non_instructional_refs.append({**ref, "tex_file": rel})

    manifest_paths = set(manifest_by_path)
    source_paths = {ref["path"] for ref in all_refs}
    manifest_not_referenced = sorted(manifest_paths - source_paths)

    chapters_under_3 = {k: v for k, v in chapter_counts.items() if v < 3}
    chapters_at_least_5 = {k: v for k, v in chapter_counts.items() if v >= 5}
    reviews_with_figures = {k: v for k, v in review_counts.items() if v >= 1}

    image2_entries = [
        entry
        for entry in manifest_entries
        if isinstance(entry, dict) and str(entry.get("generator", "")).lower().startswith("image2")
    ]
    fallback_entries = [
        entry
        for entry in manifest_entries
        if isinstance(entry, dict) and entry.get("generator") == "local-matplotlib-fallback"
    ]
    latex_entries = [
        entry
        for entry in manifest_entries
        if isinstance(entry, dict) and entry.get("generator") == "latex-tikz-labelled"
    ]

    for entry in manifest_entries:
        if not isinstance(entry, dict):
            continue
        image_path = str(entry.get("image_path", ""))
        generator = str(entry.get("generator", ""))
        priority = str(entry.get("generation_priority", ""))
        labels = entry.get("in_figure_labels", [])
        if priority != "latex-first" and not generator.lower().startswith("image2"):
            weak_generation_priority.append(image_path)
        if not isinstance(labels, list) or len([label for label in labels if str(label).strip()]) < 3:
            missing_label_metadata.append(image_path)
        if generator == "latex-tikz-labelled":
            for key in ["background_image_path", "latex_source_path"]:
                rel = entry.get(key)
                if not rel or not (ROOT / str(rel)).exists():
                    missing_intermediate_assets.append(f"{image_path}: missing {key}")
            text = pdf_text(ROOT / image_path) if image_path else ""
            expected = [str(label).strip().lower() for label in labels if str(label).strip()]
            present = [label for label in expected if label in text]
            if len(present) < min(3, len(expected)):
                missing_label_text.append(
                    {
                        "image_path": image_path,
                        "expected_labels": expected,
                        "present_labels": present,
                    }
                )

    report = {
        "total_instructional_figures_referenced": len(all_refs),
        "manifest_entries": len(manifest_entries),
        "chapter_file_count": len(chapters),
        "review_file_count": len(reviews),
        "minimum_figures_per_chapter": min(chapter_counts.values()) if chapter_counts else 0,
        "chapters_under_3": chapters_under_3,
        "chapters_at_least_5_count": len(chapters_at_least_5),
        "part_reviews_with_figures_count": len(reviews_with_figures),
        "missing_assets": sorted(set(missing_assets)),
        "weak_captions": weak_captions[:50],
        "missing_manifest_entries": sorted(set(missing_manifest_entries)),
        "manifest_not_referenced": manifest_not_referenced[:50],
        "missing_qftfigure_blocks": missing_blocks[:50],
        "non_instructional_refs": non_instructional_refs,
        "image2_entries": len(image2_entries),
        "local_fallback_entries": len(fallback_entries),
        "latex_tikz_labelled_entries": len(latex_entries),
        "missing_label_metadata": missing_label_metadata[:50],
        "missing_label_text": missing_label_text[:50],
        "weak_generation_priority": weak_generation_priority[:50],
        "missing_intermediate_assets": missing_intermediate_assets[:50],
        "chapter_counts": chapter_counts,
        "review_counts": review_counts,
    }
    print(json.dumps(report, indent=2))

    failures = []
    if len(all_refs) < 240:
        failures.append("fewer than 240 instructional figures are referenced")
    if len(manifest_entries) < 240:
        failures.append("manifest has fewer than 240 entries")
    if len(chapters) != 56:
        failures.append("main.tex does not include 56 chapter files")
    if chapters_under_3:
        failures.append("some chapters have fewer than 3 instructional figures")
    if len(chapters_at_least_5) < 20:
        failures.append("fewer than 20 chapters have at least 5 instructional figures")
    if missing_assets:
        failures.append("some referenced assets are missing")
    if weak_captions:
        failures.append("some captions are too short to be pedagogically meaningful")
    if missing_manifest_entries:
        failures.append("some referenced figures are missing manifest entries")
    if manifest_not_referenced:
        failures.append("some manifest entries are not referenced in source")
    if missing_blocks:
        failures.append("some qftfigure references are outside managed figure blocks")
    if fallback_entries:
        failures.append("some manifest entries still use unlabeled local matplotlib fallback generation")
    if not latex_entries and not image2_entries:
        failures.append("no LaTeX/TikZ labelled or image2 fallback entries are present")
    if missing_label_metadata:
        failures.append("some figures are missing in-figure label metadata")
    if missing_label_text:
        failures.append("some LaTeX/TikZ figures do not expose enough in-figure labels in the PDF")
    if weak_generation_priority:
        failures.append("some non-image2 figures do not declare latex-first generation priority")
    if missing_intermediate_assets:
        failures.append("some LaTeX/TikZ figures are missing source or background assets")

    if failures:
        print(json.dumps({"status": "fail", "failures": failures}, indent=2), file=sys.stderr)
        return 1
    print(json.dumps({"status": "pass"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
