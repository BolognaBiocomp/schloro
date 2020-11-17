#!/usr/bin/env python

import sys
sys.path.append("/home/savojard/BUSCA/tools/schloro/sclpred/tools")
import numpy
import os
from modules.cpparser import BlastCheckPointProfile

profile = numpy.array(BlastCheckPointProfile(sys.argv[1]))

outdir = sys.argv[2]
prefix = sys.argv[3]

oproff = open(os.path.join(outdir, "%s.prof" % prefix), 'w')

for i in range(profile.shape[0]):
  for j in range(profile.shape[1]):
    oproff.write("%.2f " % profile[i,j])
  oproff.write("\n")
