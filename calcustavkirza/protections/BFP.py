from textengines.interfaces import TextEngine

from calcustavkirza.classes import Element, Doc

class BFPDoc(Doc):

    def calc_ust(self, te: TextEngine, res_sc_min: list, res_sc_max: list):
        te.table_name(self.name)
        te.table_head('Наименование величины', 'Расчётная формула, обозначение', 'Результат расчёта', widths=(3,2,1))
        te.table_row('Принимаем первичный ток срабатывания равным, А', 'Iсз', self.isz)
        te.table_row(f'Время срабатывания {self.t_note} , с', 'tср', self.t)

    def table_settings(self, te: TextEngine):
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

    def ap_generate(self, te: TextEngine):
        te.ul(self.name + ' Пуск УРОВ выключателя осуществляется по логике от собственных функций защит устройства или'
                          ' от отключающего импульса по внешнему входу от всех защит, действующих на отключение '
                          'выключателя. По истечении выдержки времени при наличии тока повреждения большего уставки по '
                          'току УРОВ действует на отключение выключателей смежных питающих присоединений;')

class BFP(Element, BFPDoc):
    '''
    Класс для описания УРОВ
    isz: float # ток срабатывания в амперах
    t: float # время срабатывания
    t_note: str = "отключение вышестоящего присоединения"
    index_ct: int | None = None
    time_prot: bool = False
    name: str = 'Устройство резервирования отказа выключателя'
    name_short: str = 'УРОВ'
    '''
    isz: float # ток срабатывания в амперах
    t: float # время срабатывания
    t_note: str = "отключение вышестоящего присоединения"
    index_ct: int | None = None
    time_prot: bool = False
    name: str = 'Устройство резервирования отказа выключателя'
    name_short: str = 'УРОВ'

