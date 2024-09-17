from textengines.interfaces import TextEngine


from calcustavkirza.classes import Element

class Voltage(Element):

    u: float
    t: float = 0.0
    t_note: str = ''
    index_vt: int | None = None
    note: str = ''
    kn: float # коэффициент надёжности (отстройки)
    un: float #номинальное напряжение
    name: str = 'Контроль напряжения'

    def calc_ust(self, te: TextEngine, *args):
        te.table_name(self.name)
        te.table_head('Наименование величины', 'Расчётная формула, обозначение', 'Результат расчёта', widths=(3,2,1))
        te.table_row(f'Напряжение срабатывания расчётное, кВ',
                     te.m(r'U_{\text{ср}} = K_{\text{ОТС}} \cdot U_{\text{НОМ}}'),
                          self.un * self.kn)
        te.table_row('Коэффициент отстройки', te.m(r'K_{\text{ОТС}}'), self.kn)
        te.table_row('Номинальное напряжение, кВ', te.m(r'U_{\text{НОМ}}'), self.un)
        te.table_row(f'Принимаем напряжение срабатывания {self.note}, кВ', 'Uср', self.u)
        te.table_row(f'Время срабатывания{self.t_note}, с', 'tср', self.t)

    def table_settings(self):
        te.table_row(self.name, f'{self.u} кВ', self.t, '')

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
