from calcustavkirza.classes import Element

class Voltage(Element):

    u: float
    t: float = 0.0
    t_note: str = ''
    index_vt: int | None = None
    note: str = ''
    name: str = 'Контроль напряжения'

    def calc_ust(self):
        self.te.table_name(self.name)
        self.te.table_head('Наименование величины', 'Расчётная формула, обозначение', 'Результат расчёта', widths=(3,2,1))
        self.te.table_row(f'Напряжение срабатывания {self.note}, кВ', 'Uср', self.u)
        self.te.table_row(f'Время срабатывания, с', 'tср', self.t)

    def table_settings(self):
        self.te.table_row(self.name, f'{self.u} кВ', self.t, '')

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
