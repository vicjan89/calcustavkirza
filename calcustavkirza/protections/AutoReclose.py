from calcustavkirza.classes import Element
from textengines.interfaces import TextEngine

class AutoRecloseStore(Element):
    '''
    t: float
    t_note: str = "повторное включение"
    time_prot: bool = False
    name: str = "Автоматическое повторное включение"
    name_short: str = 'АПВ'
    '''

    t: float
    t_note: str = "повторное включение"
    time_prot: bool = False
    name: str = "Автоматическое повторное включение"
    name_short: str = 'АПВ'

class AutoReclose:

    def __init__(self, te: TextEngine, store, *args, **kwargs):
        self.te = te
        self.store = store

    def calc_settings(self):
        te.table_name(self.store.name)
        te.table_head('Наименование величины', 'Расчётная формула, обозначение', 'Результат расчёта', widths=(3,2,1))
        te.table_row('Время срабатывания, с', 'tср', self.store.t)

    def table_settings(self, te: TextEngine):
        te.table_row(self.name,'', self.t, '')

    def table_settings_bmz_data(self):
        return ( self.t, )

    def table_settings_bmz_second(self):
        return ('Т сраб,с', )
    def table_settings_bmz_first(self):
        return f'{self.name_short} {self.t_note}'

    def table_settings_bmz(self):
        return [self.table_settings_bmz_first(), self.table_settings_bmz_second(), self.table_settings_bmz_data()]
