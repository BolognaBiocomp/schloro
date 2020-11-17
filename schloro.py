import sys
import os
import numpy
import cPickle
import argparse
from sklearn.svm import SVC
from lxml import etree
from Bio import SeqIO
import tempfile
import subprocess

SCLPREDHOME="/home/savojard/BUSCA/tools/schloro/sclpred"

def main():
    DESC="SChloro: Predictor of sub-chloroplastic localization"
    parser = argparse.ArgumentParser(description=DESC)
    parser.add_argument("-f", "--fasta",
                        help = "The input multi-FASTA file name",
                        dest = "fasta", required = True)
    parser.add_argument("-o", "--outf",
                        help = "The output tabular file",
                        dest = "outf", required = True)
    ns = parser.parse_args()

    


if __name__ == "__main__":
    main()

def getNewTmpFile(prefix, suffix):
  outTmpFile = tempfile.NamedTemporaryFile(mode   = 'write',
                                           prefix = prefix,
                                           suffix = suffix,
                                           delete = False)
  outTmpFileName = outTmpFile.name
  outTmpFile.close()
  return outTmpFileName

def svmpredict(modelfile, x):
  datfname = getNewTmpFile("protein",".dat")
  outfname = getNewTmpFile("protein",".pred")
  datf = open(datfname, 'w')
  datf.write("0")
  for i in range(x.shape[1]):
    datf.write(" %d:%f" % (i+1, x[0,i]))
  datf.write("\n")
  datf.close()

  subprocess.call([os.path.join(SCLPREDHOME, 'tools', 'svm-predict'), '-b', '1', datfname, modelfile, outfname], stdout=open('/dev/null'))
  line = open(outfname).readlines()[1].split()
  pcl = int(line[0])
  prob = float(line[2])
  os.unlink(datfname)
  os.unlink(outfname)
  return pcl, prob

locmap = {0: ('Chloroplast > Chloroplast_Inner_Membrane', 'inner'),
          1: ('Chloroplast > Chloroplast_Outer_Membrane', 'outer'),
          2: ('Chloroplast > Thylakoid > Chloroplast_Thylakoid_Lumen', 'lumen'),
          3: ('Chloroplast > Chloroplast_Stroma', 'stroma'),
          4: ('Chloroplast > Thylakoid > Chloroplast_Thylakoid_Membrane', 'membrane'),
          5: ('Chloroplast > Plastoglobule', 'plastoglobule')}

featmap = {'ctp': ('Chloroplast-targeting peptide', 'transit_peptide', 0.63),
           'ttp': ('Thylakoid-targeting peptide', 'transit_peptide', 0.36),
           'spmem': ('Single-pass membrane protein', 'membrane_topology', 0.43),
           'mpmem': ('Multi-pass membrane protein', 'membrane_topology', 0.51),
           'pmem' : ('Peropheral membrane protein', 'membrane_topology', 0.27)}

fasta=sys.argv[3]
for record in SeqIO.parse(open(fasta), 'fasta'):
  acc = record.id
  length = str(len(record.seq))

  pssm = numpy.mean(numpy.array([map(float, x.split()) for x in open(sys.argv[1]).readlines()]), axis=0).reshape(1,20)
  features = {}
  for line in open(sys.argv[2]).readlines():
    line = line.split()
    features[line[1]] = (int(line[2]),float(line[3]))

  v = numpy.array([features['ctp'][0], features['ttp'][1], features['spmem'][1], features['mpmem'][1], features['pmem'][1]]).reshape(1, 5)
  x = numpy.concatenate((pssm, v), axis=1)


  ypred=[]
  yprob=[]
  for c in range(6):
    #clf = cPickle.load(open("/home/savojard/sclpred/data/svm/SCEXP2016-ML.6lab.c%d.model" % c))
    #pcl = clf.predict(x)[0]
    #prob = clf.predict_proba(x)[0,1]
    pcl, prob = svmpredict(os.path.join(SCLPREDHOME, "data", "svm", "SCEXP2016-ML.6lab.c%d.model" % c), x)
    ypred.append(pcl)
    yprob.append(prob)
    #ypred.append(clf.predict(x).reshape((1,1)))
    #yprob.append(clf.predict_proba(x).reshape((1,2)))
    #p.append((clf.predict(x), clf.predict_proba(x)))
  #ypred = numpy.concatenate(tuple(ypred), axis=1)
  #yprob = numpy.concatenate(tuple(yprob), axis=1)
  ypred = numpy.array(ypred)
  yprob = numpy.array(yprob)

  if numpy.sum(ypred) == 0:
    ypred[numpy.argmax(yprob)]=1

  root = etree.Element('protein_prediction', attrib = {'tool' : 'sclpred'})
  pinfo = etree.SubElement(root, "protein_info", attrib = {'id' : acc})
  etree.SubElement(pinfo, "length").text = length


  # TODO
  # attach probabilites to the predictions
  for feat in features:
    if features[feat][0] == 1:
      score = min(1.0, 0.5+(features[feat][1] - featmap[feat][2]))
      etree.SubElement(root, "global_feature", attrib = {'name':feat, 'id': featmap[feat][1], 'type' : 'string', 'score': str(round(score,2))}).text = featmap[feat][0]

  for c in range(6):
    if ypred[c] == 1:
      if yprob[c] < 0.5:
        score = 0.7
      else:
        score = round(yprob[c],2)
      etree.SubElement(root, "global_feature", attrib = {'id':'localization', 'name': locmap[c][1], 'type' : 'string', 'score': str(score)}).text = locmap[c][0]

  print etree.tostring(root, pretty_print = True)
  break
