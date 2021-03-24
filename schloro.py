#!/usr/bin/env python
import os
import sys
import argparse
import logging
import json
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt="[%a, %d %b %Y %H:%M:%S]")
from Bio import SeqIO
if 'SCHLORO_ROOT' in os.environ:
    SCHLORO_ROOT = os.environ.get('SCHLORO_ROOT')
else:
    logging.error("SCHLORO_ROOT environment varible is not set")
    logging.error("Please, set and export SCHLORO_ROOT to point to schloro root folder")
    sys.exit(1)
sys.path.append(SCHLORO_ROOT)

from schlorolib import workenv
from schlorolib import blast
from schlorolib import utils
from schlorolib import config

def run_json(ns):
    we = workenv.TemporaryEnv()
    ifs = open(ns.i_json)
    input_json = json.load(ifs)
    ifs.close()
    try:
        protein_jsons = []
        #for record in SeqIO.parse(ns.fasta, 'fasta'):
        for i_json in input_json:
            acc = i_json['accession']
            logging.info("Processing sequence %s" % acc)
            sequence = i_json['sequence']['sequence']
            fasta_file = we.createFile("seq.", ".fasta")
            fsofs=open(fasta_file,'w')
            #SeqIO.write([fasta], fsofs, 'fasta')
            print(">%s" % acc, file=fsofs)
            print(sequence, file=fsofs)
            fsofs.close()
            logging.info("Running PSIBLAST")
            psiblast_pssm = blast.runPsiBlast("aseq", config.BLASTDB, fasta_file, we)
            logging.info("Predicting topological features")
            elm_input_file, pssm_mat = utils.elm_encode_protein(sequence, psiblast_pssm, we)
            features = utils.schloro_feature_predict(elm_input_file, we)
            logging.info("Predicting subchloroplastic localization")
            svm_input_file = utils.svm_encode_protein(pssm_mat, features, we)
            localizations, probs = utils.schloro_localization_predict(svm_input_file, we)
            logging.info("Done, writing results to output file.")
            acc_json = utils.get_json_output(i_json, localizations, probs)
            protein_jsons.append(acc_json)
        ofs = open(ns.outf, 'w')
        json.dump(protein_jsons, ofs, indent=5)
        ofs.close()
    except:
        logging.exception("Errors occurred:")
        sys.exit(1)
    else:
        we.destroy()
        sys.exit(0)

def main():
    DESC="SChloro: Predictor of sub-chloroplastic localization"
    parser = argparse.ArgumentParser(description=DESC, prog = "schloro.py")
    parser.add_argument("-i", "--i-json", help = "The input JSON file name", dest = "i_json", required = True)
    parser.add_argument("-o", "--outf", help = "The output GFF3 file", dest = "outf", required = True)
    ns = parser.parse_args()
    run_json(ns)


if __name__ == "__main__":
    main()
