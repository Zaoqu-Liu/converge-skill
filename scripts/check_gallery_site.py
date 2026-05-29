#!/usr/bin/env python3
"""Validate Converge gallery data and static site wiring."""

from __future__ import annotations

from pathlib import Path
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
GALLERY_PATH = ROOT / "gallery" / "examples.json"
SITE_ROOT = ROOT / "site"
REQUIRED_EXAMPLE_KEYS = (
    "id",
    "title",
    "eval_case",
    "user_input",
    "weak_pattern",
    "converge_pattern",
    "why_better",
    "proof_boundary",
)
REQUIRED_SITE_FILES = (
    "index.html",
    "styles.css",
    "app.js",
    "assets/protocol-map.svg",
)
REQUIRED_SITE_PHRASES = (
    "Converge Protocol",
    "IntentBench",
    "H0-H4",
    "before/after gallery",
    "python3 -m converge benchmark",
    "python3 -m converge doctor",
)
REQUIRED_DOC_LINKS = (
    "../docs/quickstart.md",
    "../docs/protocol.md",
    "../docs/install.md",
    "../docs/host-support.md",
    "../docs/evaluation.md",
    "../intentbench/manifest.json",
    "../gallery/examples.json",
)


def load_json(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def eval_case_names() -> set[str]:
    return {path.name for path in (ROOT / "skills" / "converge" / "eval-cases").glob("*.md")}


def validate_gallery() -> list[str]:
    errors: list[str] = []
    if not GALLERY_PATH.is_file():
        return [f"missing gallery data: {GALLERY_PATH.relative_to(ROOT)}"]
    try:
        data = load_json(GALLERY_PATH)
    except Exception as exc:
        return [f"invalid gallery JSON: {exc}"]

    if data.get("schema_version") != "1.0":
        errors.append("gallery/examples.json schema_version must be 1.0")
    examples = data.get("examples")
    if not isinstance(examples, list):
        return errors + ["gallery/examples.json examples must be a list"]
    if len(examples) < 8:
        errors.append("gallery should contain at least 8 examples")

    cases = eval_case_names()
    seen_ids: set[str] = set()
    for index, item in enumerate(examples, start=1):
        if not isinstance(item, dict):
            errors.append(f"gallery example {index} must be an object")
            continue
        for key in REQUIRED_EXAMPLE_KEYS:
            value = item.get(key)
            if not isinstance(value, str) or len(value.strip()) < 8:
                errors.append(f"gallery example {index} has weak or missing {key}")
        example_id = str(item.get("id", ""))
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", example_id):
            errors.append(f"gallery example {index} has invalid id: {example_id}")
        if example_id in seen_ids:
            errors.append(f"duplicate gallery id: {example_id}")
        seen_ids.add(example_id)
        eval_case = str(item.get("eval_case", ""))
        if eval_case not in cases:
            errors.append(f"gallery example {example_id or index} references unknown eval_case: {eval_case}")
        proof = str(item.get("proof_boundary", "")).lower()
        if "proof" not in proof and "h3" not in proof and "h1" not in proof and "not " not in proof:
            errors.append(f"gallery example {example_id or index} proof_boundary is not explicit enough")
    return errors


def validate_site() -> list[str]:
    errors: list[str] = []
    for rel in REQUIRED_SITE_FILES:
        if not (SITE_ROOT / rel).is_file():
            errors.append(f"missing site file: site/{rel}")
    if errors:
        return errors

    index = (SITE_ROOT / "index.html").read_text(encoding="utf-8")
    css = (SITE_ROOT / "styles.css").read_text(encoding="utf-8")
    app = (SITE_ROOT / "app.js").read_text(encoding="utf-8")
    svg = (SITE_ROOT / "assets" / "protocol-map.svg").read_text(encoding="utf-8")

    for phrase in REQUIRED_SITE_PHRASES:
        if phrase not in index:
            errors.append(f"site/index.html missing phrase: {phrase}")
    for rel in ("styles.css", "app.js", "assets/protocol-map.svg"):
        if rel not in index:
            errors.append(f"site/index.html does not reference {rel}")
    for href in REQUIRED_DOC_LINKS:
        haystack = app if href == "../gallery/examples.json" else index
        if href not in haystack:
            errors.append(f"site is missing required link/reference: {href}")
    if "../gallery/examples.json" not in app:
        errors.append("site/app.js must load ../gallery/examples.json")
    if "grid-template-columns" not in css or "@media (max-width: 900px)" not in css:
        errors.append("site/styles.css missing core responsive layout styles")
    if re.search(r"font-size:\s*[^;]*(vw|vh|vmin|vmax)", css):
        errors.append("site/styles.css must not scale font size with viewport units")
    if "<svg" not in svg or "Converge Protocol map" not in svg:
        errors.append("site/assets/protocol-map.svg must be an informative visual asset")
    if "innerHTML" in app:
        errors.append("site/app.js must render gallery data through DOM text nodes, not innerHTML")
    if re.search(r"letter-spacing:\s*-\d", css):
        errors.append("site/styles.css must not use negative letter spacing")
    return errors


def main() -> int:
    errors = validate_gallery() + validate_site()
    print("Converge gallery/site validation")
    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
