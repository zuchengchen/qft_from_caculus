#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageStat

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "figures" / "instructional" / "manifest.json"
REPORT = ROOT / "figures" / "instructional" / "spot_review.json"
CONTACT_SHEET = ROOT / "figures" / "instructional" / "spot_review_contact_sheet.png"


def raster_for(path: Path) -> Image.Image:
    if path.suffix.lower() == ".pdf":
        with tempfile.TemporaryDirectory() as tmp:
            out_prefix = Path(tmp) / "page"
            result = subprocess.run(
                ["pdftoppm", "-png", "-singlefile", "-r", "150", str(path), str(out_prefix)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30,
                check=False,
            )
            png = out_prefix.with_suffix(".png")
            if result.returncode != 0 or not png.exists():
                raise RuntimeError(f"pdftoppm failed for {path}: {result.stderr[-800:]}")
            image = Image.open(png).convert("RGB")
            return image.copy()
    return Image.open(path).convert("RGB")


def spread_indices(count: int, samples: int) -> list[int]:
    if samples >= count:
        return list(range(count))
    return [round(i * (count - 1) / (samples - 1)) for i in range(samples)]


def image_metrics(path: Path) -> dict[str, object]:
    image = raster_for(path)
    stat = ImageStat.Stat(image)
    ranges = [hi - lo for lo, hi in image.getextrema()]
    return {
        "size": list(image.size),
        "mean_rgb": [round(v, 2) for v in stat.mean],
        "channel_ranges": ranges,
        "ok_nonblank": min(ranges) > 20,
        "ok_size": image.size[0] >= 600 and image.size[1] >= 350,
    }


def build_contact_sheet(entries: list[dict[str, object]]) -> None:
    thumb_w, thumb_h = 220, 141
    label_h = 38
    cols = 5
    rows = (len(entries) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), "#f7f4ee")
    draw = ImageDraw.Draw(sheet)

    for idx, entry in enumerate(entries):
        image = raster_for(ROOT / str(entry["image_path"]))
        image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (idx % cols) * thumb_w
        y = (idx // cols) * (thumb_h + label_h)
        px = x + (thumb_w - image.width) // 2
        py = y + (thumb_h - image.height) // 2
        sheet.paste(image, (px, py))
        label = f"{idx + 1}. {Path(str(entry['tex_file'])).stem[:22]}"
        draw.text((x + 6, y + thumb_h + 4), label, fill="#1f2933")
        labels = ", ".join(str(label) for label in entry.get("in_figure_labels", [])[:2])
        draw.text((x + 6, y + thumb_h + 20), labels[:34] or str(entry["concept"])[:30], fill="#4b5563")

    CONTACT_SHEET.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CONTACT_SHEET)


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = manifest["entries"]
    sample_entries = [entries[i] for i in spread_indices(len(entries), 25)]
    reviewed = []
    for entry in sample_entries:
        metrics = image_metrics(ROOT / entry["image_path"])
        reviewed.append(
            {
                "image_path": entry["image_path"],
                "tex_file": entry["tex_file"],
                "concept": entry["concept"],
                "caption": entry["caption"],
                "generator": entry["generator"],
                "image2_status": entry["image2_status"],
                "in_figure_labels": entry.get("in_figure_labels", []),
                "latex_source_path": entry.get("latex_source_path"),
                "background_image_path": entry.get("background_image_path"),
                **metrics,
            }
        )

    build_contact_sheet(reviewed)
    report = {
        "sample_count": len(reviewed),
        "selection": "deterministic spread across manifest entries from early, middle, late, and review chapters",
        "all_nonblank_and_readable": all(item["ok_nonblank"] and item["ok_size"] for item in reviewed),
        "all_have_label_metadata": all(len(item.get("in_figure_labels", [])) >= 3 for item in reviewed),
        "contact_sheet": str(CONTACT_SHEET.relative_to(ROOT)),
        "reviewed": reviewed,
    }
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(REPORT.relative_to(ROOT)), "contact_sheet": str(CONTACT_SHEET.relative_to(ROOT)), "all_ok": report["all_nonblank_and_readable"]}, indent=2))


if __name__ == "__main__":
    main()
