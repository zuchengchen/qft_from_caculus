#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "figures" / "instructional" / "manifest.json"


def image2_path(path: str) -> str:
    p = Path(path)
    return str(p.with_name(p.stem + "-image2.png"))


def replace_in_tex(tex_file: str, old_path: str, new_path: str) -> bool:
    path = ROOT / tex_file
    text = path.read_text(encoding="utf-8")
    if old_path not in text:
        return False
    path.write_text(text.replace(old_path, new_path), encoding="utf-8")
    return True


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    applied = []
    missing = []
    for entry in manifest["entries"]:
        old = entry["image_path"]
        new = image2_path(old)
        if not (ROOT / new).exists():
            missing.append(new)
            continue
        changed = replace_in_tex(entry["tex_file"], old, new)
        if changed or entry.get("image_path") != new:
            entry["latex_native_image_path"] = old
            entry["fallback_image_path"] = entry.get("background_image_path", old)
            entry["image_path"] = new
            entry["generator"] = "image2"
            entry["generation_priority"] = "latex-first-with-image2-fallback"
            entry["image2_status"] = "applied"
            entry["inspected"] = "pending post-replacement spot review"
            applied.append(new)

    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "applied": len(applied),
                "missing": len(missing),
                "manifest": str(MANIFEST.relative_to(ROOT)),
                "note": "Run verify_instructional_figures.py, spot_review_figures.py, and latexmk after applying replacements.",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
