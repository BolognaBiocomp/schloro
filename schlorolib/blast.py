import subprocess
from . import config as cfg

def runPsiBlast(acc, dbfile, fastaFile, workEnv):
  psiblastStdOut   = workEnv.createFile(acc+".psiblast_stdout.", ".log")
  psiblastStdErr   = workEnv.createFile(acc+".psiblast_stderr.", ".log")
  psiblastOutPssm  = workEnv.createFile(acc+".psiblast.", ".pssm")
  psiblastOutAln   = workEnv.createFile(acc+".psiblast.", ".aln")

  sequence = "".join([x.strip() for x in open(fastaFile).readlines()[1:]])
  subprocess.call(['psiblast', '-query', fastaFile,
                   '-db', dbfile,
                   '-out', psiblastOutAln,
                   '-out_ascii_pssm', psiblastOutPssm,
                   '-num_iterations', cfg.PSIBLAST_ITERATIONS,
                   '-evalue', cfg.PSIBLAST_EVALUE],
                   stdout=open(psiblastStdOut, 'w'),
                   stderr=open(psiblastStdErr, 'w'))
  return psiblastOutPssm, psiblastOutAln

def makeblastdb(dbfile):
  subprocess.call(['makeblastdb', '-in', dbfile, '-dbtype', 'prot'])
