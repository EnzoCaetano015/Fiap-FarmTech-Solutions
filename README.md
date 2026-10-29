<p align="center">
  <img src="assets/logo.png" alt="Logo da FarmTech Solutions" width="220">
</p>

# FarmTech Solutions

Sistema integrado de gestão da fazenda: monitoramento de sensores, cálculo de
área e insumos, análise em R, consulta climática, persistência Oracle, modelos
preditivos, visão computacional e alertas por e-mail via Amazon SNS.

**Enzo Caetano Peracio Rodrigues — RM 570352.** Projeto acadêmico.

## Roteiro para avaliação

1. Leia a [arquitetura geral](docs/arquitetura.md) e abra a dashboard seguindo as
   instruções abaixo. As seis abas concentram a demonstração do sistema.
2. Em **Serviços**, calcule área e insumos e reproduza as leituras simuladas.
   Consulte os dados em **Monitoramento** e os resultados em **ML e métricas** e
   **Previsão interativa**. Os modelos preditivos utilizam dados e alvos sintéticos.
3. Em **Visão agrícola**, envie uma [imagem de exemplo](evidencias/visao/agricola/exemplo_3_entrada.png).
   A inferência exige o bundle agrícola e o runtime YOLO configurados. Confira as
   [métricas reais, acertos e erros](docs/resultados-visao.md).
4. Execute o monitor em outro terminal para processar os eventos. A aba **Alertas**
   apresenta regras, ações sugeridas, tentativas e aceite de publicação no SNS.
5. Consulte as [evidências locais](evidencias/local/aceite.json), o
   [aceite AWS](evidencias/aws/aceite-aws.json) e a
   [comprovação dos e-mails](evidencias/aws/emails-recebidos.json).
   Esses arquivos registram execuções anteriores; não são uma consulta ao estado
   atual dos recursos do laboratório.

## Executar localmente

Use Python **3.11** em ambiente isolado. Na raiz do repositório:

```bash
python -m venv .venv
```

Ative o ambiente com `.venv\Scripts\Activate.ps1` no PowerShell ou
`source .venv/bin/activate` no Linux. Depois:

```bash
python -m pip install -r requirements.txt
streamlit run dashboard/app.py
```

Copie `.env.example` para `.env` e preencha somente as integrações que utilizar.
A dashboard abre sem credenciais Oracle/AWS ou pesos agrícolas. Cada serviço
informa sua indisponibilidade sem impedir o uso dos demais.

| Integração | Preparação necessária |
|---|---|
| Estatística em R | Instalar R e disponibilizar `Rscript` no PATH ou em `FARMTECH_RSCRIPT` |
| Oracle | Configurar `ORACLE_USER`, `ORACLE_PASSWORD` e `ORACLE_DSN`; scripts em [database/oracle](database/oracle) |
| Consulta climática | Acesso à internet; falhas são apresentadas como previsão indisponível |
| Visão agrícola | Instalar `requirements-visao.txt` com `constraints-colab.txt`, preparar YOLOv5 v7.0 e extrair o bundle em `models/tomate`; detalhes em [Colab](docs/colab.md) |
| Alertas SNS | Credenciais temporárias/perfil da instância, tópico em `FARMTECH_SNS_TOPIC_ARN` e assinatura de e-mail confirmada |

Os pesos agrícolas não são versionados no Git. São fornecidos no bundle de
entrega quando disponível. Sem eles, o serviço informa detector indisponível.
O estado operacional e os arquivos gerados ficam em `.runtime/` ou no caminho
definido por `FARMTECH_STATE_DIR`; esse conteúdo não integra o versionamento.

## Usar pelo terminal

Dashboard, CLI e atalhos de `scripts/` chamam os mesmos serviços.
Cada execução informa resultado, duração, arquivos gerados e erros.

