
##### packages ####
library(data.table)
library(xtable)
library(DataCombine)
library(ggplot2)
library(Hmisc)

##### function ####

shift<-function(x,shift_by){
  stopifnot(is.numeric(shift_by))
  stopifnot(is.numeric(x))
  
  if (length(shift_by)>1)
    return(sapply(shift_by,shift, x=x))
  
  out<-NULL
  abs_shift_by=abs(shift_by)
  if (shift_by > 0 )
    out<-c(tail(x,-abs_shift_by),rep(NA,abs_shift_by))
  else if (shift_by < 0 )
    out<-c(rep(NA,abs_shift_by), head(x,-abs_shift_by))
  else
    out<-x
  out
}

shift1<-function(x){
  stopifnot(is.numeric(x))
  out<-NULL
  abs_shift_by=1
  out<-c(tail(x,-abs_shift_by),rep(NA,abs_shift_by))
  out
}

shift2<-function(x){
  stopifnot(is.numeric(x))
  out<-NULL
  abs_shift_by=2
  out<-c(tail(x,-abs_shift_by),rep(NA,abs_shift_by))
  out
}

lag1<-function(x){
  out<- Lag(x, shift = 1)
  out
}


shiftm1<- function(x)  #adapt? de shift  : cr?er une variable d?cal?e de 1 vers le base. 
{
  out <- shift(x,-1)
  return(out)
}

shiftm2<- function(x)  #adapt? de shift  : cr?er une variable d?cal?e de 1 vers le base. 
{
  out <- shift(x,-2)
  return(out)
}


lagm1<- function(x)  #adapt? de shift  : cr?er une variable d?cal?e de 1 vers le base. 
{
  out <-Lag(x, shift = -1)
  return(out)
}


