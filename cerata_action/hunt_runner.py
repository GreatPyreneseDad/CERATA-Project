"""Run the CERATA hunt protocol (tools/hunt.py) against a cloned prey repo."""

import contextlib
import importlib.util
import io
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Tuple

PERMISSIVE = {"MIT", "BSD-2-Clause", "BSD-3-Clause", "Apache-2.0", "ISC", "0BSD",
              "Unlicense", "Zlib", "PSF-2.0", "MPL-2.0", "BSL-1.0", "CC0-1.0"}
COPYLEFT = {"GPL-2.0", "GPL-3.0", "LGPL-2.1", "LGPL-3.0", "AGPL-3.0"}

_LICENSE_NAMES = ("license", "licence", "copying", "license.md", "license.txt",
                  "license.rst", "licence.md", "copying.md", "license-mit", "license.mit")


NOT_NEMATOCYST_DIRS = ("scripts/", "docs/", "doc/", "examples/", "example/", "benchmarks/", "benchmark/", "perf/",
                       "bench/", "tests/", "test/", "tools/release", "ci/", ".github/")


JS_EXT = (".ts", ".tsx", ".mts", ".js", ".jsx", ".mjs")
_JS_SKIP_PARTS = {"node_modules", "dist", "build", "out", "coverage", "vendor", ".next", "__tests__"}
_JS_FN = re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\*?\s+\w+"
                    r"|^\s*(?:export\s+)?(?:const|let)\s+\w+\s*(?::[^=]+)?=\s*(?:async\s*)?(?:\([^)]*\)|\w+)\s*(?::[^=]+)?=>",
                    re.M)
_JS_CLASS = re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+\w+", re.M)


def js_nematocysts(repo: Path, max_candidates: int = 40):
    """hunt.py reads Python only; this finds JS/TS candidates with the same scoring formula."""
    out = []
    for f in repo.rglob("*"):
        if not f.is_file() or not f.name.endswith(JS_EXT):
            continue
        rel = f.relative_to(repo)
        name = f.name.lower()
        if (set(rel.parts) & _JS_SKIP_PARTS or ".git" in rel.parts or name.endswith((".d.ts", ".min.js"))
                or re.search(r"\.(test|spec|stories|config)\.", name)):
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if len(text) > 300_000:
            continue
        fns, classes, lines = len(_JS_FN.findall(text)), len(_JS_CLASS.findall(text)), text.count("\n") + 1
        if fns + classes:
            out.append({"path": str(rel), "functions": fns, "classes": classes, "lines": lines,
                        "score": (fns * 2 + classes * 3) / max(lines / 100, 1)})
    out.sort(key=lambda x: x["score"], reverse=True)
    return out[:max_candidates]


def load_hunt_module(cerata_home: Path):
    """Import tools/hunt.py without its import-time chatter."""
    path = cerata_home / "tools" / "hunt.py"
    spec = importlib.util.spec_from_file_location("cerata_hunt", path)
    mod = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(mod)
    return mod


def clone(url: str, dest: Path, depth: int = 50) -> Tuple[bool, str]:
    if not url.startswith(("https://", "http://")):  # local fixture repos in tests
        url = str(Path(url).resolve())
    r = subprocess.run(
        ["git", "clone", "--depth", str(depth), "--quiet", "--no-tags", url, str(dest)],
        capture_output=True, text=True, timeout=300,
        env={"GIT_TERMINAL_PROMPT": "0", "PATH": "/usr/bin:/bin:/usr/local/bin"},
    )
    return r.returncode == 0, r.stderr.strip()


def find_license_file(repo: Path) -> Optional[Path]:
    for f in sorted(repo.iterdir()):
        if f.is_file() and f.name.lower() in _LICENSE_NAMES:
            return f
    for f in sorted(repo.iterdir()):
        if f.is_file() and f.name.lower().startswith(("license", "licence", "copying")):
            return f
    return None


