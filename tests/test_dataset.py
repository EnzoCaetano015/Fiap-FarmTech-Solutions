import csv
import json
from pathlib import Path
import tempfile
import unittest


class DatasetTest(unittest.TestCase):
    def test_grouped_conversion_and_invalid_annotations(self):
        try:
            from PIL import Image
            from farmtech.services.visao.dataset import prepare
        except ImportError:
            self.skipTest("Instale requirements-visao para validar imagens")
        import random
        rng = random.Random(42)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"
            for split, count in (("train", 40), ("test", 8)):
                (source / split.upper()).mkdir(parents=True)
                rows = []
                for i in range(count):
                    name = f"{split}_{i}.png"
                    image = Image.new("RGB", (32, 32))
                    image.putdata([(rng.randrange(256), rng.randrange(256), rng.randrange(256)) for _ in range(1024)])
                    if i == 2:
                        exif = Image.Exif()
                        exif[274] = 6
                        image.save(source / split.upper() / name, exif=exif)
                    else:
                        image.save(source / split.upper() / name)
                    rows.append([name, 32, 32, "Tomato leaf" if i % 2 else "Tomato Early blight leaf", 1, 1, 30, 30])
                if split == "train":
                    # Copiar uma imagem de teste não é necessário: duplicata interna deve ficar no mesmo grupo.
                    image = Image.open(source / "TRAIN/train_0.png")
                    image.save(source / "TRAIN/duplicate.png")
                    image.close()
                    rows.append(["duplicate.png", 32, 32, "Tomato Early blight leaf", 1, 1, 30, 30])
                    rows.append(["train_1.png", 64, 64, "Tomato leaf", 1, 1, 30, 30])
                with (source / f"{split}_labels.csv").open("w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["filename", "width", "height", "class", "xmin", "ymin", "xmax", "ymax"])
                    writer.writerows(rows)
            destination = Path(directory) / "yolo"
            manifest = prepare(source, destination)
            groups = {}
            for record in manifest["imagens"]:
                groups.setdefault(record["grupo"], set()).add(record["split"])
            self.assertTrue(all(len(splits) == 1 for splits in groups.values()))
            self.assertIn("dimensoes_divergentes_da_anotacao", {r["motivo"] for r in manifest["excluidas"]})
            self.assertIn("duplicata_exata", {r["motivo"] for r in manifest["excluidas"]})
            for image in destination.glob("*/images/*.jpg"):
                with Image.open(image) as exported:
                    self.assertEqual(exported.getexif().get(274, 1), 1)
                    self.assertEqual(exported.size, (32, 32))
            self.assertTrue(all("export_sha256" in r for r in manifest["imagens"]))
            for label in destination.rglob("*.txt"):
                for line in label.read_text().splitlines():
                    values = line.split()
                    self.assertIn(values[0], {"0", "1"})
                    self.assertTrue(all(0 < float(x) <= 1 for x in values[1:]))
            with self.assertRaises(FileExistsError):
                prepare(source, destination)