| Serviço | Comando na raiz |
|---|---|
| Área retangular e insumos | `python -m farmtech area --length 100 --width 200 --dose 12` |
| Área circular | `python -m farmtech area --shape circulo --radius 10 --dose 12` |
| Estatística e gráficos em R | `python -m farmtech analise-r` |
| Previsão climática | `python -m farmtech clima --latitude -23.55 --longitude -46.63` |
| Replay histórico idempotente | `python -m farmtech iot --interval 1 --plot talhao-demo` |
| Nova leitura simulada | `python -m farmtech iot --live-time --plot talhao-demo` |
| Importação Oracle incremental | `python -m farmtech oracle-importar` |
| Consulta Oracle | `python -m farmtech oracle-consultar --limit 100` |
| Treinamento preditivo sintético | `python -m farmtech treinar` |
| Inferência agrícola em CPU | `python -m farmtech visao evidencias/visao/agricola/exemplo_3_entrada.png --plot talhao-demo` |
| Histórico de alertas | `python -m farmtech alertas` |
| Monitor em terminal separado | `python -m farmtech monitor --interval 10` |
| Um ciclo do monitor | `python -m farmtech monitor-uma-vez` |

O treinamento preditivo atualiza os modelos, o dataset sintético e as métricas.
Os scripts SQL históricos de recriação de tabelas são material de avaliação;
não são executados automaticamente pela aplicação. A importação da aplicação
inclui registros sem apagar a tabela e sem duplicar leituras existentes.

## Organização do repositório

Clique no nome de uma pasta para abrir seu conteúdo.

| Pasta | O que contém |
|---|---|
| [dashboard/](dashboard/) | Aplicação Streamlit: ponto de entrada `app.py`, interface e painéis de monitoramento, previsões e serviços. |
| [farmtech/](farmtech/) | Núcleo do sistema: CLI, configuração, contrato compartilhado de execução e persistência operacional SQLite. |
| [farmtech/services/](farmtech/services/) | Implementação dos serviços reutilizados pela dashboard e pelo terminal. |
| [agronomia/](farmtech/services/agronomia/) | Cálculo de área e insumos, análise estatística em R e consulta climática. |
| [iot/](farmtech/services/iot/) | Validação dos dados e reprodução temporizada das leituras simuladas. |
| [oracle/](farmtech/services/oracle/) | Importação incremental sem duplicação e consulta dos registros Oracle. |
| [preditivo/](farmtech/services/preditivo/) | Treinamento dos modelos com dados sintéticos e recomendações de manejo. |
| [visao/](farmtech/services/visao/) | Preparação do PlantDoc, treinamento YOLO e inferência agrícola em CPU. |
| [alertas/](farmtech/services/alertas/) | Regras de alerta, supressão, fila persistente, recuperação de falhas e publicação no SNS. |
| [scripts/](scripts/) | Atalhos de terminal para clima, simulação de sensores, importação Oracle e treinamento preditivo. |
| [hardware/](hardware/) | Componente físico e simulado do projeto; [esp32/](hardware/esp32/) reúne firmware, circuito, PlatformIO e Wokwi. |
| [database/](database/) | Estrutura do banco; [oracle/](database/oracle/) contém scripts SQL e explicação das consultas. |
| [data/](data/) | Dados de entrada; [sensores/](data/sensores/) contém as leituras simuladas e o dataset sintético de treinamento. |
| [models/](models/) | Artefatos dos modelos; [preditivo/](models/preditivo/) reúne regressões e metadados. O bundle agrícola fica em `models/tomate/`, fornecido separadamente e não versionado no Git. |
| [relatorios/](relatorios/) | Resultados tabulares; [preditivo/](relatorios/preditivo/) contém as métricas dos modelos sintéticos. |
| [notebooks/](notebooks/) | Notebooks por domínio: [tomate/](notebooks/tomate/) para treinamento Colab e resultados agrícolas; [objetos/](notebooks/objetos/) para relatório, reprodução e notebook original de YOLO/CNN. |
| [experiments/](experiments/) | Artefatos experimentais; [objetos/](experiments/objetos/) reúne configurações, proveniência dos dados, auditorias, curvas e resultados de detecção e classificação. |
| [infra/](infra/) | Infraestrutura; [aws/](infra/aws/) contém instalação na EC2, unidades systemd, configuração segura e verificações. |
| [docs/](docs/) | Arquitetura geral, arquitetura AWS, preparação no Colab e resultados agrícolas; [visao/](docs/visao/) contém análise de objetos, melhoria do detector e validação Make Sense. |
| [evidencias/](evidencias/) | Registros das execuções, capturas e resultados que comprovam o funcionamento. |
| [local/](evidencias/local/) | Aceite e testes locais, auditoria da reorganização e demonstrações da dashboard. |
| [aws/](evidencias/aws/) | Infraestrutura validada, testes na EC2, alertas e comprovação do recebimento dos e-mails. |
| [visao/](evidencias/visao/) | Exemplos de inferência agrícola e capturas da revisão das anotações de objetos. |
| [oracle/](evidencias/oracle/) | Validação da integração Oracle e capturas das consultas SQL. |
| [iot/](evidencias/iot/) | Registro da reprodução de leituras simuladas. |
| [analise/](evidencias/analise/) | Estatísticas descritivas e gráfico de sensores produzidos em R. |
| [clima/](evidencias/clima/) | Registro da consulta climática real. |
| [esp32/](evidencias/esp32/) | Imagens do circuito e da simulação do protótipo. |
| [assets/](assets/) | Identidade visual do projeto, incluindo a logo apresentada neste README. |
| [tests/](tests/) | Testes de serviços, dashboard, preparação do dataset e fluxos de integração. |
| [.streamlit/](.streamlit/) | Configuração visual e de execução da dashboard Streamlit. |

