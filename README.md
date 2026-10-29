# FarmTech Solutions — Sistema integrado · Fase 7

Sistema acadêmico de gestão da fazenda com serviços das fases anteriores reunidos
em uma pasta: Python/R, ESP32, Oracle, modelos preditivos, Streamlit, visão agrícola
e alertas por e-mail via Amazon SNS. **Enzo Caetano Peracio Rodrigues — RM 570352.**

## Iniciar

Use Python 3.11, crie ambiente isolado e instale `requirements.txt`.

```bash
python -m venv .venv
# Ative .venv conforme seu sistema operacional.
python -m pip install -r requirements.txt
streamlit run dashboard/src/dashboard.py
```

Copie `.env.example` para `.env` e configure as integrações disponíveis.
Não são necessárias credenciais Oracle/AWS nem pesos YOLO para abrir a dashboard.
Serviços externos indisponíveis informam erro sem interromper as outras funções.
Documentação: [arquitetura geral](docs/arquitetura.md), [Colab](docs/colab.md),
[resultados de visão](docs/resultados-visao.md) e [arquitetura AWS](docs/aws.md).

## Serviços e terminal

| Operação | Comando na raiz |
|---|---|
| Área retangular e insumos | `python -m farmtech area --length 100 --width 200 --dose 12` |
| Área circular | `python -m farmtech area --shape circulo --radius 10 --dose 12` |
| Estatística e gráficos em R | `python -m farmtech analise-r` |
| Clima | `python -m farmtech clima --latitude -23.55 --longitude -46.63` |
| Replay IoT histórico, idempotente | `python -m farmtech iot --interval 1 --plot talhao-demo` |
| Nova demonstração simulada | `python -m farmtech iot --live-time --plot talhao-demo` |
| Importação Oracle sem exclusão | `python -m farmtech oracle-importar` |
| Consulta Oracle | `python -m farmtech oracle-consultar --limit 100` |
| Treino preditivo Fase 4 | `python -m farmtech treinar` |
| Inferência agrícola | `python -m farmtech visao imagem.jpg --plot talhao-1` |
| Histórico de alertas | `python -m farmtech alertas` |
| Monitor independente | `python -m farmtech monitor --interval 10` |
| Ciclo único do monitor | `python -m farmtech monitor-uma-vez` |

Dashboard e terminal chamam as mesmas funções. Operações retornam resultado,
duração, arquivos e erros em JSON e registram a execução. Não é necessário colar
comandos arbitrários na interface. Fechar a dashboard não encerra o monitor separado.

## Organização

```text
farmtech/
  services/
    inicial/      # cálculo, insumos, R e clima
    iot/          # validação e replay de sensores simulados
    oracle/       # persistência acadêmica incremental
    preditivo/    # modelos e recomendador da Fase 4
    visao/        # PlantDoc, treinamento e inferência YOLO
    alertas/      # regras, outbox e SNS
  operations.py   # contrato compartilhado pela CLI/dashboard
  storage.py      # SQLite operacional persistente
dashboard/src/    # dashboard integrada e componentes preservados da Fase 4
prototipo-ESP32/   # circuito e sketch originais
data/             # CSVs das fases anteriores
models/           # modelos preditivos; bundle agrícola local em tomate/
sql/              # scripts Oracle e evidências anteriores
notebooks/        # treinamento agrícola no Colab
deploy/           # preflight AWS, configuração e systemd
docs/             # documentação principal, revisão da visão e evidências
tests/            # regras e fluxos de integração
```

Os entrypoints antigos continuam disponíveis como adaptadores. O estado operacional,
uploads e resultados gerados ficam em `.runtime/`, ou em `FARMTECH_STATE_DIR`.
O banco operacional SQLite não substitui Oracle. Dados e modelos anteriores foram
preservados; treinar novamente atualiza os artefatos da Fase 4 por ação explícita.

## Dashboard

Seis abas: Monitoramento, ML e métricas, Previsão interativa, Serviços, Visão agrícola
e Alertas. A aba Serviços dispara as fases pelo mesmo contrato da CLI. A aba Alertas
mostra dados observados, regra, ação sugerida, estado, tentativas e MessageId.

Os sensores do CSV e do protótipo são simulados. Os dados ampliados e alvos da
Fase 4 são sintéticos, e suas métricas não comprovam produtividade agrícola real.
O replay é a entrada integrada do IoT; não há leitura automática de um ESP32 físico.

## Visão computacional

O detector agrícola usa folhas de tomate do PlantDoc e duas classes: saudável e
com sinais de doença. Treina no Colab e executa inferência CPU na EC2. Sem o bundle
real, a função informa indisponibilidade. Nenhuma detecção é resultado inconclusivo.
Confiança >=0,50 na classe de doença gera sugestão de inspeção, sem diagnóstico
definitivo ou recomendação automática de defensivos.

Os resultados de garrafas/mochilas da Fase 6 estão em um [relatório revisado](docs/fase6/notebooks/fase6_revisada.ipynb),
com código de reprodução separado e original preservado. Consulte também a
[análise dos resultados](docs/fase6/docs/results_analysis.md), a
[melhoria do detector](docs/fase6/docs/model_improvement.md) e a
[validação Make Sense](docs/fase6/docs/makesense_validation.md). Métricas antigas não são
reutilizadas como resultado agrícola. Fonte e atribuições: [PlantDoc](https://github.com/pratikkayal/PlantDoc-Object-Detection-Dataset).

## Alertas e AWS

EC2 executa dashboard e monitor por systemd. O monitor avalia sensores e resultados
visuais a cada 10s, consolida condições da leitura e publica no SNS Standard.
Mensagens equivalentes são suprimidas por talhão durante 30 minutos; falhas ficam
pendentes com espera progressiva. Configuração e regras: [arquitetura](docs/arquitetura.md).

É preciso confirmar a assinatura de e-mail. `published`/MessageId significa aceite
pelo SNS; a evidência de recebimento deve ser capturada na caixa do destinatário.
A implantação só é considerada comprovada depois do teste real no AWS Academy.

## Validação e apresentação

```bash
python -m unittest discover -s tests -v
```

Veja os registros de [aceite local](docs/evidencias/auditoria-local/aceite.json)
e [aceite AWS](docs/evidencias/aws/aceite-aws.json). IA na AWS e algoritmos
genéticos ficam fora do escopo desta entrega.

## Resultados agrícolas e aceite atual

Treinos 30/60 concluídos na T4; validação selecionou **30 épocas**. No teste reservado de 69 imagens: mAP50 **0,6115**, mAP50:95 **0,3758**. Quatro inferências CPU foram verificadas, incluindo erros. Veja [resultados reais](docs/resultados-visao.md).

Oracle real foi validado localmente e na EC2, com dez registros e repetição sem duplicatas. A implantação AWS foi concluída em 28/10/2026: dashboard e monitor ativos, 43 testes Linux aprovados e dois e-mails reais recebidos e correlacionados com MessageId SNS. Veja [evidências AWS](docs/evidencias/aws/aceite-aws.json).

## Auditoria funcional local

43 testes passaram no ambiente atual e em uma instalação limpa. Oracle, R, API climática, treino preditivo, inferência CPU, dashboard e monitor independente foram executados. O firmware ESP32 também compilou. Registros: [aceite local](docs/evidencias/auditoria-local/aceite.json).

## Acesso AWS validado

[Dashboard EC2](http://54.166.136.107:8501), restrita ao IP autorizado. Use o talhão `talhao-aws-demo` para ver a demonstração. Consulte a [arquitetura AWS](docs/aws.md).
