import os
import sys
import subprocess
import logging
from . import config as cfg

def check_db_index(dbfile):
  for ext in ['phr', 'pin', 'psq']:
      if not os.path.isfile(dbfile + ".%s" % ext):
          return False
  return True

def runPsiBlast(acc, dbfile, fastaFile, workEnv, data_cache=None,
                num_iterations=3, num_alignments=5000, evalue=0.001,
                threads=1):
  psiblastStdOut   = workEnv.createFile(acc+".psiblast_stdout.", ".log")
  psiblastStdErr   = workEnv.createFile(acc+".psiblast_stderr.", ".log")
  psiblastOutPssm  = workEnv.createFile(acc+".psiblast.", ".pssm")
  psiblastOutAln   = workEnv.createFile(acc+".psiblast.", ".aln")
  psial2HSSPStdErr = workEnv.createFile(acc+".psial_stderr.", ".log")

  sequence = "".join([x.strip() for x in open(fastaFile).readlines()[1:]])
  exec_blast = True
  if data_cache is not None:
    if data_cache.lookup(sequence, "psiblast.pssm"):
      exec_blast = False
  if exec_blast:
    if not check_db_index(dbfile):
      makeblastdb(dbfile)
    try:
        subprocess.call(['psiblast', '-query', fastaFile,
                         '-db', dbfile,
                         '-out', psiblastOutAln,
                         '-out_ascii_pssm', psiblastOutPssm,
                         '-num_iterations', str(num_iterations),
                         '-evalue', str(evalue),
                         '-num_alignments', str(num_alignments),
                         '-num_threads', str(threads)],
                         stdout=open(psiblastStdOut, 'w'),
                         stderr=open(psiblastStdErr, 'w'))
        if data_cache is not None:
          data_cache.store(psiblastOutPssm, sequence, 'psiblast.pssm')
    except:
        logging.error("PSIBLAST failed. For details, please see stderr file %s" % psiblastStdErr)
        raise
  else:
    data_cache.retrieve(sequence, 'psiblast.pssm', psiblastOutPssm)
  return psiblastOutPssm

"""
def runPsiBlast(acc, dbfile, fastaFile, workEnv):
  psiblastStdOut   = workEnv.createFile(acc+".psiblast_stdout.", ".log")
  psiblastStdErr   = workEnv.createFile(acc+".psiblast_stderr.", ".log")
  psiblastOutPssm  = workEnv.createFile(acc+".psiblast.", ".pssm")
  psiblastOutAln   = workEnv.createFile(acc+".psiblast.", ".aln")

  sequence = "".join([x.strip() for x in open(fastaFile).readlines()[1:]])
  if not check_db_index(dbfile):
      makeblastdb(dbfile)

  try:
      subprocess.check_output(['psiblast', '-query', fastaFile,
                               '-db', dbfile,
                               '-out', psiblastOutAln,
                               '-out_ascii_pssm', psiblastOutPssm,
                               '-num_iterations', str(cfg.PSIBLAST_ITERATIONS),
                               '-evalue', str(cfg.PSIBLAST_EVALUE)],
                               stderr=open(psiblastStdErr, 'w'))
  except:
      logging.error("PSIBLAST failed. For details, please see stderr file %s" % psiblastStdErr)
      raise
  return psiblastOutPssm, psiblastOutAln
"""

def makeblastdb(dbfile):
  subprocess.call(['makeblastdb', '-in', dbfile, '-dbtype', 'prot'])
