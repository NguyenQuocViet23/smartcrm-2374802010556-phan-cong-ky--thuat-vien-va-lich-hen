"""Render factual pytest outcomes as readable PNG evidence."""

from __future__ import annotations

import re
import textwrap
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "docs" / "test-evidence"


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = (
        ["C:/Windows/Fonts/consolab.ttf", "C:/Windows/Fonts/consola.ttf"]
        if bold
        else ["C:/Windows/Fonts/consola.ttf"]
    )
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def render_test_evidence(
    test_id: str,
    title: str,
    status: str,
    duration: float,
    details: dict[str, str],
    failure: str | None = None,
) -> Path:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"^test_tc\d+_", "", title.lower())
    slug = re.sub(r"[^a-z0-9]+", "_", slug).strip("_")
    path = EVIDENCE_DIR / f"{test_id}_{slug}.png"
    font = _font(20)
    bold = _font(24, bold=True)
    lines = [
        (f"{test_id} · {title}", bold, (24, 45, 74)),
        (f"Thời điểm: {datetime.now().astimezone().isoformat(timespec='seconds')}", font, (58, 74, 98)),
        (f"Kết quả: {status} · Thời gian: {duration:.3f}s", bold, (25, 125, 70) if status == "PASS" else (177, 34, 34)),
    ]
    for key in ("Given", "When", "Expected", "Actual"):
        content = details.get(key, "Chưa được khai báo trong test.")
        lines.append((f"{key}:", bold, (24, 45, 74)))
        lines.extend((segment, font, (58, 74, 98)) for segment in textwrap.wrap(content, width=100))
    if failure:
        lines.append(("Traceback:", bold, (177, 34, 34)))
        lines.extend(
            (segment, font, (120, 28, 28))
            for line in failure.splitlines()[-24:]
            for segment in textwrap.wrap(line, width=112) or [""]
        )

    height = max(320, 70 + len(lines) * 34)
    image = Image.new("RGB", (1440, height), "#ffffff")
    draw = ImageDraw.Draw(image)
    y = 28
    for value, line_font, color in lines:
        draw.text((32, y), value, font=line_font, fill=color)
        y += 35
    image.save(path)
    return path


def save_summary(results: list[dict[str, Any]]) -> None:
    if not results:
        return
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    (EVIDENCE_DIR / "results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    image = Image.new("RGB", (1440, 90 + 42 * (len(results) + 1)), "#ffffff")
    draw = ImageDraw.Draw(image)
    font = _font(18)
    bold = _font(22, bold=True)
    draw.text((24, 20), "Báo cáo test case", font=bold, fill="#18324f")
    headers = ("Mã", "Tên", "Kết quả", "Thời gian")
    x_positions = (24, 155, 1040, 1190)
    y = 64
    for x, value in zip(x_positions, headers):
        draw.text((x, y), value, font=bold, fill="#18324f")
    for result in results:
        y += 40
        values = (
            result["id"],
            result["title"][:65],
            result["status"],
            f'{result["duration"]:.3f}s',
        )
        color = "#17814b" if result["status"] == "PASS" else "#b12222"
        for index, (x, value) in enumerate(zip(x_positions, values)):
            draw.text((x, y), value, font=font, fill=color if index == 2 else "#344c65")
    image.save(EVIDENCE_DIR / "_summary.png")
