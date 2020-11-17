#!/bin/bash

# Signature: tpppredr.sh $sequence $uniref90 $sclpred_output

#source ~/anaconda2/bin/activate schloro
#source activate schloro

SCHLOROHOME=/home/savojard/BUSCA/tools/schloro

seq=$1
#uni=$2
pssm=$2
out=$3
tmpd=$4

tools=${SCHLOROHOME}/sclpred/tools
bin=${SCHLOROHOME}/sclpred
data=${SCHLOROHOME}/sclpred/data


#tmpd=tmp-$(echo $$)

#mkdir -p ${tmpd}


bn=$(basename $seq .fasta)

#psiblast -db $uni -query $seq -evalue 0.001 -out_ascii_pssm ${tmpd}/$(basename $seq .fasta).blast.pssm -num_iterations 3 -num_threads 1 &> /dev/null

#if [[ -f ${tmpd}/$(basename $seq .fasta).blast.pssm ]]; then
if [[ -f ${pssm} && $(cat ${pssm} | wc -l) -ne 0 ]]; then
#python ${tools}/parse_blast_cp_pssm.py ${tmpd}/$(basename $seq .fasta).blast.pssm ${tmpd} $(basename $seq .fasta)
python ${tools}/parse_blast_cp_pssm.py ${pssm} ${tmpd} ${bn}
else
python ${tools}/fasta2pssm.py $seq ${tmpd} ${bn}
fi
python ${tools}/fasta2hydro.py $seq ${tmpd} 1 ${bn}

#paste -d" " ${tmpd}/$(basename $seq .fasta).pssm ${tmpd}/$(basename $seq .fasta).hydro > ${tmpd}/$(basename $seq .fasta).pssm.hydro.i
paste -d" " ${tmpd}/${bn}.pssm ${tmpd}/${bn}.hydro > ${tmpd}/${bn}.pssm.hydro.i
echo "${bn}.pssm.hydro.i 0.0" > ${tmpd}/ELM.input.pssm.hydro.txt

${tools}/elm_predict.py -p ${tmpd} -i ${tmpd}/ELM.input.pssm.hydro.txt -m ${data}/elm/SCEXP2016-ML.spmem.model -o ${tmpd}/${bn}.spmem.pred -l -t -w 15 -d 21 -k logistic -b
${tools}/elm_predict.py -p ${tmpd} -i ${tmpd}/ELM.input.pssm.hydro.txt -m ${data}/elm/SCEXP2016-ML.mpmem.model -o ${tmpd}/${bn}.mpmem.pred -l -t -w 15 -d 21 -k logistic -b
${tools}/elm_predict.py -p ${tmpd} -i ${tmpd}/ELM.input.pssm.hydro.txt -m ${data}/elm/SCEXP2016-ML.pmem.model -o ${tmpd}/${bn}.pmem.pred -l -t -w 15 -d 21 -k logistic -b
${tools}/elm_predict.py -p ${tmpd} -i ${tmpd}/ELM.input.pssm.hydro.txt -m ${data}/elm/SCEXP2016-ML.ctp.model -o ${tmpd}/${bn}.ctp.pred -l -t -w 15 -d 21 -k logistic -b
${tools}/elm_predict.py -p ${tmpd} -i ${tmpd}/ELM.input.pssm.hydro.txt -m ${data}/elm/SCEXP2016-ML.ttp.model -o ${tmpd}/${bn}.ttp.pred -l -t -w 15 -d 21 -k logistic -b

cat /dev/null > ${tmpd}/${bn}.feat.pred

awk -v t=0.5 '{print $1,"ctp",($3>t ? 1 : 0),$3}' ${tmpd}/${bn}.ctp.pred >> ${tmpd}/${bn}.feat.pred
awk -v t=0.5 '{print $1,"ttp",($3>t ? 1 : 0),$3}' ${tmpd}/${bn}.ttp.pred >> ${tmpd}/${bn}.feat.pred
awk -v t=0.5 '{print $1,"spmem",($3>t ? 1 : 0),$3}' ${tmpd}/${bn}.spmem.pred >> ${tmpd}/${bn}.feat.pred
awk -v t=0.5 '{print $1,"mpmem",($3>t ? 1 : 0),$3}' ${tmpd}/${bn}.mpmem.pred >> ${tmpd}/${bn}.feat.pred
awk -v t=0.5 '{print $1,"pmem",($3>t ? 1 : 0),$3}' ${tmpd}/${bn}.pmem.pred >> ${tmpd}/${bn}.feat.pred

#python ${bin}/sclpred.py ${tmpd}/$(basename $seq .fasta).pssm ${tmpd}/$(basename $seq .fasta).feat.pred $seq > $out
python ${bin}/sclpred.py ${tmpd}/${bn}.pssm ${tmpd}/${bn}.feat.pred $seq > $out
#rm -rf ${tmpd}
