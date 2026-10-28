args <- commandArgs(trailingOnly=TRUE)
if (length(args) != 2) stop("Uso: Rscript analise.R entrada.csv pasta_saida")
dados <- read.csv(args[1], stringsAsFactors=FALSE)
colunas <- c("umidade", "temperatura", "ph", "n", "p", "k", "nivel_chuva")
if (!all(colunas %in% names(dados)) || nrow(dados) == 0) stop("CSV sem leituras ou colunas esperadas")
for (coluna in colunas) {
  if (!is.numeric(dados[[coluna]]) || any(!is.finite(dados[[coluna]]))) stop(paste("Dados inv\u00e1lidos:", coluna))
}
dir.create(args[2], recursive=TRUE, showWarnings=FALSE)
resumo <- data.frame(variavel=colunas,
  media=sapply(dados[colunas], mean), mediana=sapply(dados[colunas], median),
  desvio=sapply(dados[colunas], sd), minimo=sapply(dados[colunas], min), maximo=sapply(dados[colunas], max))
write.csv(resumo, file.path(args[2], "estatisticas.csv"), row.names=FALSE)
png(file.path(args[2], "sensores.png"), width=1200, height=800)
par(mfrow=c(2,2))
for (coluna in c("umidade", "temperatura", "ph")) plot(dados[[coluna]], type="o", main=coluna, xlab="Leitura simulada", ylab=coluna)
barplot(colSums(dados[c("n","p","k")]), main="Presen\u00e7a de nutrientes", ylab="Leituras")
dev.off()
print(resumo)
