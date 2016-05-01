data = read.table('~/tmp/myvals.txt')
cmin = 0
cmax = 1
cstep = .01

vals = seq(cmin, cmax, cstep)
colors = colorRampPalette(c('white', 'blue'))(length(vals))
for (v in data[, 1]) {
    pos = which(vals >= v)[1]
    rgb = col2rgb(colors[pos])
    print(sprintf('%f -> R=%d, G=%d, B=%d', v, rgb[1], rgb[2], rgb[3]))
}
