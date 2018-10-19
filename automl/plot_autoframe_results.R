# makes binary classification plots 
# (from ggplot's documentation)
# The lower and upper hinges correspond to the first and third quartiles (the 
# 25th and 75th percentiles). The whiskers extend from the hinge to the 
# largest/smallest value no further than 1.5 * IQR from the hinge (where IQR is the 
# inter-quartile range, or distance between the first and third quartiles).
# Data beyond the end of the whiskers are called "outlying" points and are
# plotted individually. In a notched box plot, the notches extend
# 1.58 * IQR / sqrt(n). This gives a roughly 95% confidence interval for 
# comparing medians. See McGill et al. (1978) for more details.
# level 0 of the dataframe is the negative class! So, it's usually the first one
# alphabetically, except for diganosis groups, where nv=1, rem=2, per=3, so
# remission is the negative. Improvers are always the negative as well, 


res_file = '~/Documents/baseline_prediction/autoframeDL_summary_10192018.csv'

multiplot <- function(..., plotlist=NULL, file, cols=1, layout=NULL, t_str, leg) {
  library(grid)

  # Make a list from the ... arguments and plotlist
  plots <- c(list(...), plotlist)

  numPlots = length(plots)

  # If layout is NULL, then use 'cols' to determine layout
  if (is.null(layout)) {
    # Make the panel
    # ncol: Number of columns of plots
    # nrow: Number of rows needed, calculated from # of cols
    layout <- matrix(seq(1, cols * ceiling(numPlots/cols)),
                    ncol = cols, nrow = ceiling(numPlots/cols))
  }

 if (numPlots==1) {
    print(plots[[1]])

  } else {
    # Set up the page, adding two new rows one for title and one for legend
    grid.newpage()
    pushViewport(viewport(layout = grid.layout(nrow(layout) + 2, ncol(layout), 
                                               heights = unit(c(.5, .5, 4, 4),
                                                              "null"))))
    grid.text(t_str, vp = viewport(layout.pos.row = 1, layout.pos.col = 1:3))
    leg$vp = viewport(layout.pos.row = 2, layout.pos.col = 1:3)
    grid.draw(leg)
    # Make each plot, in the correct location
    for (i in 1:numPlots) {
      # Get the i,j matrix positions of the regions that contain this subplot
      matchidx <- as.data.frame(which(layout == i, arr.ind = TRUE))
      print(plots[[i]], vp = viewport(layout.pos.row = matchidx$row + 2,
                                      layout.pos.col = matchidx$col))
    }
  }
}

g_legend <- function(a.gplot){ 
  tmp <- ggplot_gtable(ggplot_build(a.gplot)) 
  leg <- which(sapply(tmp$grobs, function(x) x$name) == "guide-box") 
  legend <- tmp$grobs[[leg]] 
  return(legend)} 


library(ggplot2)
res = read.csv(res_file)
targets = unique(res$target)

# modifying phenotypes for legend
levels(res$pheno)[grepl('aparc', levels(res$pheno))] <- "rsFMRI"
levels(res$pheno)[grepl('ad', levels(res$pheno))] <- "DTI; AD"
levels(res$pheno)[grepl('ALL', levels(res$pheno))] <- "DTI; all"
levels(res$pheno)[grepl('thick', levels(res$pheno))] <- "thickness"
mycolors=c('red','orange','yellow', 'green', 'cyan', 'navy', 'purple')

for (target in targets) {
    print(sprintf('Drawing %s', target))

    p1<-ggplot(res[res$target == target,], aes(x=pheno, y=auc, fill=pheno)) +
    geom_boxplot(notch=T) + ylim(0, 1) + labs(y = "Area under ROC curve") + 
    theme(legend.title=element_blank(), legend.position="top")
    # add number of permutations to the labels
    phenos = unique(res$pheno)
    labels = c()
    for (p in phenos) {
        idx = res$target == target & res$pheno == p
        ngood = sum(!is.na(res[idx,]$auc))
        labels = c(labels, sprintf('%s (%d perms)     ', p, ngood))
    }
    p1 = p1 + scale_fill_manual(breaks=phenos, labels=labels, values=mycolors)
    p1 = p1 + geom_hline(yintercept=.5, linetype="dashed", color = "black") 
    p2<-ggplot(res[res$target == target,], aes(x=pheno, y=f1, fill=pheno)) +
    geom_boxplot(notch=T) + ylim(0, 1) + labs(y = "F1-score (mean prec, sens)") + scale_fill_manual(breaks=phenos, labels=labels, values=mycolors)
    p3<-ggplot(res[res$target == target,], aes(x=pheno, y=acc, fill=pheno)) +
    geom_boxplot(notch=T) + ylim(0, 1) + labs(y = "Accuracy")+ scale_fill_manual(breaks=phenos, labels=labels, values=mycolors)

    # let's add some horizontal lines for random accuracy
    cnt = 1
    for (p in phenos) {
        idx = res$target == target & res$pheno == p
        ratio = unique(as.character(res[idx,]$ratio))
        dummy = as.numeric(max(strsplit(ratio, ';')[[1]]))
        p3 = p3 + geom_hline(yintercept=dummy, linetype="dashed", color = mycolors[cnt]) 
        cnt = cnt + 1
    }
    p4<-ggplot(res[res$target == target,], aes(x=pheno, y=sens, fill=pheno)) +
    geom_boxplot(notch=T) + ylim(0, 1) + labs(y = "Sensitivity (TP/(TP+FN))")+ scale_fill_manual(breaks=phenos, labels=labels, values=mycolors)
    p5<-ggplot(res[res$target == target,], aes(x=pheno, y=spec, fill=pheno)) +
    geom_boxplot(notch=T) + ylim(0, 1) + labs(y = "Specificity (TN/(TN+FP))")+ scale_fill_manual(breaks=phenos, labels=labels, values=mycolors)
    p6<-ggplot(res[res$target == target,], aes(x=pheno, y=prec, fill=pheno)) +
    geom_boxplot(notch=T) + ylim(0, 1) + labs(y = "Precision/PPV (TP/(TP+FP))")+ scale_fill_manual(breaks=phenos, labels=labels, values=mycolors)
    t = theme(axis.title.x=element_blank(),
            axis.text.x=element_blank(),
            axis.ticks.x=element_blank(),
            legend.position="none")
    leg = g_legend(p1)

    pic_fname = sprintf('~/tmp/%s.pdf', target)
    pdf(pic_fname) 
    multiplot(p1 + t, p4 + t, p3 + t, p5 + t , p2 + t, p6 + t, cols=3, t_str=target, leg=leg)
    dev.off()
}
