"""Make ``scripts/`` importable, as it is when a script is run directly."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
