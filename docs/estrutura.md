# Estrutura do repositório

Clique no nome de uma pasta para abrir seu conteúdo.

| Pasta | O que contém |
|---|---|
| [dashboard/](../dashboard/) | Aplicação Streamlit: ponto de entrada `app.py`, interface e painéis de monitoramento, previsões e serviços. |
| [farmtech/](../farmtech/) | Núcleo do sistema: CLI, configuração, contrato compartilhado de execução e persistência operacional SQLite. |
| [farmtech/services/](../farmtech/services/) | Implementação dos serviços reutilizados pela dashboard e pelo terminal. |
| [agronomia/](../farmtech/services/agronomia/) | Cálculo de área e insumos, análise estatística em R e consulta climática. |
| [iot/](../farmtech/services/iot/) | Validação dos dados e reprodução temporizada das leituras simuladas. |
| [oracle/](../farmtech/services/oracle/) | Importação incremental sem duplicação e consulta dos registros Oracle. |
| [preditivo/](../farmtech/services/preditivo/) | Treinamento dos modelos com dados sintéticos e recomendações de manejo. |
| [visao/](../farmtech/services/visao/) | Preparação do PlantDoc, treinamento YOLO e inferência agrícola em CPU. |
| [alertas/](../farmtech/services/alertas/) | Regras de alerta, supressão, fila persistente, recuperação de falhas e publicação no SNS. |
| [scripts/](../scripts/) | Atalhos de terminal para clima, simulação de sensores, importação Oracle e treinamento preditivo. |
| [hardware/](../hardware/) | Componente físico e simulado do projeto; [esp32/](../hardware/esp32/) reúne firmware, circuito, PlatformIO e Wokwi. |
| [database/](../database/) | Estrutura do banco; [oracle/](../database/oracle/) contém scripts SQL e explicação das consultas. |
| [data/](../data/) | Dados de entrada; [sensores/](../data/sensores/) contém as leituras simuladas e o dataset sintético de treinamento. |
| [models/](../models/) | Artefatos dos modelos; [preditivo/](../models/preditivo/) reúne regressões e metadados. O bundle agrícola fica em `models/tomate/`, fornecido separadamente e não versionado no Git. |
| [relatorios/](../relatorios/) | Resultados tabulares; [preditivo/](../relatorios/preditivo/) contém as métricas dos modelos sintéticos. |
| [notebooks/](../notebooks/) | Notebooks por domínio: [tomate/](../notebooks/tomate/) para treinamento Colab e resultados agrícolas; [objetos/](../notebooks/objetos/) para relatório, reprodução e notebook original de YOLO/CNN. |
| [experiments/](../experiments/) | Artefatos experimentais; [objetos/](../experiments/objetos/) reúne configurações, proveniência dos dados, auditorias, curvas e resultados de detecção e classificação. |
| [infra/](../infra/) | Infraestrutura; [aws/](../infra/aws/) contém instalação na EC2, unidades systemd, configuração segura e verificações. |
| [docs/](../docs/) | Arquitetura geral, arquitetura AWS, preparação no Colab e resultados agrícolas; [visao/](../docs/visao/) contém análise de objetos, melhoria do detector e validação Make Sense. |
| [evidencias/](../evidencias/) | Registros das execuções, capturas e resultados que comprovam o funcionamento. |
| [local/](../evidencias/local/) | Aceite e testes locais, auditoria da reorganização e demonstrações da dashboard. |
| [aws/](../evidencias/aws/) | Infraestrutura validada, testes na EC2, alertas e comprovação do recebimento dos e-mails. |
| [visao/](../evidencias/visao/) | Exemplos de inferência agrícola e capturas da revisão das anotações de objetos. |
| [oracle/](../evidencias/oracle/) | Validação da integração Oracle e capturas das consultas SQL. |
| [iot/](../evidencias/iot/) | Registro da reprodução de leituras simuladas. |
| [analise/](../evidencias/analise/) | Estatísticas descritivas e gráfico de sensores produzidos em R. |
| [clima/](../evidencias/clima/) | Registro da consulta climática real. |
| [esp32/](../evidencias/esp32/) | Imagens do circuito e da simulação do protótipo. |
| [assets/](../assets/) | Identidade visual do projeto, incluindo a logo apresentada neste README. |
| [tests/](../tests/) | Testes de serviços, dashboard, preparação do dataset e fluxos de integração. |
| [requirements/](../requirements/) | Dependências da aplicação, desenvolvimento, visão e constraints do Colab. |
| [.streamlit/](../.streamlit/) | Configuração visual e de execução da dashboard Streamlit. |

A organização segue responsabilidades do sistema. O experimento de garrafas e
mochilas permanece como estudo comparativo de visão, separado do detector de
tomate usado na operação agrícola. Datas, hashes, identificadores de execução e
caminhos originais em registros históricos foram preservados para rastreabilidade.

## Onde colocar novos arquivos

- Código de interface: `dashboard/`; regras e serviços compartilhados: `farmtech/`.
- Dados de entrada: `data/`; modelos: `models/`; métricas consolidadas: `relatorios/`.
- Notebooks: `notebooks/<domínio>/`; configurações e resultados de experimentos: `experiments/<domínio>/`.
- Guias e explicações: `docs/`; capturas, logs e comprovantes de execução: `evidencias/<componente>/`.
- Firmware: `hardware/`; scripts SQL: `database/`; instalação e operação na nuvem: `infra/`.
- Dependências compartilhadas: `requirements/`; ambientes experimentais independentes podem manter seu próprio `requirements.txt`.

Arquivos temporários e estado operacional ficam em `.runtime/`, ignorado pelo Git.
O ambiente `.venv/`, o `.env`, os dados PlantDoc e os pesos agrícolas também ficam
fora do versionamento. Preserve identificadores e caminhos nos registros históricos;
atualize referências nos comandos executáveis quando mover arquivos.

## Instalação e notebooks

- [Perfis de dependências](../requirements/README.md): aplicação, testes e visão agrícola.
- [Guia dos notebooks](../notebooks/README.md): finalidade e requisitos de cada domínio.
- [README principal](../README.md): execução local, CLI e roteiro para avaliação.
