from calcustavkirza.classes import Element
from calcustavkirza.Pris import Pris


class Setting(Element):
    pris: list[Pris] | None = None
    note: str = ''


    def do(self, te, res_sc_min, res_sc_max):
        te.h1('Выбор уставок РЗА')
        te.p(self.note)
        if self.pris:
            for p in self.pris:
                p.calc_ust(te=te, res_sc_min=res_sc_min, res_sc_max=res_sc_max)

    def table_settings(self, te):
        te.h1('Таблица уставок РЗА')
        if self.pris:
            for p in self.pris:
                p.table_settings(te=te)
