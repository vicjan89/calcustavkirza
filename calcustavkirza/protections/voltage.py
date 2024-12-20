from textengines.interfaces import TextEngine


from calcustavkirza.classes import Element, Doc

class VoltageDoc(Doc):

    def calc_ust(self, te: TextEngine, **kwargs):
        te.table_name(self.name)
        te.table_head('Наименование величины', 'Расчётная формула, обозначение', 'Результат расчёта', widths=(3,2,1))
        if self.un and self.kn:
            te.table_row(f'Напряжение срабатывания расчётное{self.u_note}, кВ',
                         te.m(r'U_{\text{ср}} = K_{\text{ОТС}} \cdot U_{\text{НОРМ}}'),
                         f'{self.un * self.kn:.2f}')
            te.table_row('Коэффициент отстройки', te.m(r'K_{\text{ОТС}}'), self.kn)
            te.table_row(f'Напряжение в нормальном режиме {self.un_note}, кВ', te.m(r'U_{\text{НОРМ}}'),
                         f'{self.un:.2f}')
        if self.u:
            te.table_row(f'Принимаем напряжение срабатывания {self.note}, кВ', 'Uср', self.u)
        if self.t:
            te.table_row(f'Время срабатывания {self.t_note}, с', 'tср', self.t)

    def table_settings(self, te: TextEngine):
        te.table_row(self.name, f'{self.u} кВ', self.t, self.t_note)

    def table_settings_bmz_data(self):
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

class Voltage(Element, VoltageDoc):
    '''
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
    u: float
    u_note: str = ''
    t: float = 0.0
    t_note: str = ''
    index_vt: int | None = None
    note: str = ''
    kn: float # коэффициент надёжности (отстройки)
    un: float #нормальное напряжение
    un_note: str = ''
    name: str = 'Контроль напряжения'

