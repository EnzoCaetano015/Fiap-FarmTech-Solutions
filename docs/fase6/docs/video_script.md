# Roteiro do vídeo — até cinco minutos

[Assistir ao vídeo de apresentação](https://youtu.be/xQRzp8BzaPY) — **4min34s**, publicação **não listada**. URL, título, duração e indicador de visibilidade conferidos na página do YouTube em 13/10/2026. A conferência de metadados não constitui uma revisão integral do conteúdo do vídeo.

| Tempo | Tela e fala sugerida |
|---|---|
| 0:00–0:25 | README/notebook: nome/RM e comparação de YOLO própria, COCO e CNN, classes bottle/backpack. |
| 0:25–0:55 | Dataset e evidências Make Sense: 80 fotos, 40 por classe, 32/4/4, 91 caixas. Explicar a origem Open Images e a revisão/exportação dos labels no Make Sense. |
| 0:55–1:45 | Tabela 30/60 e curvas: yolov5s do zero, 640, batch 16, seed 42, patience 0. Val mAP50:95 0,000096376 versus 0,040407; 165,22/294,21 s. Seleção de 60 pela validação, checkpoint época 59. |
| 1:45–2:25 | Teste e painel YOLO: mAP50:95 0,005039; nenhuma caixa a 0,25. COCO detectou garrafas, nenhuma mochila. Mostrar que garrafa incidental na foto backpack é real. COCO mAP indisponível; confiança não é precisão. |
| 2:25–3:15 | CNN: três blocos, 224×224, batch 8, 30 épocas, checkpoint val_loss época 29. Curvas, matriz [[4,0],[1,3]], accuracy 7/8=87,5%, F1 macro 0,8730. Mostrar mochila classificada como bottle. |
| 3:15–4:10 | Benchmark: médias 34,22/20,97/16,99 ms; medianas 35,99/20,22/16,30 ms. Mesmas oito imagens/T4, warm-up excluído. Entradas/tarefas diferentes; accuracy não equivale a mAP. COCO mais direta, YOLO exige caixas/treino, CNN classifica sem localizar. |
| 4:10–4:45 | Conclusões: ganho de validação não virou bom teste YOLO; CNN acertou 7/8 nesse teste pequeno, sem provar generalização. Limitações: 8 imagens, anotação de foco, ausência de mochilas detectadas. Mais dados/revisão independente são trabalhos futuros. |
| 4:45–5:00 | Mostrar arquivos, notebook com outputs, evidências e repositório publicado; pesos/runs no Drive. Encerrar antes de 5 minutos. |

Ensaie e confirme duração. Use resultados reais e mantenha atribuições das fotos.
Não exponha credenciais/autorização do Drive. Preserve a procedência das anotações e o método de revisão registrado na documentação. Publique como **não listado**, envie URL e duração para incluir
no README e conferir acesso. URL publicada: [YouTube](https://youtu.be/xQRzp8BzaPY). Duração conferida: **4min34s**.


Atualização para a gravação: na parte YOLO, mostrar o baseline fraco e em seguida
a melhoria COCO, deixando explícita a inicialização pré-treinada. Seleção val:
60 épocas/época 58; teste mAP50:95
0.7597. Mostrar imagens com caixas corretas das duas classes e
contagens por classe. Substituir tempo de explicação existente; não exceder cinco
minutos. Dizer que o teste adicional é retrospectivo e a base é pequena.
