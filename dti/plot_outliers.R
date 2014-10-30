library(ggplot2)
data_dir = '~/data/dti_longitudinal/'
gf_name = sprintf('%s/boys_girls_gf.txt', data_dir)
s='FA'
data_name = sprintf('%s/all_%s_skeletonised.txt', data_dir,s)
gf = read.table(gf_name, sep='\t', header=1)
colnames(gf) = c('maskid','mrn','age')
brain_data = read.table(data_name)
data = as.matrix(brain_data[,4:dim(brain_data)[2]])
mean_data = colMeans(data)

####
# settings with NV boys only
# outliars = c(1273,1009,1430,488,306,394,950)
# gt15 = c(708,1011,1273)
# gt12 = c(708,1011,1273,806,1451,1009,1430,306,314,488,1154,373,1217,708,1011,
#          1273,1010,1429,1009,1430,806,1451)
# rm_me = c(outliars, gt12)
####

####
# settings with everybody
gt15 = c(708,1011,1182,1247,1273)
outliers = c(295,303,306,311,325,352,394,398,461,488,577,643,695,823,1009,1023,
             1229,1273,1315,1369,1456)
rm_me = c(outliers, gt15)

idx = vector(length=length(mean_data), mode='logical')
for (i in rm_me) {
    idx = idx | gf$maskid==i
}
df = data.frame(age=gf$age[!idx],mean=mean_data[!idx],group=as.factor(gf$mrn[!idx]))
p = ggplot(df,aes(x=age,y=mean,color=group))+geom_point(size=5)+geom_line()+
    ggtitle(s) + theme(legend.position="none")
print(p)
