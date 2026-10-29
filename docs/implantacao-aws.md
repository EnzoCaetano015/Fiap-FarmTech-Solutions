# FarmTech — implantação AWS comprovada

**Concluída e validada em 28/10/2026**, no AWS Academy, região `us-east-1`.
Dashboard: [abrir sistema](http://54.166.136.107:8501).
O acesso está restrito ao IP do apresentador nas portas 22 e 8501; outro IP precisa
de atualização explícita das regras `/32`. Não há abertura pública irrestrita.

## Recursos e instalação

| Item | Configuração efetiva |
|---|---|
| EC2 | `i-09a66c2f286224171` · Ubuntu 22.04 LTS · `t3.medium` |
| AMI | `ami-033ea4ff4a9c726dc` · publisher Canonical `099720109477` |
| EBS | 30 GB `gp3`, criptografado; verificações EC2/sistema/EBS aprovadas |
| Security Group | `sg-017cf11ead242b775` · SSH/dashboard somente IPv4 `/32` |
| Credenciais AWS na instância | `LabInstanceProfile` / `LabRole`, provedor SDK `iam-role`, IMDSv2 obrigatório |
| SNS | `arn:aws:sns:us-east-1:063386412529:farmtech-alertas` · Standard · assinatura de e-mail confirmada |
| Runtime | Python 3.11.18, R 4.1.2, PyTorch 2.5.1+cpu, sklearn 1.8.0, Streamlit 1.49.1 |
| Serviços | `farmtech-dashboard` e `farmtech-monitor`: ativos e habilitados no systemd |
| Estado operacional | `/var/lib/farmtech/operacao.sqlite3`, separado de Oracle |

Instalação automatizada por cloud-init, com pacote SHA-256 conferido e administração
por SSM. O pacote de instalação trafegou por bucket privado, com bloqueio de acesso
público, SSE-S3 e expiração de sete dias para os artefatos. A aplicação executa com
os arquivos no EBS e não depende desse bucket durante a operação. Não foram criados
usuários IAM, novas funções IAM, chaves AWS persistentes ou NAT Gateway.

As três configurações Oracle foram enviadas somente após autorização explícita do
usuário, para `SecureString /farmtech/fase7/oracle`. A instância as recuperou pelo
perfil IAM e gravou `.env` com permissão `600`. Credenciais não acompanham o pacote,
o Git, os logs de evidência ou o código de inicialização. O parameter deve ser
tratado como segredo; não mostrar seu conteúdo em gravações.

## Funcionamento comprovado na EC2

- **43 testes passaram no Linux**, além dos 43 anteriores no Windows e dos 43 em
  instalação limpa. `pip check` também passou.
- Área de 100×200 m: 2 ha; dose de 12 kg/ha: 24 kg. CSV e serviço R executados.
- API climática real acessível. Oracle real retornou 10 leituras; duas importações
  repetidas inseriram zero e não apagaram dados. Consulta pela dashboard passou.
- Três modelos preditivos carregaram e produziram valores finitos; dados/alvos
  sintéticos continuam identificados. Não foram iniciados treinamentos na EC2.
- Bundle agrícola e commit YOLO conferidos; inferência CPU gerou imagem anotada
  com confiança de **0,6493655443** para sinais de doença no exemplo demonstrativo.
- HTTP interno e externo: **200 / ok**. Chrome carregou as seis abas e mostrou
  as duas leituras simuladas do talhão `talhao-aws-demo` e os dois registros de alerta.

## Alertas enviados e recebidos

O teste usou uma leitura **simulada**, com umidade 25%, pH 5,4, N/P/K ausentes e chuva
forte. As cinco condições foram consolidadas em um e-mail; a ação de baixa umidade
orientou verificar o talhão e **adiar irrigação**. A imagem de tomate gerou o segundo
e-mail, sugerindo registrar a imagem e inspecionar as plantas com responsável técnico.

| Origem | MessageId SNS | Recebido no Gmail, São Paulo |
|---|---|---|
| Sensores | `c4912498-5e18-5ce8-b4f9-47c4d6bedf57` | 28/10/2026 20:33:58 |
| Visão | `f906d166-2a46-56d9-9ad6-b23aa2f60eac` | 28/10/2026 20:34:08 |

**Aceite SNS e recebimento foram comprovados separadamente.** A API do Gmail
encontrou ambas as mensagens na caixa de entrada; o evento no corpo e o cabeçalho
`x-amz-sns-message-id` correspondem aos registros publicados pela EC2. Evidências
salvam somente os campos necessários, com destinatário mascarado e sem link de
cancelamento de assinatura.

O teste parou o serviço da dashboard durante as publicações. O monitor permaneceu
ativo, foi reiniciado entre as duas origens e manteve o estado SQLite. Uma nova
leitura equivalente foi processada sem criar outra mensagem, comprovando a
supressão durante 30 minutos. Ao terminar, ambos os serviços voltaram a ficar ativos.

## Operação, reinício e encerramento

Os serviços iniciam automaticamente com a EC2. Para manutenção pelo SSM, execute:

```bash
sudo systemctl status farmtech-dashboard farmtech-monitor --no-pager
sudo systemctl restart farmtech-dashboard farmtech-monitor
sudo journalctl -u farmtech-monitor -n 50 --no-pager
```

Depois de reiniciar o monitor, leituras equivalentes ainda dentro da janela de
supressão não geram novo e-mail. Para uma apresentação nova, use um talhão distinto
ou aguarde os 30 minutos. Não use IDs SNS locais de testes como evidência real.

A EC2 foi deixada **ligada** para uso/apresentação. Ao terminar, pare a instância
para preservar o orçamento e encerre a sessão conforme as instruções do Learner Lab:

```powershell
aws ec2 stop-instances --instance-ids i-09a66c2f286224171 --region us-east-1
```

Ao abrir outra sessão, confira o IP público e as regras do Security Group. O Lab
pode parar/iniciar a instância e alterar o IPv4. Descubra o endereço vigente com:

```powershell
aws ec2 describe-instances --instance-ids i-09a66c2f286224171 --region us-east-1 --query "Reservations[0].Instances[0].PublicIpAddress" --output text
```

Use SSM para manutenção sem ampliar o SSH. Backups do SQLite devem usar a API de
backup ou o monitor parado, preservando o WAL. Não copie `.env` em pacotes de entrega.
O segredo Oracle permanece em Parameter Store e no disco criptografado da instância;
se houver rotação, atualize ambos de forma controlada e reinicie os serviços.

## Limitações mantidas

O detector é acadêmico e conserva falsos positivos/omissões (mAP50:95 de teste
0,3758); suas mensagens sugerem inspeção, não diagnóstico. O ESP32 físico/Wokwi não
foi executado: firmware compilado e integração demonstrada pelo CSV simulado.
Disponibilidade e endereço da aplicação estão vinculados às sessões e ao orçamento
do laboratório. Os desafios opcionais de IA AWS e algoritmos genéticos permanecem
fora do escopo aprovado.

## Evidências e fontes

No projeto: `docs/evidencias/aws/` (testes, serviços, segurança, imagens, outbox e
recebimento dos e-mails). Os resultados locais e do Colab permanecem preservados.
Instruções atuais do Learner Lab foram consultadas: regiões us-east-1/us-west-2,
tamanho medium permitido, EBS gp3 até 100 GB e perfis de laboratório existentes.

Referências: [provedor de credenciais IMDS](https://docs.aws.amazon.com/sdkref/latest/guide/feature-imds-credentials.html),
[confirmação e entrega SNS por e-mail](https://docs.aws.amazon.com/sns/latest/dg/sns-email-notifications.html).

Não houve commit ou push automático nesta etapa.
Commit sugerido: `feat(deploy): implanta FarmTech na AWS Academy com alertas SNS`.
