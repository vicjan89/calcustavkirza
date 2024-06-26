from textengines.interfaces import TextEngine


from calcustavkirza.classes import Element

class BFP(Element):
    isz: float # в процентах от номинального тока
    t: float
    t_note: str = "отключение вышестоящего присоединения"
    index_ct: int | None = None
    time_prot: bool = False
    name: str = 'Устройство резервирования отказа выключателя'
    name_short: str = 'УРОВ'

    def calc_ust(self, te: TextEngine, res_sc_min: list, res_sc_max: list):
        te.table_name(self.name)
        te.table_head('Наименование величины', 'Расчётная формула, обозначение', 'Результат расчёта', widths=(3,2,1))
        te.table_row('Принимаем первичный ток срабатывания равным, А', 'Iсз', self.isz)
        te.table_row(f'Время срабатывания {self.t_note} , с', 'tср', self.t)

    def table_settings(self):
        te.table_row(self.name, f'{self.isz} A', self.t, '')

    def table_settings_bmz_data(self):
        res = []
        if self.index_ct is not None:
            res.extend([self.isz * self.pris.ct[self.index_ct].i1, self.pris.ct[self.index_ct].i2 * self.isz])
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
