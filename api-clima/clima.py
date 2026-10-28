from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from farmtech.services.inicial import weather
def obter_nivel_chuva(latitude, longitude):
    return weather(latitude, longitude)["dados"]["nivel_chuva"]
def descrever_nivel(nivel):
    return {0: "SEM CHUVA", 1: "CHUVA FRACA/MODERADA", 2: "CHUVA FORTE"}.get(nivel, "PREVISÃO INDISPONÍVEL")
if __name__ == "__main__":
    from farmtech.__main__ import main
    raise SystemExit(main(["clima", *sys.argv[1:]]))
