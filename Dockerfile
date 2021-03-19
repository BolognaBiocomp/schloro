# Base Image
FROM continuumio/miniconda3

# Metadata
LABEL base.image="continuumio/miniconda3"
LABEL version="1.0"
LABEL software="SChloro"
LABEL software.version="1.0"
LABEL description="an open source software tool to predict sub-chloroplastic localization"
LABEL website="https://schloro.biocomp.unibo.it"
LABEL documentation="https://schloro.biocomp.unibo.it"
LABEL license="GNU GENERAL PUBLIC LICENSE Version 3"
LABEL tags="Proteomics"
LABEL maintainer="Castrense Savojardo <castrense.savojardo2@unibo.it>"

ENV PYTHONDONTWRITEBYTECODE=true SCHLORO_ROOT=/usr/src/schloro PATH=/usr/src/schloro:$PATH

WORKDIR /usr/src/schloro

COPY . .

RUN conda update -n base conda && \
   conda install --yes nomkl blast -c bioconda && \
   conda install --yes nomkl libsvm -c conda-forge && \
   conda install --yes nomkl biopython && \
   conda clean -afy \
   && find /opt/conda/ -follow -type f -name '*.a' -delete \
   && find /opt/conda/ -follow -type f -name '*.pyc' -delete \
   && find /opt/conda/ -follow -type f -name '*.js.map' -delete

WORKDIR /seqdb/

RUN apt-get update -y && \
    apt-get install -y wget

RUN wget https://share.biocomp.unibo.it/biocomp/sp2021_01/uniprot_sprot.fasta.gz && \
    gunzip uniprot_sprot.fasta.gz && \
    makeblastdb -in uniprot_sprot.fasta -dbtype prot

WORKDIR /data/

ENTRYPOINT ["/usr/src/schloro/schloro.py"]