def classify_license_text(text: str) -> str:
    t = " ".join(text.lower().split())
    if "gnu affero general public license" in t:
        return "AGPL-3.0"
    if "gnu lesser general public license" in t or "gnu library general public license" in t:
        return "LGPL-3.0" if "version 3" in t else "LGPL-2.1"
    if "gnu general public license" in t:
        return "GPL-3.0" if "version 3" in t else "GPL-2.0"
    if "mozilla public license" in t and "2.0" in t:
        return "MPL-2.0"
    if "apache license" in t and "version 2.0" in t:
        return "Apache-2.0"
    if "permission is hereby granted, free of charge" in t:
        return "MIT"
    if "redistribution and use in source and binary forms" in t:
        return "BSD-3-Clause" if ("neither the name" in t or "names of its contributors" in t) else "BSD-2-Clause"
    if "permission to use, copy, modify, and/or distribute this software" in t:
        return "ISC"
    if "this is free and unencumbered software released into the public domain" in t:
        return "Unlicense"
    if "boost software license" in t:
        return "BSL-1.0"
    if "python software foundation license" in t:
        return "PSF-2.0"
    return "UNKNOWN"


def license_verdict(spdx: str, allow_copyleft: bool) -> Tuple[bool, str]:
    base = spdx.replace("-only", "").replace("-or-later", "")
    if base in PERMISSIVE:
        extra = " (file-level copyleft: keep MPL headers on consumed files)" if base == "MPL-2.0" else ""
        return True, f"{spdx}: permissive, safe to consume with attribution{extra}"
    if base in COPYLEFT:
        if allow_copyleft:
            return True, f"{spdx}: copyleft. Consumption allowed by `allow-copyleft`; your obligations change"
        return False, f"{spdx}: copyleft. Consumption blocked (set `allow-copyleft: true` to override)"
    return False, f"{spdx}: license not recognised. Consumption blocked until a human verifies it"


def live_signals(info: Optional[Dict]) -> Dict:
    """Observed facts from the GitHub API. Reported beside the lens, never folded into it."""
    if not info:
        return {}
    pushed = info.get("pushed_at")
    days = None
    if pushed:
        dt = datetime.fromisoformat(pushed.replace("Z", "+00:00"))
        days = (datetime.now(timezone.utc) - dt).days
    lic = (info.get("license") or {}).get("spdx_id")
    return {
        "stars": info.get("stargazers_count"),
        "forks": info.get("forks_count"),
        "open_issues": info.get("open_issues_count"),
        "archived": info.get("archived"),
        "days_since_push": days,
        "api_license": lic if lic and lic != "NOASSERTION" else None,
        "description": (info.get("description") or "")[:200],
        "default_branch": info.get("default_branch"),
    }


def hunt(hunt_mod, prey_path: Path, url: str, info: Optional[Dict],
         allow_copyleft: bool) -> Dict:
    structure = hunt_mod.analyze_repo_structure(prey_path)
    quality = hunt_mod.analyze_code_quality(prey_path)
    coherence = hunt_mod.calculate_repo_coherence(structure, quality)
    found = hunt_mod.identify_nematocysts(prey_path, max_candidates=40) + js_nematocysts(prey_path)
    found.sort(key=lambda x: x["score"], reverse=True)
    nematocysts = [n for n in found
                   if not n["path"].lower().startswith(NOT_NEMATOCYST_DIRS)
                   and not n["path"].endswith(("conftest.py", "noxfile.py", "__main__.py"))][:15]
    viability = hunt_mod.determine_viability(coherence)

    lic_file = find_license_file(prey_path)
    spdx = classify_license_text(lic_file.read_text(errors="ignore")) if lic_file else "NONE"
    signals = live_signals(info)
    if spdx in ("UNKNOWN", "NONE") and signals.get("api_license"):
        spdx = signals["api_license"]
    consumable, lic_note = license_verdict(spdx, allow_copyleft)
    if signals.get("archived"):
        viability["warnings"].append("Archived upstream: fossil prey, no future fixes")

    head = subprocess.run(["git", "-C", str(prey_path), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    return {
        "url": url,
        "commit": head,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "structure": structure,
        "quality": quality,
        "coherence": coherence,
        "viability": viability,
        "nematocyst_candidates": nematocysts,
        "license": {"spdx": spdx, "file": lic_file.name if lic_file else None,
                    "consumable": consumable, "note": lic_note},
        "signals": signals,
    }
