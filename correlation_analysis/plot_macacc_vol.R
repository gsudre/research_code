# set up roi variable first!
brainSeed = c('thalamusR')
brainTarget = c('cortexR')

getSlopes <- function(baseApprox, baseData, fuApprox, fuData) {
    slopes = array()
    slopes[1] = lm(baseApprox ~ rowSums(baseData))$coefficients[2]
    slopes[2] = lm(fuApprox ~ rowSums(fuData))$coefficients[2]
    return(slopes)
}

nperms=1000
library(ggplot2)
bootstrapCI <- function() 
{
    slopes <- array(data=0, dim=c(nperms, 3))
    for (p in 1:nperms) {
        cnt = 1
        for (g in c('NV','remission','persistent')) {
            nsubjs = sum(group==g & idx_base)
            blabels = sample.int(nsubjs, replace = TRUE)
            gidxb = which(group==g & idx_base)[blabels]
            gidxf = which(group==g & idx_last)[blabels]
            tmp = 0
            for (i in 1:length(brainSeed)) {
                txt = sprintf('%s[idx_base | idx_last,]', brainSeed[i])
                eval(parse(text=sprintf('data=cbind(%s)', txt)))
                approx = rowMeans(data)
                txt = sprintf('%s[,%sroi]', brainTarget[i], brainTarget[i])
                eval(parse(text=sprintf('data=cbind(%s)', txt)))
                tmp = getSlopes(approx[gidxb], data[gidxb,], 
                                approx[gidxf], data[gidxf,])
                slopes[p,cnt] = slopes[p,cnt] + (tmp[2]-tmp[1])
            }
            cnt = cnt + 1
        }
    }
    cis = array(dim=c(3,2))
    # find out the CI for each slope
    for (s in 1:3) {
        sortedSlopes = sort(slopes[,s])
        cis[s,1] = sortedSlopes[ceiling(.025*nperms)]
        cis[s,2] = sortedSlopes[ceiling(.975*nperms)]
    }
    return(cis)
}

df = data.frame(group=c('NV','NV','remission','remission','persistent','persistent'),
                visit=c('baseline','last','baseline','last','baseline','last'))
df$slopes = 0
df2 = data.frame(group=c('NV','remission','persistent'))
df2$slopes = 0
df2$lci = 0
df2$uci = 0

for (i in 1:length(brainSeed)) {
    txt = sprintf('%s[idx_base | idx_last,]', brainSeed[i])
    eval(parse(text=sprintf('data=cbind(%s)', txt)))
    approx = rowMeans(data)
    txt = sprintf('%s[,%sroi]', brainTarget[i], brainTarget[i])
    eval(parse(text=sprintf('data=cbind(%s)', txt)))

    for (g in c('NV','remission','persistent')) {
        df$slopes[df$group==g] = getSlopes(approx[group==g & idx_base], data[group==g & idx_base,],
                                           approx[group==g & idx_last], data[group==g & idx_last,])
    }

    df2$slopes[1] = df2$slopes[1] + df$slopes[2]-df$slopes[1]
    df2$slopes[2] = df2$slopes[2] + df$slopes[4]-df$slopes[3]
    df2$slopes[3] = df2$slopes[3] + df$slopes[6]-df$slopes[5]
}
ci = bootstrapCI()
df2$lci = df2$lci + ci[,1]
df2$uci = df2$uci + ci[,2]

df2[,2:4] = df2[,2:4]/max(df2[,2:4])  # normalizing units
p2 = ggplot(df2, aes(x=group, y=slopes)) + 
    geom_errorbar(aes(ymin=lci, ymax=uci), colour="black", width=.001, position=pd) +
    geom_point(size=8, position=pd) +
    theme_bw() + theme(text = element_text(size=32)) + labs(x=NULL, y=NULL)
    theme(legend.justification=c(1,0), legend.position=c(0.6,0))
print(p2) 