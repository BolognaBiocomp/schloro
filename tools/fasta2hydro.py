#!/usr/bin/env python

import sys
from Bio import SeqIO
from Bio.SeqUtils import ProtParam, ProtParamData
import numpy

try:
  seqrec = SeqIO.parse(open(sys.argv[1]), 'fasta')
except:
  raise

outdir = sys.argv[2]
prefix = sys.argv[4]

aaOrder = 'VLIMFWYGAPSTCHRKQEND'
w = int(sys.argv[3])
s={'A': 0.7, 'C': 0.7777777777777778, 'E': 0.1111111111111111, 'D': 0.1111111111111111, 'G': 0.4555555555555555, 'F': 0.8111111111111111, 'I': 1.0, 'H': 0.14444444444444443, 'K': 0.06666666666666668, 'M': 0.7111111111111111, 'L': 0.9222222222222223, 'N': 0.1111111111111111, 'Q': 0.1111111111111111, 'P': 0.3222222222222222, 'S': 0.41111111111111115, 'R': 0.0, 'T': 0.4222222222222222, 'W': 0.4, 'V': 0.9666666666666666, 'Y': 0.35555555555555557, 'X': 0.0}
for record in seqrec:
  try:
    outfile = open(outdir + '/' + prefix + '.hydro', 'w')
  except: 
    raise
  if not w == 1:
    seq = "X" * (w/2)  + str(record.seq) + "X" * (w/2)
    hydro = ProtParam.ProteinAnalysis(seq).protein_scale(s, w)
  else:
    seq = str(record.seq)
    hydro = [s[a] for a in seq]
  for v in hydro:
    outfile.write("%.3f\n" % v)
  outfile.close()

