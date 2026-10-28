import csv
import math
import os
import shutil
import subprocess
import uuid
from pathlib import Path
from datetime import datetime, timezone
from ...config import ROOT, state_dir


def positive(value, name, allow_zero=False):
    value = float(value)
    if not math.isfinite(value) or (value < 0 if allow_zero else value <= 0):
        raise ValueError(f"{name}: informe um número {'não negativo' if allow_zero else 'positivo'} finito")
    return value


def area(shape="retangulo", length=1, width=1, radius=1, dose=0):
    dose = positive(dose, "Dose", allow_zero=True)
    if shape == "retangulo":
        square_meters = positive(length, "Comprimento") * positive(width, "Largura")
    elif shape == "circulo":
        square_meters = math.pi * positive(radius, "Raio") ** 2
    else:
        raise ValueError("Formato deve ser retangulo ou circulo")
    if not math.isfinite(square_meters) or not math.isfinite(square_meters / 10000 * dose):
        raise ValueError("Dimensões ou dose excedem o limite numérico")
    record = {"data_hora": datetime.now(timezone.utc).isoformat(), "formato": shape,
              "area_m2": square_meters, "area_ha": square_meters / 10000,
              "dose_kg_ha": dose, "insumo_kg": square_meters / 10000 * dose}
    path = state_dir() / f"area_{uuid.uuid4().hex}.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=record)
        writer.writeheader()
        writer.writerow(record)
    return {"dados": record, "arquivos": [str(path)]}


def analysis_r(csv_path=None):
    configured = os.getenv("FARMTECH_RSCRIPT")
    exe = configured if configured and Path(configured).is_file() else shutil.which("Rscript")
    if not exe:
        raise RuntimeError("Rscript indisponível. Instale R e inclua Rscript no PATH.")
    output = state_dir() / f"analise_r_{uuid.uuid4().hex}"
    output.mkdir()
    command = [exe, "--vanilla", str(ROOT / "farmtech/services/inicial/analise.R"),
               str(csv_path or ROOT / "data/sensores_fase2.csv"), str(output)]
    result = subprocess.run(command, capture_output=True, text=True, timeout=120, check=True)
    return {"dados": {"saida": result.stdout}, "arquivos": [str(p) for p in output.iterdir()]}


def weather(latitude=-23.55, longitude=-46.63):
    latitude, longitude = float(latitude), float(longitude)
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        raise ValueError("Coordenadas inválidas")
    import requests
    try:
        response = requests.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": latitude, "longitude": longitude, "hourly": "rain,precipitation_probability",
            "forecast_days": 1, "timezone": "auto"}, timeout=10)
        response.raise_for_status()
        hourly = response.json()["hourly"]
        rain = [float(v) for v in hourly["rain"] if v is not None]
        probability = [float(v) for v in hourly["precipitation_probability"] if v is not None]
        if not rain or not probability or not all(math.isfinite(v) for v in rain + probability):
            raise ValueError("Resposta climática incompleta")
        level = 2 if max(rain) >= 5 or max(probability) >= 70 else (
            1 if max(rain) >= 1 or max(probability) >= 40 else 0)
    except (requests.RequestException, KeyError, TypeError, ValueError) as exc:
        raise RuntimeError("Previsão indisponível: não foi possível consultar dados climáticos válidos") from exc
    return {"dados": {"nivel_chuva": level, "descricao": ["Sem chuva", "Chuva fraca/moderada", "Chuva forte"][level]}}
