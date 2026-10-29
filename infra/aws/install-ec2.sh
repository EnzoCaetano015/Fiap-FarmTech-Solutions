#!/usr/bin/env bash
set -euo pipefail
# Executar como ubuntu em /opt/farmtech após copiar o projeto e configurar .env.
cd /opt/farmtech
test -f .env || { echo 'Crie .env com as configurações e ARN do tópico SNS'; exit 1; }
sudo apt-get update
sudo apt-get install -y python3 python3-venv r-base git libgl1 libglib2.0-0
# Ubuntu 22.04 fornece Python 3.10. Instalar 3.11 isolado via uv do PyPI.
python3 -m venv .bootstrap
.bootstrap/bin/python -m pip install 'uv>=0.8,<1'
.bootstrap/bin/uv python install 3.11
.bootstrap/bin/uv venv --python 3.11 --seed .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
# PyTorch CPU economiza disco e memória na EC2. Não treinar nesta instância.
.venv/bin/python -m pip install torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cpu
.venv/bin/python -m pip install -r requirements/visao.txt -c requirements/constraints-colab.txt
mkdir -p .runtime
if [ ! -d .runtime/yolov5 ]; then
  git clone --branch v7.0 --depth 1 https://github.com/ultralytics/yolov5.git .runtime/yolov5
fi
YOLOv5_AUTOINSTALL=false .venv/bin/python -m pip install -r .runtime/yolov5/requirements.txt -c requirements/constraints-colab.txt
sudo install -d -o ubuntu -g ubuntu -m 700 /var/lib/farmtech
chmod 600 .env
sudo install -m 644 infra/aws/farmtech-dashboard.service /etc/systemd/system/
sudo install -m 644 infra/aws/farmtech-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now farmtech-dashboard farmtech-monitor
sudo systemctl --no-pager status farmtech-dashboard farmtech-monitor
