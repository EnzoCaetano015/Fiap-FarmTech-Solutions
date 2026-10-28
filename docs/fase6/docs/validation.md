# Coleta e integração do dataset da Fase 6

Data: 02/10/2026. As imagens foram coletadas e salvas conforme pedido atual
do usuário, que amplia o escopo anterior de preparação sem dataset.

## Entrega

- 80 fotos reais: 40 bottle e 40 backpack.
- 64 imagens no treino, 8 na validação e 8 no teste: 32/4/4 por classe.
- 80 labels YOLO, totalizando 91 bounding boxes.
- Fotos JPEG em `fase6/data/{train,val,test}/images/`.
- Labels TXT correspondentes em `fase6/data/{train,val,test}/labels/`.
- Metadados em `data/sources.csv`, `annotations_source.json` e
  `dataset_summary.json`; README e notebook atualizados para o dataset integrado.
- Pacote de transferência `dataset_fase6.zip`: 17,41 MB, com fotos, labels,
  contrato e metadados de atribuição. Extrair a pasta data no Drive para Colab.
- Contact sheets das 40 fotos de cada classe disponíveis junto ao pacote.

Não há arquivos Python separados, pasta src ou pasta tests na entrega.
Este registro descreve a coleta em 02/10/2026. Resultados posteriores reais foram consolidados em 13/10/2026; veja a atualização abaixo.

## Fonte e seleção

