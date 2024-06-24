import math

from calcustavkirza.classes import Element

class ControlBFP(Element):
    isz: float
    isz_ef: float | None = None
    index_ct: int | None = None
    index_ct_ef: int | None = None
    note: str = 'отключение при условии срабатывания одного из токовых органов и получении сигнала УРОВ'
    name: str = 'Котроль УРОВ'
    name_short: str = 'Котроль УРОВ'

    def calc_ust(self):
        self.te.table_name(self.name)
        self.te.table_head('Наименование величины', 'Расчётная формула, обозначение', 'Результат расчёта', widths=(3, 2, 1))
        self.te.table_row('Первичный фазный ток срабатывания защиты принимаем, А',
                          'Iсз', f'{self.isz}')
        if self.isz_ef:
            self.te.table_row('Первичный ток нулевой последовательности срабатывания защиты принимаем, А',
                              'Iсз', f'{self.isz_ef}')

    def table_settings(self):
        self.te.table_row(self.name, f'{self.isz} A', self.t, '') #TODO add isz_ef

    def table_settings_bmz_data(self):
        res = [self.isz, '', '', '']
        if self.index_ct is not None:
            res[1] = self.pris.ct[self.index_ct].i1toi2(self.isz)
        if self.isz_ef:
            res[2] = self.isz_ef
        if self.index_ct_ef is not None:
            res[3] = self.pris.ct[self.index_ct_ef].i1toi2(self.isz_ef)
        return res

    def table_settings_bmz_second(self):
        return ['А перв', 'А втор', 'А(НП) перв', 'А(НП) втор']

    def table_settings_bmz_first(self):
        return f'{self.name_short} {self.note}'

    def table_settings_bmz(self):
        return [self.table_settings_bmz_first(), self.table_settings_bmz_second(), self.table_settings_bmz_data()]
