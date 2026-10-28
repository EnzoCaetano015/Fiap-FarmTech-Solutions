"""Treinos GPU externos explícitos; exportação de bundle sem métricas fictícias."""
import argparse
import csv
import importlib.metadata
import json
import shutil
import subprocess
import sys
from time import perf_counter
from pathlib import Path
from . import CLASSES, sha256


def train(dataset, runtime, destination):
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError("Treinamento planejado para Colab GPU: GPU CUDA indisponível")
    dataset, runtime, destination = map(lambda p: Path(p).resolve(), (dataset, runtime, destination))
    if destination.exists():
        raise FileExistsError("Use uma pasta nova; não sobrescreva experimentos")
    manifest = json.loads((dataset / "manifest.json").read_text(encoding="utf-8"))
    head = subprocess.check_output(["git", "-C", str(runtime), "rev-parse", "HEAD"], text=True).strip()
    tag = subprocess.check_output(["git", "-C", str(runtime), "rev-parse", "v7.0^{commit}"], text=True).strip()
    if head != tag:
        raise ValueError("Runtime deve estar fixado no commit oficial v7.0")
    destination.mkdir(parents=True)
    summaries = []
    for epochs in (30, 60):
        name = f"tomate_{epochs}"
        command = [sys.executable, str(runtime / "train.py"), "--data", str(dataset / "data.yaml"),
                   "--weights", str(runtime / "yolov5s.pt"), "--img", "640", "--batch-size", "16",
                   "--epochs", str(epochs), "--seed", "42", "--patience", "0", "--workers", "2",
                   "--project", str(destination / "runs"), "--name", name]
        started = perf_counter()
        subprocess.run(command, cwd=runtime, check=True)
        training_seconds = perf_counter() - started
        run = destination / "runs" / name
        with (run / "results.csv").open() as f:
            rows = [{k.strip(): float(v) for k, v in row.items()} for row in csv.DictReader(f)]
        # best.pt é salvo pelo fitness oficial, dominado por mAP50:95; avaliar cada checkpoint
        # em validação evita inferir seu valor da época arredondada no results.csv.
        sys.path.insert(0, str(runtime))
        import val
        values, _, times = val.run(data=str(dataset / "data.yaml"), weights=str(run / "weights/best.pt"),
                                  task="val", imgsz=640, device="0", plots=False,
                                  project=destination / "validation_metrics", name=name)
        summaries.append({"epochs": epochs, "map50": float(values[2]), "map50_95": float(values[3]),
                          "training_seconds": training_seconds,
                          "weights": str(run / "weights/best.pt"), "history": rows,
                          "timing_ms": list(map(float, times))})
    selected = max(summaries, key=lambda r: (r["map50_95"], r["map50"], -r["epochs"]))
    (destination / "selection.json").write_text(json.dumps({"criterio": "map50_95 de validação, map50, menos épocas",
                "selected_epochs": selected["epochs"], "runs": summaries}, indent=2))
    import val
    values, class_maps, times = val.run(data=str(dataset / "data.yaml"), weights=selected["weights"],
                              task="test", imgsz=640, device="0", plots=True,
                              project=destination / "test", name="selected")
    bundle = destination / "bundle"
    bundle.mkdir()
    shutil.copy2(selected["weights"], bundle / "best.pt")
    shutil.copy2(destination / "selection.json", bundle / "selection.json")
    shutil.copy2(dataset / "manifest.json", bundle / "dataset_manifest.json")
    metrics = {"precision": float(values[0]), "recall": float(values[1]), "map50": float(values[2]),
               "map50_95": float(values[3]), "timing_ms": list(map(float, times))}
    metrics["map50_95_por_classe"] = dict(zip(CLASSES, map(float, class_maps)))
    versions = {name: importlib.metadata.version(name) for name in ("torch", "torchvision", "numpy", "pandas", "Pillow")}
    export = {"classes": CLASSES, "yolo_version": "v7.0", "yolo_commit": head,
              "weights_sha256": sha256(bundle / "best.pt"), "dataset_fingerprint": manifest["fingerprint"],
              "versions": versions, "selected_epochs": selected["epochs"], "test_metrics": metrics,
              "alert_confidence": .5, "device": torch.cuda.get_device_name(0)}
    (bundle / "manifest.json").write_text(json.dumps(export, indent=2, ensure_ascii=False), encoding="utf-8")
    shutil.make_archive(str(destination / "tomate_bundle"), "zip", bundle)
    print(json.dumps(export, indent=2, ensure_ascii=False))
    return export


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("dataset", "runtime", "destination"):
        parser.add_argument(name)
    train(**vars(parser.parse_args()))
