# from
# https://raw.githubusercontent.com/stylianos-kampakis/logisticSPCA/master/R/supervised_pca.R

#this function computes the pca_matrix for a given alpha parameter
spca.computePCA<-function(input){
  
  pca_matrix<-prcomp(as.matrix(input))
  
  return(pca_matrix)
  
}

#this function returns a the indices of the columns to be kept
#the input should be a data.frame and the target a vector
spca.selectInputs<-function(input,target,alpha,family=binomial()){
  num_col<-ncol(input)
  keep<-logical(num_col)
  
  #select the variables
  for (i in 1:num_col){
    
    m1<-glm.fit(matrix(c(rep(1,length(input[[i]])),as.numeric(as.vector(input[[i]]))),ncol=2),
                as.vector(target),family=family)
    #first coef is always intercept
    if(abs(coef(m1)[2])>alpha){
      keep[i]=TRUE  
    }
    else{
      
      keep[i]=FALSE
    }
    
  }
  
  return(keep)
  
}


#runs glm supervised PCA and returns the predictions
#if components is not provided, then it calculates the components on the input data
#PCA_matrix can be computed by the function spca.computePCA
predict.spca<-function(model,input,num_components){
  
  
  if(is.null(pca_matrix)){
    pca_matrix<-spca.computePCA(input,target,alpha,family)
  }
  
  input<-data.frame(predict(pca_matrix,data))
  
  if(num_components<ncol(inputs)){
    inputs=inputs[,1:num_components]
  }
  
  
  res<-predict(model,input,type="response")
  
  return(res)
  
}

#conducts logistic supervised PCA and returns the model
spca.fit<-function(input,target,alpha,family=binomial()){
  keep=spca.selectInputs(input,target,alpha,family)
  
  input=input[,keep]
  input=apply(input,2,function(x) as.numeric(x))
  
  pca_matrix<-spca.computePCA(input)
  input=predict(pca_matrix,input)
  
  m1<-glm.fit(input,target,family=family)
  class(m1)=append(class(m1),"spca")
  
  m1$pca_matrix=pca_matrix
  m1$keep_columns_index=keep
  
  return(m1)
  
}

summary.spca<-function(model){
  
  return(summary.glm(model))
}