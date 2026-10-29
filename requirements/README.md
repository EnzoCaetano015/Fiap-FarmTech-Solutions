# Dependências

Execute os comandos na raiz do repositório, usando Python 3.11 e o ambiente virtual ativo.
As versões e faixas existentes foram preservadas na reorganização.

| Arquivo | Uso | Inclui |
|---|---|---|
| `base.txt` | Dashboard, CLI e serviços comuns | Dependências da aplicação |
| `dev.txt` | Desenvolvimento e validação de notebooks | `base.txt` e nbformat |
| `visao.txt` | Inferência agrícola e treinamento no Colab GPU | `base.txt`, PyTorch e utilitários de visão |
| `constraints-colab.txt` | Fixação de versões do ambiente de visão | Restrições; não instala pacotes por si só |

## Aplicação

```bash
python -m pip install -r requirements.txt
streamlit run dashboard/app.py
```

O `requirements.txt` da raiz aponta para `requirements/base.txt`, mantendo o
comando de instalação usado pelas ferramentas de deploy.

## Desenvolvimento

```bash
python -m pip install -r requirements/dev.txt
python -m unittest discover -s tests -v
```

## Visão agrícola

```bash
python -m pip install -r requirements/visao.txt -c requirements/constraints-colab.txt
```

O checkout oficial YOLOv5 v7.0 também precisa de suas próprias dependências,
instaladas com as mesmas constraints. Veja o [guia do Colab](../docs/colab.md).
Na EC2, o [instalador](../infra/aws/install-ec2.sh) seleciona PyTorch CPU.

O estudo de objetos mantém um ambiente independente em
[`experiments/objetos/requirements.txt`](../experiments/objetos/requirements.txt).
Consulte o [guia dos notebooks](../notebooks/README.md) antes de reproduzi-lo.
