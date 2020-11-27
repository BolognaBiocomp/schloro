## schloro - Prediction of protein sub-chloroplastic localization

#### Publication

Savojardo C., Martelli P.L., Fariselli P., Casadio R. [SChloro: directing Viridiplantae proteins to six chloroplastic sub-compartments](https://academic.oup.com/bioinformatics/article/33/3/347/2623363), *Bioinformatics* (2017) **33**(3): 347-353.

### The SChloro Docker image

Image availbale on DockerHub [https://hub.docker.com/r/bolognabiocomp/schloro](https://hub.docker.com/r/bolognabiocomp/schloro)

#### Usage of the image

The first step to run SChloro Docker container is the pull the container image. To do so, run:

```
$ docker pull bolognabiocomp/schloro
```

Now the SChloro Docker image is installed in your local Docker environment and ready to be used. To show SChloro help page run:

```
$ docker run bolognabiocomp/schloro -h

usage: schloro.py [-h] {multi-fasta,pssm} ...

SChloro: Predictor of sub-chloroplastic localization

optional arguments:
  -h, --help          show this help message and exit

subcommands:
  valid subcommands

  {multi-fasta,pssm}  additional help
    multi-fasta       Multi-FASTA input module
    pssm              PSSM input module (one sequence at a time)
```
The program can be run in two different modes:
- **multi-fasta** mode, accepting a FASTA file in input containing one or more sequences. In this mode, SChloro internally computes a sequence profile using PSIBLAST for each sequence in the input file and then predicts sub-chloroplastic localization.
- **pssm** mode, accepting a FASTA file containing a single protein sequence and a pre-computed PSSM file obtained by PSI-BLAST (using -out_ascii_pssm option). In this case, the computation of the sequence profile i skipped. The provided PSSM must be generated from the input sequence (an exception is raised otherwise). Only a single protein sequence can be processed in this mode.

#### Multi-fasta mode  
The show the SChloro help in multi-fasta mode run:

```
$ docker run bolognabiocomp/schloro multi-fasta -h

usage: schloro.py multi-fasta [-h] -f FASTA -d DBFILE -o OUTF

SChloro: Multi-FASTA input module.

optional arguments:
  -h, --help            show this help message and exit
  -f FASTA, --fasta FASTA
                        The input multi-FASTA file name
  -d DBFILE, --dbfile DBFILE
                        The PSIBLAST DB file
  -o OUTF, --outf OUTF  The output GFF3 file
```

Three arguments are accepted:
- The full path of the input FASTA file containing protein sequences to be predicted;
- The output GFF3 file where predictions will be stored;
- The database used to generate sequence profiles using PSI-BLAST.

Let's now try a concrete example. First of all, let's download an example sequence from UniProtKB, e.g. the Preprotein translocase subunit SCY2, chloroplastic from *Arabidopsis thaliana* (accession F4IQV7):

```
$ wget https://www.uniprot.org/uniprot/F4IQV7.fasta
```

Secondly, we need to obtain a protein sequence database for sequence profile generation. We can use either a large one such as the UniRef90 sequence database or a smaller one like the UniProtKB/SwissProt. In the former case, the computation of the sequence profile can be very slow. For simplicity, let's download and unzip the UniProtKB/SwissProt database:

```
$ wget ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz
$ unzip uniprot_sprot.fasta.gz
```
Now, we are ready to run SChloro on our input protein. Run:

```
$ docker run -v $(pwd):/data/ -v $(pwd):/seqdb/ bolognabiocomp/schloro -f F4IQV7.fasta -o F4IQV7.gff -d uniprot_sprot.fasta
```

In the example above, we are mapping the current program working directory ($(pwd)) to the /data/ folder inside the container. This will allow the container to see the external FASTA file F4IQV7.fasta and the database file uniprot_sprot.fasta.

After running SChloro, a database index is generated (using makeblastdb) for the input database, if not present.

The file F4IQV7.gff now contains the SChloro prediction in GFF3 format:
```
$ cat F4IQV7.gff

##gff-version 3
sp|F4IQV7|SCY2_ARATH	SChloro	Chloroplast thylakoid membrane	1	575	0.629293	.	.	Ontology_term:GO:0009535;evidence=ECO:0000256


```
Columns are as follows:
- Column 1: the protein ID/accession as reported in the FASTA input file;
- Column 2: the name of tool performing the annotation (i.e. SChloro)
- Column 3: the annotated feature along the sequence. Here, the complete input sequence is annotated with the corresponding subcellular localization.
- Column 4: start position of the feature (always 1);
- Column 5: end position of the feature (always the sequence length);
- Column 6: feature annotation score as assigned by SChloro;
- Columns 7,8: always empty, reported for compliance with GFF3 format
- Column 9: Description field. Gene Ontology Cellular Component terms and evidence codes are reported.

#### PSSM mode

The show the SChloro help in pssm mode run:

```
$ docker run bolognabiocomp/schloro pssm -h

usage: schloro.py pssm [-h] -f FASTA -p PSIBLAST_PSSM -o OUTF

SChloro: PSSM input module.

optional arguments:
  -h, --help            show this help message and exit
  -f FASTA, --fasta FASTA
                        The input FASTA file name (one sequence)
  -p PSIBLAST_PSSM, --pssm PSIBLAST_PSSM
                        The PSIBLAST PSSM file
  -o OUTF, --outf OUTF  The output GFF3 file
```

Three arguments are accepted:
- The full path of the input FASTA file containing protein sequences to be predicted;
- The output GFF3 file where predictions will be stored;
- A PSSM file previously generated with PSI-BLAST.

With the protein in the example above (F4IQV7) and the sequence database (uniprot_sprot.fasta), we can create a PSSM file using PSI-BLAST:

```
$ psiblast -query F4IQV7.fasta -db uniprot_sprot.fasta -out_ascii_pssm F4IQV7.pssm -evalue 0.001 -num_iterations 3
```

The generated PSSM can be now used as input to Schloro in pssm mode:

```
$ docker run -v $(pwd):/data/ -f F4IQV7.fasta -p F4IQV7.pssm -o F4IQV7.gff
```

In pssm mode, since no sequence database is used to generate the profile, we can skip the mounting of the /seqdb/ folder in the container.

The file F4IQV7.gff now contains the SChloro prediction in GFF3 format as detailed above.

### Install and use SChloro from source

Source code available on GitHub at [https://github.com/BolognaBiocomp/schloro](https://github.com/BolognaBiocomp/schloro).

#### Installation and configuration

SChloro is designed to run on Unix/Linux platforms. The software was written using the Python programming language and it was tested under the Python version 3.

To obtain SChloro, clone the repository from GitHub:

```
$ git clone https://github.com/BolognaBiocomp/schloro
```

This will produce a directory schloro. Before running schloro you need to set and export a variable named SCHLORO_ROOT to point to the schloro installation dir:
```
$ export SCHLORO_ROOT='/path/to/schloro'
```

Before running the program, you need to install SChloro dependencies. We suggest to use Conda (we suggest [Miniconda3](https://docs.conda.io/en/latest/miniconda.html)) create a Python virtual environment and activate it.

To create a conda env for schloro:

```
$ conda create -n schloro
```
To activate the environment:

```
$ conda activate schloro
```

The following Python libraries/tools are required:

- biopython
- blast
- libsvm

To install all requirements run the followgin commands:

```
$ conda install blast -c bioconda
$ conda install libsvm -c conda-forge
$ conda install biopython
```

Now you are able to use schloro (see next Section). Remember to keep the environment active.
If you wish, you can copy the “schloro.py” script to a directory in the users' PATH.

#### Usage

To show SChloro help page run:

```
$ ./schloro.py -h

usage: schloro.py [-h] {multi-fasta,pssm} ...

SChloro: Predictor of sub-chloroplastic localization

optional arguments:
  -h, --help          show this help message and exit

subcommands:
  valid subcommands

  {multi-fasta,pssm}  additional help
    multi-fasta       Multi-FASTA input module
    pssm              PSSM input module (one sequence at a time)
```
The program can be run in two different modes:
- **multi-fasta** mode, accepting a FASTA file in input containing one or more sequences. In this mode, SChloro internally computes a sequence profile using PSIBLAST for each sequence in the input file and then predicts sub-chloroplastic localization.
- **pssm** mode, accepting a FASTA file containing a single protein sequence and a pre-computed PSSM file obtained by PSI-BLAST (using -out_ascii_pssm option). In this case, the computation of the sequence profile i skipped. The provided PSSM must be generated from the input sequence (an exception is raised otherwise). Only a single protein sequence can be processed in this mode.

#### Multi-fasta mode  
The show the SChloro help in multi-fasta mode run:

```
$ schloro.py multi-fasta -h

usage: schloro.py multi-fasta [-h] -f FASTA -d DBFILE -o OUTF

SChloro: Multi-FASTA input module.

optional arguments:
  -h, --help            show this help message and exit
  -f FASTA, --fasta FASTA
                        The input multi-FASTA file name
  -d DBFILE, --dbfile DBFILE
                        The PSIBLAST DB file
  -o OUTF, --outf OUTF  The output GFF3 file
```

Three arguments are accepted:
- The full path of the input FASTA file containing protein sequences to be predicted;
- The output GFF3 file where predictions will be stored;
- The database used to generate sequence profiles using PSI-BLAST.

Let's now try a concrete example. First of all, let's download an example sequence from UniProtKB, e.g. the Preprotein translocase subunit SCY2, chloroplastic from *Arabidopsis thaliana* (accession F4IQV7):

```
$ wget https://www.uniprot.org/uniprot/F4IQV7.fasta
```

Secondly, we need to obtain a protein sequence database for sequence profile generation. We can use either a large one such as the UniRef90 sequence database or a smaller one like the UniProtKB/SwissProt. In the former case, the computation of the sequence profile can be very slow. For simplicity, let's download and unzip the UniProtKB/SwissProt database:

```
$ wget ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz
$ unzip uniprot_sprot.fasta.gz
```
Now, we are ready to run SChloro on our input protein. Run:

```
$ ./schloro.py -f F4IQV7.fasta -o F4IQV7.gff -d uniprot_sprot.fasta
```

After running SChloro, a database index is generated (using makeblastdb) for the input database, if not present.

The file F4IQV7.gff now contains the SChloro prediction in GFF3 format as detailed above:
```
$ cat F4IQV7.gff

##gff-version 3
sp|F4IQV7|SCY2_ARATH	SChloro	Chloroplast thylakoid membrane	1	575	0.629293	.	.	Ontology_term:GO:0009535;evidence=ECO:0000256
```

#### PSSM mode
The show the SChloro help in pssm mode run:

```
$ ./schloro.py pssm -h

usage: schloro.py pssm [-h] -f FASTA -p PSIBLAST_PSSM -o OUTF

SChloro: PSSM input module.

optional arguments:
  -h, --help            show this help message and exit
  -f FASTA, --fasta FASTA
                        The input FASTA file name (one sequence)
  -p PSIBLAST_PSSM, --pssm PSIBLAST_PSSM
                        The PSIBLAST PSSM file
  -o OUTF, --outf OUTF  The output GFF3 file
```

Three arguments are accepted:
- The full path of the input FASTA file containing protein sequences to be predicted;
- The output GFF3 file where predictions will be stored;
- A PSSM file previously generated with PSI-BLAST.

With the protein in the example above (F4IQV7) and the sequence database (uniprot_sprot.fasta), we can create a PSSM file using PSI-BLAST:

```
$ psiblast -query F4IQV7.fasta -db uniprot_sprot.fasta -out_ascii_pssm F4IQV7.pssm -evalue 0.001 -num_iterations 3
```

The generated PSSM can be now used as input to Schloro in pssm mode:

```
$ ./schloro.py -f F4IQV7.fasta -p F4IQV7.pssm -o F4IQV7.gff
```

The file F4IQV7.gff now contains the SChloro prediction in GFF3 format as detailed above.

Please, reports bugs to: castrense.savojardo2@unibo.it
