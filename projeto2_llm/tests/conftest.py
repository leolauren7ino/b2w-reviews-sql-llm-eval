import sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(P), str(P.parent)]
