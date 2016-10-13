rm(list=ls())
gc()
library(Gmisc)
# n = 10
path = '/home/benjello/openfisca/fonction-publique/fonction_publique/sandox/transition_matrix.csv'
position_path = '/home/benjello/openfisca/fonction-publique/fonction_publique/sandox/position.csv'
transitions = read.csv(path, row.names = "initial", stringsAsFactors = FALSE)
positions = read.csv(position_path, row.names = "initial", stringsAsFactors = FALSE)
transition_mtrx = transitions  # [1:n, 1:n]
htmlTable(transition_mtrx, title = "Transitions", ctable = TRUE)

transitionPlot(transition_mtrx)

library(reshape2)
library(riverplot)

proto_edges = transition_mtrx
proto_edges['N1'] = rownames(transition_mtrx)  
proto_edges
edges = melt(proto_edges, id.var = 'N1', variable.name = 'N2', value.name = 'Value', factorsAsStrings = TRUE)
edges$N2 = as.character(edges$N2)

nodes <- data.frame(ID = unique(c(edges$N1, edges$N2)), stringsAsFactors = FALSE)
rownames(nodes) <- nodes$ID
nodes
nodes$y = c(1:(nrow(nodes)/2), 1:(nrow(nodes)/2))
library(RColorBrewer)
palette = paste0(brewer.pal(4, "Set1"), "60")

styles = lapply(nodes$y, function(n) {
  list(col = palette[n+1], lty = 0, textcol = "black")
  })
names(styles) = nodes$ID
r <- makeRiver(
  nodes, 
  edges, 
  node_xpos = c(rep(1, nrow(nodes)/2), rep(2, nrow(nodes)/2)),
  node_styles = styles
  )
r
plot(r) 

x <- riverplot.example()
plot(x)
x
