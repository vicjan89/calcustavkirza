from textengines.interfaces import TextEngine


from calcustavkirza.classes import Element, Doc


class AvrDoc(Doc):

    def calc_ust(self, te: TextEngine, **kwargs):
        te.table_name(self.name)
        te.table_head('Наименование величины', 'Расчётная формула, обозначение', 'Результат расчёта',
                           widths=(3,2,1))
        if self.t:
            te.table_row(f'Время срабатывания на отключение основного питания и включение резервного {self.note}, с',
                              'tср=tср вышестоящего АВР + dt', self.t)
        if self.tpred:
            te.table_row(f'Время срабатывания на отключение основного питания вышестоящего АВР, с',
                              'tср пред.', self.tpred)
        if self.tvozvr:
            te.table_row(f'Время срабатывания возврата АВР (по рекомендациям завода-изготовителя терминалов защит), с',
                              'tвозвр', self.tvozvr)

    def table_settings(self):
        t_str = ''
        if self.t:
            t_str += f'Время срабатывания на отключение основного питания = {self.t}'
        if self.tvozvr:
            t_str += f' Время срабатывания возврата АВР = {self.tvozvr}'
        te.table_row(self.name, f'{self.note}', t_str, '')

    def table_settings_bmz_data(self):
        return ( self.t, )

    def table_settings_bmz_second(self):
        return ('Т сраб,с', )
    def table_settings_bmz_first(self):
        return f'{self.name_short} {self.t_note}'

    def table_settings_bmz(self):
        return [self.table_settings_bmz_first(), self.table_settings_bmz_second(), self.table_settings_bmz_data()]


class Avr(Element, AvrDoc):

    t: float
    t_note: str = "отключение основного питания и включение резервного"
    tpred: float
    tvozvr: float | None = None
    note: str = ''
    name: str = 'Автоматическое включение резерва'
    name_short: str = 'АВР'

