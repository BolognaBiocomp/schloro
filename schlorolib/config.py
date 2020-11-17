import os

SCHLORO_ROOT = os.environ.get('SCHLORO_ROOT')


ELM_MODELS = {'ctp': "",
              'mpmem': "",
              'pmem': "",
              'spmem': "",
              'ttp': ""}

SVM_MODELS = {0: "",
              1: "",
              2: "",
              3: "",
              4: "",
              5: ""}

ELM_WINDOW = 15
ELM_INPUT_SIZE = 21
ELM_ACTIVATION = "logistic"

PSIBLAST_ITERATIONS = 3
PSIBLAST_EVALUE = 0.001
