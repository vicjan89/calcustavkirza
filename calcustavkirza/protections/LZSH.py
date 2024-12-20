from textengines.interfaces import TextEngine


from calcustavkirza.classes import Element, Doc

class LZSHDoc(Doc):

    def calc_ust(self, te: TextEngine, res_sc_min: list, res_sc_max: list):
        if not self.name:
            self.name = 'Логическая защита шин'
        te.table_name(self.name)
        te.table_head('Наименование величины', 'Расчётная формула, обозначение', 'Результат расчёта', widths=(3,2,1))
        if self.irmax:
            iszpredv = self.Kn/self.Kv*self.Ksz*self.irmax
            te.table_row('Первичный ток срабатывания защиты по отстройке от тока нагрузки, А',
                         'Iсз≥Кн / Кв·Ксзп·Iрмакс', f'{iszpredv:.2f}')
            te.table_row('Коэффициент надёжности', 'Кн', self.Kn)
            te.table_row('Коэффициент возврата', 'Кв', self.Kv)
            te.table_row('Коэффициент самозапуска', 'Ксзп', self.Ksz)
            te.table_row('Максимальный рабочий ток или номинальный ток ТТ, А', 'Iрмакс', f'{self.irmax:.2f}')
        if self.ikz_otstr:
            te.table_row(f'Первичный ток срабатывания защиты по отстройке от тока {self.ikz_otstr_note}, А',
                         'Iсз≥Кн·Iкз.отстр', f'1.1·{self.ikz_otstr} = {1.1*self.ikz_otstr:.2f}')
        te.table_row('Принимаем первичный ток срабатывания защиты равным, А', 'Iсз', self.isz)
        if self.i_kz_end_index is not None:
            i_kz_min = res_sc_min[str(self.i_kz_end_index)][1]
        else:
            i_kz_min = self.i_kz_min
        if i_kz_min and self.isz:
            k_ch = i_kz_min / self.isz
            te.table_row('Проверка коэффициента чувствительности',
                         'Кч=Iкзмин/Iсз >= 1.5', f'{k_ch:.2f}')
            te.table_row(f'Минимальный ток КЗ в конце защищаемого участка приведенный к напряжению места установки '
                         f'защиты, A', 'Iкзмин', f'{i_kz_min:.1f}')
        if self.t:
            te.table_row('Время срабатывания защиты, с', 'tср', self.t)
        if self.k:
            te.table_row(f'Коэффициент, характеризующий вид зависимой характеристики', 'k', self.k)

    def table_settings(self, te: TextEngine):
        t_str = ''
        if self.t:
            t_str += str(self.t)
        if self.k:
            t_str += f'K={self.k} (зависимая время-токовая характеристика)'
        te.table_row(self.name, f'{self.isz} A', t_str, self.t_note)

    def table_settings_bmz_data(self):
        res = [self.isz]
        if self.index_ct is not None:
            res.append(self.pris.ct[self.index_ct].i1toi2(self.isz))
        res.extend([self.t, self.k])
        return res

    def table_settings_bmz_second(self):
        res = ['А перв']
        if self.index_ct is not None:
            res.append('А втор')
        res.extend(['Т сраб,с', 'К харк'])
        return res

    def table_settings_bmz_first(self):
        return f'{self.name_short} {self.t_note}'

    def table_settings_bmz(self):
        return [self.table_settings_bmz_first(), self.table_settings_bmz_second(), self.table_settings_bmz_data()]

    def ap_generate(self, te: TextEngine):
        te.ul(self.name + ', выполняется отдельными токовыми ступенями терминалов защит')

class LZSH(Element):
    '''
    :param isz: ток срабатывания
    :type isz: float
    :param i_kz_min: митимальный ток КЗ для проверки чувтсвительности
    :type i_kz_min: float
    :param t: время срабатывания
    :type t: float
    '''
    isz: float
    ikz_otstr: float | None = None
    ikz_otstr_note: str = ''
    i_kz_min: float
    t: float | None = None
    t_note: str = ''
    index_ct: int | None = None
    k: float | None = None
    Kn: float = 1.1
    Kv: float = 0.95
    Ksz: float = 1.3 # коэффициент самозапуска
    irmax: float | None = None #ток нагрузки максимальный
    name: str = 'Логическая защита шин'
    name_short: str = 'ЛЗШ'

