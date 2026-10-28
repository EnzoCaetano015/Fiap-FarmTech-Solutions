"""Baixa apenas o recorte de tomate dos autores, em revisão Git fixa por download."""
import csv
import io
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import quote
from .dataset import MAPPING


def fetch(destination):
    import requests
    destination = Path(destination)
    if destination.exists():
        raise FileExistsError("Use uma pasta nova para o download PlantDoc")
    repo = "pratikkayal/PlantDoc-Object-Detection-Dataset"
    response = requests.get(f"https://api.github.com/repos/{repo}/commits/master", timeout=30)
    response.raise_for_status()
    revision = response.json()["sha"]
    base = f"https://raw.githubusercontent.com/{repo}/{revision}"
    jobs = []
    destination.mkdir(parents=True)
    for split in ("train", "test"):
        response = requests.get(f"{base}/{split}_labels.csv", timeout=30)
        response.raise_for_status()
        rows = list(csv.DictReader(io.StringIO(response.text)))
        names = {row["filename"]: hashlib.sha256(row["filename"].encode()).hexdigest() + ".jpg" for row in rows}
        # URLs originais podem conter '?' e nomes longos, inválidos no Windows.
        # CSV local aponta para nomes portáveis, mantendo a origem em outra coluna.
        with (destination / f"{split}_labels.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[*rows[0], "original_filename"])
            writer.writeheader()
            for row in rows:
                writer.writerow({**row, "filename": names[row["filename"]], "original_filename": row["filename"]})
        filenames = {row["filename"] for row in rows if row["class"] in MAPPING}
        rejected = {row["filename"] for row in rows if row["class"] not in MAPPING}
        folder = destination / split.upper()
        folder.mkdir()
        for name in sorted(filenames - rejected):
            if Path(name).name != name:
                raise ValueError("Nome de arquivo inválido")
            jobs.append((f"{base}/{split.upper()}/{quote(name, safe='')}", folder / names[name]))
    def download(job):
        url, path = job
        for attempt in range(3):
            try:
                answer = requests.get(url, timeout=60)
                answer.raise_for_status()
                path.write_bytes(answer.content)
                return
            except requests.RequestException:
                if attempt == 2:
                    raise
    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(download, jobs))
    metadata = {"repository": repo, "commit": revision, "images": len(jobs)}
    (destination / "source.json").write_text(json.dumps(metadata, indent=2))
    return metadata


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("destination")
    print(json.dumps(fetch(parser.parse_args().destination), indent=2))
