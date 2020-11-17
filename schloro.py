import os
import sys
import argparse
from Bio import SeqIO

SCHLORO_ROOT = os.environ.get('SCHLORO_ROOT')
sys.path.append(SCHLORO_ROOT)

from schlorolib import workenv
from schlorolib import blast
from schlorolib import utils

def main():
    DESC="SChloro: Predictor of sub-chloroplastic localization"
    parser = argparse.ArgumentParser(description=DESC)
    parser.add_argument("-f", "--fasta",
                        help = "The input multi-FASTA file name",
                        dest = "fasta", required = True)
    parser.add_argument("-d", "--dbfile",
                        help = "The PSIBLAST DB file",
                        dest = "dbfile", required= True)
    parser.add_argument("-o", "--outf",
                        help = "The output tabular file",
                        dest = "outf", required = True)

    ns = parser.parse_args()

    we = workenv.TemporaryEnv()
    for record in SeqIO.parse(open(fasta), 'fasta'):
        acc = record.id
        sequence = str(record.seq)
        fasta_file = we.createFile("seq.", ".fasta")
        SeqIO.write([record], fasta_file, 'fasta')
        psiblast_pssm, _ = blast.runPsiBlast("aseq", ns.dbfile, fasta_file, we)
        elm_input_file, pssm_mat = utils.elm_encode_protein(sequence, psiblast_pssm, we)
        features = utils.schloro_feature_predict(elm_input_file, we)
        svm_input_file = utils.svm_encode_protein(pssm_mat, features)
        localizations, probs = utils.schloro_localization_predict(svm_input_file, we)
        utils.write_output(ns.outf, localizations, probs)
        sys.exit(0)

if __name__ == "__main__":
    main()
