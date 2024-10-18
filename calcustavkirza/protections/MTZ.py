from textengines.interfaces import TextEngine


from calcustavkirza.classes import Element


class MTZ(Element):
    '''
    i_kz_end_index: int | None = None #index bus in end protected element
    i_kz_min: float | None = None #use if index is none
    i_kz_min_note: str = ''
    index_kz_min_res: int | None = None
    i_kz_min_res: float | None = None
    i_kz_min_res_note: str = ''
    irmax: float | None = None
    kn: float = 1.1
    kns: float = 1.1
    Kv: float = 0.95
    Ksz: float = 1.3 # коэффициент самозапуска
    isz: int
    isz_note: str = ''
    index_ct: int | None = None
    t: float | str | None = None
    k: int | None = None # коэффициент кривой обратнозависимой характеристики
    t_note: str  = ''
    t_au: float | None = None
    isz_posl: float | None = None
    isz_posl_note: str = ''
    isz_prev: float | None = None
    isz_prev_note: str = ''
    bl: bool = False
    time_prot: bool = True
    name: str = 'Максимальная токовая защита'
    name_short: str = 'МТЗ'
    '''
    i_kz_end_index: int | None = None #index bus in end protected element
    i_kz_min: float | None = None #use if index is none
    i_kz_min_note: str = ''
    index_kz_min_res: int | None = None
    i_kz_min_res: float | None = None
    i_kz_min_res_note: str = ''
    irmax: float | None = None
    kn: float = 1.1
    kns: float = 1.1
    Kv: float = 0.95
    Ksz: float = 1.3 # коэффициент самозапуска
    isz: int
    isz_note: str = ''
    index_ct: int | None = None
    t: float | str | None = None
    k: int | None = None # коэффициент кривой обратнозависимой характеристики
    t_note: str  = ''
    t_au: float | None = None
    isz_posl: float | None = None
    isz_posl_note: str = ''
    isz_prev: float | None = None
    isz_prev_note: str = ''
    bl: bool = False
    time_prot: bool = True
    name: str = 'Максимальная токовая защита'
    name_short: str = 'МТЗ'

    def calc_ust(self, te: TextEngine, res_sc_min: list, res_sc_max: list):
        te.table_name(self.name)
        te.table_head('Наименование величины', 'Расчётная формула, обозначение', 'Результат расчёта', widths=(3,2,1))
        if self.irmax:
            iszpredv = self.kn/self.Kv*self.Ksz*self.irmax
            te.table_row('Первичный ток срабатывания защиты по отстройке от тока нагрузки, А',
                              'Iсз≥Кн / Кв·Ксзп·Iрмакс', f'{iszpredv:.2f}')
            te.table_row('Коэффициент надёжности', 'Кн', self.kn)
            te.table_row('Коэффициент возврата', 'Кв', self.Kv)
            te.table_row('Коэффициент самозапуска', 'Ксзп', self.Ksz)
            te.table_row('Максимальный рабочий ток или номинальный ток ТТ, А', 'Iрмакс', f'{self.irmax:.2f}')
        if self.isz_prev:
            te.table_row(f'Первичный ток срабатывания защиты по условию согласования с предыдущей защитой '
                              f'{self.isz_prev_note}, А',
                              'Iсз ≥ Kн.с.·Iсз.посл.', f'{self.kns}*{self.isz_prev} ={self.kns*self.isz_prev:.2f}')
            te.table_row('Коэффициент надёжности согласования с предыдущей защитой',
                              'Kн.с.', self.kns)
        if self.isz_posl:
            te.table_row(f'Первичный ток срабатывания защиты по условию согласования с последующей защитой '
                         f'{self.isz_posl_note}, А',
                         'Iсз ≥ Iсз.посл./Kн.с.', f'{self.isz_posl}/{self.kns} ={self.isz_posl/self.kns:.2f}')
            te.table_row('Коэффициент надёжности согласования с последующей защитой',
                         'Kн.с.', self.kns)
        te.table_row(f'Принимаем первичный ток срабатывания защиты {self.isz_note} равным, А', 'Iсз', self.isz)
        if self.i_kz_end_index is not None:
            i_kz_min = res_sc_min[str(self.i_kz_end_index)][1]
        else:
            i_kz_min = self.i_kz_min
        if i_kz_min:
            k_ch = i_kz_min / self.isz
            te.table_row('Проверка коэффициента чувствительности в основной зоне',
                              'Кч=Iкзмин/Iсз >= 1.5', f'{k_ch:.2f}')
            te.table_row(f'Минимальный ток КЗ в конце защищаемого участка приведенный к напряжению места установки '
                              f'защиты', f'Iкзмин{self.i_kz_min_note}', f'{i_kz_min:.1f}')
        if self.index_kz_min_res is not None:
            i_kz_min_res = res_sc_min[str(self.index_kz_min_res)][1]
        else:
            if self.i_kz_min_res:
                i_kz_min_res = self.i_kz_min_res
            else:
                i_kz_min_res = None
        if i_kz_min_res:
            k_ch_res = i_kz_min_res / self.isz
            note = ''
            if k_ch_res < 1.3:
                note = '. Допускается не резервировать отключения КЗ (п.3.2.17 ПУЭ)'
            te.table_row(f'Проверка коэффициента чувствительности в зоне резервирования{note}',
                              'Кч=Iкзмин/Iсз >= 1.3', f'{k_ch_res:.2f}')
            te.table_row(f'Минимальный ток КЗ в конце зоны резервирования приведенный к напряжению места установки '
                              f'защиты, A', 'Iкзмин', f'{self.i_kz_min_res_note} {i_kz_min_res}')
        if self.t is not None:
            te.table_row(f'Время срабатывания защиты, с {self.t_note}', 'tср', self.t)
        if self.k:
            te.table_row(f'Коэффициент, характеризующий вид зависимой характеристики', 'k', self.k)
        if self.bl:
            te.table_row('Блокирует ЛЗШ без выдержки времени, с', 't', 0)
        if self.t_au:
            te.table_row('Время срабатывания защиты при автоматическом ускорении, с', 't АУ', self.t_au)
        if i_kz_min and (k_ch < 1.5):
            self.add_warning(f'Коэффициент чувствительности мал ({k_ch:.2f})')
        if i_kz_min_res and k_ch_res < 1.3:
            self.add_warning(f'Коэффициент чувствительности в зоне резервирования мал ({k_ch:.2f})')

    def table_settings(self, te: TextEngine):
        t_str = ''
        if self.t is not None:
            t_str += str(self.t)
        if self.k:
            t_str += f'K={self.k} (зависимая время-токовая характеристика)'
        if self.t_au:
            t_str += f' tау={self.t_au}'
        note = self.isz_note
        if self.bl:
            note = 'При пуске блокирует вышестоящую ЛЗШ. ' + note
        te.table_row(self.name, f'{self.isz} A', t_str, note)

    def table_settings_bmz_data(self):
        res = [self.isz]
        if self.index_ct is not None:
            res.append(self.pris.ct[self.index_ct].i1toi2(self.isz))
        else:
            res.append('')
        res.extend([self.t, self.k, self.t_au])
        return res

    def table_settings_bmz_second(self):
        res = ['А перв']
        res.append('А втор')
        res.extend(['Т сраб,с', 'К харк', 'Т сраб АУ,с'])
        return res

    def table_settings_bmz_first(self):
        return f'{self.name_short} {self.t_note if self.t_note else "отключение"}'

    def table_settings_bmz(self):
        return [self.table_settings_bmz_first(), self.table_settings_bmz_second(), self.table_settings_bmz_data()]