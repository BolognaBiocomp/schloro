import numpy as np
from . import config as cfg
from . import cppparser as pbp

def seq_to_hydro(sequence):
    v = []
    for aa in sequence:
        v.append(cfg.KD.get(aa, 0.0))
    return np.array(v)

def elm_encode_protein(sequence, psiblast_pssm, we):
    output_dat = we.createFile("elm.input.",".dat")
    hydrophobicity = seq_to_hydro(sequence)
    pssm_mat = pdb.BlastCheckPointPSSM(psiblast_pssm)
    mat = np.concatenate((pssm_mat,hydrophobicity),axis=1)
    np.savetxt(output_dat, mat)
    return output_dat, pssm_mat

def elm_predict(elmproffile, elmmodel, elmbin, we):
    elmdatlistfile = we.createFile("elm.",".list.txt")
    elmoutputfile = we.createFile("elm.",".out.txt")
    elmprofdir = os.path.dirname(elmproffile)
    olist = open(elmdatlistfile, 'w')
    olist.write("%s 0.0\n" % os.path.basename(elmproffile))
    olist.close()
    serr = we.createFile("elm.",".serr")
    sout = we.createFile("elm.",".sout")
    sp.check_call([elmbin,
                   '-p',
                   elmprofdir,
                   '-i',
                   elmdatlistfile,
                   '-m',
                   elmmodel,
                   '-o',
                   elmoutputfile,
                   '-l', '-t', '-w', '27', '-d', '20', '-b'],
                  stderr = open(serr, 'w'),
                  stdout = open(sout, 'w'))
    ret = float(open(elmoutputfile).read().strip().split()[2])
    return ret

def schloro_feature_predict(elm_input_file, we):
    features = []
    for ft in ['ctp', 'ttp', 'spmem', 'mpmem', 'pmem']:
        v = elm_predict(elm_input_file, cfg.ELM_MODELS[ft], cfg.ELMBIN, we)
        features.append(v)
    return np.array(features).reshape(1,5)

def svm_encode_protein(pssm_mat, features):
    output_dat = we.createFile("svm.input.",".dat")
    mat = np.concatenate((np.mean(pssm_mat,axis=0),features), axis=1)
    datf = open(output_dat, 'w')
    datf.write("0")
    for i in range(x.shape[1]):
      datf.write(" %d:%f" % (i+1, mat[0,i]))
    datf.write("\n")
    datf.close()
    return output_dat

def schloro_localization_predict(svm_input_file, we):
    ypred=[]
    yprob=[]
    for c in range(0,6):
        outfname = we.createFile("svm.output.c%d." % c,".dat")
        subprocess.call([cfg.SVMBIN, '-b', '1', svm_input_file, cfg.SVM_MODELS[c], outfname], stdout=open('/dev/null'))
        line = open(outfname).readlines()[1].split()
        pcl = int(line[0])
        prob = float(line[2])
        ypred.append(pcl)
        yprob.append(prob)
    if np.sum(ypred) == 0:
        ypred[np.argmax(yprob)]=1
    return ypred, yprob

def write_output(output_file, localizations, probs):
    pass
