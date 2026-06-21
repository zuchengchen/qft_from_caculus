#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "figures" / "instructional" / "manifest.json"
OUT = ROOT / "tmp" / "imagegen" / "qft_figures_image2_prompts.jsonl"
README = ROOT / "tmp" / "imagegen" / "README-qft-figures-image2.md"


STYLE = (
    "serious university textbook scientific illustration; clean bitmap rendering; "
    "white or warm off-white page background; high contrast; muted teal, gold, gray, and red accents; "
    "include concise readable in-image labels, axis names, arrow labels, or region markers where helpful; "
    "use only short plain English labels and simple symbols; no long equations, no watermark; "
    "conceptually accurate, uncluttered, print-friendly"
)


def prompt_for(entry: dict[str, object]) -> str:
    chapter = entry["chapter_title"]
    concept = entry["concept"]
    caption = entry["caption"]
    return (
        f"Create an original instructional bitmap illustration for the concept '{concept}' "
        f"in the chapter '{chapter}'. Pedagogical intent: {caption} "
        "The image must not be a bare unlabelled picture: include clear short text markers "
        "inside the figure, such as axis labels, coordinate labels, labelled arrows, labelled "
        "regions, or input/output labels. Keep labels sparse, correct, large, and legible."
    )


def image2_path(entry: dict[str, object]) -> str:
    path = Path(str(entry["image_path"]))
    return str(path.with_name(path.stem + "-image2.png"))


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = manifest["entries"]
    OUT.parent.mkdir(parents=True, exist_ok=True)

    with OUT.open("w", encoding="utf-8") as handle:
        for entry in entries:
            payload = {
                "prompt": prompt_for(entry),
                "use_case": "scientific-educational",
                "style": STYLE,
                "composition": "landscape 4:3, centered, generous margins, labelled axes/arrows/regions where helpful",
                "constraints": "original image; include concise legible labels or markers; no long equations; no watermark; print-friendly",
                "quality": "medium",
                "size": "1536x1024",
                "out": image2_path(entry),
                "metadata": {
                    "source_manifest_id": entry["id"],
                    "latex_native_image_path": entry["image_path"],
                    "fallback_image_path": entry.get("background_image_path", entry["image_path"]),
                    "latex_source_path": entry.get("latex_source_path"),
                    "tex_file": entry["tex_file"],
                    "chapter_title": entry["chapter_title"],
                    "concept": entry["concept"],
                    "caption": entry["caption"],
                },
            }
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

    README.write_text(
        """# QFT Figure image2 Batch Prompts

This directory contains a prepared JSONL batch input for replacing LaTeX-native or local fallback figures with image2-generated bitmap assets only where the source-native result is not good enough.

The figure program is LaTeX-first. Prefer TikZ/PGFPlots/LaTeX-native figures for exact axes, arrows, labels, symbolic notation, and Feynman-style diagrams. Use these image2 prompts as a fallback for concepts that need richer physical or geometric illustration.

Generated images should not be bare pictures. Each image2 prompt asks for concise in-image markers such as axis labels, coordinate labels, arrow meanings, region labels, or input/output labels. Spot-review every generated image for label correctness and legibility before replacing a source-native figure.

Prepared file:

```bash
tmp/imagegen/qft_figures_image2_prompts.jsonl
```

The current environment did not expose a project-copyable built-in image2 output path and did not provide `OPENAI_API_KEY`, so this file is a ready-to-run handoff rather than an executed API batch.

When `OPENAI_API_KEY` is available, run:

```bash
python "${CODEX_HOME:-$HOME/.codex}/skills/.system/imagegen/scripts/image_gen.py" generate-batch \\
  --input tmp/imagegen/qft_figures_image2_prompts.jsonl \\
  --out-dir figures/instructional-image2 \\
  --concurrency 5
```

The bundled CLI may choose its own output naming under `--out-dir`. If exact paths are required, run entries one by one with the `out` value from each JSONL row.

After image2 assets are generated for any figures where the LaTeX-native result is not good enough, update `figures/instructional/manifest.json` entries from `latex-tikz-labelled` to the image2 paths, then rerun:

```bash
python3 scripts/verify_instructional_figures.py
python3 scripts/spot_review_figures.py
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```
""",
        encoding="utf-8",
    )
    print(json.dumps({"prompts": str(OUT.relative_to(ROOT)), "entries": len(entries), "readme": str(README.relative_to(ROOT))}, indent=2))


if __name__ == "__main__":
    main()
