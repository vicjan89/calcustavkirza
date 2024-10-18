from textengines.interfaces import TextEngine


from calcustavkirza.classes import Element

class CTS(Element):
    '''
    Current Transformer Superviser function
    u: float
    u_note: str = ''
    t: float = 0.0
    t_note: str = ''
    index_vt: int | None = None
    note: str = ''
    kn: float # коэффициент надёжности (отстройки)
    un: float #нормальное напряжение
    name: str = 'Контроль напряжения'
    '''
    u0: float
    u0_note: str = ''
    i0: float
    i0_note: str = ''
    t: float = 0.0
    t_note: str = ''
    note: str = 'все значения приведены во вторичных величинах'
    kn: float # коэффициент надёжности (отстройки)
    un: float #нормальное напряжение
    un_note: str = ''
    inorm: float # normal current
    inorm_note: str = ''
    name: str = 'Контроль исправности цепей тока'
    name_short: str = 'CTS'

    def calc_ust(self, te: TextEngine, *args):
        te.table_name(self.name)
        te.table_head('Наименование величины', 'Расчётная формула, обозначение', 'Результат расчёта',
                      widths=(3,2,1))
        te.table_row(f'Напряжение нулевой последовательности вторичное в нормальном режиме {self.un_note}, В',
                     te.m(r'3U0_{\text{НОРМ}}'), f'{self.un:.2f}')
        te.table_row('Коэффициент отстройки', te.m(r'K_{\text{ОТС}}'), self.kn)
        te.table_row(f'Напряжение срабатывания нулевой последовательности вторичное расчётное, В',
                     te.m(r'U_{\text{ср}} = K_{\text{ОТС}} \cdot U_{\text{НОРМ}}'),
                          f'{self.un * self.kn:.2f}')
        te.table_row(f'Принимаем напряжение срабатывания нулевой последовательности, В', '3U0ср', self.u0)
        te.table_row(f'Ток нулевой последовательности вторичный в нормальном режиме {self.inorm_note}, A',
                     te.m(r'3I0_{\text{НОРМ}}'), f'{self.inorm:.2f}')
        te.table_row(f'Ток срабатывания нулевой последовательности вторичный расчётный {self.i0_note}, В',
                     te.m(r'3I0_{\text{ср}} = K_{\text{ОТС}} \cdot I_{\text{НОРМ}}'),
                     f'{self.inorm * self.kn:.2f}')
        te.table_row(f'Принимаем ток срабатывания нулевой последовательности {self.note}, А',
                     te.m(r'3I0_{\text{ср}}'), self.i0)
        te.table_row(f'Время срабатывания {self.t_note}, с', 'tср', self.t)

    def table_settings(self, te: TextEngine):
        note = [self.note]
        if self.t_note:
            note.append(self.t_note)
        note = ','.join((note))
        te.table_row(self.name, f'3u0={self.u0}В 3i0={self.i0}A', self.t, note)

    def table_settings_bmz_data(self): #TODO not relised
        res = [self.u]
        if self.index_vt is not None:
            res.append(self.pris.vt[self.index_vt].u1tou2(self.u))
        res.append(self.t)
        return res

    def table_settings_bmz_second(self):
        res = ['U перв']
        if self.index_vt is not None:
            res.append('U втор')
        res.append('Т сраб,с')
        return res

    def table_settings_bmz_first(self):
        return f'{self.name} {self.t_note}'

    def table_settings_bmz(self):
        return [self.table_settings_bmz_first(), self.table_settings_bmz_second(), self.table_settings_bmz_data()]
