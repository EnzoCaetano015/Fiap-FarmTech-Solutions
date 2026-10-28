# Dataset integrado — bottle e backpack

Foram salvas localmente 80 fotos do [Open Images](https://storage.googleapis.com/openimages/web/download_v7.html)
em 02/10/2026: 40 garrafas (`0: bottle`) e 40 mochilas (`1: backpack`).
As imagens foram inspecionadas visualmente; latas, potes, malas e bolsas de
ombro inadequadas foram descartadas. Fotos não foram geradas por IA.

| Split do projeto | bottle | backpack | Total |
|---|---:|---:|---:|
| train | 32 | 32 | 64 |
| val | 4 | 4 | 8 |
| test | 4 | 4 | 8 |
| Total | 40 | 40 | 80 |

Cada split contém `images/` com JPEGs e `labels/` com o TXT do mesmo stem.
São 80 labels, contendo 91 caixas delimitadoras. Os labels foram convertidos
das anotações existentes do Open Images para `class_id x_center y_center width height`,
com coordenadas normalizadas. Em 02/10/2026, as 80 imagens e seus labels foram
importados no Make Sense, revisados visualmente com assistência de IA e
exportados pelo próprio site. Foram ajustadas 13 imagens, incluindo uma
mochila ausente e a remoção de uma mala indevidamente marcada como mochila.
As caixas têm origem nas anotações do Open Images; a revisão assistida não equivale a uma revisão humana independente.
Veja [procedimento](../docs/makesense.md) e [validação](../docs/makesense_validation.md).

Os labels seguem a classe de foco original de cada imagem para manter o
contrato de classificação da CNN. Objetos incidentais da outra classe não
são anotados exaustivamente; isso limita a avaliação de detecção. Há também
uma foto de representação impressa de garrafa e uma candidata a mochila com
rodinhas. Essas limitações devem ser consideradas na análise acadêmica.

O manifesto da CNN usa os labels, não os nomes dos arquivos. Cada imagem tem
somente uma das duas classes de interesse; múltiplos objetos da mesma classe
são permitidos. A distribuição é por imagem, não por quantidade de caixas.

## Origem, licença e reprodução

- `sources.csv`: caminho local, ID, classe, split, URLs de download e original,
  autoria, perfil, título, licença informada na fonte, dimensões e SHA-256.
- `annotations_source.json`: bounding boxes originais e URLs dos CSVs oficiais.
- `dataset_summary.json`: contagens verificadas, seed 42 e método de anotação.

As imagens selecionadas vêm de 79 autores. Metadados da fonte informam
[CC BY 2.0](https://creativecommons.org/licenses/by/2.0/) para as fotos; as
anotações do Open Images são [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Preserve `sources.csv` para atribuição e consulte as páginas originais de cada
foto para sua licença atual. Os JPEGs foram copiados do bucket público oficial
sem recortar ou alterar pixels nesta coleta.

O subconjunto usa 75 imagens do split `test` e 5 do split `validation` da fonte.
Os splits do projeto foram definidos novamente em 32/4/4 por classe: não são
uma reprodução dos splits oficiais do Open Images. Autores repetidos ficam
somente no treino. Nenhum arquivo idêntico foi distribuído entre splits.

## Armazenamento

As fotos e seus labels estão salvos em `fase6/data/` e continuam ignorados
pelo Git. O clone do repositório não traz esses arquivos. Para Colab, transfira
o pacote do dataset ao Drive e extraia `data/` dentro da pasta da Fase 6, ou
configure `FASE6_DATASET` para o diretório que contém train, val e test.
Configurações, este README e os metadados de origem são versionáveis.
