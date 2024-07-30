from textengines.interfaces import TextEngine


from calcustavkirza.classes import Element


class LZSH(Element):
    isz: float
    ikz_otstr: float | None = None
    ikz_otstr_note: str = ''
    i_kz_min: float
    t: float | None = None
    t_note: str = 'отключение'
    index_ct: int | None = None
    k: float | None = None
    Kn: float = 1.1
    Kv: float = 0.95
    Ksz: float = 1.3 # коэффициент самозапуска
    irmax: float | None = None #ток нагрузки максимальный
    bl: bool = False
    time_prot: bool = True
    name: str = 'Логическая защита шин'
    name_short: str = 'ЛЗШ'

    def calc_ust(self, te: TextEngine, res_sc_min: list, res_sc_max: list):
        if not self.name:
            self.name = 'Логическая защита шин'
        te.table_name(self.name)
        te.table_head('Наименование величины', 'Расчётная формула, обозначение', 'Результат расчёта', widths=(3,2,1))
        if self.irmax:
            Irmax = self.irmax
        else:
            Irmax = self.net.res_pf.get_max(self.pris.loc)
        iszpredv = self.Kn/self.Kv*self.Ksz*Irmax
        te.table_row('Первичный ток срабатывания защиты по отстройке от тока нагрузки, А',
                          'Iсз≥Кн / Кв·Ксзп·Iрмакс', f'{iszpredv:.2f}')
        te.table_row('Коэффициент надёжности', 'Кн', self.Kn)
        te.table_row('Коэффициент возврата', 'Кв', self.Kv)
        te.table_row('Коэффициент самозапуска', 'Ксзп', self.Ksz)
        te.table_row('Максимальный рабочий ток или номинальный ток ТТ, А', 'Iрмакс', f'{Irmax:.2f}')
        if self.ikz_otstr:
            te.table_row(f'Первичный ток срабатывания защиты по отстройке от тока {self.ikz_otstr_note}, А',
                              'Iсз≥Кн·Iкз.отстр', f'1.1·{self.ikz_otstr} = {1.1*self.ikz_otstr:.2f}')
        te.table_row('Принимаем первичный ток срабатывания защиты равным, А', 'Iсз', self.isz)
        k_ch = self.i_kz_min / self.isz
        te.table_row('Проверка коэффициента чувствительности',
                          'Кч=Iкзмин/Iсз >= 1.5', f'{k_ch:.2f}')
        te.table_row(f'Минимальный ток КЗ в конце защищаемого участка приведенный к напряжению места установки '
                          f'защиты', 'Iкзмин', f'{self.i_kz_min}')
        if self.t:
            te.table_row('Время срабатывания защиты, с', 'tср', self.t)
        if self.k:
            te.table_row(f'Коэффициент, характеризующий вид зависимой характеристики', 'k', self.k)
        if self.bl:
            te.table_row('Блокировка вышестоящего ЛЗШ без выдержки времени', 'I', self.isz)

    def table_settings(self):
        t_str = ''
        if self.t:
            t_str += str(self.t)
        if self.k:
            t_str += f'K={self.k} (зависимая время-токовая характеристика)'
        te.table_row(self.name, f'{self.isz} A', t_str, 'При пуске блокирует вышестоящую ЛЗШ (выполнить отдельным '
                                                             'токовым органом, не блокируемым блокирующими '
                                                             'органами)' if self.bl else '')

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
