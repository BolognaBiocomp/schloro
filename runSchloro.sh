#!/bin/bash


SCHLOROHOME=/home/savojard/BUSCA/tools/schloro

source /home/savojard/miniconda2/bin/activate schloro

wrp=${SCHLOROHOME}/sclpred_wrapper.sh

fasta=$1
#db=$2
pssm=$2
outxml=$3
outf=$4
tmpd=$5

#bash ${wrp} ${fasta} ${db} ${outxml} ${tmpd}
bash ${wrp} ${fasta} ${pssm} ${outxml} ${tmpd}
python ${SCHLOROHOME}/sclpred/tabize.py ${outxml} > ${outf}