A organização segue responsabilidades do sistema. O experimento de garrafas e
mochilas permanece como estudo comparativo de visão, separado do detector de
tomate usado na operação agrícola. Datas, hashes, identificadores de execução e
caminhos originais em registros históricos foram preservados para rastreabilidade.

## Documentação e artefatos para consulta

| Material | Conteúdo |
|---|---|
| [Arquitetura geral](docs/arquitetura.md) | Componentes, contratos, persistência e regras de alerta |
| [Arquitetura AWS](docs/aws.md) | EC2, rede, identidade, armazenamento e mensageria |
| [Colab](docs/colab.md) | Origem dos dados, preparação, treinamento e exportação |
| [Resultados agrícolas](docs/resultados-visao.md) | Validação, teste reservado, exemplos e limitações |
| [Análise de objetos](docs/visao/results_analysis.md) | Comparação de YOLO e CNN, métricas e tempos |
| [Melhoria do detector de objetos](docs/visao/model_improvement.md) | Experimento complementar com transferência de aprendizado |
| [Validação Make Sense](docs/visao/makesense_validation.md) | Revisão da rotulação e evidências |
| [Relatório de objetos](notebooks/objetos/relatorio.ipynb) | Leitura acadêmica com saídas reais preservadas |
| [Resultados do tomate](notebooks/tomate/resultados.ipynb) | Síntese do experimento agrícola |
| [Protótipo ESP32](hardware/esp32/PROTOTIPO.md) | Componentes e uso da simulação Wokwi |
| [Consultas Oracle](database/oracle/CONSULTAS_FARMTECH.md) | SQL e evidências das consultas |

## Validação e limites

```bash
python -m unittest discover -s tests -v
```

A suíte verifica cálculos, entradas inválidas, importação Oracle transacional,
simulação idempotente, regras de alerta, supressão, recuperação de falhas e ações
da dashboard. As integrações externas são isoladas na suíte; comprovações reais
estão em `evidencias/`.

Os sensores são simulados. O replay CSV é a entrada IoT integrada; não há leitura
automática de ESP32 físico. As previsões usam alvos sintéticos e não comprovam
produtividade agrícola real. O detector de tomate selecionou o experimento de
30 épocas pela validação; no teste reservado, obteve mAP50 **0,6115** e mAP50:95
**0,3758**, com falsos positivos e omissões documentados.

Detecção de sinais de doença com confiança mínima de 0,50 sugere inspeção humana.
Ausência de detecção é inconclusiva. O monitor funciona independentemente da
dashboard. `published` e `MessageId` representam aceite pelo SNS; o recebimento
do e-mail deve ser comprovado separadamente. IA gerenciada na AWS e algoritmos
genéticos não integram este escopo.
