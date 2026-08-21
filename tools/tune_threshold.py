"""
tools/tune_threshold.py
-----------------------
Root-level wrapper script for scam_detector threshold tuning utility.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure workspace root and scam_detector are on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from scam_detector.tools.tune_threshold import main

if __name__ == "__main__":
    main()
