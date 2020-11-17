import os

SCHLORO_ROOT = os.environ.get('SCHLORO_ROOT')


KD = {'A': 0.7,
      'C': 0.7777777777777778,
      'E': 0.1111111111111111,
      'D': 0.1111111111111111,
      'G': 0.4555555555555555,
      'F': 0.8111111111111111,
      'I': 1.0,
      'H': 0.14444444444444443,
      'K': 0.06666666666666668,
      'M': 0.7111111111111111,
      'L': 0.9222222222222223,
      'N': 0.1111111111111111,
      'Q': 0.1111111111111111,
      'P': 0.3222222222222222,
      'S': 0.41111111111111115,
      'R': 0.0,
      'T': 0.4222222222222222,
      'W': 0.4,
      'V': 0.9666666666666666,
      'Y': 0.35555555555555557,
      'X': 0.0}

ELM_MODELS = {'ctp': os.path.join(SCHLORO_ROOT, 'data', 'elm', 'SCEXP2016-ML.ctp.model'),
              'mpmem': os.path.join(SCHLORO_ROOT, 'data', 'elm', 'SCEXP2016-ML.mpmem.model'),
              'pmem': os.path.join(SCHLORO_ROOT, 'data', 'elm', 'SCEXP2016-ML.pmem.model'),
              'spmem': os.path.join(SCHLORO_ROOT, 'data', 'elm', 'SCEXP2016-ML.spmem.model'),
              'ttp': os.path.join(SCHLORO_ROOT, 'data', 'elm', 'SCEXP2016-ML.ttp.model')}

SVM_MODELS = {0: "",
              1: "",
              2: "",
              3: "",
              4: "",
              5: ""}

ELM_WINDOW = 15
ELM_INPUT_SIZE = 21
ELM_ACTIVATION = "logistic"

ELMBIN = os.path.join(SCHLORO_ROOT, 'tools', 'elm_predict.py')
SVMBIN = "svm-predict"

PSIBLAST_ITERATIONS = 3
PSIBLAST_EVALUE = 0.001

locmap = {0: ('Chloroplast > Chloroplast_Inner_Membrane', 'inner'),
          1: ('Chloroplast > Chloroplast_Outer_Membrane', 'outer'),
          2: ('Chloroplast > Thylakoid > Chloroplast_Thylakoid_Lumen', 'lumen'),
          3: ('Chloroplast > Chloroplast_Stroma', 'stroma'),
          4: ('Chloroplast > Thylakoid > Chloroplast_Thylakoid_Membrane', 'membrane'),
          5: ('Chloroplast > Plastoglobule', 'plastoglobule')}

featmap = {'ctp': ('Chloroplast-targeting peptide', 'transit_peptide', 0.63),
           'ttp': ('Thylakoid-targeting peptide', 'transit_peptide', 0.36),
           'spmem': ('Single-pass membrane protein', 'membrane_topology', 0.43),
           'mpmem': ('Multi-pass membrane protein', 'membrane_topology', 0.51),
           'pmem' : ('Peropheral membrane protein', 'membrane_topology', 0.27)}
