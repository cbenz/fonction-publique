##### SORTIES POUR LA NOTE ####
library(stats)
library(xtable)
library(ggplot2)
### CVS des distributions 

path <- "C:/Users/s.rabate/Desktop/CNRACL/fonction_publique/bordeaux/results/"

table <- read.table(paste0(path,"destinations.csv"),sep=",", header=T)
table <- table[which(table[,1]=="annees_2011_2014"),]

# -NA
var = c("nombre","largest_1_pct","largest_2_pct","largest_3_pct","largest_5_pct")
table <- table[-1,]
table[,var[2:5]] <- table[,var[2:5]]*100

# Outcome moyen (avec/sans poids)
mean_var <- matrix(ncol=5,nrow=2)
var = c("nombre","largest_1_pct","largest_2_pct","largest_3_pct","largest_5_pct")

for(v in 1:length(var))
{
mean_var[1,v] <- mean(table[,var[v]])
mean_var[2,v] <- weighted.mean(table[,var[v]],w=table$population)
}


desc <- t(mean_var)


rownames(desc) <- c("Nombre de destinations","\% pour la destination majoritaire",
                    "\% pour les 2 destinations majoritaires","\% pour les 3 destinations majoritaires","\% pour les 5 destinations majoritaires")
colnames(desc) <- c("Moyenne simple","Moyenne pondérée")

print(xtable(desc,align="l|cc",
             caption="Destinations en cas de changement de grade",
             digit=1),sanitize.text.function=identity)



# Plot distribution: 
int <- seq(1,101,2)
distr_pct<- matrix(ncol=length(int),nrow=4)
for (t in 1:(length(int)))
{
distr_pct[1,t]<- length(which(table$largest_1_pct>=int[t] & table$largest_1_pct<int[t]+2))/length(table$largest_1_pct)
distr_pct[2,t]<- length(which(table$largest_2_pct>=int[t] & table$largest_2_pct<int[t]+2))/length(table$largest_2_pct)
distr_pct[3,t]<- length(which(table$largest_3_pct>=int[t] & table$largest_3_pct<int[t]+2))/length(table$largest_3_pct)
distr_pct[4,t]<- length(which(table$largest_5_pct>=int[t] & table$largest_5_pct<int[t]+2))/length(table$largest_5_pct)
}  

cdf <- matrix(ncol=length(int),nrow=4)
for (t in 1:(length(int)))
{
  cdf[1,t]<- length(which(table$largest_1_pct<int[t]+2))/length(table$largest_1_pct)
  cdf[2,t]<- length(which(table$largest_2_pct<int[t]+2))/length(table$largest_2_pct)
  cdf[3,t]<- length(which(table$largest_3_pct<int[t]+2))/length(table$largest_3_pct)
  cdf[4,t]<- length(which(table$largest_5_pct<int[t]+2))/length(table$largest_5_pct)
} 

df <- as.data.frame((distr_pct[3,]))
df$pct <- int
df$v_pct <- df[,3]

pdf(paste0(path,"distr_p3.pdf"))
ggplot(df,aes(x=pct,y=v_pct))+ 
  geom_bar(stat="identity",position="dodge") +
  xlab("% pour les trois destinations majoritaires")+ylab("Proportion")+ ylim(0, 0.15) + theme_bw()+
  theme(axis.text=element_text(size=15),axis.title=element_text(size=15,face="bold",vjust=-0.2),axis.title.y=element_text(vjust=0.1))
dev.off()


# Plot percentiles
percentile[1,]<- quantile(table$largest_1_pct,probs = seq(0, 1, 0.01))
percentile[2,]<- quantile(table$largest_2_pct,probs = seq(0, 1, 0.01))
percentile[3,]<- quantile(table$largest_3_pct,probs = seq(0, 1, 0.01))
percentile[4,]<- quantile(table$largest_5_pct,probs = seq(0, 1, 0.01))


pct <- seq(0,100,1)

pdf(paste0(path,"pct.pdf"))
x <- df$pct
n_col <- rev(c("black","grey30","grey60","grey80"))
par(ask=F)
layout(matrix(c(1,1), nrow=1,ncol=1, byrow=TRUE), heights=c(6))
par(mar=c(4.1,4.1,0.2,0.2))
plot  (x,rep(NA,length(x)),ylim=c(0,100),ylab="% des destinations en n+1",xlab="Percentile")
# lines(x,exit_rate_nomro[1,]       ,col=n_col[3],lwd=3, lty=2)
lines(x,percentile[1,],col=n_col[1],lwd=3)
lines(x,percentile[2,],col=n_col[2],lwd=3)
lines(x,percentile[3,],col=n_col[3],lwd=3)
lines(x,percentile[4,],col=n_col[4],lwd=3)
legend("bottomright",legend=c("1 destination principale","2 destinations principales","3 destinations principales","5 destinations principales"),
       col=n_col,ncol=1,lty=1,lwd=3)
dev.off()



