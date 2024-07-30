from textengines.docxengine import DOCX
# from calcustavkirza.protections.T3WPDIF import T3WPDIF
from calcustavkirza.Net import Net
from pandapowertools.net import Net as pptNet
from textengines.restructuredtextengine import ReStructuredText
import ezdxf
from calcustavkirza.Calc import Calc
from store.store import JsonStorage, TomlStorage, YamlStorage
from calcustavkirza.Settting import Setting



def scheme():
    pp_net = pptNet('../pandapowertools/Полоцк')
    pp_net.load()
    te = ReStructuredText(path='Polimir/Polimir.rst')
    n = Net(net=pp_net.net, te=te)
    n.create()
    te.save()

def calc_kz():
    te = ReStructuredText(path=r'Polimir\Polimir_sc.rst')
    res = []
    modes = [r'Polimir\3-х фазное КЗ в максимальном режиме', r'Polimir\2-х фазное КЗ в минимальном режиме']
    for mode in modes:
        s = YamlStorage(mode)
        name = mode.split('\\')[-1]
        res.append([name, s.read()])
    c = Calc(te=te, res_sc=res)
    c.do()
    te.save()

def ust():
    s_max = YamlStorage(r'Polimir\3-х фазное КЗ в максимальном режиме')
    s_min = YamlStorage(r'Polimir\2-х фазное КЗ в минимальном режиме')
    res_sc_min = s_min.read()
    res_sc_max = s_max.read()
    te = ReStructuredText(path=r'Polimir\Polimir_ust_vl_110.rst')
    st = TomlStorage(r'Polimir\settings_vl_110.toml')
    data = st.read()
    p = Setting(**data)
    p.do(te=te, res_sc_min=res_sc_min, res_sc_max=res_sc_max)
    te.save()

# scheme()
# calc_kz()
ust()
