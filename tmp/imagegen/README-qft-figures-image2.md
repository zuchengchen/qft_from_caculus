# QFT Figure image2 Batch Prompts

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
python "${CODEX_HOME:-$HOME/.codex}/skills/.system/imagegen/scripts/image_gen.py" generate-batch \
  --input tmp/imagegen/qft_figures_image2_prompts.jsonl \
  --out-dir figures/instructional-image2 \
  --concurrency 5
```

The bundled CLI may choose its own output naming under `--out-dir`. If exact paths are required, run entries one by one with the `out` value from each JSONL row.

After image2 assets are generated for any figures where the LaTeX-native result is not good enough, update `figures/instructional/manifest.json` entries from `latex-tikz-labelled` to the image2 paths, then rerun:

```bash
python3 scripts/verify_instructional_figures.py
python3 scripts/spot_review_figures.py
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```
