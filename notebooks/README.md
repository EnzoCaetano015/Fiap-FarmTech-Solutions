# Notebooks por domínio

| Notebook | Finalidade |
|---|---|
| [tomate/treinamento_colab.ipynb](tomate/treinamento_colab.ipynb) | Preparação dos dados, treinamento agrícola com GPU e exportação do bundle |
| [tomate/resultados.ipynb](tomate/resultados.ipynb) | Síntese dos resultados agrícolas |
| [objetos/relatorio.ipynb](objetos/relatorio.ipynb) | Relatório acadêmico de YOLO/CNN com saídas preservadas |
| [objetos/reproducao.ipynb](objetos/reproducao.ipynb) | Reprodução do estudo de objetos a partir dos pacotes históricos |
| [objetos/original.ipynb](objetos/original.ipynb) | Registro original do experimento de objetos |

O fluxo agrícola usa o projeto atual e os perfis em `requirements/`.
Siga o [guia do Colab](../docs/colab.md) e envie o projeto completo, incluindo
essa pasta, no arquivo `FarmTech.zip`.

O estudo de objetos usa os pacotes externos `fase6_colab_preparacao.zip` e
`dataset_fase6_final.zip`, indicados no notebook de reprodução. O pacote de apoio
recria a estrutura histórica `fase6/`; os caminhos desse ambiente não apontam
diretamente para as pastas atuais do repositório. Configurações e resultados
versionados estão em [experiments/objetos](../experiments/objetos/).

Saídas, métricas e identificadores dos experimentos anteriores são registros
históricos. Preserve-os ao reorganizar arquivos. Novos treinamentos devem gerar
novas pastas de sessão conforme o fluxo de cada notebook.
