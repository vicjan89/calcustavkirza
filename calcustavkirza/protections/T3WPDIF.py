import math
import os


from textengines.interfaces import TextEngine


from calcustavkirza.classes import Element

class T3WPDIF(Element):
    sn_mva: float
    i_mv: float
    i_lv: float
    v_hv: float
    v_mv: float
    v_lv: float
    i_ct_hv: int
    i_ct_mv: int
    i_ct_lv: int
    i2_ct_hv: int = 5
    i2_ct_mv: int = 5
    i2_ct_lv: int = 5
    Kots: float = 1.15 #рекомендация ABB
    K_per: float
    EndSection1: float = 1.15 #рекомендация ABB
    EndSection2: float = 2.0 #рекомендация ABB
    s2: float
    s3: float = 0.65 #рекомендация ABB 0.5-0.65
    dfvir: float = 0.05
    dU: float #погрешность из-за регулирования равна количеству ступеней РПН минус 1 делёное на 2 умноженное на %
    # изменения напряжения одной ступени делёное на 100
    id: float
    index_ct: int | None = None
    t: float | None = None
    t_note: str  = ''
    time_prot: bool = True
    name: str = 'Дифференциальная защита'
    name_short: str = 'ДЗ'

    def calc_ust(self, te: TextEngine, res_sc_min: list, res_sc_max: list):
        te.table_name(self.name)
        te.table_head('Наименование величины', 'Расчётная формула, обозначение', 'Результат расчёта', widths=(3,2,1))
        te.table_row('Номинальная мощность трансформатора, МВА', 'Sном.',self.sn_mva)
        te.table_row('Номинальное напряжение обмотки высокого напряжения, кВ', 'Uвн.',self.v_hv)
        te.table_row('Номинальное напряжение обмотки среднего напряжения, кВ', 'Uсн.',self.v_mv)
        te.table_row('Номинальное напряжение обмотки низкого напряжения, кВ', 'Uнн.',self.v_lv)
        sqrt3 = math.sqrt(3)
        i_hv = self.sn_mva / self.v_hv / sqrt3 * 1000
        te.table_row('Номинальный первичный ток обмотки высокого напряжения, A', 'Iвн=Sном вн/√3/Uвн', f'{i_hv:.1f}')
        te.table_row('Номинальный первичный ток обмотки среднего напряжения, A', 'Iсн=Sном сн/√3/Uсн', f'{self.i_mv}')
        te.table_row('Номинальный первичный ток обмотки низкого напряжения, A', 'Iнн=Sном нн/√3/Uнн', f'{self.i_lv}')

        te.table_row('Коэффициент трансформации ТТ со стороны высокого напряжения трансформатора, A', 'Kтт вн',
                     f'{self.i_ct_hv}/{self.i2_ct_hv}')
        te.table_row('Коэффициент трансформации ТТ со стороны среднего напряжения трансформатора, A', 'Kтт сн',
                     f'{self.i_ct_mv}/{self.i2_ct_mv}')
        te.table_row('Коэффициент трансформации ТТ со стороны низкого напряжения трансформатора, A', 'Kтт нн',
                     f'{self.i_ct_lv}/{self.i2_ct_lv}')

        te.table_row('Номинальный вторичный ток обмотки высокого напряжения, A', 'I2вн=Iвн/Kтт вн',
                     f'{i_hv * self.i2_ct_hv / self.i_ct_hv:.1f}')
        te.table_row('Номинальный вторичный ток обмотки среднего напряжения, A', 'I2сн=Iсн/Kтт сн',
                     f'{self.i_mv * self.i2_ct_mv / self.i_ct_mv:.1f}')
        te.table_row('Номинальный вторичный ток обмотки низкого напряжения, A', 'I2нн=Iнн/Kтт нн',
                     f'{self.i_lv * self.i2_ct_lv / self.i_ct_lv:.1f}')

        te.table_row('Кратность номинального тока ВН трансформатора к номинальному току ТТ', 'Iвн/Iтт вн ≤ 4',
                     f'{i_hv / self.i_ct_hv:.1f}')
        te.table_row('Кратность номинального тока СН трансформатора к номинальному току ТТ', 'Iсн/Iтт cн ≤ 4',
                     f'{self.i_mv / self.i_ct_mv:.1f}')
        te.table_row('Кратность номинального тока НН трансформатора к номинальному току ТТ', 'Iнн/Iтт нн ≤ 4',
                     f'{self.i_lv / self.i_ct_lv:.1f}')

        i_nb = math.sqrt((self.K_per * 0.1) ** 2 * (1 +  self.dU + self.dfvir) + (self.dU + self.dfvir) ** 2)
        id_calc = self.Kots * self.EndSection1 * i_nb
        s2 = (self.Kots * i_nb * self.EndSection2 - self.id) / (self.EndSection2 - self.EndSection1)
        f_inb = r"I_{\text{нб.расч}*}"
        f_kots = r"K_{\text{отс}}"
        te.table_row('Принимаем тормозной ток окончания первого участка', 'EndSection1', f'{self.EndSection1}')
        te.table_row('Принимаем тормозной ток окончания второго участка', 'EndSection2', f'{self.EndSection2}')
        te.table_row('Дифференциальный расчётный ток срабатывания, о.е.',
                          te.m(r'I_d \geq ' + f_kots + r' \cdot EndSection1 \cdot ' + f_inb), f'{id_calc:.3f}')
        te.table_row('Принимаем дифференциальный ток срабатывания, о.е.', te.m('I_d'), self.id)
        te.table_row('Коэффициент отстройки', te.m(r'K_{\text{отс}}'), self.Kots)
        f_k_per = r"K`_{\text{пер}}"
        f_dU = r"\Delta U_{\text{рег}*}"
        f_df = r"\Delta f_{\text{выр}*}"
        te.table_row('Расчётный ток небаланса (формула приведена в конце таблицы), о.е.', te.m(f_inb), f'{i_nb:.3f}')
        te.table_row('Коэффициент учитывающий переходных процесс', te.m(f_k_per), self.K_per)
        te.table_row('Полная относительная погрешность ТТ в установившемся режиме, о.е.', te.m(r'\varepsilon_*'),
                     0.1)
        te.table_row('Относительная погрешность вызванная регулированием напряжения трансформатора', te.m(f_dU),
                     self.dU)
        te.table_row('Относительная погрешность выравнивания токов плеч', te.m(f_df), self.dfvir)
        f_s2 = r"\frac{" + f_kots + r" \cdot " + f_inb + (r" \cdot EndSection2 - I_d}{EndSection2 - EndSection1} \leqslant s2 "
                                                          r"\leqslant 0.5")
        te.table_row('Коэффициент наклона на втором участке расчётный', te.m(f_s2), f'{s2:.2f}')
        te.table_row('Коэффициент наклона на втором участке принимаем', 'SlopeSection2', f'{self.s2}')
        te.table_row('Коэффициент наклона на третьем участке принимаем', 'SlopeSection3', f'{self.s3}')
        te.table_row('Уставка блокировки при броске тока намагничивания принимается, %', 'I2 / I1', 14)
        te.table_row('Уставка блокировки при при перевозбуждении сердечника трансформатора, %', 'I5 / I1', 25)
        te.table_row('Коэффициент чувствительности дифференциальной защиты', 'Кч = id min kz / id ≥ 2',
                     'Проверку допускается не проводить так как условие выполняется всегда')

        te.math(f_inb + r" = \sqrt{(" + f_k_per + r" \cdot \varepsilon_*)^2 \cdot (1 + " +
                       f_dU + r" + " + f_df + r") + (" + f_dU + r" + " + f_df + r")^2}")
        if self.id <= 0.2:
            te.warning('Согласно рекомандациям ABB минимальный дифференциальный ток должен быть более 0.2')
        if self.s2 < s2:
            te.warning('s2 должно выбираться больше чем рассчитанное значение s2')
        if s2 > 0.5:
            te.warning('s2 должно быть не больше 0.5')

    def table_settings(self):
        t_str = ''
        if self.t:
            t_str += str(self.t)
        if self.k:
            t_str += f'K={self.k} (зависимая время-токовая характеристика)'
        if self.t_au:
            t_str += f' tау={self.t_au}'
        te.table_row(self.name, f'{self.isz} A', t_str, 'При пуске блокирует вышестоящую ЛЗШ' if self.bl else '')

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
