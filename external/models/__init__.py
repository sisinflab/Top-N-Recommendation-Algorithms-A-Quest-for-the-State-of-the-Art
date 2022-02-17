def import_model_by_backend(tensorflow_cmd, pytorch_cmd):
    import sys
    for _backend in sys.modules["external"].backend:
        if _backend == "tensorflow":
            exec(tensorflow_cmd)
        elif _backend == "pytorch":
            exec(pytorch_cmd)
            break


from .most_popular import MostPop
from .Proxy import ProxyRecommender
from .msap import MSAPMF
from .AdversarialMF import AdversarialMF
from .ktup import KTUP
from .cke import CKE
from .mkr import MKR
from .cofm import CoFM
from .convmf import ConvMF
from .kgflex import KGFlex
from .kgflex_tf import KGFlexTF
from .convmf import ConvMF
from .hrdr import HRDR
from .KaVAE import KaVAE

import sys
for _backend in sys.modules["external"].backend:
    if _backend == "tensorflow":
        from .hrdr.HRDR import HRDR
        from .deepconn.DeepCoNN import DeepCoNN
    elif _backend == "pytorch":
        from .ngcf.NGCF import NGCF
        from .lightgcn.LightGCN import LightGCN
        from .pinsage.PinSage import PinSage
        from .gat.GAT import GAT
        from .gcmc.GCMC import GCMC
        from .disen_gcn.DisenGCN import DisenGCN
        from .mmgcn.MMGCN import MMGCN
        from .dgcf.DGCF import DGCF
        from .egcf.EGCF import EGCF
        from .lgacn.LGACN import LGACN
