# Validação real da revisão no Make Sense

Data: 02/10/2026. Ferramenta: https://www.makesense.ai/.
Método: revisão assistida por IA, com inspeção visual das capturas do editor e correções pelos
controles do site. Referência inicial: caixas do Open Images, sem detector.

Foram revisadas 80 imagens e obtidas duas exportações YOLO reais (64 + 16).
Os 80 labels oficiais foram substituídos somente após a validação dos ZIPs.
O pedido atual do usuário de revisar as imagens coletadas ampliou a revisão
para validação/teste; as fotos, a distribuição e a separação dos splits foram
preservadas. O backup mantém todos os labels originais.

| Split | Imagens/labels | bottle | backpack | Caixas |
|---|---:|---:|---:|---:|
| test | 8 | 4 | 4 | 9 |
| train | 64 | 32 | 32 | 73 |
| val | 8 | 4 | 4 | 9 |

Total: 80 imagens, 80 labels e 91 caixas. Foram alteradas 13 imagens, sem troca
de classe. Nenhum label inválido, par ausente ou imagem com duas classes
anotadas foi encontrado. As contagens por classe continuam 32/4/4.
Diferenças apenas de arredondamento até 0,000002 não contam como correção.

| Split | Label alterado | Caixas antes → depois |
|---|---|---:|
| train | `backpack_20d393f65a9807c9.txt` | 1 → 1 |
| train | `backpack_23487f4bf993138c.txt` | 1 → 1 |
| train | `backpack_425e746b1b3ff4d8.txt` | 1 → 1 |
| train | `backpack_528219663af7c0d2.txt` | 1 → 2 |
| train | `backpack_6ea3590bdc6f214a.txt` | 1 → 1 |
| train | `backpack_76b8f1a90bcf997d.txt` | 1 → 1 |
| train | `backpack_80e7f359721d28d1.txt` | 2 → 1 |
| train | `backpack_838932fef9f0d687.txt` | 1 → 1 |
| train | `backpack_85afb20c62ea8d90.txt` | 1 → 1 |
| train | `backpack_8eb63dd5f3f7b7f4.txt` | 1 → 1 |
| train | `backpack_b33b34153db3acdd.txt` | 1 → 1 |
| train | `backpack_f96e6b95f8e12bf4.txt` | 1 → 1 |
| val | `backpack_fe5a65073bd23137.txt` | 1 → 1 |

As principais correções reduziram caixas que incluíam partes de pessoas,
ajustaram caixas em fundo branco, acrescentaram uma mochila azul ausente
e removeram a mala com rodinhas marcada como mochila. As demais caixas
foram conferidas e mantidas. A contagem total se mantém porque uma caixa
foi acrescentada e outra removida.

## Evidências e integridade

- [Mochila vermelha com caixa ajustada](evidencias/makesense/train_002.png).
- [Mochila azul adicionada](evidencias/makesense/train_008.png).
- [Mala excluída da anotação](evidencias/makesense/train_017.png).
- [Garrafas revisadas](evidencias/makesense/train_033.png).
- [Caixa ajustada em validação/teste](evidencias/makesense/val_test_008.png).
- [Exportação de treino](evidencias/makesense/export_train_dialog.png).
- [Exportação de validação/teste](evidencias/makesense/export_val_test_dialog.png).

CRC dos dois ZIPs: sem falhas. Todos os nomes correspondem a uma única
imagem no split correto; IDs são 0/1, valores finitos, dimensões positivas,
centros normalizados e bordas dentro de [0,1] com tolerância de 0,00001
para arredondamento. O mapeamento de classes da exportação foi conferido.

SHA-256 da exportação de treino: `3320e5cc7c872a6dc4e4c8fecfd05c2659c704d72ff58024b44c750ae763f7e7`.
SHA-256 da exportação de validação/teste: `c4db38f4ce99be9a109c0bcfbd881209e305597e034ed04be35deaf540e6ee3b`.

## Limitações

A revisão foi assistida por IA, não é uma declaração de revisão humana
independente realizada pelo aluno. Os labels seguem a classe de foco de
cada imagem, preservando o contrato da CNN; objetos incidentais da outra
classe não foram anotados exaustivamente. Isso limita a avaliação de detecção.
`bottle_084b363c71a7f958.jpg` mostra a representação impressa de uma garrafa
em uma máquina; `backpack_b33b34153db3acdd.jpg` é uma candidata a mochila com
rodinhas. Esses casos da seleção original foram preservados e devem ser
considerados nas conclusões. Não foi executado treinamento nesta revisão.

## Verificações após integração

O validador do notebook retornou `ready`, com 80 imagens, 80 labels e manifesto
de 80 linhas. As 22 células de código foram executadas localmente com
`RUN_EXPERIMENTS=False`; o smoke test real da CNN em CPU produziu `(1, 2)`.
O schema nbformat está válido e os outputs do notebook permaneceram vazios.
Os hashes das 80 fotos correspondem à proveniência original. Os 160 arquivos
de fotos/labels e os ZIPs locais continuam ignorados. O diff ficou limitado
a `fase6/`, sem erros de whitespace, treinamento, pesos ou resultados fictícios.

Commit sugerido: `feat(fase6): revisa rotulos no Make Sense e registra evidencias`.

Evidência complementar da lista de classes, recarregada no site nesta preparação: [bottle e backpack](evidencias/makesense/classes_bottle_backpack.png). Esta captura documenta a configuração, sem substituir as exportações e evidências da revisão original.
