import math

from calcustavkirza.classes import Element

class OverLoad(Element):
    isz: float
    index_ct: int | None = None
    t: float
    t_note: str = 'сигнал'
    sn: int
    un: float
    name: str = 'Перегрузка'
    name_short: str = 'Перегрузка'

    def calc_ust(self):
        self.te.table_name(self.name)
        self.te.table_head('Наименование величины', 'Расчётная формула, обозначение', 'Результат расчёта', widths=(3, 2, 1))
        inom = self.sn / self.un / math.sqrt(3)
        self.te.table_row('Первичный ток срабатывания защиты по условию срабатывания при достижении номинального тока, А',
                          'Iсз≥·Iном', f'{inom:.2f}')
        self.te.table_row('Первичный ток срабатывания защиты принимаем, А',
                          'Iсз', f'{self.isz}')
        self.te.table_row('Время срабатывания на сигнал', 't', self.t)

    def table_settings(self):
        self.te.table_row(self.name, f'{self.isz} A', self.t, '')

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
