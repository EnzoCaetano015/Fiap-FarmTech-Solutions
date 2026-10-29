from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from farmtech.services.iot import replay
def popular_banco(caminho_csv=None, modo_continuo=False):
    return replay(csv_path=caminho_csv, interval=1 if modo_continuo else 0)
if __name__ == "__main__":
    from farmtech.__main__ import main
    raise SystemExit(main(["iot", *sys.argv[1:]]))
