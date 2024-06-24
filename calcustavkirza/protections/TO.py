import math


from textengines.interfaces import TextEngine


from calcustavkirza.classes import Element


class TO(Element):
    i_kz_begin_index: int # индекс шины для проверки чувствительности
    i_kz_end_index: int | None = None # индекс шины для отстройки тока срабатывания
    kn: float = 1.1
    Kns: float = 1.1
    isz: int
    isz_note: str = ''
    index_ct: int | None = None
    isz_posl: float | None = None
    isz_posl_note: str = ''
    t: float
    t_note: str  = ''
    note: str  = ''
    k: int | None = None # коэффициент кривой обратнозависимой характеристики
    i_btn: float | None = None
    time_prot: bool = True
    name: str = 'Токовая отсечка'
    name_short: str = 'ТО'

    def calc_ust(self, te: TextEngine, res_sc_min: list, res_sc_max: list):
        te.table_name(self.name)
        te.table_head('Наименование величины', 'Расчётная формула, обозначение', 'Результат расчёта', widths=(3,2,1))
        if self.i_kz_end_index is not None:
            i_kz_max  = self.net.res_sc_bus.get_max(self.i_kz_end_index)
            bus_u = self.net.net.bus.at[self.i_kz_end_index, 'vn_kv']
            if bus_u != 10:
                i_kz_max = i_kz_max / 10.5 * bus_u
            te.table_row('Ток срабатывания защиты по условию отстройки от КЗ в конце защищаемого участка, А',
                              r'I ≥ Kн*Iкз.конц.', f'{i_kz_max:.2f}* {self.kn} ={i_kz_max*self.kn:.2f}')
            te.table_row('Коэффициент надёжности отстройки', te.m(r'K_{H}'), self.kn)
        # if self.i_btn:
        #     i_btn = self.i_btn
        # else:
        #     i_btn = self.net.res_mci.get_max(self.pris.loc)
        # te.table_row('Ток срабатывания защиты по условию отстройки от броска тока намагничивания '
        #                   'трансформаторов, А', te.m(r'I ≥ K_{BTH} \cdot \frac{\sum S_n}{U_n \cdot \sqrt{3}}'),
        #                   f'{i_btn:.2f}')
        # te.table_row('Коэффициент отстройки от броска тока намагничивания ', te.m(r'K_{BTH}'), 4)
        if self.isz_posl:
            te.table_row(f'Первичный ток срабатывания защиты по условию согласования с последующей защитой '
                              f'{self.isz_posl_note}, А',
                              'Iсз ≥ Kн.с.·Iсз.посл.', f'{self.Kns}*{self.isz_posl} ={self.Kns*self.isz_posl:.2f}')
            te.table_row('Коэффициент надёжности согласования с последующей защитой',
                              'Kн.с.', self.Kns)
        te.table_row(f'Принимаем первичный ток срабатывания защиты {self.isz_note} равным, А', 'Iсз', self.isz)
        i_kz_max_begin = res_sc_max[self.i_kz_begin_index][1]
        k_ch = i_kz_max_begin/self.isz
        te.table_row('Проверка коэффициента чувствительности при КЗ в начале линии',
                          'Кч=Iкзмакс/Iсз', f'{k_ch:.2f}')
        te.table_row(f'Максимальный ток КЗ в начале защищаемого участка приведенный к напряжению места установки '
                          f'защиты', 'Iкзмакс', f'{i_kz_max_begin:.2f}')
        te.table_row(f'Время срабатывания защиты {self.note}, с', 'tср', self.t)


        # if i_btn >= self.isz:
        #     te.warning(f'Бросок тока намагничивания токовой отсечки {self.pris.name} больше уставки ({i_btn})')
        if k_ch < 1.2:
            te.warning(f'Коэффициент чувствительности токовой отсечки {self.pris.name} мал ({k_ch:.2f}) ' \
                            f'Нужна уставка {i_kz_max/1.2:.2f}')
        if self.i_kz_end_index is not None and i_kz_max > self.isz:
            te.warning(f'Токовая отсечка {self.pris.name} не отстроена от КЗ в конце защищаемого участка '
                            f'({i_kz_max})')

    def table_settings(self):
        t_str = ''
        if self.t:
            t_str += str(self.t)
        if self.k:
            t_str += f'K={self.k}'
        te.table_row(self.name, f'{self.isz} A', t_str, '')

    def table_settings_bmz_data(self):
        res = [self.isz]
        if self.index_ct is not None:
            res.append(self.pris.ct[self.index_ct].i1toi2(self.isz))
        res.append(self.t)
        return res

    def table_settings_bmz_second(self):
        res = ['А перв']
        if self.index_ct is not None:
            res.append('А втор')
        res.append('Т сраб,с')
        return res

    def table_settings_bmz_first(self):
        return f'{self.name_short} {self.t_note if self.t_note else "отключение"}'

    def table_settings_bmz(self):
        return [self.table_settings_bmz_first(), self.table_settings_bmz_second(), self.table_settings_bmz_data()]
