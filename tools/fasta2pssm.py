#!/usr/bin/env python

import sys
from Bio import SeqIO
import numpy

try:
  seqrec = SeqIO.parse(open(sys.argv[1]), 'fasta')
except:
  raise

outdir = sys.argv[2]
prefix = sys.argv[3]
#aaOrder = 'VLIMFWYGAPSTCHRKQEND'
#Changed 10/09/2017
aaOrder = "ARNDCQEGHILKMFPSTWYV"

for record in seqrec:
  try:
    #outfile = open(outdir + '/' + record.id + '.i', 'w')
    outfile = open(outdir + '/' + prefix + '.pssm', 'w')
  except: 
    raise
  seq = str(record.seq)
  for aa in seq:
    v = numpy.zeros(20)
    try:
      i = aaOrder.index(aa)
      v[i] = 1.0
    except ValueError:
      pass
    l = ''
    for el in v:
      l += '%1.1f ' % el
    outfile.write(l[:-1]+'\n')
  outfile.close()

