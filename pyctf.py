"""This is the main interface for the Python CTF library. It adds a few
things to the SWIG wrapped layer."""

import os, math
import ctf                      # SWIG module
from markers import markers
from getHC import getHC
from getHM import getHM
import fid
#from sensortopo import sensortopo

class dsWrap(ctf.MEGH):         # These methods are added to the ds object after it is created.

	def getSensorList(self, cls = ctf.TYPE_MEG):
		"Return a list of the channel names in ds, of class cls."

		nchan = self.getNumberOfChannels()
		l = []
		for i in range(nchan):
			if self.getChannelType(i) == cls:
				l.append(self.getChannelName(i))
		return l

	def pretrig(self):
		"Return the pretrigger length in seconds"

		return self.getPreTrig()

	def getTimePt(self, samp):
		"Convert a sample number within a trial to a time in seconds."

		preTrig = self.getPreTrig()
		return float(samp) / self.getSampleRate() - preTrig

	def getSampleNo(self, t):
		"Convert a time in seconds to a relative sample number."

		t += self.getPreTrig()
		return int(math.floor(t * self.getSampleRate() + .5))

	def removeProcessing(self):
		pass

	def isAverage(self):
		return self.getAvg() > 0

	def getHLCData(self, t, chan):
		return getHM(self, t, chan)

# This is the top level interface, pyctf.dsopen()

def dsopen(dsname):
	if dsname[-1] == '/':
		dsname = dsname[:-1]
	s = os.path.splitext(dsname)
	if s[1] != '.ds':
		raise Exception, "%s is not a dataset name" % dsname

	# get the SWIG wrapper for MEGH and change its class

	ds = ctf.dsopen(dsname)
	ds.__class__ = dsWrap

	# create a mapping from channel name to number

	d = {}
	for m in range(ds.getNumberOfChannels()):
	    n = ds.getChannelName(m).split('-')[0]
	    d[n] = m
	ds.channel = d

	# get the marks, if any
	ds.marks = markers(dsname)

	# get the dewar coordinates of the head from the hc file, if any
	hc = ds.dsname + '/' + ds.setname + '.hc'
	try:
		n, l, r = getHC(hc, 'dewar')
		ds.dewar = n, l, r

		# compute the transform into the head frame
		ds.dewar_to_head = fid.fid(n, l, r)

		# compute the head coordinates in the head frame
		ds.head = [fid.fid_transform(ds.dewar_to_head, x) for x in ds.dewar]
	except:
		pass
	return ds

