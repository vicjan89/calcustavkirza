from textengines.interfaces import TextEngine


from calcustavkirza.classes import Element


class Avr:

    def __init__(self, te: TextEngine, store, *args, **kwargs):
        self.te = te
        self.store = store

    def calc_settings(self):
        self.te.table_name(self.store.name)
        self.te.table_head('Наименование величины', 'Расчётная формула, обозначение', 'Результат расчёта',
                           widths=(3,2,1))
        if self.store.t:
            self.te.table_row(f'Время срабатывания на отключение основного питания и включение резервного {self.note}, с',
                              'tср=tср вышестоящего АВР + dt', self.t)
        if self.store.t_subsequent:
            self.te.table_row(f'Время срабатывания на отключение основного питания вышестоящего АВР, с',
                              'tср пред.', self.store.t_subsequent)
        if self.store.tvozvr:
            self.te.table_row(f'Время срабатывания возврата АВР (по рекомендациям завода-изготовителя терминалов защит), с',
                              'tвозвр', self.store.tvozvr)

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


class AvrStore(Element):

    t: float
    t_note: str = "отключение основного питания и включение резервного"
    tpred: float
    tvozvr: float | None = None
    note: str = ''
    name: str = 'Автоматическое включение резерва'
    name_short: str = 'АВР'

