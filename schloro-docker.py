#!/usr/bin/env python
import os
import sys
import argparse
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt="[%a, %d %b %Y %H:%M:%S]")
from Bio import SeqIO

SCHLORO_ROOT = os.environ.get('SCHLORO_ROOT')
sys.path.append(SCHLORO_ROOT)

from schlorolib import workenv
from schlorolib import blast
from schlorolib import utils
from schlorolib import config

def run_multifasta(ns):
    we = workenv.TemporaryEnv()
    ofs = open(ns.outf, 'w')
    print("##gff-version 3", file = ofs)
    try:
        for record in SeqIO.parse(ns.fasta, 'fasta'):
            acc = record.id
            logging.info("Processing sequence %s" % acc)
            sequence = str(record.seq)
            fasta_file = we.createFile("seq.", ".fasta")
            SeqIO.write([record], fasta_file, 'fasta')
            logging.info("Running PSIBLAST")
            dbfile = os.path.join(config.DOCKER_PSIBLAST_DBDIR, os.path.basename(ns.dbfile))
            psiblast_pssm, _ = blast.runPsiBlast("aseq", dbfile, fasta_file, we)
            logging.info("Predicting topological features")
            elm_input_file, pssm_mat = utils.elm_encode_protein(sequence, psiblast_pssm, we)
            features = utils.schloro_feature_predict(elm_input_file, we)
            logging.info("Predicting subchloroplastic localization")
            svm_input_file = utils.svm_encode_protein(pssm_mat, features, we)
            localizations, probs = utils.schloro_localization_predict(svm_input_file, we)
            logging.info("Done, writing results to output file.")
            utils.write_gff_output(acc, sequence, ofs, localizations, probs)
        ofs.close()
    except:
        logging.exception("Errors occurred:")
        sys.exit(1)
    else:
        we.destroy()
        sys.exit(0)

def run_pssm(ns):
    we = workenv.TemporaryEnv()
    ofs = open(ns.outf, 'w')
    print("##gff-version 3", file = ofs)
    try:
        record = SeqIO.read(ns.fasta, "fasta")
    except:
        logging.exception("Error reading FASTA: file is not FASTA or more than one sequence is present")
        sys.exit(1)
    else:
        acc = record.id
        logging.info("Processing sequence %s" % acc)
        sequence = str(record.seq)
        logging.info("Using user-provided PSSM file, skipping PSIBLAST")
        psiblast_pssm = ns.psiblast_pssm
        try:
            utils.check_sequence_pssm_match(sequence, psiblast_pssm)
        except:
            logging.exception("Error in PSSM: sequence and provided PSSM do not match.")
            sys.exit(1)
        else:
            try:
                fasta_file = we.createFile("seq.", ".fasta")
                SeqIO.write([record], fasta_file, 'fasta')
                logging.info("Predicting topological features")
                elm_input_file, pssm_mat = utils.elm_encode_protein(sequence, psiblast_pssm, we)
                features = utils.schloro_feature_predict(elm_input_file, we)
                logging.info("Predicting subchloroplastic localization")
                svm_input_file = utils.svm_encode_protein(pssm_mat, features, we)
                localizations, probs = utils.schloro_localization_predict(svm_input_file, we)
                logging.info("Done, writing results to output file.")
                utils.write_gff_output(acc, sequence, ofs, localizations, probs)
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

    subparsers   = parser.add_subparsers(title = "subcommands",
                                         description = "valid subcommands",
                                         help = "additional help",
                                         required = True)

    multifasta  = subparsers.add_parser("multi-fasta",
                                        help = "Multi-FASTA input module",
                                        description = "SChloro: Multi-FASTA input module.")
    pssm  = subparsers.add_parser("pssm", help = "PSSM input module (one sequence at a time)",
                                  description = "SChloro: PSSM input module.")
    multifasta.add_argument("-f", "--fasta",
                            help = "The input multi-FASTA file name",
                            dest = "fasta", required = True)
    multifasta.add_argument("-d", "--dbfile",
                            help = "The PSIBLAST DB file",
                            dest = "dbfile", required= True)
    multifasta.add_argument("-o", "--outf",
                        help = "The output GFF3 file",
                        dest = "outf", required = True)
    multifasta.set_defaults(func=run_multifasta)

    pssm.add_argument("-f", "--fasta",
                        help = "The input FASTA file name (one sequence)",
                        dest = "fasta", required = True)
    pssm.add_argument("-p", "--pssm",
                        help = "The PSIBLAST PSSM file",
                        dest = "psiblast_pssm", required= True)
    pssm.add_argument("-o", "--outf",
                        help = "The output GFF3 file",
                        dest = "outf", required = True)
    pssm.set_defaults(func=run_pssm)
    if len(sys.argv) == 1:
        parser.print_help()
    else:
        ns = parser.parse_args()
        ns.func(ns)


if __name__ == "__main__":
    main()
