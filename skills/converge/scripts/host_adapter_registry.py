#!/usr/bin/env python3
"""Shared host adapter registry helpers for Converge skill scripts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
CURSOR_RULE_TEXT = """---
description: "Converge intent reconstruction. Use when the user asks to think through fuzzy work, clarify an idea, make a decision, draft a plan, evaluate a technical route, or explicitly invokes converge."
alwaysApply: false
---

# Converge - Owner-Mode Intent Reconstruction

Read `~/.cursor/skills/converge/SKILL.md` and follow that skill when Converge is relevant.

Use Converge to reconstruct intent, inspect accessible context, verify drift-prone claims when needed, make an owner recommendation, and produce the next usable reply, plan, decision, or artifact.

For simple direct tasks, use the skill's Universal Intent Guard briefly, then execute the task instead of adding ceremony.
"""


def load_registry(root: Path = ROOT) -> dict[str, Any]:
    path = root / "host-adapters.json"
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def host_entries(root: Path = ROOT) -> list[dict[str, Any]]:
    hosts = load_registry(root).get("hosts")
    if not isinstance(hosts, list):
        raise ValueError("host-adapters.json hosts must be a list")
    return [host for host in hosts if isinstance(host, dict)]


def install_targets(root: Path = ROOT) -> dict[str, Path]:
    targets: dict[str, Path] = {}
    for host in host_entries(root):
        install = host.get("install", {})
        if not isinstance(install, dict) or install.get("copy_skill") is not True:
            continue
        target_key = install.get("target_key")
        anchors = install.get("anchors", [])
        if not isinstance(target_key, str) or not isinstance(anchors, list) or not anchors:
            continue
        first_anchor = anchors[0]
        if isinstance(first_anchor, str):
            targets[target_key] = Path(first_anchor).expanduser()
    return targets


def parse_targets(value: str, targets: Mapping[str, Path]) -> list[str]:
    if value == "all":
        return list(targets)
    names = [item.strip() for item in value.split(",") if item.strip()]
    unknown = [name for name in names if name not in targets]
    if unknown:
        raise ValueError(f"unknown target(s): {', '.join(unknown)}")
    return names


def cursor_rule_path(root: Path = ROOT) -> Path | None:
    for host in host_entries(root):
        if host.get("host_id") != "cursor":
            continue
        install = host.get("install", {})
        if not isinstance(install, dict):
            continue
        bridge_files = install.get("bridge_files", [])
        if not isinstance(bridge_files, list):
            continue
        for bridge in bridge_files:
            if not isinstance(bridge, dict) or bridge.get("kind") != "cursor-rule":
                continue
            path = bridge.get("path")
            if isinstance(path, str):
                return Path(path).expanduser()
    return None
