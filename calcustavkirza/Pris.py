from textengines.interfaces import TextEngine

from calcustavkirza.classes import Element
from calcustavkirza.protections.MTZ import MTZ
from calcustavkirza.protections.TO import TO
from calcustavkirza.protections.EF import EF
from calcustavkirza.protections.LZSH import LZSH
from calcustavkirza.protections.BFP import BFP
from calcustavkirza.protections.ControlBFP import ControlBFP
from calcustavkirza.protections.EFdir import EFdir
from calcustavkirza.protections.AutoReclose import AutoReclose
from calcustavkirza.protections.Avr import Avr
from calcustavkirza.protections.voltage import Voltage
from calcustavkirza.protections.overload import OverLoad
from calcustavkirza.protections.T3WPDIF import T3WPDIF
from calcustavkirza.Net import Net


class CT(Element):
    mark: str
    i1: int
    i2: int

    def i1toi2(self, i1):
        return i1 / self.i1 * self.i2

class VT(Element):
    mark: str
    u1: int | float
    u2: int

    def u1tou2(self, u1):
        return u1 / self.u1 * self.u2

class Pris(Element):
    loc: dict | None = None
    ct: list[CT] | None = None
    vt: list[VT] | None = None
    dif: list[T3WPDIF] | None = None
    mtz: list[MTZ] | None = None
    to: list[TO] | None = None
    ef: list[EF] | None = None
    lzsh: list[LZSH] | None = None
    bfp: list[BFP] | None = None
    cbfp: list[ControlBFP] | None = None
    efdir: list[EFdir] | None = None
    apv: list[AutoReclose] | None = None
    avr: list[Avr] | None = None
    voltage: list[Voltage] | None = None
    overload: list[OverLoad] | None = None
    net: Net | None = None
    note: str = ''

    def get_protections(self):
        prot = []
        if self.mtz:
            prot.extend(self.mtz)
        if self.to:
            prot.extend(self.to)
        # if self.ef:
        #     prot.extend(self.ef)
        if self.lzsh:
            prot.extend(self.lzsh)
        # if self.bfp:
        #     prot.extend(self.bfp)
        # if self.efdir:
        #     prot.extend(self.efdir)
        return prot

    def get_rza(self) -> tuple:
        return (self.to, self.mtz, self.lzsh, self.overload, self.bfp, self.cbfp, self.ef, self.efdir, self.apv, self.avr,
                self.voltage)


    def calc_ust(self, te: TextEngine, res_sc_min, res_sc_max):
        te.h2(self.name)
        if self.note:
            te.p(self.note)
        if self.dif:
            for p in self.dif:
                p.calc_ust(te=te, res_sc_min=res_sc_min, res_sc_max=res_sc_max)
        if self.mtz:
            for p in self.mtz:
                p.calc_ust(te=te, res_sc_min=res_sc_min, res_sc_max=res_sc_max)
        if self.lzsh:
            for p in self.lzsh:
                p.calc_ust(te=te, res_sc_min=res_sc_min, res_sc_max=res_sc_max)
        if self.to:
            for p in self.to:
                p.calc_ust(te=te, res_sc_min=res_sc_min, res_sc_max=res_sc_max)
        if self.bfp:
            for p in self.bfp:
                p.calc_ust(te=te, res_sc_min=res_sc_min, res_sc_max=res_sc_max)
        if self.cbfp:
            for p in self.cbfp:
                p.calc_ust(te=te, res_sc_min=res_sc_min, res_sc_max=res_sc_max)
        if self.ef:
            for p in self.ef:
                p.calc_ust(te=te, res_sc_min=res_sc_min, res_sc_max=res_sc_max)
        if self.efdir:
            for p in self.efdir:
                p.calc_ust(te=te, res_sc_min=res_sc_min, res_sc_max=res_sc_max)
        if self.apv:
            for p in self.apv:
                p.calc_ust(te=te, res_sc_min=res_sc_min, res_sc_max=res_sc_max)
        if self.avr:
            for p in self.avr:
                p.calc_ust(te=te, res_sc_min=res_sc_min, res_sc_max=res_sc_max)
        if self.voltage:
            for p in self.voltage:
                p.calc_ust(te=te, res_sc_min=res_sc_min, res_sc_max=res_sc_max)
        if self.overload:
            for p in self.overload:
                p.calc_ust(te=te, res_sc_min=res_sc_min, res_sc_max=res_sc_max)
    def table_settings(self):
        te.table_name(self.name)
        te.table_head('Функция РЗА', 'Величина срабатывания', 'Время срабатывания, сек', 'Примечание')
        if self.mtz:
            for p in self.mtz:
                p.table_settings()
        if self.lzsh:
            for p in self.lzsh:
                p.table_settings()
        if self.to:
            for p in self.to:
                p.table_settings()
        if self.bfp:
            for p in self.bfp:
                p.table_settings()
        if self.cbfp:
            for p in self.cbfp:
                p.table_settings()
        if self.ef:
            for p in self.ef:
                p.table_settings()
        if self.efdir:
            for p in self.efdir:
                p.table_settings()
        if self.apv:
            for p in self.apv:
                p.table_settings()
        if self.avr:
            for p in self.avr:
                p.table_settings()
        if self.voltage:
            for p in self.voltage:
                p.table_settings()
        if self.overload:
            for p in self.overload:
                p.table_settings()

    def table_settings_bmz(self):
        res = []
        for protectiona_group in  self.get_rza():
            if protectiona_group:
                for prot in protectiona_group:
                   res.append(prot.table_settings_bmz())
        return res