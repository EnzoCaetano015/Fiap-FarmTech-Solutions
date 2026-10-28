# FarmTech Solutions — Fase 6: Visão Computacional

**Enzo Caetano Peracio Rodrigues — RM 570352** · Projeto individual

Experimentos reais concluídos no Colab em **13/10/2026**, Tesla T4. Todo o código
Python está no [notebook obrigatório](notebook/EnzoCaetanoPeracioRodrigues_rm570352_pbl_fase6.ipynb), com outputs preservados
e controles externos desativados após a execução. Sem src, tests ou arquivos .py.
Abra a [cópia executada no Colab](https://colab.research.google.com/drive/1tOPqLqF--WRhIR8VweO8-4SQi4PKFW-j) no Drive conectado. A versão pública
no GitHub depende do commit/push do aluno; nenhum foi feito automaticamente.

## Dataset e métodos

80 fotos Open Images: bottle (0) e backpack (1), 40 por classe, distribuição
32/4/4 por classe (64/8/8 no total), 80 labels e 91 caixas. Labels importados,
revisados e corrigidos no Make Sense, exportados em YOLO. Veja a
[procedência e revisão](docs/makesense_validation.md),
[contrato](data/README.md) e [atribuições](data/sources.csv).
Fotos e labels brutos continuam ignorados pelo Git; pacote conferido no Drive.

YOLOv5s oficial v7.0 do zero: 30/60 épocas, 640, batch 16, seed 42, patience 0.
CNN própria: três blocos, 224×224, batch 8, 30 épocas, augmentation só no treino,
checkpoint pela menor val_loss. COCO usa yolov5s pré-treinada sem treino nesta base.
Selecionamos a YOLO de 60 épocas exclusivamente em validação (melhor época 59).
As três abordagens usaram as mesmas oito imagens de teste.

## Resultados de teste

| Abordagem | Tarefa e métrica | Resultado | Média / mediana (ms/imagem) |
|---|---|---:|---:|
| YOLO customizada | Detecção, mAP@0.5:0.95 | 0,005039 | 34,22 / 35,99 |
| YOLO COCO | Detecção, mAP não calculado | Indisponível | 20,97 / 20,22 |
| CNN própria | Classificação, accuracy | 0,875 (7/8) | 16,99 / 16,30 |

CNN: F1 macro 0,873016; matriz `[[4,0],[1,3]]`. YOLO própria teve nenhuma
detecção com confiança mínima 0,25; COCO detectou garrafas, mas nenhuma mochila.
Essa limitação pertence aos baselines originais. A melhoria complementar abaixo demonstrou ambas as classes.
**Accuracy e mAP medem tarefas diferentes. Confiança não é precisão.**
O teste pequeno e as diferentes entradas limitam conclusões e comparação de tempos.
Veja [análise completa](docs/results_analysis.md), curvas, tabelas e evidências
reais em results; pesos/runs permanecem no Drive, fora do Git.

## Execução e entrega

Para reproduzir no Colab, crie uma pasta **Fase6** no Google Drive e coloque
**estes três arquivos na raiz da pasta**:

```text
Fase6/
├── EnzoCaetanoPeracioRodrigues_rm570352_pbl_fase6.ipynb
├── fase6_colab_preparacao.zip
└── dataset_fase6_final.zip
```

As pastas `data/` e `experiments/` são criadas durante a execução; não são
arquivos de entrada obrigatórios. Não é necessário clonar o repositório ou
criar as pastas manualmente. O caminho usado nesta execução é
`/content/drive/MyDrive/Faculdade/Fiap/Fase6`; ajuste-o se guardar Fase6 em outro local.
Upload, extração, diagnóstico, GPU dos dois frameworks e experimentos foram
conferidos. Leia o [roteiro de execução/recuperação](docs/colab_execution.md)
antes de habilitar ações; não sobrescreva a sessão existente.
A preparação local foi validada em Python 3.11 isolado, incluindo smoke test
real de CNN em CPU. A execução GPU usou Python 3.12.13 no runtime 2026.07.

Estrutura: config (YAML/manifesto), data (contrato/proveniência e dados locais
ignorados), notebook (código e outputs), results (artefatos pequenos reais),
docs (arquitetura, verificações, análise e vídeo). Dependências em requirements.txt.
Não instalar globalmente nem versionar ZIPs, pesos, ambientes ou runs.

## Pendências de aceite

[Assistir ao vídeo de apresentação](https://youtu.be/xQRzp8BzaPY) — **4min34s**, publicação **não listada**. URL, título, duração e indicador de visibilidade conferidos na página do YouTube em 13/10/2026. A conferência de metadados não constitui uma revisão integral do conteúdo do vídeo.
O [roteiro com os números reais](docs/video_script.md) está pronto.
As predições originais não demonstraram mochilas; o experimento complementar
com pesos COCO demonstra detecções corretas das duas classes, preservando o histórico.
Publicação da versão no GitHub/commit/push fica com o aluno.
Não implementamos ESP32-CAM ou segmentação. Fine tuning foi usado no experimento complementar autorizado.

Veja [arquitetura](docs/architecture.md), [validação](docs/validation.md),
[análise dos resultados](docs/results_analysis.md).


## Melhoria complementar concluída

Fine tuning COCO 30/60 executado na T4, com os mesmos dados. Seleção por
validação: **60 épocas**, checkpoint **58**.
Teste observado: **mAP50 0.9950; mAP50:95 0.7597**.
Detecções corretas por IoU >=0,5/confiança >=0,25 demonstradas para **bottle e backpack**.
Os resultados fracos do treino do zero permanecem preservados; este ganho vem
de um experimento complementar com pesos COCO, explicitamente autorizado.
Veja [análise e contagens por classe](docs/model_improvement.md) e a seção 15
do notebook. Não é novo teste cego. O vídeo está disponível no link acima; as alterações desta documentação ainda precisam ser publicadas no GitHub.

Limitações complementares: uma mochila sem detecção a 0,25 e um copo marcado
como garrafa. O objetivo mínimo de distinguir/localizar as duas classes foi
comprovado neste conjunto, sem afirmar funcionamento perfeito em qualquer imagem.
