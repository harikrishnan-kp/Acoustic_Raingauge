"""
Root-level pytest conftest.

Ensures the project root is on sys.path so that import modules correctly no matter
which directory ``pytest`` is invoked from (repo root, ``test/``, or an
IDE test runner with a different working directory).
"""

import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
