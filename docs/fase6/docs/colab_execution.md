# Reprodução no Google Colab

## 1. Prepare a pasta Fase6

No Google Drive, crie uma pasta **Fase6**. Coloque somente estes três arquivos
diretamente na raiz dela:

```text
Fase6/
├── EnzoCaetanoPeracioRodrigues_rm570352_pbl_fase6.ipynb
├── fase6_colab_preparacao.zip
└── dataset_fase6_final.zip
```

O notebook contém o código. O pacote de preparação contém as configurações
e dependências de apoio. O pacote do dataset contém as imagens, os labels e
a procedência das fotos. Não extraia os ZIPs manualmente e não precisa clonar
o GitHub. As pastas **data** e **experiments** serão criadas pelo notebook.

Para apenas consultar os resultados, abra o notebook: os outputs já estão
salvos e não exigem GPU nem novo treinamento.

## 2. Abra o notebook e ajuste o caminho

Abra o arquivo `.ipynb` com o Google Colab. A pasta pode estar em qualquer local
do seu Drive. Nesta execução ela fica em **Meu Drive → Faculdade → Fiap → Fase6**,
correspondente a `/content/drive/MyDrive/Faculdade/Fiap/Fase6`.

Se usar **Meu Drive → Fase6**, o caminho será `/content/drive/MyDrive/Fase6`.
Antes de executar, ajuste as três referências à pasta no notebook:

- Na primeira célula, o caminho `source` do arquivo `fase6_colab_preparacao.zip`.
- Em **Configuração e caminhos**, a variável `DRIVE_BASE`.
- Para executar também a melhoria complementar, `IMPROVEMENT_BASE` na seção 15.

Use o mesmo caminho nas três referências. `DRIVE_DATASET` e `DATASET_ZIP`
são derivados de `DRIVE_BASE`.

## 3. Prepare uma nova execução

1. Faça uma cópia do notebook para preservar os resultados existentes. Selecione
   **GPU T4**. O ambiente comprovado foi runtime **2026.07**, Python 3.12.13;
   se essa versão não estiver disponível, valide a compatibilidade antes de treinar.
2. Na primeira célula, habilite `MOUNT_BOOTSTRAP_DRIVE=True`, execute e autorize
   o acesso ao Drive. Na preparação, use `USE_SUPPORT_ZIP=True`.
3. Execute as células na ordem apresentada. Habilite `INSTALL_DEPENDENCIES`
   e `INSTALL_TF_GPU_LIBRARIES` na instalação inicial. A compatibilidade usada
   instala cuDNN 8 isolada para TensorFlow, preservando as bibliotecas do PyTorch.
   Se houver o conflito de JAX descrito na célula, use `REMOVE_UNUSED_COLAB_JAX`
   somente no runtime temporário. Após um reinício, execute novamente as definições
   com as instalações já concluídas desativadas.
4. Em configuração, habilite `MOUNT_DRIVE`. Escolha um **novo `SESSION_NAME`**.
   Na preparação do experimento, habilite `EXTRACT_DATASET` apenas se `data/`
   ainda não existir, além de `PREPARE_YOLO`, `INSTALL_YOLO_DEPENDENCIES` na
   primeira instalação e `RUN_PREFLIGHT`. Mantenha `RUN_EXPERIMENTS=False`
   até o diagnóstico passar.
5. Confira **Dataset validado**, as 80 imagens, a distribuição 64/8/8 e a
   disponibilidade de GPU nos dois frameworks. O notebook verifica os hashes
   dos ZIPs e bloqueia datasets inconsistentes. Não substitua o pacote de apoio
   original: seu hash faz parte dessa conferência.
6. Habilite `START_FINAL_EXPERIMENTS` e execute os experimentos em ordem:
   YOLO do zero 30/60 épocas, seleção pela validação, teste da selecionada,
   YOLO COCO, CNN por 30 épocas e comparação. Para a seção 15, use uma nova
   `IMPROVEMENT_SESSION_NAME` e os controles próprios de preparação, instalação,
   treino e teste. O teste complementar depende da seleção e validação.
7. Salve o notebook executado. `EXPORT_RESULTS=True` gera o pacote dos resultados
   pequenos. Pesos e runs permanecem em `experiments/`, fora do Git.

Os controles estão **False** no notebook entregue para evitar reexecutar
treinamentos ao abrir o arquivo. Não sobrescreva as sessões de referência
`fase6_final_001` e `fase6_transfer_001`, nem extraia o dataset sobre uma pasta
existente. Sem GPU ou diante de falhas no diagnóstico, resolva a inconsistência
antes de executar os treinos, mantendo os parâmetros previstos.

## Resultados e apresentação

[Notebook executado](https://colab.research.google.com/drive/1tOPqLqF--WRhIR8VweO8-4SQi4PKFW-j)
e [vídeo de apresentação](https://youtu.be/xQRzp8BzaPY), 4min34s, não listado.
Veja [análise](results_analysis.md), [arquitetura](architecture.md) e
[melhoria complementar](model_improvement.md). A melhoria preserva os baselines
do zero e usa um teste retrospectivo; não ajuste parâmetros pelos acertos do teste.
