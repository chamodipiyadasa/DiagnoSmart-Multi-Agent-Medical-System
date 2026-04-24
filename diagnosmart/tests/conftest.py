"""Test configuration for package import path setup."""

from __future__ import annotations

import sys
from pathlib import Path

# Add repository root to Python path so `import diagnosmart` works in tests.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
