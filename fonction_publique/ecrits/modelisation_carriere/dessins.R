library(plotrix)
library(pBrackets)

### SCHEMAS CNRACL ###

### 0. Initialisation ####

place = "ipp"
if (place == "ipp"){
  data_path = "M:/CNRACL/output/"
  git_path =  'U:/Projets/CNRACL/fonction-publique/fonction_publique/'
}
if (place == "mac"){
  data_path = "/Users/simonrabate/Desktop/data/CNRACL/"
  git_path =  '/Users/simonrabate/Desktop/IPP/CNRACL/fonction_publique/'
}
fig_path = paste0(git_path,"ecrits/modelisation_carriere/Figures/")
                  
## IPP color
ncol <- c("darkcyan","cyan2")


pdf(paste0(fig_path,"schema_censoring.pdf"))
par(mar=c(3,3,1,1))
# Empty plot
# 2003 à 2020
plot(x=seq(1,18,1),y=rep(NA,18),ylim=c(0,40),axes=F,,type="n", xlab="", ylab="",xaxt="n",yaxt="n",ann=FALSE)
u <- par("usr") 
arrows(u[1], u[3], u[2]*0.9, u[3], xpd = TRUE, lwd = 3) 
abline(v=5, lwd=3)
abline(v=12, lwd=3)
axis(1, at=c(5, 12 ),labels=c("2011","2015"),tck=0)
# Cas 1: entrée en sortie dans les années
segments(x0= 6, x1=11, y0=35, y1=35,col=ncol[1],lwd=4,lty=1)
text((11+6)/2,  35, labels="(1)", pos=3,col="black")
# Cas 2: entrée avant sortie entre
segments(x0= 2, x1=8, y0=25, y1=25,col=ncol[1],lwd=4,lty=1)
text((2+10)/2,  25, labels="(2)", pos=3,col="black")
# Cas 3: entrée avant sortie après
segments(x0= 7, x1=15, y0=15, y1=15,col=ncol[1],lwd=4,lty=1)
text((7+13)/2,  15, labels="(3)", pos=3,col="black")
# Cas 4: entrée avant sortie après
segments(x0= 3, x1=14, y0=05, y1=05,col=ncol[1],lwd=4,lty=1)
text((3+14)/2,  05, labels="(4)", pos=3,col="black")
dev.off()





