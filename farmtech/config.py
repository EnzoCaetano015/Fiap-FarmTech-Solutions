from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]


def state_dir():
    path = Path(os.getenv("FARMTECH_STATE_DIR", ROOT / ".runtime"))
    path.mkdir(parents=True, exist_ok=True)
    return path


def initialize_environment():
    try:
        from dotenv import dotenv_values
        # Variáveis reais do ambiente têm precedência. Campos inicialmente vazios
        # podem ser preenchidos no .env enquanto a dashboard já está aberta.
        for key, value in dotenv_values(ROOT / ".env").items():
            if value and not os.getenv(key):
                os.environ[key] = value
    except ImportError:
        pass
