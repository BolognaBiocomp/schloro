import os
import numpy as np
import subprocess as sp
import logging
from . import config as cfg
from . import cpparser as pbp

def get_data_cache(cache_dir):
    import os
    from . import datacache
    ret = None
    if cache_dir is not None:
        if os.path.isdir(cache_dir):
            ret = datacache.DataCache(cache_dir)
    return ret

def seq_to_hydro(sequence):
    v = []
    for aa in sequence:
        v.append(cfg.KD.get(aa, 0.0))
    return np.array(v).reshape((len(sequence),1))

def elm_encode_protein(sequence, psiblast_pssm, we):
    output_dat = we.createFile("elm.input.",".dat")
    hydrophobicity = seq_to_hydro(sequence)
    pssm_mat = pbp.BlastCheckPointPSSM(psiblast_pssm)
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
                   '-l', '-t',
                   '-w', str(cfg.ELM_WINDOW),
                   '-d', str(cfg.ELM_INPUT_SIZE),
                   '-k', cfg.ELM_ACTIVATION,
                   '-b'],
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

def svm_encode_protein(pssm_mat, features, we):
    output_dat = we.createFile("svm.input.",".dat")
    mat = np.concatenate((np.mean(pssm_mat,axis=0).reshape(1,20),features), axis=1)
    datf = open(output_dat, 'w')
    datf.write("0")
    for i in range(mat.shape[1]):
      datf.write(" %d:%f" % (i+1, mat[0,i]))
    datf.write("\n")
    datf.close()
    return output_dat

def schloro_localization_predict(svm_input_file, we):
    ypred=[]
    yprob=[]
    for c in range(0,6):
        outfname = we.createFile("svm.output.c%d." % c,".dat")
        sp.call([cfg.SVMBIN, '-b', '1', svm_input_file, cfg.SVM_MODELS[c], outfname], stdout=open('/dev/null'))
        line = open(outfname).readlines()[1].split()
        pcl = int(line[0])
        prob = float(line[2])
        ypred.append(pcl)
        yprob.append(prob)
    if np.sum(ypred) == 0:
        ypred[np.argmax(yprob)]=1
    return ypred, yprob

def write_gff_output(acc, sequence, output_file, localizations, probs):
    l = len(sequence)
    for c in range(0,6):
        if localizations[c] == 1:
            print(acc, "SChloro", cfg.locmap[c][0], 1, l, probs[c], ".", ".",
            "Ontology_term=%s;evidence=ECO:0000256" % cfg.locmap[c][1],
            file = output_file, sep = "\t")

def get_json_output(acc, sequence, localizations, probs):
    acc_json = {'accession': acc, 'dbReferences': [], 'comments': []}
    acc_json['sequence'] = {
                              "length": len(sequence),
                              "sequence": sequence
                           }
    for c in range(0,6):
        if localizations[c] == 1:
            loc = cfg.locmap[c]
            go_info = cfg.GOINFO[loc[1]]
            acc_json['dbReferences'].append({
                "id": loc[1],
                "type": "GO",
                "properties": {
                  "term": go_info['GO']['properties']['term'],
                  "source": "IEA:SChloro",
                  "score": round(float(probs[c]),2)
                },
                "evidences": [
                  {
                    "code": "ECO:0000256",
                    "source": {
                      "name": "SAM",
                      "id": "SChloro",
                      "url": "https://schloro.biocomp.unibo.it",
                    }
                  }
                ]
            })
            acc_json['comments'].append({
                "type": "SUBCELLULAR_LOCATION",
                "locations": [
                  {
                    "location": {
                      "value": go_info["uniprot"]["location"]["value"],
                      "score": round(float(probs[c]),2),
                      "evidences": [
                        {
                          "code": "ECO:0000256",
                          "source": {
                            "name": "SAM",
                            "id": "SChloro",
                            "url": "https://schloro.biocomp.unibo.it",
                          }
                        }
                      ]
                    }
                  }
                ]
            })
    return acc_json

def check_sequence_pssm_match(sequence, psiblast_pssm):
    try:
        pssm_mat = pbp.BlastCheckPointPSSM(psiblast_pssm)
    except:
        logging.error("Failed reading/parsing PSSM file")
        raise
    else:
        try:
            assert(len(sequence) == pssm_mat.shape[0])
        except:
            logging.error("Sequence and PSSM have different lengths")
            raise

    return True