Usada a skill vercel:agent-browser para consultar os downloads oficiais do
[Open Images](https://storage.googleapis.com/openimages/web/download_v7.html).
O download seletivo usou o bucket público `open-images-dataset`, conforme
o [downloader oficial](https://github.com/openimages/dataset/blob/master/downloader.py).
Os metadados de classes, imagens, bounding boxes e labels humanamente verificados
foram baixados dos links oficiais observados no navegador.

IDs resolvidos por nome: Bottle `/m/04dr76w` e Backpack `/m/01940j`.
Imagens com ambas as classes anotadas, grupos, desenhos e anotações inside
foram excluídas. A inspeção visual descartou latas, potes, malas, bolsas de
ombro e enquadramentos inadequados presentes entre os candidatos da fonte.
As caixas existentes foram usadas na coleta inicial; a revisão posterior
no Make Sense está registrada em makesense_validation.md.

As 80 fotos selecionadas são de 79 autores. São 75 imagens originalmente
do split test e 5 do validation do Open Images. Os splits locais 32/4/4 foram
definidos com seed 42; autor repetido foi mantido somente no treino.
Os splits do projeto não representam o benchmark oficial do Open Images.

## Licença e anotações

Metadados da fonte informam CC BY 2.0 para as fotos; anotações são disponibilizadas
pelo Open Images em CC BY 4.0. Autor, título, perfil, página original e licença
informada estão registrados para cada imagem em sources.csv. Esses registros
não representam uma auditoria da licença atual de cada página Flickr;
consulte as URLs originais caso vá redistribuir as fotos publicamente.

As fotos foram copiadas dos JPEGs do bucket oficial, sem recorte ou edição
de pixels na coleta. As caixas foram convertidas de xyxy normalizado para
centro/largura/altura YOLO com IDs locais 0/1; não são predições de modelo.
Na coleta inicial não foi usado Make Sense. Em 02/10/2026, a revisão assistida importou,
revisou visualmente e corrigiu os labels no site, com exportações YOLO reais
e capturas de tela. Veja [validação da revisão](makesense_validation.md).

## Verificação executada na coleta — histórico de 02/10/2026

- Schema Jupyter validado; outputs continuam vazios no notebook entregue.
- As 22 células de código executaram em sequência com RUN_EXPERIMENTS=False:
  dataset ready, manifesto com 80 linhas, nenhum download de pesos ou treinamento.
- 80 JPEGs decodificados/verificados com Pillow; SHA-256 conferido contra sources.csv.
- 80 hashes distintos; nenhum autor compartilhado entre splits do projeto.
- Labels lidos pelo validador do notebook: classes 0/1, coordenadas válidas,
  quantidade de caixas consistente e nenhuma imagem sem label.
- Todas as seis contagens por classe/split correspondem a 32/4/4.
- CNN construída e compilada em CPU; saída sintética (1,2).
- ZIP verificado: 80 JPGs, 80 TXTs, integridade CRC sem falha.
- git check-ignore confirmou que as 80 fotos e 80 labels continuam ignorados.
- git diff confirmou README raiz e fases 3, 4 e 5 sem alterações.
- Nenhum peso ou resultado acadêmico fictício adicionado.

## Próximos passos registrados na coleta (histórico)

Para o ambiente local, o dataset já está integrado. Para Colab, transfira o ZIP
ao Drive, extraia data/ e configure o caminho no notebook. Depois execute os
treinamentos YOLO 30/60 e CNN, inferências, métricas, gráficos, conclusões,
prints e vídeo. Esses experimentos não foram executados nesta coleta.

As fotos e labels estão presentes no projeto local, mas não acompanham
commit/push por estarem ignorados. Os arquivos de configuração, documentação
e atribuição são versionáveis. Nenhum commit ou push foi executado.

Commit sugerido para esta etapa:
`feat(fase6): integra dataset de garrafas e mochilas com labels e proveniência`

## Revisão posterior no Make Sense

As 80 imagens foram revisadas no editor em 02/10/2026, com exportações YOLO
reais, 13 imagens corrigidas e preservação das 91 caixas totais e dos splits.
O pacote atualizado é `dataset_fase6_final.zip`; o pacote da coleta descrito
acima é histórico. `sources.csv` mantém a quantidade de caixas originais em
`source_bounding_boxes` e a contagem atual em `bounding_boxes`.
Veja [registro completo](makesense_validation.md).

## Preparação para as tasks 11–22 — histórico de 02/10/2026

Em 02/10/2026, o notebook passou a ter 50 células, 26 de código. As células
foram executadas localmente com todas as ações externas e acadêmicas desligadas.
Fixtures temporárias e mocks verificaram a extração protegida, SHA-256/CRC,
rejeição de sobrescrita e caminhos inseguros, diagnóstico de imagens ilegíveis,
labels inválidos, dataset vazio, manifesto, comandos 30/60 equivalentes,
seleção em val com desempate por tempo, campos indisponíveis, tempos e filtros.
O pipeline de inferência produziu oito evidências com mock em pasta temporária,
e a recuperação desses arquivos foi verificada. Esses dados não são resultados
acadêmicos e não foram incorporados em results.

A CNN real foi construída/compilada em CPU, com model.summary e inferência
sintética de saída (2,2). O notebook entregue continua sem outputs acadêmicos.
A GPU Colab e a execução conjunta dos frameworks só poderão ser confirmadas
pelo usuário no preflight. Treinos e análises finais continuam pendentes.
Confira README.md e results_analysis.md para o estado da entrega e os resultados.

Verificação final: adaptadores oficiais compilados e exercitados com mocks; callback `on_model_save` conferido em melhoria/empate e seleção da linha correspondente do CSV; `ComputeLoss` e avaliação de oito imagens conferidos. Diff restrito a fase6, `git diff --check` sem erros e regras de ignore verificadas. Os adaptadores ainda precisam de execução real no Colab.

## Atualização — execução real de 13/10/2026

- 27 células da preparação e, após consolidação, as 30 células finais executadas
  localmente com ações externas False;
  casos temporários/mocks de ZIP, labels, filtros, comandos, seleção e métricas.
- CNN CPU construída/compilada, model.summary e inferência (2,2).
- Runtime GPU, 30/60 épocas YOLO e 30 CNN completos; configurações, CSVs,
  callbacks, checkpoint hashes e seleção por validação conferidos.
- Oito nomes comuns nas três abordagens; 16 JPEGs de inferência processados.
- Pacote original CRC válido e SHA-256 dos 41 arquivos conferidos.
- Painel e tabela qualitativos realmente executados em Jupyter local a partir
  dos resultados, sem inferências novas ou alterações nas métricas originais.
- Notebook consolidado validado por nbformat/AST, sem outputs de erro, mantendo
  outputs reais. Flags resetadas após execução, conforme metadata fase6_delivery.
- Dados brutos/pesos/runs/ZIPs permanecem ignorados; diff exclusivo fase6.

Veja results/audit/final_audit.json e results_analysis.md.
Vídeo/publicação pelo aluno e detecção positiva de backpack continuam não comprovados.

## Validação final da melhoria

36 células de código da entrega executadas localmente com controles externos
False; nenhuma instalação, Drive, GPU ou novo treinamento nessa validação.
Contagens de IoU/TP/FP/FN de val/test recalculadas diretamente dos labels
Make Sense imutáveis e das predições reais, correspondendo aos CSVs exportados.
41 arquivos originais e 46 arquivos do pacote complementar conferidos por SHA-256.
Painel real executado no Colab, com FN e FP destacados; nenhum resultado removido.
Diff só fase6 e git diff --check aprovado; dados brutos/pesos/runs ignorados.
Commit sugerido: `feat(fase6): melhora deteccao das duas classes com fine tuning validado`.
