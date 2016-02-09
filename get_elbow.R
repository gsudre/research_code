# Finds the elbow in the plot based on the maximal distance to a line
# http://paulbourke.net/geometry/pointlineplane/pointline.r
distancePointSegment <- function(px, py, x1, y1, x2, y2) {
 ## px,py is the point to test.
 ## x1,y1,x2,y2 is the line to check distance.
 ##
 ## Returns distance from the line, or if the intersecting point on the line nearest
 ## the point tested is outside the endpoints of the line, the distance to the
 ## nearest endpoint.
 ##
 ## Returns 9999 on 0 denominator conditions.
 lineMagnitude <- function(x1, y1, x2, y2) sqrt((x2-x1)^2+(y2-y1)^2)
 ans <- NULL
 ix <- iy <- 0   # intersecting point
 lineMag <- lineMagnitude(x1, y1, x2, y2)
 if( lineMag < 0.00000001) {
   warning("short segment")
   return(9999)
 }
 u <- (((px - x1) * (x2 - x1)) + ((py - y1) * (y2 - y1)))
 u <- u / (lineMag * lineMag)
 if((u < 0.00001) || (u > 1)) {
   ## closest point does not fall within the line segment, take the shorter distance
   ## to an endpoint
   ix <- lineMagnitude(px, py, x1, y1)
   iy <- lineMagnitude(px, py, x2, y2)
   if(ix > iy)  ans <- iy
   else ans <- ix
 } else {
   ## Intersecting point is on the line, use the formula
   ix <- x1 + u * (x2 - x1)
   iy <- y1 + u * (y2 - y1)
   ans <- lineMagnitude(px, py, ix, iy)
 }
 ans
}

# for example
svd = eigen(cc)
absev = abs(svd$values)
plot(absev)


x=1:length(absev)
dists = vector()
for (i in x) {
    dists = c(dists, distancePointSegment(i, absev[i], x[1], absev[1], max(x), min(absev)))
}
pos = which.max(dists)
pct = sum(absev[1:pos])/sum(absev)
# Using M(eff) from SimpleM, as in http://www.ncbi.nlm.nih.gov/pubmed/19434714
cat(sprintf('Elbow = %d, %.2f of variance\n', pos, pct))
# Using M(eff) from Galwey 2009
meff = (sum(sqrt(absev))^2)/sum(absev)
cat(sprintf('Galwey Meff = %.2f\n', meff))