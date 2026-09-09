"""Repository paths shared by every script in the package.

ROOT is the repository root; DATA, RESULTS, DOCS and PILOTS hang off it.  Importing this module also puts
src/ on sys.path so `from client_async import ...` resolves from anywhere.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"
DOCS = ROOT / "docs"
PILOTS = ROOT / "pilots"
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
