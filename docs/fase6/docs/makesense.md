# Revisão das anotações no Make Sense

Em 02/10/2026, foi utilizado https://www.makesense.ai/ para revisar todas as
80 imagens já coletadas: um projeto com 64 imagens de treino e outro com as
16 imagens de validação/teste. As caixas originais foram importadas como
referência; a revisão assistida por IA inspecionou capturas de cada imagem no editor e realizou
as correções com os controles de desenho e exclusão do próprio site.

## Procedimento reproduzível

1. Abra o Make Sense, carregue as imagens e escolha Object Detection.
2. Defina as classes na ordem `bottle`, `backpack`, correspondentes a 0 e 1.
3. Em Actions > Import Annotations, selecione YOLO e carregue os TXT com um
   `labels.txt` contendo essas duas classes, uma por linha.
4. Revise cada imagem, ajuste caixas para os objetos visíveis, remova rótulos
   incorretos e confira a classe de cada caixa. Nesta revisão, foi mantida
   a classe de foco de cada imagem, conforme o manifesto da CNN.
5. Em Actions > Export Annotations, escolha o pacote ZIP YOLO e Export.
6. Valide nomes, classes, coordenadas, dimensões positivas e correspondência
   com as imagens antes de integrar. Guarde a exportação original e um backup.

## Arquivos locais preservados

- `.artifacts/makesense/train_images.zip`: apenas as 64 fotos de treino.
- `.artifacts/makesense/train_makesense_export.zip`: exportação real de 64 labels.
- `.artifacts/makesense/val_test_makesense_export.zip`: exportação real de 16 labels.
- `.artifacts/makesense/labels_before_makesense.zip`: backup dos labels anteriores.
- `docs/evidencias/makesense/`: capturas reais do editor e das opções de exportação.

Os ZIPs e os labels estão ignorados pelo Git. O navegador cancelou o download
convencional; os bytes originais do Blob ZIP produzido pelo botão Export
foram capturados e gravados sem modificar o arquivo gerado pelo site.
Não houve geração de uma exportação substituta por conversão local.

A operação e a revisão visual foram assistidas por IA via automação de navegador.
Não foi realizada revisão humana independente.
Veja [contagens, mudanças e limitações](makesense_validation.md).
