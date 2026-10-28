# Validação funcional local — FarmTech Fase 7

## Resultado e liberação

Os fluxos funcionais locais passaram, com **43 testes no ambiente atual e os mesmos
43 em uma instalação limpa de Python 3.11.18**, criada a partir dos requisitos.
A dashboard respondeu HTTP 200/`ok`. **O upload e a inferência também foram confirmados
no Chrome**, com a amostra enviada manualmente pelo usuário e execução do botão
“Analisar imagem”: imagem anotada, classe de sinais de doença e confiança de 0,6494.
O evento visual permaneceu salvo após reiniciar a dashboard.

**O critério funcional local está atendido para iniciar a etapa de validação AWS.**
O servidor foi reiniciado para carregar os arquivos finais. A inferência e a imagem
no Chrome foram verificadas na sessão anterior ao reinício; a permanência do
resultado em reruns da versão final foi testada no Streamlit AppTest com modelo real.
Reiniciar o servidor abre nova sessão de upload, sem apagar imagens e eventos salvos.

Não houve publicação AWS, envio de e-mail, commit ou push. Credenciais e modelos
anteriores foram preservados. EC2, SNS real e chegada dos e-mails continuam sujeitos
à validação no laboratório, conforme a etapa adiada pelo usuário.

## Verificações executadas

| Área | Evidência de funcionamento |
|---|---|
| Fase 1 | Retângulo 100×200 m = 2 ha; dose 12 kg/ha = 24 kg; círculo, CSV e rejeição de valores inválidos |
| R | Script real, sete variáveis, estatísticas conferidas com pandas e gráfico gerado |
| Clima | Consulta real; indisponibilidade produz erro de previsão sem interromper dashboard |
| IoT | Dez leituras, reprodução temporizada, repetição histórica sem duplicatas e nova simulação com horário atual |
| ESP32 | Sketch original compilado; RAM 21.656 bytes e flash 278.453 bytes; hardware não conectado |
| Oracle | Dez registros mantidos; importações repetidas e duas simultâneas inseriram zero; consultas real e pela dashboard |
| Fase 4 | Seis treinos reais, três modelos selecionados e previsões finitas em cópias isoladas; originais preservados |
| Dashboard | Seis abas, ações reais de serviços, métricas/previsões, falhas externas isoladas e upload com modelo real via AppTest |
| Visão | Inferência CPU, imagem anotada, hashes, arquivo corrompido rejeitado e limite de 10 MB |
| PlantDoc | 530/134/69 imagens, todos os 733 hashes exportados e caixas verificados; nenhum grupo ou SHA entre splits |
| Alertas | Limites, chuva forte, consolidação, supressão por talhão/30 min, falhas, backoff, concorrência e lease |
| Monitor | Processo independente da dashboard, leitura nova, reinício e continuidade; publicador local de teste |
| SNS | Contrato do SDK validado com botocore Stubber; nenhum envio externo |
| Notebooks | Cinco documentos válidos; notebooks revisado da Fase 6 e de resultados agrícolas reexecutados |
| Instalação | Ambiente limpo sem PyTorch opcional passou a suíte; dependências atuais e sintaxe do instalador Linux conferidas |

## Correções aplicadas

- Eventos inválidos são isolados com `processed=-1` e erro visível no histórico;
  não impedem o processamento das próximas leituras. Migração preserva o SQLite existente.
- Payloads visuais exigem classes/confianças válidas; imagens inválidas e talhão vazio
  são rejeitados antes de carregar o detector.
- Monitoramento filtra talhão/origem no banco antes de limitar a quantidade de eventos.
- Resultado visual permanece nos reruns e fica associado ao hash da imagem e ao talhão.
- Programa antigo de treino passa pelo mesmo contrato JSON da CLI; quatro adaptadores
  foram testados também fora da pasta do projeto.
- Versão mínima do Streamlit alinhada à versão efetivamente testada (1.49.1).
- Firmware fixa Espressif32 6.9.0 e DHT 1.4.6. A configuração anterior sem versão
  buscava dependências novas que falharam na extração por caminhos longos no Windows.
  A configuração fixada compilou sem modificar o sketch. Referência da plataforma:
  [manifesto oficial](https://raw.githubusercontent.com/platformio/platform-espressif32/v6.9.0/platform.json).

## Limitações comprovadas

O detector continua um protótipo: mAP50:95 de teste **0,3758**, falsos positivos e
omissões registrados. Nesta auditoria, imagem branca e ruído geraram falsos positivos
com confiança aproximada de **0,409 e 0,345**. Nenhum dos dois acionou a regra de
alerta de 0,50. O caso sem detecções foi validado com saída controlada do detector,
produzindo “Inconclusivo” sem alerta. Não alteramos os limiares para favorecer os testes.

Wokwi/ESP32 físico não foram executados: a entrada demonstrativa integrada é o replay
CSV, identificado como simulação. A compilação não comprova comportamento elétrico.

EC2, perfil do laboratório, SNS real e recebimento de e-mails só podem ser comprovados
na etapa AWS, adiada pelo usuário. Publicação aceita pelo SNS e chegada à caixa devem
ser registradas separadamente. Estes requisitos da entrega continuam pendentes.

Firmware compilado SHA-256: `ea9d7e898c62f6762d17fe1893051279a13b6cb84910738d2513594cee483850`.

## Evidências e reprodução

Projeto: `C:/Pessoal/faculdade/Cap-1-Um-Mapa-do-Tesouro`.
Veja `docs/evidencias/auditoria-local/` no projeto e os JSONs em `validacao-local/`
nos outputs. Os identificadores de publicação locais começam com `LOCAL`/`test`
ou pertencem ao Stubber; não são apresentados como evidência AWS.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m streamlit run dashboard/src/dashboard.py
```

**Commit sugerido:** `fix(farmtech): corrige fluxos e valida integração local`

Evidência adicional: `docs/evidencias/auditoria-local/visao-navegador.json` e screenshot `visao-navegador.png`. Nenhum e-mail foi enviado nessa verificação.
