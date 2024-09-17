import math


from textengines.interfaces import TextEngine


from calcustavkirza.classes import Element


class TO(Element):
    i_kz_begin_index: int | None = None # индекс шины для проверки чувствительности
    i_kz_begin: int | None = None # ток КЗ в максимальном режиме в начале линии для проверки чувствительности
    i_kz_end_index: int | None = None # индекс шины для отстройки тока срабатывания
    i_kz_end: int | None = None # ток КЗ в максимальном режиме в конце линии для отстройки тока срабатывания
    i_kz_end_note: str = ''
    kn: float = 1.1
    Kns: float = 1.1
    isz: int
    isz_note: str = ''
    index_ct: int | None = None
    isz_posl: float | None = None
    isz_posl_note: str = ''
    isz_prev: float | None = None #ток срабатывания токовой отсечки предыдещей защиты
    isz_prev_note: str = ''
    t: float = 0.
    t_note: str  = ''
    note: str  = ''
    k: int | None = None # коэффициент кривой обратнозависимой характеристики
    i_btn: float | None = None
    time_prot: bool = True
    name: str = 'Токовая отсечка'
    name_short: str = 'ТО'

    def sogl_posl(self, te: TextEngine):
        isz_posl_sogl = self.isz_posl/self.Kns
        if isz_posl_sogl <= self.isz:
            self.add_warning('Защита не согласована с последующей защитой')
        te.table_row(f'Первичный ток срабатывания защиты по условию согласования с последующей защитой '
                     f'{self.isz_posl_note}, А',
                     'Iсз ≤ Iсз.посл./Kн.с.', f'{self.isz_posl}/{self.Kns} ={isz_posl_sogl:.2f}')
        te.table_row('Коэффициент надёжности согласования с последующей защитой',
                     'Kн.с.', self.Kns)

    def sogl_prev(self, te: TextEngine):
        isz_prev_sogl = self.isz_prev * self.Kns
        if isz_prev_sogl >= self.isz:
            self.add_warning('Защита не согласована с предыдущей защитой')
        te.table_row(f'Первичный ток срабатывания защиты по условию согласования с последующей защитой '
                     f'{self.isz_prev_note}, А',
                     'Iсз ≤ Iсз.пред.*Kн.с.', f'{self.isz_prev}*{self.Kns} ={isz_prev_sogl:.2f}')
        te.table_row('Коэффициент надёжности согласования с последующей защитой',
                     'Kн.с.', self.Kns)

    def total(self, te: TextEngine):
        te.table_row(f'Принимаем первичный ток срабатывания защиты {self.isz_note} равным, А', 'Iсз', self.isz)
        te.table_row(f'Время срабатывания защиты {self.note}, с', 'tср', self.t)

    def head(self, te: TextEngine):
        te.table_head('Наименование величины', 'Расчётная формула, обозначение', 'Результат расчёта', widths=(3,2,1))

    def calc_ust(self, te: TextEngine, res_sc_min: list, res_sc_max: list):
        te.table_name(self.name)
        self.head(te)
        if self.i_kz_end_index is not None or self.i_kz_end is not None:
            if self.i_kz_end_index is not None:
                i_kz_max  = res_sc_max[self.i_kz_end_index][1]
            else:
                i_kz_max = self.i_kz_end
            te.table_row('Ток срабатывания защиты по условию отстройки от КЗ в конце защищаемого участка, А',
                              r'I ≥ Kн*Iкз.конц.', f'{self.kn} * {i_kz_max:.2f} ={i_kz_max*self.kn:.2f}')
            te.table_row('Максимальный ток КЗ в конце защищаемого участка', f'Iкз.конц.{self.i_kz_end_note}',
                         i_kz_max)
            te.table_row('Коэффициент надёжности отстройки', te.m(r'K_{H}'), self.kn)
        if self.i_btn:
            te.table_row('Ток срабатывания защиты по условию отстройки от броска тока намагничивания '
                              'трансформаторов, А', te.m(r'I ≥ K_{BTH} \cdot \frac{\sum S_n}{U_n \cdot \sqrt{3}}'),
                              f'{self.i_btn:.2f}')
            te.table_row('Коэффициент отстройки от броска тока намагничивания ', te.m(r'K_{BTH}'), 4)
        if self.isz_posl:
            self.sogl_posl(te)
        if self.isz_prev:
            self.sogl_prev(te)
        self.total(te)
        if self.i_kz_begin_index is not None:
            i_kz_max_begin = res_sc_max[str(self.i_kz_begin_index)][1]
        else:
            i_kz_max_begin = self.i_kz_begin
        k_ch = i_kz_max_begin/self.isz
        te.table_row('Проверка коэффициента чувствительности при КЗ в начале линии',
                          'Кч=Iкзмакс/Iсз', f'{k_ch:.2f}')
        te.table_row(f'Максимальный ток КЗ в начале защищаемого участка приведенный к напряжению места установки '
                          f'защиты', 'Iкзмакс', f'{i_kz_max_begin:.2f}')


        if self.i_btn and self.i_btn >= self.isz:
            self.add_warning(f'Бросок тока намагничивания токовой отсечки больше уставки ({i_btn})')
        if k_ch < 1.2:
            self.add_warning(f'Коэффициент чувствительности токовой отсечки мал ({k_ch:.2f}) ' \
                            f'Нужна уставка {i_kz_max/1.2:.2f}')
        if self.i_kz_end_index is not None and i_kz_max > self.isz:
            self.add_warning(f'Токовая отсечка не отстроена от КЗ в конце защищаемого участка '
                            f'({i_kz_max})')
        self.write_warnings(te)

    def table_settings(self, te: TextEngine):
        t_str = ''
        if self.t is not None:
            t_str += str(self.t)
        if self.k:
            t_str += f'K={self.k}'
        te.table_row(self.name, f'{self.isz} A', t_str, self.isz_note)

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
