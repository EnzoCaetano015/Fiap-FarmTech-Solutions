# Implantação e demonstração no AWS Academy

## 1. Pré-condições verificáveis

Inicie o Learner Lab na conta da faculdade, leia suas instruções atuais e confira
regiões, serviços, tipos de instância e permissões. O ponto de partida é `us-east-1`,
mas a restrição real do laboratório prevalece. A Fase 5 documentou uma estimativa
de EC2/EBS; isso não prova que exista uma instância reutilizável.

Use credenciais temporárias da sessão em perfil do AWS CLI no seu computador,
incluindo session token, ou use o perfil de instância disponibilizado pelo laboratório
na EC2. Não as coloque no repositório, vídeo ou `.env` do projeto. Não crie usuários IAM.

```bash
python deploy/aws.py preflight --region us-east-1
```

O preflight consulta STS, regiões, instâncias, oferta t3.medium e tópicos SNS.
Ele não autoriza nem garante criação: registre recusas e confira as instruções do Lab.
Não há requisito de S3, Lambda, SageMaker ou Bedrock nesta arquitetura.

## 2. SNS

```bash
python deploy/aws.py sns --region us-east-1 --email SEU_EMAIL_AUTORIZADO
```

O comando cria/reutiliza `farmtech-alertas`, verifica assinaturas existentes e
solicita assinatura somente se necessário. Abra o e-mail e confirme a assinatura.
Guarde o ARN no `.env` como `FARMTECH_SNS_TOPIC_ARN`.
Os funcionários destinatários precisam autorizar e confirmar seus endereços.
Veja [assinatura SNS](https://docs.aws.amazon.com/sns/latest/api/API_Subscribe.html).

## 3. EC2

Na console do laboratório, configure:

- Ubuntu Server 22.04 LTS, x86_64, obtida do publisher oficial Canonical;
- t3.medium (4 GiB), 30 GB EBS gp3 criptografado;
- perfil de instância disponibilizado pelo Lab com acesso SNS efetivamente permitido;
- IMDSv2 obrigatório; chave SSH do grupo gerenciada fora do Git;
- subnet com saída para internet; Security Group com 22 e 8501 somente do IP /32 do apresentador.

```bash
python deploy/aws.py security-group --region us-east-1 --vpc-id VPC_DO_LAB --presenter-cidr SEU_IPV4/32
```

O comando cria um grupo novo e recusa modificar um grupo já existente. Não abre
portas para 0.0.0.0/0. Se o IP mudar, atualize conscientemente as regras na console.
Consulte [tipos EC2](https://aws.amazon.com/ec2/instance-types/general-purpose/)
e [credenciais pelo perfil de instância](https://docs.aws.amazon.com/sdkref/latest/guide/feature-imds-credentials.html).

Copie o projeto (sem `.git`, `.env` local, ambientes e dados privados) para
`/opt/farmtech`, com propriedade do usuário `ubuntu`. Pelo SSH:

```bash
sudo mkdir -p /opt/farmtech
sudo chown ubuntu:ubuntu /opt/farmtech
# Copiar/extrair FarmTech-Fase7.zip e colocar seu conteúdo nessa pasta.
cd /opt/farmtech
cp .env.example .env
nano .env
# Configurar SNS, Oracle se disponível e os caminhos do bundle.
bash deploy/install-ec2.sh
```

O instalador usa o Python padrão só para inicializar uv do PyPI e instala Python
3.11 isolado. Cria `.venv`, instala R e dependências, checkout YOLO oficial v7.0,
PyTorch CPU e dois serviços systemd. Não instala TensorFlow para inferência agrícola.
O código do YOLO e seus termos/licença precisam acompanhar o uso acadêmico.

Extraia o bundle do Colab em `/opt/farmtech/models/tomate`, contendo `best.pt` e
`manifest.json`. O checkout YOLO precisa corresponder ao commit do manifesto.
Carregue apenas pesos gerados e verificados pelo grupo.

```bash
sudo systemctl restart farmtech-dashboard farmtech-monitor
sudo systemctl --no-pager status farmtech-dashboard farmtech-monitor
sudo journalctl -u farmtech-monitor -n 50 --no-pager
```

Abra `http://IP_PUBLICO:8501` pelo IP autorizado. Para trafegar dados privados,
prefira túnel SSH: `ssh -L 8501:localhost:8501 ubuntu@IP_PUBLICO` e abra localhost.
O protótipo não inclui autenticação pública nem TLS; mantenha o acesso restrito.

## 4. Demonstração com evidências

1. Mostrar região, perfil da instância e assinatura confirmada sem expor credenciais.
2. Abrir dashboard EC2 e reproduzir CSV com horários atuais no talhão de demonstração.
3. Registrar evento, regra, status `published` e `MessageId`.
4. Mostrar o e-mail recebido com a ação sugerida (diferente do e-mail de confirmação).
5. Enviar uma imagem agrícola de demonstração; conferir detecção de doença >=0,50,
   evento visual e segundo e-mail. Se não houver detecção, registrar resultado inconclusivo.
6. Fechar a dashboard e provar pelo terminal que o monitor permanece ativo.
7. Repetir uma condição no mesmo talhão e conferir supressão durante 30 minutos.

Os arquivos em `docs/evidencias/` registram o que foi validado. Não marcar implantação,
treinamento ou e-mail como concluídos apenas porque o código ou ARN existem.

## 5. Operação e encerramento

Backups do estado operacional devem ser feitos com o monitor parado ou com a API
de backup SQLite; copiar só o arquivo principal durante escrita WAL pode perder dados.
O conteúdo operacional não deve ser versionado.

```bash
sudo systemctl stop farmtech-dashboard farmtech-monitor
```

Depois da apresentação, pare a EC2 na console e encerre a sessão do laboratório
conforme as instruções da faculdade. Confira volumes e recursos remanescentes.
Sessões podem encerrar instâncias e mudar IP público; confirme serviços e credenciais
após reinício. Não se assume operação contínua fora da sessão nem custo zero.
