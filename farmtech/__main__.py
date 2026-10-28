import argparse
import json
import sys
from .operations import execute


def parser():
    root = argparse.ArgumentParser(description="FarmTech Solutions — Fase 7")
    subs = root.add_subparsers(dest="service", required=True)
    area = subs.add_parser("area")
    area.add_argument("--shape", choices=["retangulo", "circulo"], default="retangulo")
    for name in ("length", "width", "radius"):
        area.add_argument(f"--{name}", type=float, default=1)
    area.add_argument("--dose", type=float, default=0, help="kg por hectare")
    analysis = subs.add_parser("analise-r")
    analysis.add_argument("--csv-path")
    climate = subs.add_parser("clima")
    climate.add_argument("--latitude", type=float, default=-23.55)
    climate.add_argument("--longitude", type=float, default=-46.63)
    iot = subs.add_parser("iot")
    iot.add_argument("--csv-path")
    iot.add_argument("--plot", default="talhao-demo")
    iot.add_argument("--interval", type=float, default=1)
    iot.add_argument("--live-time", action="store_true", help="Gerar uma nova simulação com horário atual")
    oracle = subs.add_parser("oracle-importar")
    oracle.add_argument("--csv-path")
    query = subs.add_parser("oracle-consultar")
    query.add_argument("--limit", type=int, default=100)
    subs.add_parser("treinar")
    vision = subs.add_parser("visao")
    vision.add_argument("image")
    vision.add_argument("--plot", default="talhao-demo")
    vision.add_argument("--bundle")
    for command in ("alertas", "monitor-uma-vez"):
        subs.add_parser(command)
    monitor = subs.add_parser("monitor")
    monitor.add_argument("--interval", type=float, default=10)
    return root


def main(argv=None):
    # JSON da CLI também deve ser UTF-8 quando stdout é redirecionado no Windows.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    args = vars(parser().parse_args(argv))
    service = args.pop("service")
    if service == "monitor":
        from .services.alertas import monitor
        try:
            monitor(**args)
        except KeyboardInterrupt:
            return 0
    else:
        record = execute(service, **args)
        print(json.dumps(record, ensure_ascii=False, indent=2, default=str))
        return 0 if record["sucesso"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
