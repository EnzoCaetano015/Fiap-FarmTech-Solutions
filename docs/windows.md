# Ambiente local Windows

Use Python 3.11 para o ambiente definitivo. O teste desta implementação foi realizado
também em Python 3.12 isolado. O Python global 3.14 não é o ambiente dos modelos.
Uma opção é instalar Python 3.11 pelo instalador oficial, sem substituir outras versões.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m streamlit run dashboard/src/dashboard.py
```

Para análise R, inclua a pasta `bin` da instalação existente no PATH da sessão:

```powershell
$env:Path = 'C:\Program Files\R\R-4.6.1\bin;' + $env:Path
.\.venv\Scripts\python.exe -m farmtech analise-r
```

A versão instalada foi encontrada nesse caminho durante a implementação. Ajuste-o
se a instalação mudar. O script usa somente R base, sem instalar pacotes adicionais.
Alternativamente, configure `FARMTECH_RSCRIPT=C:/Program Files/R/R-4.6.1/bin/Rscript.exe`
no `.env`; assim a dashboard encontra o executável sem alterar o PATH do Windows.

Configure Oracle no `.env` apenas se tiver acesso. Crie a tabela com
`sql/01_create_table.sql` **somente em um schema novo**. Os scripts históricos podem
ter operações destrutivas; não use scripts completos para recriar um banco já populado.
O importador integrado não executa DDL nem apaga dados. A conexão real depende
do servidor e da rede da faculdade/VPN quando aplicável.

```powershell
.\.venv\Scripts\python.exe -m farmtech oracle-importar
.\.venv\Scripts\python.exe -m farmtech oracle-consultar
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Terminal separado para monitoramento:

```powershell
.\.venv\Scripts\python.exe -m farmtech monitor
```

Sem ARN/credenciais AWS válidos, os alertas ficam pendentes e a falha é registrada.
Não há envio simulado apresentado como e-mail recebido.

## Inferência agrícola local em CPU

O treinamento fica no Colab. Para usar o bundle exportado no computador:

```powershell
.\.venv\Scripts\python.exe -m pip install torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -r requirements-visao.txt -c constraints-colab.txt
git clone --branch v7.0 --depth 1 https://github.com/ultralytics/yolov5.git .runtime/yolov5
.\.venv\Scripts\python.exe -m pip install -r .runtime/yolov5/requirements.txt -c constraints-colab.txt
# Extrair o bundle real em models/tomate antes de inferir.
.\.venv\Scripts\python.exe -m farmtech visao imagem.jpg --plot talhao-demo
```

Se `.runtime/yolov5` já existir, confira seu commit em vez de repetir o clone.


## Compilação do protótipo ESP32

A auditoria compilou o sketch preservado com Espressif32 6.9.0 e DHT 1.4.6,
fixados em `prototipo-ESP32/platformio.ini`. Instale PlatformIO em ambiente separado
e execute `python -m platformio run --project-dir prototipo-ESP32`.
No Windows, use um `PLATFORMIO_CORE_DIR` curto se encontrar erro de caminho longo.
Isso compila o firmware; não grava uma placa e não substitui a demonstração física.
