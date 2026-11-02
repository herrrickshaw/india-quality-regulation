"""Constants and helpers shared by the generator and verifier scripts.

Scripts are run as ``python3 scripts/<name>.py``, so ``scripts/`` is on
``sys.path`` and this module imports as ``_common``.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS = REPO_ROOT / "docs"

# (docs/ sub-directory, human heading) in the order they appear in every
# generated file (coverage table, compendium).
CATEGORY_ORDER = [
    ("apex-accreditation", "Apex & Accreditation Infrastructure"),
    ("bis-core", "Cross-Sector Statutory — BIS Core"),
    ("food-agriculture", "Food & Agriculture"),
    ("health-pharma", "Health, Pharma & AYUSH"),
    ("energy-safety-environment", "Energy, Safety & Environment"),
    ("telecom-electronics", "Telecom & Electronics"),
    ("textiles", "Textiles & Handicrafts"),
    ("ip-trademarks", "Origin & Trademarks"),
    ("legal-metrology", "Legal Metrology"),
    ("private-voluntary", "Private / Industry Voluntary Marks"),
]

H1_RE = re.compile(r"^# (.+)$", re.M)


def slugify(title: str) -> str:
    """Approximation of GitHub's heading-anchor algorithm."""
    s = title.lower()
    s = re.sub(r"[^\w\- ]+", "", s)
    s = s.strip().replace(" ", "-")
    s = re.sub(r"-+", "-", s)
    return s
