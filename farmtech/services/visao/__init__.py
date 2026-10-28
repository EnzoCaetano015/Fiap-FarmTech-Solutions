"""Inferência apenas com bundle agrícola explícito e YOLOv5 v7.0 local."""
import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from ...config import ROOT, state_dir
from ...storage import add_event

CLASSES = ["folha_saudavel", "folha_com_sinais_de_doenca"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def infer(image, plot="talhao-demo", bundle=None):
    if not str(plot).strip():
        raise ValueError("Talhão é obrigatório")
    bundle = Path(bundle or os.getenv("FARMTECH_VISION_BUNDLE", ROOT / "models/tomate"))
    manifest_path = bundle / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError("Detector agrícola indisponível: exporte o bundle real no Colab e configure FARMTECH_VISION_BUNDLE")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("classes") != CLASSES or manifest.get("yolo_version") != "v7.0":
        raise ValueError("Bundle incompatível: classes agrícolas ou versão incorretas")
    weights = bundle / "best.pt"
    if not weights.is_file() or sha256(weights) != manifest.get("weights_sha256"):
        raise ValueError("Checkpoint ausente ou SHA-256 divergente")
    from PIL import Image, ImageOps, UnidentifiedImageError
    try:
        with Image.open(image) as source:
            source.verify()
        with Image.open(image) as source:
            rgb = ImageOps.exif_transpose(source).convert("RGB")
            rgb.thumbnail((1920, 1920))
            rgb.info.clear()
    except (OSError, ValueError, UnidentifiedImageError, Image.DecompressionBombError) as exc:
        raise ValueError("Imagem inválida ou ilegível; envie um arquivo PNG ou JPEG válido") from exc
    runtime = Path(os.getenv("FARMTECH_YOLO_RUNTIME", ROOT / ".runtime/yolov5"))
    if not (runtime / "hubconf.py").is_file():
        raise FileNotFoundError("Runtime YOLO ausente: prepare o checkout oficial v7.0 conforme docs/colab.md")
    import subprocess
    revision = subprocess.check_output(["git", "-C", str(runtime), "rev-parse", "HEAD"], text=True).strip()
    if revision != manifest.get("yolo_commit"):
        raise ValueError("Runtime YOLO divergente do commit registrado no treinamento")
    import numpy as np
    import torch
    torch.set_num_threads(2)
    # Pesos são código serializado: carregar somente os gerados/verificados pelo grupo.
    model = torch.hub.load(str(runtime), "custom", path=str(weights), source="local", device="cpu")
    names = list(model.names.values()) if isinstance(model.names, dict) else list(model.names)
    if names != CLASSES:
        raise ValueError("Classes internas do checkpoint não correspondem ao manifesto")
    model.conf = .25
    model.iou = .45
    identifier = uuid.uuid4().hex
    output = state_dir() / "visao" / identifier
    output.mkdir(parents=True)
    try:
        # PNG preserva exatamente os pixels enviados ao modelo, sem nova perda JPEG.
        rgb.save(output / "entrada.png")
        with torch.inference_mode():
            results = model(np.array(rgb, copy=True), size=640)
        detections = [{"classe": CLASSES[int(row[5])], "confianca": float(row[4]),
                       "caixa_xyxy": [float(x) for x in row[:4]]} for row in results.xyxy[0].cpu().tolist()]
        Image.fromarray(results.render()[0]).save(output / "anotada.jpg")
    finally:
        rgb.close()
    payload = {"deteccoes": detections, "imagem": str(output / "entrada.png"),
               "imagem_sha256": sha256(output / "entrada.png"), "imagem_original_sha256": sha256(image),
               "pesos_sha256": manifest["weights_sha256"],
               "resultado": "Detecções observadas" if detections else "Inconclusivo: nenhuma detecção",
               "simulado": False}
    stamp = datetime.now(timezone.utc).isoformat()
    event_id = add_event("visao", plot, stamp, payload, identifier)
    (output / "resultado.json").write_text(json.dumps({**payload, "evento": event_id}, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"dados": {**payload, "evento": event_id}, "arquivos": [str(p) for p in output.iterdir()]}
