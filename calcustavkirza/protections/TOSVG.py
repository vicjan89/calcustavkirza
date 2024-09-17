import math

from textengines.interfaces import TextEngine


from calcustavkirza.protections.TO import TO



class TOSVG(TO):
    q: float #номинальная реактивная мощность БСК
    u: float #номинальное напряжение сети
    ku: float = 1. #коэффициент загрузки БСК по напряжению
    isc_svg_index: int #индекс(индексы) шины подключения БСК
    kn: float = 1.5

    def calc_q(self, te: TextEngine, i_close: str, q: str, i_nom, s_sc_max, isz: str, isc_svg: str,
               res_sc_min, res_sc_max):
        self.head(te)
        te.table_row('Действующее значение максимального тока включения БСК в максимальном режиме',
                     te.m(
                         r'I_{\text{ВКЛ.БСК}} = \sqrt{2} \cdot I_{\text{НОМ.БСК}} \sqrt{\frac{S_{\text{КЗ}}}{Q_{\text{Н.БСК}}}}'),
                     i_close)
        te.table_row('Номинальная реактивная мощность БСК, МВА', te.m(r'Q_{\text{Н.БСК}}'), q)
        te.table_row('Номинальный ток БСК, A',
                     te.m(r'I_{\text{НОМ.БСК}} = \frac{Q_{\text{Н.БСК}}}{U_{\text{НОМ}} \cdot \sqrt{3}}'), i_nom)
        te.table_row('Мощность короткого замыкания в месте установки БСК в максимальном режиме, ВА',
                     te.m(r'S_{\text{КЗ}} = I_{\text{КЗ}} \cdot U_{\text{НОМ}} \cdot \sqrt{3}'), s_sc_max)
        te.table_row('Ток срабатывания защиты по условию отстройки от броска тока включения в максимальном режиме, А',
                     te.m(r'I_{\text{ср}} \geq K_{\text{ОТС}} \cdot I_{\text{ВКЛ.БСК}}'), isz)
        te.table_row('Коэффициент отстройки', te.m(r'K_{\text{ОТС}}'), self.kn)
        te.table_row('Максимальный ток КЗ в месте подключения конденсаторов', te.m(r'I_{\text{КЗ}}'), isc_svg)
        if self.i_kz_end_index is not None:
            i_kz_end_index = str(self.i_kz_end_index)
            i_kz_min = res_sc_min[i_kz_end_index][1]
            i_kz_max = res_sc_max[i_kz_end_index][1]
        else:
            i_kz_min = self.i_kz_min
            i_kz_max = self.i_kz_max
        k_ch_min = i_kz_min / self.isz
        te.table_row('Проверка коэффициента чувствительности при КЗ в конце кабельной линии в минимальном режиме ',
                     'Кч=Iкзмин/Iсз', f'{k_ch_min:.2f}')
        k_ch_max = i_kz_max / self.isz
        te.table_row('Проверка коэффициента чувствительности при КЗ в конце кабельной линии в максимальном режиме ',
                     'Кч=Iкзмакс/Iсз', f'{k_ch_max:.2f}')

        if k_ch_max < 1.2:
            self.add_warning(f'Коэффициент чувствительности токовой отсечки мал ({k_ch_min:.2f}) ' \
                       f'Нужна уставка {i_kz_min / 1.2:.2f}')

    def calc_ust(self, te: TextEngine, res_sc_min: list, res_sc_max: list):
        te.table_name(self.name)
        isc_svg = res_sc_max[str(self.isc_svg_index)][1]
        i_nom = self.q / self.u / math.sqrt(3)
        s_sc_max = isc_svg * self.u * math.sqrt(3)
        i_close_max = math.sqrt(2) * i_nom * math.sqrt(s_sc_max / self.q)
        isz = self.kn * i_close_max
        self.calc_q(te, f'{i_close_max:.1f}', f'{self.q}', f'{i_nom:.1f}', f'{s_sc_max:.1f}',
                 f'{isz:.1f}', f'{isc_svg:.1f}', res_sc_min, res_sc_max)
        if self.isz_posl:
            self.sogl_posl(te)
        self.total(te)

class TOFC(TOSVG):
    q: list[float] #номинальная реактивная мощность конденсаторов
    isc_svg_index: list[int] #индексы шин подключения БСК
    common_bus_index: int | str #индекс общей шини, к которой подключены ветви

    def _iclose_sum(self, iclose: list[float], isc: float): #TODO упростить формулы до исключения напряжения
        '''
        Возвращает общий ток включения нескольких батарей конденсаторов подключенных к общей шине
        :param iclose: список токов поочерёдного включения БСК
        :param isc: ток короткого замыкания на общей шине
        '''
        zsc = 10000 / math.sqrt(3) / isc
        zclose = [10000 / math.sqrt(3) / i for i in iclose]
        z0 = [z - zsc for z in zclose]
        zsum = 1 / sum([1 / z for z in z0])
        z_total = zsum + zsc
        iclose_sum = 10000 / math.sqrt(3) / z_total
        return iclose_sum


    def calc_ust(self, te: TextEngine, res_sc_min: list, res_sc_max: list):
        te.table_name(self.name)
        i_nom = [q / self.u / math.sqrt(3) for q in self.q]
        isc = [res_sc_max[str(index)][1]  for index in self.isc_svg_index]
        s_sc_max = [i * self.u * math.sqrt(3) for i in isc]
        i_close_max = []
        for num, q in enumerate(self.q):
            i_close_max.append(math.sqrt(2) * i_nom[num] * math.sqrt(s_sc_max[num] / q))
        i_close_max_sum = self._iclose_sum(i_close_max, res_sc_max[str(self.common_bus_index)][1])
        isz = self.kn * i_close_max_sum
        self.calc_q(te, '+ '.join([f'{i:.1f}' for i in i_close_max]),
                    '; '.join([str(q) for q in self.q]), '; '.join([f'{i:.1f}' for i in i_nom]),
                    '; '.join([f'{s:.1f}' for s in s_sc_max]), f'общий ток включения получен методом '
                                                               f'эквивалентирования схемы замещения ФКУ {isz:.1f}',
                    '; '.join([f'{i:.1f}' for i in isc]), res_sc_min, res_sc_max)
        self.total(te)