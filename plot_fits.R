getStart <- function(y, x) 
{
    # scaling and shifting response so that it's between 0 and 1
    z = y
    if (min(z) <= 0) {
        z <- z - 1.05 * min(z)
    }
    z <- z/(1.05 * max(z))
    z <- log(z/(1 - z))
    xy = data.frame(y,x,z)
    aux <- coef(lm(x ~ z, xy))
    pars <- tryCatch({
        as.vector(coef(nls(y ~ 1/(1 + exp((xmid - x)/scal)), data = xy, start = list(xmid = aux[1L], scal = aux[2L]), algorithm = "plinear")))
    }, error = function(err) {
        # If the nls fails, we could not find a good Asym parameter, so just 
        # go ahead and return the 75% quantile of the data
        #         print('getStart() did not converge, defaulting to quantiles...')
        c(aux[1L], aux[2L], quantile(y)[4])
    })
    value <- c(pars[3L], pars[1L], pars[2L])
    return(value)
}

tryModel <- function(dg) {
    pnlsCtl = c(.001, .01, .1, 1, 10)
    cur_control = 1
    initial = getStart(dg$y,dg$age)
    m.logis = 0
    while ((length(m.logis)<=1) && (cur_control <= length(pnlsCtl))) {
        m.logis <- tryCatch({
            nlme(y ~ SSlogis(age, Asym, xmid, scal), fixed=Asym+xmid+scal ~ 1, start=c(initial[1],initial[2],initial[3]), random=pdDiag(Asym ~ 1), data=dg, control=list(pnlsTol=pnlsCtl[cur_control]))
        }, error = function(err) {
            print(sprintf('ERROR: nmle() did not converge, trying pnlsTol=%.2f', pnlsCtl[cur_control+1]))
            0
        }, warning = function(war) {
            print(sprintf('WARNING: nmle() did not converge, trying pnlsTol=%.2f', pnlsCtl[cur_control+1]))
            0
        }, finally={cur_control <- cur_control + 1})
    }
    return(m.logis)
}

G1 = "NV"
G2 = "ADHD"
data = dtL_thalamus_1473
idx <- (gf_1473$DX==G1 | gf_1473$DX==G2) & gf_1473$MATCH5==1
d = data.frame(age=gf_1473[idx,]$AGESCAN, y=colSums(data[g,idx]), subject=as.factor(gf_1473[idx,]$PERSON.x),group=gf_1473[idx,]$DX)
dg<-groupedData(y~age|subject, data=d)
dgs = subset(dg,group==G1)
x=min(d$age):max(d$age)
fitG1 <- tryModel(dgs)
plot(dgs$age,dgs$y, xlab='Age', ylab='Surface area', col="blue")
betas <- fixef(fitG1)
lines(x,betas[1]/(1+exp((betas[2]-x)/betas[3])),col='blue', lwd=3)
print(sprintf('Group %s 99pct of asymptote: %.2f', G1, betas[2]-betas[3]*log(1/.99-1)))
print(sprintf('Group %s xmid: %.2f', G1, betas[2]))
dgs = subset(dg,group==G2)
initial = getStart(dgs$y,dgs$age)
fitG2 <- tryModel(dgs)
points(dgs$age,dgs$y, xlab='Age', ylab='Surface area', col="red")
betas <- fixef(fitG2)
lines(x,betas[1]/(1+exp((betas[2]-x)/betas[3])),col='red', lwd=3)
print(sprintf('Group %s 99pct of asymptote: %.2f', G2, betas[2]-betas[3]*log(1/.99-1)))
print(sprintf('Group %s xmid: %.2f', G2, betas[2]))
legend("bottomright", c(G1,G2), cex=0.8, col=c("blue","red"),lty=1, lwd=2, bty="n")