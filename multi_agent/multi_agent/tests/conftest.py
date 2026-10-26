import sys
from pathlib import Path

ROOT = str(Path(__file__).resolve().parents[2])

# Đưa thư mục chứa package multi_agent lên đầu sys.path
if ROOT in sys.path:
    sys.path.remove(ROOT)

sys.path.insert(0, ROOT)
