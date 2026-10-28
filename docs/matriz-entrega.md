# Matriz de atendimento e aceite

| Requisito | Implementação/evidência | Situação |
|---|---|---|
| Pasta única com serviços | farmtech/services + dados, SQL e ESP32 preservados | Implementado |
| Dashboard evoluída da Fase 4 | Seis abas e funções compartilhadas com CLI | Testado localmente |
| Fase 1 Python/R | Área, insumos, CSV, estatística R e API climática | Python/R e consulta real à API climática validados |
| Fase 2 IoT | Protótipo preservado e replay temporizado identificado como simulação | Replay testado; hardware não conectado |
| Fase 3 Oracle | Importação incremental transacional e consulta | Validado no Oracle real: 10 inserções, repetição sem duplicatas e consulta pela dashboard |
| Fase 4 ML | Modelos/recomendador existentes integrados | Base sintética explicitada; carga e previsão verificadas na interface |
| Revisão Fase 6 | Notebook enxuto, reprodução auxiliar e original preservado | Revisão executada lendo artefatos reais |
| Detector agrícola | Preparação PlantDoc e treino Colab 30/60 | Treinos reais concluídos, seleção por validação e quatro inferências CPU verificadas |
| Infraestrutura AWS | Preflight, configuração EC2/SNS e serviços systemd | Consultar evidencias/STATUS.md |
| E-mail com ação corretiva | Fila, regras, supressão, repetição e MessageId | Código testado; chegada de e-mail exige demonstração real |
| Documentação integrada | README, arquitetura, Windows, EC2, Colab e roteiro | Entregue |
| IA AWS/algoritmos genéticos | Desafios opcionais | Fora do escopo aprovado |

Uma pendência externa não deve ser substituída por screenshot simulado ou métrica
estimada. Atualize a situação somente após executar e registrar a evidência.

Auditoria ampliada: [43 testes e integrações reais](validacao-local.md). Upload real via framework aprovado; upload, inferência e imagem anotada confirmados também no Chrome. Firmware compilado. EC2/SNS/e-mail recebido permanecem sem comprovação.
