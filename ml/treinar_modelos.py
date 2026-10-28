from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from farmtech.services.preditivo.training import *  # Compatibilidade com a Fase 4.
if __name__ == "__main__":
    from farmtech.__main__ import main
    raise SystemExit(main(["treinar", *sys.argv[1:]]))
