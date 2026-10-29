#!/bin/bash
set -euo pipefail
test -f /opt/farmtech/.runtime/install-complete
systemctl is-active farmtech-dashboard farmtech-monitor
sudo -u ubuntu -H bash <<'BASH'
set -euo pipefail
cd /opt/farmtech
export YOLOv5_AUTOINSTALL=false
mkdir -p /var/lib/farmtech/evidencias
.venv/bin/python -m pip check
.venv/bin/python -m unittest discover -s tests -v > /var/lib/farmtech/evidencias/testes-linux.txt 2>&1
tail -n 6 /var/lib/farmtech/evidencias/testes-linux.txt
.venv/bin/python - <<'PY'
import hashlib,json,math,os,subprocess,sys,tempfile
from pathlib import Path
import boto3,joblib,pandas as pd,requests
from farmtech.config import initialize_environment
initialize_environment()
report={'platform':sys.platform,'python':sys.version.split()[0],'checks':{}}
def run(name,callback):
    try:
        data=callback()
        report['checks'][name]={'ok':True,'data':data}
    except Exception as exc:
        report['checks'][name]={'ok':False,'error_type':type(exc).__name__}
def operation(name,**kwargs):
    from farmtech.operations import execute
    result=execute(name,**kwargs)
    assert result['sucesso'],result['erro']
    assert all(Path(p).is_file() and Path(p).stat().st_size>0 for p in result['arquivos'])
    return result['dados']
def oracle():
    first=operation('oracle-importar')
    second=operation('oracle-importar')
    data=operation('oracle-consultar',limit=100)
    assert first['inseridos']==second['inseridos']==0 and len(data)==10
    return {'first':first,'second':second,'rows':len(data)}
def predictions():
    from dashboard.paineis import FEATURES,TARGETS
    frame=pd.read_csv('data/sensores/treino_sintetico.csv')[FEATURES].iloc[:1]
    values={target:float(joblib.load(f'models/preditivo/modelo_{target}.joblib').predict(frame)[0]) for target in TARGETS}
    assert all(math.isfinite(value) for value in values.values())
    return {'synthetic':True,'predictions':values}
def rscript():
    from farmtech.operations import execute
    result=execute('analise-r')
    assert result['sucesso'] and len(result['arquivos'])==2
    return {'files':result['arquivos']}
def models():
    from farmtech.services.visao import sha256
    manifest=json.loads(Path('models/tomate/manifest.json').read_text())
    commit=subprocess.check_output(['git','-C','.runtime/yolov5','rev-parse','HEAD'],text=True).strip()
    assert commit==manifest['yolo_commit']
    assert sha256(Path('models/tomate/best.pt'))==manifest['weights_sha256']
    import torch,torchvision
    assert torch.__version__.startswith('2.5.1') and not torch.cuda.is_available()
    return {'torch':torch.__version__,'yolo_commit':commit,'weights_sha256':manifest['weights_sha256']}
with tempfile.TemporaryDirectory() as directory:
    os.environ['FARMTECH_STATE_DIR']=directory
    run('area',lambda:operation('area',length=100,width=200,dose=12))
    run('R',rscript)
    run('weather',lambda:operation('clima'))
    run('oracle',oracle)
    run('predictions',predictions)
    run('bundle_cpu',models)
    run('http_local',lambda:{'status':requests.get('http://127.0.0.1:8501/_stcore/health',timeout=10).status_code})
    from streamlit.testing.v1 import AppTest
    def dashboard():
        app=AppTest.from_file('dashboard/app.py',default_timeout=60).run()
        assert not app.exception and len(app.tabs)==6
        app.button(key='action_oracle-consultar').click().run()
        assert not app.exception and app.session_state['result_oracle-consultar']['sucesso']
        return {'tabs':[t.label for t in app.tabs],'oracle_rows':len(app.session_state['result_oracle-consultar']['dados'])}
    run('dashboard',dashboard)
credentials=boto3.Session().get_credentials()
report['aws_credentials_provider']=credentials.method
report['all_checks_passed']=all(item['ok'] for item in report['checks'].values())
Path('/var/lib/farmtech/evidencias/servicos-linux.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(report,indent=2,ensure_ascii=False))
if not report['all_checks_passed']:sys.exit(1)
PY
BASH
