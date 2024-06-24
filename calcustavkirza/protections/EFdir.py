import math

from calcustavkirza.classes import Element

class EFdir(Element):
    icmin: float
    index_ct: int | None = None
    Kch: float = 1.5
    Kch_note: str
    fmch: float = 10
    dir: str
    isz: float
    t: float
    t_au: float | None = None
    time_prot: bool = False

    def calc_ust(self):
        if not self.name:
            self.name = 'Направленная токовая защита нулевой последовательности'
        self.te.table_name(self.name)
        self.te.table_head('Наименование величины', 'Расчётная формула, обозначение', 'Результат расчёта', widths=(3,2,1))
        self.te.table_row('Первичный ток срабатывания защиты по условию обеспечения чувствительности в ремонтном режиме сети, А',
                          'Iсз≤Icmin/Кч', f'{self.icmin/self.Kch:.2f}')
        self.te.table_row('Минимальный ёмкостный ток сети (отключены все присоединения кроме одного с наименьшей ёмкостью), А',
                          'Icmin', self.icmin)
        self.te.table_row('Коэффициент чувствительности минимальный',
                          'Кч', self.Kch)
        self.te.table_row('Принимаем первичный ток срабатывания защиты равным, А', 'Iсз', self.isz)
        k_ch = self.icmin / self.isz
        assert k_ch >= 1.0, f'Коэффициент чувствительности НТЗНП {self.pris.name} мал ({k_ch:.2f})'
        self.te.table_row('Проверка коэффициента чувствительности',
                          'Кч=Icmin/Iсз >= 1.5', f'{k_ch:.2f} {self.Kch_note}')
        self.te.table_row('Направление защиты. Для исключения срабатывания из-за угловой погрешности ТЗЛК (до 30°) '
                          'угол повёрнут дополнительно на 40°', 'φмч',
                          f'{self.fmch}° направление {self.dir}. При недостоверном определении направления ступень блокируется')
        self.te.table_row('Время срабатывания защиты, с', 'tср', self.t)
        if self.t_au:
            self.te.table_row('Время срабатывания защиты при автоматическом ускорении, с', 't АУ', self.t_au)

    def table_settings(self):
        ...

    def table_settings_bmz_data(self):
        res = [self.isz]
        if self.index_ct is not None:
            res.append(self.pris.ct[self.index_ct].i1toi2(self.isz))
        res.extend([self.t, self.t_au])
        return res

    def table_settings_bmz_second(self):
        res = ['А перв']
        if self.index_ct is not None:
            res.append('А втор')
        res.extend(['Т сраб,с', 'Т сраб АУ,с'])
        return res

    def table_settings_bmz_first(self):
        return f'{self.name_short} {self.t_note if self.t_note else "отключение"}'

    def table_settings_bmz(self):
        return [self.table_settings_bmz_first(), self.table_settings_bmz_second(), self.table_settings_bmz_data()]
