import math
import os


from pathlib import Path


from classes import Element

class T3WPDIF(Element):
    sn_mva: float
    i_mv: float
    i_lv: float
    v_hv: float
    v_mv: float
    v_lv: float
    Kots: float = 1.1
    id: float
    index_ct: int | None = None
    t: float | None = None
    t_note: str  = ''
    time_prot: bool = True
    name: str = 'Дифференциальная защита'
    name_short: str = 'ДЗ'

    def calc_ust(self):
        path = os.path.dirname(os.path.abspath(__file__))
        if not self.name:
            self.name = 'Дифференциальная защита'
        self.te.table_name(self.name)
        self.te.table_head('Наименование величины', 'Расчётная формула, обозначение', 'Результат расчёта', widths=(3,2,1))
        self.te.table_row('Номинальная мощность трансформатора, МВА', 'Sном.',self.sn_mva)
        self.te.table_row('Номинальное напряжение обмотки высокого напряжения, кВ', 'Uвн.',self.v_hv)
        self.te.table_row('Номинальное напряжение обмотки среднего напряжения, кВ', 'Uсн.',self.v_mv)
        self.te.table_row('Номинальное напряжение обмотки низкого напряжения, кВ', 'Uнн.',self.v_lv)
        sqrt3 = math.sqrt(3)
        i_hv = self.sn_mva / self.v_hv / sqrt3 * 1000
        self.te.table_row('Номинальный первичный ток обмотки высокого напряжения, A', 'Iвн=Sном/√3/Uвн', f'{i_hv:.1f}')
        self.te.table_row('Номинальный первичный ток обмотки среднего напряжения, A', 'Iвн=Sном/√3/Uсн', f'{self.i_mv}')
        self.te.table_row('Номинальный первичный ток обмотки низкого напряжения, A', 'Iвн=Sном/√3/Uнн', f'{self.i_lv}')
        self.te.table_row('Дифференциальный ток срабатывания, о.е.',
                          'Id ≥ Kотс*Iнб.расч./Iвн', 12)
        self.te.table_row('Коэффициент отстройки', 'Котс', self.Kots)
        
