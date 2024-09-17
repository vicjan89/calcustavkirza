import math


from textengines.interfaces import TextEngine


from calcustavkirza.protections.MTZ import MTZ


class MTZSVG1(MTZ):
    q: float #номинальная реактивная мощность БСК в кВА
    u: float #номинальное напряжение сети
    ku: float = 1.35 #коэффициент загрузки БСК по напряжению
    kn: float = 1.3
    t: float = 1.


    def calc_ust(self, te: TextEngine, res_sc_min: list, res_sc_max: list):
        te.table_name(self.name)
        te.table_head('Наименование величины', 'Расчётная формула, обозначение', 'Результат расчёта', widths=(3, 2, 1))
        i_nom = self.q / self.u / math.sqrt(3)
        te.table_row('Первичный ток срабатывания защиты по отстройке от тока перегрузки конденсаторов при повышении '
                     'напряжения , А',
                     te.m(r'I_{\text{ср}} \geq K_{\text{ОТС}} \cdot K_U \cdot I_{\text{НОМ.БСК}}'),
                     f'{self.kn} * {self.ku} * {i_nom:.1f} ={i_nom * self.kn * self.ku:.1f}')
        te.table_row('Номинальная реактивная мощность БСК, МВА', te.m(r'Q_{\text{Н.БСК}}'), self.q)
        te.table_row('Номинальный ток БСК, A',
                     te.m(r'I_{\text{НОМ.БСК}} = \frac{Q_{\text{Н.БСК}}}{U_{\text{НОМ}} \cdot \sqrt{3}}'), f'{i_nom:.1f}')
        te.table_row('Коэффициент отстройки', te.m(r'K_{\text{ОТС}}'), self.kn)
        te.table_row('Коэффициент запаса, учитывающий перенапряжения в сети, допустимые для БСК в течение '
                     'ограниченного времени', te.m('K_U'), self.ku)
        if self.isz_prev:
            te.table_row(f'Первичный ток срабатывания защиты по условию согласования с предыдущей защитой '
                         f'{self.isz_prev_note}, А',
                         'Iсз ≥ Iсз.посл./Kн.с.', f'{self.isz_prev}/{self.kns} ={self.isz_prev / self.kns:.2f}')
            te.table_row('Коэффициент надёжности согласования с предыдущей защитой',
                         'Kн.с.', self.kns)
        te.table_row(f'Принимаем первичный ток срабатывания защиты ({self.isz_note}) равным, А', 'Iсз', self.isz)
        if self.i_kz_end_index is not None:
            i_kz_min = res_sc_min[str(self.i_kz_end_index)][1]
        else:
            i_kz_min = self.i_kz_min
        k_ch = i_kz_min / self.isz
        te.table_row('Проверка коэффициента чувствительности в основной зоне',
                     'Кч=Iкзмин/Iсз >= 1.5', f'{k_ch:.2f}')
        te.table_row(f'Минимальный ток КЗ в конце защищаемого участка приведенный к напряжению места установки '
                     f'защиты', f'Iкзмин{self.i_kz_min_note}', f'{i_kz_min:.1f}')
        te.table_row(f'Время срабатывания защиты, с {self.t_note}', 'tср', self.t)
        if self.bl:
            te.table_row('Блокирует ЛЗШ без выдержки времени, с', 't', 0)
        if k_ch < 1.5:
            te.warning(f'Коэффициент чувствительности мал ({k_ch:.2f})')

class MTZSVG2(MTZ):
    q: float #номинальная реактивная мощность БСК в кВА
    u: float #номинальное напряжение сети
    kn: float = 1.3
    t: float = 1.5
    name: str = 'Максимальная токовая защита от перегрузки токами высших гармоник (ANSI 51R(49))'
    name_short: str = 'МТЗ ANSI51R(49)'


    def calc_ust(self, te: TextEngine, res_sc_min: list, res_sc_max: list):
        te.table_name(self.name)
        te.table_head('Наименование величины', 'Расчётная формула, обозначение', 'Результат расчёта', widths=(3, 2, 1))
        i_nom = self.q / self.u / math.sqrt(3)
        te.table_row('Первичный ток срабатывания защиты по отстройке от тока перегрузки БСК токами высших гармоник '
                     '(ступень должна реагировать на полный действующий ток всех гармоник (51R RMS overcurrent '
                     'protection). Возможно использование токового органа от тепловой (термической) перегрузки (ANSI 49 '
                     'Thermal overload protection), А',
                     te.m(r'I_{\text{ср}} \geq K_{\text{ОТС}} \cdot I_{\text{НОМ.БСК}}'),
                     f'{self.kn} * {i_nom:.1f} ={i_nom * self.kn:.1f}')
        te.table_row('Номинальная реактивная мощность БСК, МВА', te.m(r'Q_{\text{Н.БСК}}'), self.q)
        te.table_row('Номинальный ток БСК, A',
                     te.m(r'I_{\text{НОМ.БСК}} = \frac{Q_{\text{Н.БСК}}}{U_{\text{НОМ}} \cdot \sqrt{3}}'), f'{i_nom:.1f}')
        te.table_row('Коэффициент отстройки', te.m(r'K_{\text{ОТС}}'), self.kn)
        if self.isz_prev:
            te.table_row(f'Первичный ток срабатывания защиты по условию согласования с предыдущей защитой '
                         f'{self.isz_prev_note}, А',
                         'Iсз ≥ Iсз.посл./Kн.с.', f'{self.isz_prev}/{self.kns} ={self.isz_prev / self.kns:.2f}')
            te.table_row('Коэффициент надёжности согласования с предыдущей защитой',
                         'Kн.с.', self.kns)
        te.table_row(f'Принимаем первичный ток срабатывания защиты ({self.isz_note}) равным, А', 'Iсз', self.isz)
        te.table_row(f'Время срабатывания защиты, с {self.t_note}', 'tср', self.t)
        if self.bl:
            te.table_row('Блокирует ЛЗШ без выдержки времени, с', 't', 0)
