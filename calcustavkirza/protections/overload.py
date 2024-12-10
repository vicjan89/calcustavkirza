import math

from textengines.interfaces import TextEngine

from calcustavkirza.classes import Element, Doc

class OverloadDoc(Doc):

    def calc_ust(self, te: TextEngine, res_sc_min: list, res_sc_max: list):
        te.table_name(self.name)
        te.table_head('Наименование величины', 'Расчётная формула, обозначение', 'Результат расчёта', widths=(3, 2, 1))
        if self.sn and self.un and self.Kn:
            inom = self.sn / self.un / math.sqrt(3) * self.Kn
            te.table_row('Первичный ток срабатывания защиты по условию срабатывания при достижении номинального тока, А',
                         'Iсз≥·Iном·Кн', f'{inom:.2f}')
            te.table_row('Коэффициент надёжности', 'Кн', self.Kn)
        if self.isz:
            te.table_row('Первичный ток срабатывания защиты принимаем, А',
                         'Iсз', f'{self.isz}')
        if self.t:
            te.table_row('Время срабатывания', 't', f'{self.t} {self.t_note}')

    def table_settings(self, te: TextEngine):
        te.table_row(self.name, f'{self.isz} A', self.t, '')

    def table_settings_bmz_data(self):
        res = [self.isz]
        if self.index_ct is not None:
            res.append(self.pris.ct[self.index_ct].i1toi2(self.isz))
        res.append(self.t)
        return res

    def table_settings_bmz_second(self):
        res = ['А перв']
        if self.index_ct is not None:
            res.append('А втор')
        res.append('Т сраб,с')
        return res

    def table_settings_bmz_first(self):
        return f'{self.name_short} {self.t_note}'

    def table_settings_bmz(self):
        return [self.table_settings_bmz_first(), self.table_settings_bmz_second(), self.table_settings_bmz_data()]

class OverLoad(Element, OverloadDoc):
    '''
    isz: float
    index_ct: int | None = None
    t: float
    t_note: str = 'на сигнал'
    Kn: float = 1.1
    sn: int #мощность в кВА
    un: float
    name: str = 'Перегрузка'
    name_short: str = 'Перегрузка'
    '''
    isz: float
    index_ct: int | None = None
    t: float
    t_note: str = 'на сигнал'
    Kn: float = 1.1
    sn: int #мощность в кВА
    un: float
    name: str = 'Перегрузка'
    name_short: str = 'Перегрузка'

