"""Test configuration to ensure project root is importable."""
import sys
from pathlib import Path

# Prepend repo root so `import notif` works without editable install
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
