"""Conversão PlantDoc. Nenhuma imagem é baixada ou métrica produzida ao importar."""
import argparse
import csv
import hashlib
import json
import random
import shutil
from collections import defaultdict
from pathlib import Path
from . import CLASSES, sha256

DISEASES = {"Tomato leaf late blight", "Tomato mold leaf", "Tomato leaf yellow virus",
            "Tomato leaf mosaic virus", "Tomato leaf bacterial spot", "Tomato Early blight leaf",
            "Tomato Septoria leaf spot"}
MAPPING = {"Tomato leaf": 0, **{name: 1 for name in DISEASES}}


def dhash(image):
    from PIL import Image
    pixels = list(image.convert("L").resize((9, 8), Image.Resampling.LANCZOS).getdata())
    value = 0
    for y in range(8):
        for x in range(8):
            value = (value << 1) | (pixels[y * 9 + x] > pixels[y * 9 + x + 1])
    return value


def prepare(source, destination):
    from PIL import Image
    source, destination = Path(source), Path(destination)
    if destination.exists():
        raise FileExistsError("Destino já existe: use nova pasta para preservar splits")
    records = []
    invalid = []
    for split in ("train", "test"):
        grouped = defaultdict(list)
        with (source / f"{split}_labels.csv").open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                grouped[row["filename"]].append(row)
        for name, annotations in sorted(grouped.items()):
            # Excluir imagens com caixas de classes não mapeadas: não tratá-las como fundo.
            if not annotations or any(row["class"] not in MAPPING for row in annotations):
                continue
            path = source / split.upper() / name
            if path.resolve().parent != (source / split.upper()).resolve():
                raise ValueError("Nome de imagem inválido no CSV")
            try:
                with Image.open(path) as img:
                    width, height = img.size
                    img.load()
                    if width < 10 or height < 10:
                        raise ValueError("Imagem pequena")
                    perceptual = dhash(img)
            except (OSError, ValueError) as exc:
                invalid.append({"imagem": name, "motivo": type(exc).__name__})
                continue
            boxes = []
            for row in annotations:
                if (int(row["width"]), int(row["height"])) != (width, height):
                    invalid.append({"imagem": name, "motivo": "dimensoes_divergentes_da_anotacao"})
                    break
                x1, y1, x2, y2 = [float(row[k]) for k in ("xmin", "ymin", "xmax", "ymax")]
                if not (0 <= x1 < x2 <= width and 0 <= y1 < y2 <= height):
                    invalid.append({"imagem": name, "motivo": "caixa_fora_da_imagem"})
                    break
                boxes.append((MAPPING[row["class"]], (x1+x2)/2/width, (y1+y2)/2/height,
                              (x2-x1)/width, (y2-y1)/height))
            if len(boxes) != len(annotations):
                continue
            records.append({"path": path, "original": annotations[0].get("original_filename", name), "origin": split, "hash": sha256(path),
                            "dhash": perceptual, "boxes": boxes})
    # Componentes conexos por SHA ou distância dHash <=4. Toda derivação candidata fica junta.
    parents = list(range(len(records)))
    def find(i):
        while parents[i] != i:
            parents[i] = parents[parents[i]]
            i = parents[i]
        return i
    for i, left in enumerate(records):
        for j in range(i):
            right = records[j]
            if left["hash"] == right["hash"] or (left["dhash"] ^ right["dhash"]).bit_count() <= 4:
                parents[find(i)] = find(j)
    test_groups = {find(i) for i, row in enumerate(records) if row["origin"] == "test"}
    train_groups = sorted({find(i) for i, row in enumerate(records)
                           if row["origin"] == "train" and find(i) not in test_groups})
    if len(train_groups) < 5:
        raise ValueError("Grupos insuficientes para treino/validação")
    # Divisão por grupo, sem usar métricas ou resultados do teste.
    random.Random(42).shuffle(train_groups)
    validation = set(train_groups[:max(1, round(len(train_groups)*.2))])
    exported = []
    excluded = list(invalid)
    seen_hash = set()
    for i, row in enumerate(records):
        group = find(i)
        if row["origin"] == "train" and group in test_groups:
            excluded.append({"imagem": row["path"].name, "motivo": "sobreposicao_com_teste"})
            continue
        split = "test" if row["origin"] == "test" else ("val" if group in validation else "train")
        if row["hash"] in seen_hash:
            excluded.append({"imagem": row["path"].name, "motivo": "duplicata_exata"})
            continue
        seen_hash.add(row["hash"])
        exported.append({**row, "split": split, "group": group})
    for split in ("train", "val", "test"):
        classes = {box[0] for row in exported if row["split"] == split for box in row["boxes"]}
        if classes != {0, 1}:
            raise ValueError(f"Split {split} sem ambas as classes")
    destination.mkdir(parents=True)
    provenance = []
    for row in exported:
        split = row["split"]
        image_dir, label_dir = destination / split / "images", destination / split / "labels"
        image_dir.mkdir(parents=True, exist_ok=True)
        label_dir.mkdir(parents=True, exist_ok=True)
        # As caixas foram verificadas na matriz original de pixels. Remover EXIF
        # sem girar a matriz impede cv2/YOLO de girar a foto sem girar os labels.
        name = row["hash"] + ".jpg"
        with Image.open(row["path"]) as source_image:
            source_image.convert("RGB").save(image_dir / name, "JPEG", quality=95, exif=b"")
        (label_dir / f"{row['hash']}.txt").write_text("\n".join(
            f"{box[0]} " + " ".join(f"{v:.8f}" for v in box[1:]) for box in row["boxes"]) + "\n")
        provenance.append({"original": row["original"], "origem": row["origin"], "split": split,
                           "sha256": row["hash"], "dhash": str(row["dhash"]), "grupo": row["group"],
                           "export_sha256": sha256(image_dir / name),
                           "classes": sorted({b[0] for b in row["boxes"]})})
    yaml = f"path: {json.dumps(str(destination.resolve()))}\ntrain: train/images\nval: val/images\ntest: test/images\nnames: {json.dumps(CLASSES)}\n"
    (destination / "data.yaml").write_text(yaml, encoding="utf-8")
    fingerprint = hashlib.sha256(json.dumps(provenance, sort_keys=True).encode()).hexdigest()
    metadata = {"fonte": "https://github.com/pratikkayal/PlantDoc-Object-Detection-Dataset",
                "licenca": "CC-BY-4.0; preservar atribuições e limitações das imagens originais",
                "seed": 42, "mapping": MAPPING, "fingerprint": fingerprint,
                "preprocessing": "RGB JPEG quality95; matriz original de pixels; EXIF removido sem rotação",
                "imagens": provenance, "excluidas": excluded,
                "observacao": "dHash sinaliza derivações; revisão visual de candidatos ainda é necessária"}
    if (source / "source.json").is_file():
        metadata["revisao_fonte"] = json.loads((source / "source.json").read_text())
    groups = defaultdict(list)
    for i, record in enumerate(records):
        groups[find(i)].append({"imagem": record["original"], "origem": record["origin"], "sha256": record["hash"]})
    metadata["grupos_similares_para_revisao"] = [members for members in groups.values() if len(members) > 1]
    (destination / "manifest.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    return metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("destination")
    args = parser.parse_args()
    result = prepare(args.source, args.destination)
    print(json.dumps({"fingerprint": result["fingerprint"], "imagens": len(result["imagens"])}, indent=2))
