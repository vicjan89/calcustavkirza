import math


from textengines.interfaces import TextEngine


from calcustavkirza.classes import Element


class EF(Element):
    '''
    Класс описывает токовую защиту нулевой последовательности
    '''
    R: int | float | None = None
    Kch: int = 1.5
    Kn: float = 1.2 # to take into account the capacity of transformers and motors, we take a coefficient equal to 1.2
    Ul: float = 10
    isz: float
    isz_note: str = ''
    ic: float | None = None
    ic_note: str = ''
    index_ct: int | None = None
    t: float
    t_note: str = 'отключение'
    t1: float | None = None
    t1_note: str = ''
    t_au: float | None = None
    time_prot: bool = False
    name: str = 'Токовая защита нулевой последовательности'
    name_short: str = 'ТЗНП'

    def calc_ust(self, te: TextEngine, *args):
        te.table_name(self.name)
        te.table_head('Наименование величины', 'Расчётная формула, обозначение', 'Результат расчёта', widths=(3,2,1))
        if self.R:
            ir = self.Ul /  self.R / math.sqrt(3) * 1000
            iszpredv = ir / self.Kch
            te.table_row('Первичный ток срабатывания защиты по обеспечению чувствительности к току резистора, А',
                              'Iсз≤Uф/(Кч*R)', f'{iszpredv:.2f}')
            te.table_row('Коэффициент чувствительности', 'Кч', self.Kch)
            te.table_row('Сопротивление резистора заземления нейтрали', 'R', self.R)
        if self.ic:
            te.table_row('Первичный ток срабатывания защиты по условию отстройки от собственного ёмкостного тока '
                              'при внешнем замыкании на землю, А', 'Iсз ≥ Ic*Kн',
                              f'{self.ic}*{self.Kn} = {self.ic*self.Kn:.1f}')

        te.table_row(f'Принимаем первичный ток срабатывания защиты равным {self.isz_note}, А', 'Iсз', self.isz)
        if self.R:
            k_ch = ir / self.isz
            if k_ch < 1.5:
                self.add_warning(f'Коэффициент чувствительности ТЗНП мал ({k_ch:.2f})')
            te.table_row('Проверка коэффициента чувствительности', 'Кч=Iрезист/Iсз >= 1.5', f'{k_ch:.2f}')
        te.table_row('Время срабатывания защиты по условию селективности, с', 'tср', self.t)
        if self.t_au:
            te.table_row('Время срабатывания защиты при автоматическом ускорении, с', 't АУ', self.t_au)
        if self.t1:
            te.table_row(f'Время срабатывания защиты {self.t1_note}, с', 't1ср', self.t1)
        self.write_warnings(te)

    def table_settings(self, te: TextEngine):
        t_str = ''
        if self.t:
            t_str += f't={self.t}сек.'
        if self.t1:
            t_str += f' t1={self.t1}сек. {self.t1_note}'
        if self.t_au:
            t_str += f' tау={self.t_au}'
        te.table_row(self.name, f'{self.isz} A', t_str, '')

    def table_settings_bmz_data(self):
        res = [self.isz]
        if self.index_ct is not None:
            res.append(self.pris.ct[self.index_ct].i1toi2(self.isz))
        else:
            res.append('')
        res.extend([self.t, self.t_au])
        if self.t1:
            res.append(f'{self.t1} {self.t1_note}')
        return res

    def table_settings_bmz_second(self):
        res = ['А перв']
        res.append('А втор')
        res.extend(['Т сраб,с', 'Т сраб АУ,с'])
        if self.t1:
            res.append('Т1 сраб,с')
        return res

    def table_settings_bmz_first(self):
        return f'{self.name_short} {self.t_note}'

    def table_settings_bmz(self):
        return [self.table_settings_bmz_first(), self.table_settings_bmz_second(), self.table_settings_bmz_data()]
