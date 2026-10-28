# Detector agrícola — preparação, treinamento e inferência

Use `notebooks/treino_tomate_colab.ipynb` no Colab com GPU T4 e runtime Python
3.11/3.12. O notebook recebe o ZIP do projeto, instala as dependências fixadas,
prepara dados, treina e exporta um bundle real. Se o runtime tiver outra versão,
selecione um runtime compatível antes de prosseguir.

## Dataset

Fonte: [PlantDoc Object Detection dos autores](https://github.com/pratikkayal/PlantDoc-Object-Detection-Dataset),
licença declarada CC-BY-4.0. Cite Singh et al., PlantDoc: A Dataset for Visual Plant
Disease Detection, CoDS-COMAD 2020. Preserve atribuição, revisão de origem e as
limitações decorrentes de imagens coletadas da internet.

`farmtech.services.visao.fetch` baixa somente imagens do recorte de tomate de uma
revisão Git registrada. Nomes locais são hashes para aceitar caminhos Windows.
Anotações originais e nomes de origem permanecem rastreáveis nos CSVs.

`dataset.prepare` converte caixas para YOLO e mapeia:

- `Tomato leaf` para `folha_saudavel`;
- late blight, mold, yellow virus, mosaic virus, bacterial spot, early blight e
  Septoria para `folha_com_sinais_de_doenca`;
- outras categorias, incluindo ácaros, ficam fora; imagens com anotações de
  classes excluídas não são tratadas como negativos silenciosamente.

Verifica integridade e dimensões, caixas, SHA-256 e similaridade dHash. Agrupa
candidatos derivados por distância dHash <=4; elimina duplicatas exatas e remove
do treino os grupos que também aparecem no teste oficial. dHash é uma heurística:
revise visualmente os candidatos e documente derivações não identificadas.
Não examine previsões ou ajuste parâmetros usando as imagens reservadas do teste.
As imagens exportadas são RGB/JPEG de qualidade 95, sem EXIF. A matriz original
de pixels é preservada na orientação usada pelas caixas; não se gira a imagem
isoladamente. O manifesto distingue SHA-256 da origem e do JPEG exportado.

Reserva 20% dos grupos restantes de treino para validação, seed 42, e exige ambas
as classes nos três splits. O manifesto contém origem, grupo, hash, classes e
exclusões. A proporção de imagens pode variar de 20% porque grupos são indivisíveis.

```bash
python -m farmtech.services.visao.fetch .runtime/plantdoc_source
python -m farmtech.services.visao.dataset .runtime/plantdoc_source .runtime/tomate_dataset
```

## Treinamento

YOLOv5s oficial v7.0, pesos COCO, 640px, batch 16, seed42, patience0, 30 e 60 épocas.
Seleção por mAP50:95 de validação; empate por mAP50 e menos épocas. Cada best.pt
é medido em validação; somente o escolhido vai ao teste. Dados, configuração e
hardware precisam ser iguais entre os dois treinos.

```bash
python -m farmtech.services.visao.train .runtime/tomate_dataset .runtime/yolov5 experiments/tomate_nova_sessao
```

Execute no Colab GPU, mantendo o destino no Drive. Se falhar, preserve a sessão;
uma nova execução usa pasta nova e não finge retomar um treino incompleto. Após
instalações, reinicie o kernel se solicitado e reestabeleça ROOT/runtime/dataset.
O ambiente usa `constraints-colab.txt`; não reutiliza a complexa configuração
TensorFlow/PyTorch do experimento antigo, pois a nova inferência utiliza só YOLO.

`tomate_bundle.zip` inclui best.pt, hash SHA-256, classes, commit YOLO, versões,
manifesto do dataset, seleção e métricas do teste. Não preencha esses resultados
manualmente; este projeto não contém pesos agrícolas substitutos.

## Inferência

Instale requirements-visao e requirements do checkout oficial usando as constraints.
Extraia o bundle para models/tomate; configure FARMTECH_YOLO_RUNTIME e
FARMTECH_VISION_BUNDLE se usar outros caminhos.

```bash
python -m farmtech visao caminho/imagem.jpg --plot talhao-1
```

A inferência usa CPU, entrada 640, caixas visíveis a confiança >=0,25 e alertas
somente a >=0,50 para sinais de doença. Salva entrada, imagem anotada, JSON e
evento operacional. Um retorno saudável não prova ausência de doença; nenhuma
caixa resulta em “Inconclusivo”. Documente acertos, falsos positivos e omissões,
sem comparar diretamente estas métricas com as antigas classes bottle/backpack.