# < td > K < sub > ВН < / sub > = I < sub > ТТ.ВН < / sub > / I < sub > ном.ВН < / sub > < / td >
# < td > {{'%.2f' | format(cell.transformers[prot.ti_hv].i1 / i_nom_hv)}} < / td >
# < / tr >
# < tr >
# < td > Номинальный
# ток
# трансформаторов
# тока
# высокого
# напряжения < / td >
# < td > I < sub > ТТ.ВН < / sub > < / td >
# < td > {{cell.transformers[prot.ti_hv].i1}} < / td >
# < / tr >
# < tr >
# < td > Коэффициент
# кратности
# для
# обмотки
# низкого
# напряжения < / td >
# < td > K < sub > НН < / sub > = I < sub > ТТ.НН < / sub > / I < sub > ном.НН < / sub > < / td >
# < td > {{'%.2f' | format(cell.transformers[prot.ti_lv].i1 / i_nom_lv)}} < / td >
# < / tr >
# < tr >
# < td > Номинальный
# ток
# трансформаторов
# тока
# низкого
# напряжения < / td >
# < td > I < sub > ТТ.НН < / sub > < / td >
# < td > {{cell.transformers[prot.ti_lv].i1}} < / td >
# < / tr >
# { % set
# dU = prot.Nrpn // 2 * prot.dUrpn / 100 %}
# < tr >
# < td > Ток
# срабатывания
# дифференциальной
# защиты
# с
# торможением, о.е. < / td >
# < td > I < sub > д > < / sub > = K < sub > отс < / sub > (K < sub > одн <
#                                                           / sub > & middot; & epsilon;+ & Delta;U+ & Delta; & fnof; < sub > ВЫР < / sub >) & middot;
# I < sup > * < / sup > < sub > ном.нагр < / sub > < / td >
# { % set
# i_d = prot.Kots * (prot.Kodn * prot.E + dU + prot.dFvyr) %}
# < td > {{'%.3f' | format(i_d)}} < / td >
# < / tr >
# < tr >
# < td > Коэффициент
# отстройки < / td >
# < td > K < sub > отс < / sub > < / td >
# < td > {{prot.Kots}} < / td >
# < / tr >
# < tr >
# < td > Коэффициент
# однотипности
# трансформаторов
# тока < / td >
# < td > K < sub > одн < / sub > < / td >
# < td > {{prot.Kodn}} < / td >
# < / tr >
# < tr >
# < td > Относительное
# значение
# полной
# погрешности
# трансформаторов
# тока < / td >
# < td > & epsilon; < / td >
# < td > {{prot.E}} < / td >
# < / tr >
# < tr >
# < td > Составляющая
# погрешности
# обусловленная
# наличием
# РПН < / td >
# < td > & Delta;
# U < / td >
# < td > {{dU}} < / td >
# < / tr >
# < tr >
# < td > Коэффициент, учитывающий
# погрешности
# цифрового
# выравнивания < / td >
# < td > & fnof; < sub > ВЫР < / sub > < / td >
# < td > {{prot.dFvyr}} < / td >
# < / tr >
# < tr >
# < td > Номинальный
# ток
# нагрузки, о.е. < / td >
# < td > I < sup > * < / sup > < sub > ном.нагр < / sub > < / td >
# < td > 1 < / td >
# < / tr >
# < tr >
# < td > Вторичный
# ток
# срабатывания
# дифференциальной
# защиты
# с
# торможением, А < / td >
# < td > I < sub > д > втор < / sub > = I < sub > д > < / sub > & middot;
# I < sub > ном.ВН < / sub > / (I < sub > ТТ.ВН </ sub > / 5) < / td >
# < td > {
#     {'%.3f' | format(i_d * i_nom_hv / cell.transformers[prot.ti_hv].i1 * cell.transformers[prot.ti_hv].i2)}} < / td >
# < / tr >
# < tr >
# < td > Тормозной
# ток
# второго
# перегиба, о.е. < / td >
# < td > I < sub > б2 < / sub > = 2 & middot;
# I < sup > * < / sup > < sub > норм.перегр < / sub > < / td >
# { % set
# i_b2 = 2 * prot.Kperegr %}
# < td > {{i_b2}} < / td >
# < / tr >
# < tr >
# < td > Дифференциальный
# ток
# второго
# перегиба, о.е. < / td >
# < td > I < sub > д > 2 < / sub > = K < sub > отс < / sub > (K < sub > одн <
#                                                             / sub > & middot; & epsilon;+ & Delta;U+ & Delta; & fnof; < sub > ВЫР < / sub >) & middot;
# I < sup > * < / sup > < sub > норм.перегр < / sub > < / td >
# { % set
# i_d2 = prot.Kots2 * (prot.Kodn * prot.E + dU + prot.dFvyr) * prot.Kperegr %}
# < td > {{'%.3f' | format(i_d2)}} < / td >
# < / tr >
# < tr >
# < td > Коэффициент
# отстройки < / td >
# < td > K < sub > отс < / sub > < / td >
# < td > {{prot.Kots2}} < / td >
# < / tr >
# < tr >
# < td > Угол
# наклона
# второго
# участка, гр. < / td >
# < td > & fnof;
# 1 = arctg(I < sub > д > 2 < / sub > / I < sub > б2 < / sub >) < / td >
# < td > {{'%.1f' | format(degrees(atan(i_d2 / i_b2)))}} < / td >
# < / tr >
# < tr >
# < td > Принимаем
# угол
# наклона
# второго
# участка, гр. < / td >
# < td > & fnof;
# 1 & ge;
# 12 < / td >
# < td > {{prot.f1}} < / td >
# < / tr >
# < tr >
# < td > Тормозной
# ток
# первого
# перегиба, о.е. < / td >
# < td > I < sub > б1 < / sub > = I < sub > д > < / sub > / tg & fnof;
# 1 < / td >
# { % set
# i_b1 = i_d / tan(radians(prot.f1)) %}
# < td > {{'%.2f' | format(i_b1)}} < / td >
# < / tr >
# { % set
# i_kz_max_lv = calc_net.get_sc_by_mode(calc_net.net.trafo.lv_bus[cell.index_trafo], prot.mode_max) %}
# { % set
# i_kz_max = i_kz_max_lv / calc_net.net.trafo.vn_hv_kv[cell.index_trafo] * calc_net.net.trafo.vn_lv_kv[
#     cell.index_trafo] %}
# { % set
# i_kz_max_pu = i_kz_max / i_nom_hv %}
# < tr >
# < td > Угол
# наклона
# третьего
# участка, гр. < / td >
# < td > & fnof;
# 2 = arctg((K < sub > отс <
#            / sub > (K < sub > пер < / sub > & middot;K < sub > одн < / sub > & middot; & epsilon;+ & Delta;U+ & Delta; & fnof; < sub > ВЫР < / sub >) & middot;
# I < sup > * < / sup > < sub > внеш.кз < / sub > - tg & fnof;
# 1 & middot;
# I < sub > б2 < / sub >) / (2 & middot;I < sup > * < / sup > < sub > внеш.кз < / sub > - I < sub > б2 < / sub >) < / td >
#                                                                                                                     < td > {
#                                                                                                                         {
#                                                                                                                             '%.1f' | format(
#                                                                                                                                 degrees(
#                                                                                                                                     atan(
#                                                                                                                                         (
#                                                                                                                                                     prot.Kots2 * (
#                                                                                                                                                         prot.Kper * prot.Kodn * prot.E + dU + prot.dFvyr) * i_kz_max_pu - i_d2) / (
#                                                                                                                                                     2 * i_kz_max_pu - i_b2))))}} < / td >
#                                                                                                                                                                                      < / tr >
#                                                                                                                                                                                          < tr >
#                                                                                                                                                                                          < td > Принимаем
# угол
# наклона
# третьего
# участка, гр. < / td >
#                  < td > & fnof;
# 2 & ge;
# 26 < / td >
#        < td > {{prot.f2}} < / td >
#                               < / tr >
#                                   < tr >
#                                   < td > Максимальный
# двухфазный
# ток
# внешнего
# короткого
# замыкания, A < / td >
#                  < td > I < sub > внеш.кз.НН < / sub > < / td >
#                                                            < td > {{'%.1f' | format(i_kz_max_lv)}} < / td >
#                                                                                                        < / tr >
#                                                                                                            < tr >
#                                                                                                            < td > Максимальный
# ток
# внешнего
# короткого
# замыкания
# приведенный
# к
# стороне
# высокого
# напряжения, А < / td >
#                   < td > I < sub > внеш.кз < / sub > = I < sub > внеш.кз.НН < / sub > & middot;
# U < sub > нн < / sub > / U < sub > вн < / sub > < / td >
#                                                     < td > {{'%.1f' | format(i_kz_max)}} < / td >
#                                                                                              < / tr >
#                                                                                                  < tr >
#                                                                                                  < td > Максимальный
# ток
# внешнего
# короткого
# замыкания
# приведенный
# к
# стороне
# высокого
# напряжения, о.е. < / td >
#                      < td > I < sup > * < / sup > < sub > внеш.кз < / sub > < / td >
#                                                                                 < td > {{'%.1f' | format(
#     i_kz_max_pu)}} < / td >
#                        < / tr >
#                            < tr >
#                            < tr >
#                            < td > Уставка
# блокировки
# при
# броске
# тока
# намагничивания
# принимается, % < / td >
#                    < td > I2 / I1 < / td >
#                                       < td > 14
# Перекрестная
# блокировка
# введена < / td >
#             < / tr >
#                 < tr >
#                 < td > Уставка
# блокировки
# при
# при
# перевозбуждении
# сердечника
# трансформатора, % < / td >
#                       < td > I5 / I1 < / td >
#                                          < td > {{prot.i5_i1}}
# Перекрестная
# блокировка
# введена < / td >
#             < / tr >
#                 < td > Ток
# срабатывания
# дифференциальной
# токовой
# отсечки
# по
# условию
# отстройки
# от
# броска
# тока
# намагничивания, о.е. < / td >
#                          < td > I < sub > д >> < / sub > = (5 & hellip;10) & middot;
# I < sup > * < / sup > < sub > ном. < / sub > < / td >
#                                                  < td > {{prot.Kbtn}} < / td >
#                                                                           < / tr >
#                                                                               { % set
# i_d_ots = prot.Kots_dots * prot.Knb * i_kz_max_pu %}
# < tr >
#   < td > Ток
# срабатывания
# дифференциальной
# токовой
# отсечки
# по
# условию
# отстройки
# от
# максимального
# тока
# небаланса
# при
# переходном
# режиме
# внешнего
# КЗ, о.е. < / td >
#              < td > I < sub > д >> < / sub > = K < sub > отс < / sub > & middot;
# K < sub > нб < / sub > & middot;
# I < sup > * < / sup > < sub > внеш.кз < / sub > < / td >
#                                                     < td > {{'%.2f' | format(i_d_ots)}} < / td >
#                                                                                             < / tr >
#                                                                                                 < tr >
#                                                                                                 < td > Коэффициент
# отстройки < / td >
#               < td > K < sub > отс < / sub > < / td >
#                                                  < td > {{prot.Kots_dots}} < / td >
#                                                                                < / tr >
#                                                                                    < tr >
#                                                                                    < td > Принимаем
# ток
# срабатывания
# дифференциальной
# токовой
# отсечки, о.е. < / td >
#                   < td > I < sub > д >> < / sub > < / td >
#                                                       < td > {{'%.2f' | format(i_d_ots)}} < / td >
#                                                                                               < / tr >
#                                                                                                   { % set
# i_kz_min_lv = calc_net.get_sc_by_mode(calc_net.net.trafo.lv_bus[cell.index_trafo], prot.mode_min) %}
# { % set
# i_kz_min = i_kz_min_lv / calc_net.net.trafo.vn_hv_kv[cell.index_trafo] * calc_net.net.trafo.vn_lv_kv[
#     cell.index_trafo] %}
# { % set
# i_kz_min_pu = i_kz_min / i_nom_hv %}
# < tr >
#   < td > Минимальный
# двухфазный
# ток
# внешнего
# короткого
# замыкания, A < / td >
#                  < td > I < sub > внеш.кз.НН < / sub > < / td >
#                                                            < td > {{'%.1f' | format(i_kz_min_lv)}} < / td >
#                                                                                                        < / tr >
#                                                                                                            < tr >
#                                                                                                            < td > Минимальный
# двухфазный
# ток
# внешнего
# короткого
# замыкания
# приведенный
# к
# стороне
# высокого
# напряжения, A < / td >
#                   < td > I < sub > внеш.кз < / sub > = I < sub > внеш.кз.НН < / sub > & middot;
# U < sub > нн < / sub > / U < sub > вн < / sub > < / td >
#                                                     < td > {{'%.1f' | format(i_kz_min)}} < / td >
#                                                                                              < / tr >
#                                                                                                  < tr >
#                                                                                                  < td > Минимальный
# двухфазный
# ток
# внешнего
# короткого
# замыкания
# приведенный
# к
# стороне
# высокого
# напряжения, о.е. < / td >
#                      < td > I < sup > * < / sup > < sub > внеш.кз < / sub > = I < sub > внеш.кз < / sub > / I < sub > ном.ВН < / sub > < / td >
#                                                                                                                                            < td > {
#                                                                                                                                                {
#                                                                                                                                                    '%.1f' | format(
#                                                                                                                                                        i_kz_min_pu)}} < / td >
#                                                                                                                                                                           < / tr >
#                                                                                                                                                                               < tr >
#                                                                                                                                                                               < td > Ток
# срабатывания
# защиты, соответствующий
# режиму
# минимального
# тока
# КЗ
# о.е. < / td >
#          < td > I < sub > сз < / sub > = I < sub > д > < / sub > + tg & fnof;
# 1 & middot;
# (I < sub > б2 </ sub > -I < sub > б1 < / sub >) + tg & fnof;
# 2 & middot;
# (I < sup >* < / sup > < sub > внеш.кз < / sub > -I < sub > б2 < / sub >) < / td >
#                                                                              { % set
# i_sz = i_d + tan(radians(prot.f1)) * (i_b2 - i_b1) + tan(radians(prot.f2)) * (i_kz_min_pu - i_b2) %}
# < td > {{'%.1f' | format(i_sz)}} < / td >
#                                      < / tr >
#                                          < tr >
#                                          < td > Коэффициент
# чувствительности
# дифференциальной
# защиты
# с
# торможением < / td >
#                 < td > K < sub > ч < / sub > = I < sup > * < / sup > < sub > внеш.кз < / sub > / I < sub > сз < / sub > & ge;
# 2 < / td >
#       < td > {{'%.1f' | format(i_kz_min_pu / i_sz)}} < / td >
#                                                          < / tr >
# if k_ch < 1.5:
#             self.te.warning(f'Коэффициент чувствительности МТЗ {self.pris.name} мал ({k_ch:.2f})')

    def table_settings(self):
        t_str = ''
        if self.t:
            t_str += str(self.t)
        if self.k:
            t_str += f'K={self.k} (зависимая время-токовая характеристика)'
        if self.t_au:
            t_str += f' tау={self.t_au}'
        self.te.table_row(self.name, f'{self.isz} A', t_str, 'При пуске блокирует вышестоящую ЛЗШ' if self.bl else '')

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
