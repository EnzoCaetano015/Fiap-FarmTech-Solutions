from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from farmtech.services.oracle import import_csv
if __name__ == "__main__":
    from farmtech.__main__ import main
    raise SystemExit(main(["oracle-importar", *sys.argv[1:]]))
