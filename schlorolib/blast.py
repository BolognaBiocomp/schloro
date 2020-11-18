import sys
import subprocess
import logging
from . import config as cfg

def runPsiBlast(acc, dbfile, fastaFile, workEnv):
  psiblastStdOut   = workEnv.createFile(acc+".psiblast_stdout.", ".log")
  psiblastStdErr   = workEnv.createFile(acc+".psiblast_stderr.", ".log")
  psiblastOutPssm  = workEnv.createFile(acc+".psiblast.", ".pssm")
  psiblastOutAln   = workEnv.createFile(acc+".psiblast.", ".aln")

  sequence = "".join([x.strip() for x in open(fastaFile).readlines()[1:]])
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

def makeblastdb(dbfile):
  subprocess.call(['makeblastdb', '-in', dbfile, '-dbtype', 'prot'])
