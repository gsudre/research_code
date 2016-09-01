# gets specific columns Philip needs from a CSV file
import sys
import glob


dir_name = '/Volumes/Shaw/VR Project/2015:2016/Participants_E/'
files = glob.glob(dir_name + '*_Hist.csv')

header = ['fname', '5Deg', '10Deg', '20Deg', 'In FOV'] + ['%d dg' % d for d in range(-135, 136)]
data = [header]
for fname in files:
	fid = open(fname, 'r')
	line = fid.readline()
	row = [fname.split('/')[-1]]
	while len(line) > 0:
		# print line
		if line.find("Time Spent") >= 0 and line.find("Percentage") >= 0:
			line = fid.readline()
			line = fid.readline()
			row += line.split(',')[6:10]
		if line.find("Histogram - Yaw (percent)") >= 0:
			line = fid.readline()
			dg = []
			cnt = 0
			while cnt < 271:
				line = fid.readline()
				items = line.split(',')[1]
				dg.append(items)
				cnt += 1
			row += dg
		line = fid.readline()
	fid.close()
	data.append(row)

fout = open(dir_name + 'cropped.csv', 'w')
for r in data:
	fout.write(','.join(r) + '\n')
fout.close() 