# need to run dissimilarity.R first to get the data matrices!
roi1 = 'VP'
roi2 = 'VL'
nperms=1000

bootstrapSE <- function(data, nperms) 
{
    corrs <- vector(mode = "numeric", length = nperms) 
    num_subjs = dim(data)[1]
    for (i in 1:nperms) {
        perm_labels <- sample.int(num_subjs, replace = TRUE)
        perm_data <- data[perm_labels, ]
        corrs[i] = cor(perm_data)[2]
    }
    return(sd(corrs)/sqrt(num_subjs))
}

x = which(colnames(nmatb)==roi1)
y = which(colnames(nmatb)==roi2)
df = data.frame(group=c('NV','NV','remission','remission','persistent','persistent'),
                visit=c('baseline','follow-up','baseline','follow-up','baseline','follow-up'))
df$corr = c(ncorb[x,y],ncorl[x,y],rcorb[x,y],rcorl[x,y],pcorb[x,y],pcorl[x,y])
df$se = c(bootstrapSE(nmatb[,c(x,y)],nperms),bootstrapSE(nmatl[,c(x,y)],nperms),
          bootstrapSE(rmatb[,c(x,y)],nperms),bootstrapSE(rmatl[,c(x,y)],nperms),
          bootstrapSE(pmatb[,c(x,y)],nperms),bootstrapSE(pmatl[,c(x,y)],nperms))

pd = position_dodge(.1)
p = ggplot(df, aes(x=visit, y=corr, colour=group, group=group)) + 
    geom_errorbar(aes(ymin=corr-se, ymax=corr+se), colour="black", width=.1, position=pd) +
    geom_line(position=pd) +
    geom_point(position=pd, size=3, shape=21, fill="white") + # 21 is filled circle
    xlab("Visit") +
    ylab(sprintf("Correlation between %s and %s", roi1, roi2)) +
    scale_colour_hue(name="Groups", # Legend label, use darker colors
                     breaks=c("NV", "remission", "persistent"),
                     labels=c("NV", "remission", "persistent"),
                     l=40) +                  # Use darker colors, lightness=40
    ggtitle("Difference in correlations over time") +
#     scale_y_continuous(limits=c(0, max(dfc$len + dfc$se)),    # Set y range
#                        breaks=0:20*4) +                       # Set tick every 4
    theme_bw() +
    theme(legend.justification=c(1,0), legend.position=c(1,0))
print(p)