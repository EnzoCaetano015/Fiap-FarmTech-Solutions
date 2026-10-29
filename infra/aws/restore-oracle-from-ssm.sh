#!/bin/bash
set -euo pipefail
/usr/bin/python3 - <<'PY'
import boto3,json,os,pwd,tempfile
from pathlib import Path
values=json.loads(boto3.client('ssm',region_name='us-east-1').get_parameter(Name='/farmtech/fase7/oracle',WithDecryption=True)['Parameter']['Value'])
assert set(values)=={'ORACLE_USER','ORACLE_PASSWORD','ORACLE_DSN'}
path=Path('/opt/farmtech/.env')
original=path.read_text(encoding='utf-8')
lines=[line for line in original.splitlines() if line.split('=',1)[0] not in values]
lines.extend(key+'='+json.dumps(value,ensure_ascii=False) for key,value in values.items())
fd,name=tempfile.mkstemp(prefix='.env-',dir=path.parent)
with os.fdopen(fd,'w',encoding='utf-8') as stream:stream.write('\n'.join(lines)+'\n')
user=pwd.getpwnam('ubuntu')
os.chmod(name,0o600)
os.chown(name,user.pw_uid,user.pw_gid)
os.replace(name,path)
session=boto3.Session(region_name='us-east-1')
credentials=session.get_credentials()
print(json.dumps({'oracle_configured':True,'permissions_octal':oct(path.stat().st_mode&0o777),
                  'aws_credentials_provider':credentials.method,'secrets_printed':False}))
PY
