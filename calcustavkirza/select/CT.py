import math
import cmath
import traceback
import random

from pydantic import BaseModel, field_validator
import matplotlib.pyplot as plt


from calcustavkirza.classes import Element
from calcustavkirza.Isc import CaseSC
from textengines.interfaces import TextEngine

LOADS_DATA = [  # устройство, мощность потребления, ток при котором измерена мощность
    ['токовые входа микропроцессорного герминала', 0.5, 5],
    ['токовые цепи измерительного преобразователя', 1, 5],
    ['токовые цепи счётчика электрической энергии', 0.5, 5],
    ['реле РНТ-567', 5, 5],  #obsidian\work\factory_documentation\ЧЭАЗ\РНТ-565_566_567.djvu
    ['ION', 0.0625, 10], #https://download.schneider-electric.com/files?p_Doc_Ref=7ML12-0266-01&p_enDocType=User+guide&p_File_Name=7ML12-0266-01.pdf
    ['счётчик АЛЬФА А1800', 0.003, 5], #obsidian\work\factory_documentation\Учёт электроэнергии\Шкаф АИИСКУЭ бл.6.pdf
]

class NotSaturation(ValueError):
    ...

class MethodNotReliable(ValueError):
    ...

class CT(Element):
    model: str
    i1: int
    i2: int
    accuracy: str | None = None
    sn: int # номинальная вторичная нагрузка, ВА
    r2: float = 4 #активное сопротивление вторичной обмотки
    x2: float = 0 #реактивное сопротивление вторичной обмотки
    cos: float = 0.8 #косинус номинального значения угла сопротивления нагрузки
    s2ta: float | None = None #нагрузка на ТТ, обусловленная сопротивлением его вторичной обмотки R2ТТ (ориентировочно принимается 0,2·Sном)
    kn: int # номинальная предельная кратность
    k_circuit: float = 1 #коэффициент схемы соединений токовых цепей
    kr: float = 0.86 #коэффициент остаточной намагниченности
    kprn: float = 1 #коэффициент переходного режима номинальный (для ТТ класса Р равен 1 согласно примечания к Б.39 ПНСТ 283-2018)
    i_term: int | None = None
    ikz_max: int | None = None
    isz_max: float | None = None
    p: float = 0.0175 #удельное сопротивление
    length: float #длина кабеля токовых цепей в метрах
    s: float = 2.5 #сечение жилы кабеля токовых цепей в мм квадратных
    r_cont: float = 0.1 #сопротивление соединительных контактов
    loads: list | None = None
    cases: list[CaseSC] | None = None
    ka: float = 1.4 #коэффициент, учитывающий влияние апериодической составляющей тока КЗ (1,4 – для защит без выдержки времени, 1 – для защит с выдержкой времени)
    alfa: float = 0.9 #коэффициент, учитывающий возможное отклонение действительной характеристики данного ТТ от типовой
    ku: float = 2. #ударный коэффициент (для расчёта напряжения на зажимах ТТ)
    v: float = 0 #фаза периодической составляющей в момент КЗ в радианах

    @field_validator('accuracy')
    @classmethod
    def validate_accuracy(cls, v: str | None) -> str | None:
        if v is None:
            return v
        values = ('10P', '5P', '10PR', '5PR', '0.5', '0.5S', '0.2', '0.2S')
        if v in values:
            return v
        raise ValueError(f'accuracy must be {", ".join(values)}')

    @property
    def e(self):
        if self.accuracy in ('10P', '10PR'):
            return 10
        if self.accuracy in ('5P', '5PR'):
            return 5
        if self.accuracy in ('0.5', '0.5S'):
            return 0.5
        if self.accuracy in ('0.2', '0.2S'):
            return 0.2

    def metods(self, te: TextEngine):
        te.h2('Методика выполнения расчётов')
        te.h3('Проверка коэффициента трансформации релейных обмоток трансформаторов тока')
        te.p('Номинальный ток первичной обмотки ТТ должен быть больше максимально возможного тока нагрузки: ' +
                  te.m('I<sub>Н1</sub>≥I<sub>макс.</sub>') + 'Номинальный ток вторичной обмотки принимается равным 1 А или 5 А')
        te.p('По термической односекундной стойкости ток в цепи измерения тока терминала не должен превышать значения' +
                  te.m('100⋅I<sub>H2</sub>') + ' (при двухсекундной - не более ' + te.m('40⋅I<sub>H2</sub>') +
                  '. Поэтому для ТТ '
                  'используемых для подключения терминалов защит, для которых максимальное время ликвидации КЗ в зоне '
                  'действия защиты составляет менее 1 с (с учетом отказа основной защиты и ликвидации КЗ в результате '
                  'действия резервных или смежных защит защищаемого элемента), должно выполняться условие ' +
                  te.m('I<sub>H1</sub> ≥ <sup>Iкз.макс.</sup>&frasl;<sub>100</sub>'))
        te.p('Для ТТ используемых для подключения терминалов защит, для которых максимальное время ликвидации КЗ '
                  'в зоне действия защиты составляет более 1 с, но менее 2 с (с учетом отказа основной защиты и '
                  'ликвидации КЗ в результате действия резервных или смежных защит защищаемого элемента), должно '
                  'выполняться условие  I<sub>H1</sub> ≥ <sup>Iкз.макс.</sup>&frasl;<sub>40</sub>')
        te.p('I<sub>кз.макс</sub> - максимально возможное значение тока КЗ проходящего через обмотку '
                  'рассматриваемого ТТ')
        te.h3('Расчет мощности обмоток трансформаторов тока')
        te.p('Суммарное сопротивление нагрузки составляет: '
                  'Z<sub>СУММ</sub>=Z<sub>КАБ</sub>+Z<sub>ПОТР</sub>+Z<sub>КОН</sub>,')
        te.p('где Z<sub>КАБ</sub> - сопротивление кабельной линии от трансформатора тока до конечного потребителя; '
                  'Z<sub>ПОТР</sub> -сопротивление подключенной нагрузки; Z<sub>КОН</sub> - переходное сопротивление '
                  'контактов, принимается равным 0,05 Ом при количестве подключенных устройств три и менее и 0,1 Ом при '
                  'количестве приборов более трех')
        te.p('Сопротивление кабельной линии от трансформатора тока до конечного потребителя составляет: '
                  'R<sub>КАБ</sub>=ρ⋅<sup>l</sup>&frasl;<sub>S</sub>, где ρ – удельное сопротивление меди равное '
                  '0,0175 Ом⋅<sup>мм2</sup>&frasl;<sub>м</sub>; l – длина контрольного кабеля, м; '
                  'S – сечение контрольного кабеля, мм2')
        te.p('Мощность обмотки трансформатора тока должна составлять не менее: '
                  'W=I<sup>2</sup><sub>H2</sub>⋅Z<sub>СУММ</sub>,')
        te.p('где I<sub>Н2</sub> - номинальный ток вторичной обмотки ТТ')
        te.h3('Проверка ТТ на 10 % погрешность')
        te.p('Расчетная проверка на 10 % погрешность выполняется для максимального тока внешнего короткого '
                  'замыкания с учетом фактического значения сопротивления нагрузки Z<sub>н.факт.расч.</sub>')
        te.p('Сопротивление нагрузки ТТ при трехфазном (двухфазном) коротком замыкании (схема соединения ТТ полная '
                  'звезда) определяется формулой:')
        te.p('Z<sub>н.факт.расч.</sub>=ρ⋅<sup>l</sup>&frasl;<sub>S</sub>+R<sub>реле</sub>+R<sub>пер</sub>,')
        te.p('где ρ – удельное сопротивление меди равное 0,0175 Ом⋅<sup>мм2</sup>&frasl;<sub>м</sub>; l – длина '
                  'контрольного кабеля, м; S – сечение контрольного кабеля, мм2')
        te.p('R<sub>реле</sub> – сопротивление подключённых к токовым цепям реле защиты, Ом')
        te.p('R<sub>пер</sub> – сопротивление контактов, принимается равным 0,05 Ом при количестве подключенных '
                  'устройств три и менее и 0,1 Ом при количестве приборов более трех')
        te.p('При схеме соединения ТТ в неполную звезду сопротивление нагрузки ТТ определяется формулой (при '
                  'двухфазном коротком замыкании):')
        self.p('Z<sub>н.факт.расч.</sub>=2&middot;ρ⋅<sup>l</sup>&frasl;<sub>S</sub>+R<sub>реле</sub>+R<sub>пер</sub>,')
        te.p('Предельно допустимая кратность тока K<sub>10доп</sub> в заданном классе точности при фактической '
                  'расчетной нагрузке определяется по кривым предельной кратности на основе Z<sub>н.факт.расч.</sub>')
        te.p('Максимальная расчетная кратность ТТ при внешнем коротком замыкании определяется по формуле: '
                  'K<sub>макс.внеш</sub>=I <sub>макс.внеш</sub>/I<sub>H1</sub>,')
        te.p('где I<sub>макс.внеш</sub> – максимальный расчетный ток;')
        te.p('I<sub>H1</sub> – номинальный первичный ток ТТ')
        te.p('Полная погрешность ТТ не превышает 10 % при выполнении условия: '
                  'K<sub>10доп</sub> > K<sub>макс.расч</sub>')
        te.p('В общем случае максимальный расчетный ток определяется по формуле:')
        te.p('I<sub>макс.расч.</sub> = k<sub>a</sub>&middot;I<sub>1макс.</sub>, где')
        te.p('I<sub>1макс.</sub> - максимальный ток, проходящий через трансформатор тока при к. з. в таких точках '
                  'защищаемой сети, где увеличение погрешностей трансформатора тока сверх допустимой может вызвать '
                  'неправильное действие защиты;')
        te.p('k<sub>a</sub> - коэффициент, учитывающий влияние на быстродействующие защиты переходных процессов '
                  'при к. з., которые сопровождаются прохождением апериодических составляющих в токе к. з.')
        te.p('В случае использования обычных токовых защит (МТЗ с независимой выдержкой времени, ТО) максимальный '
                  'ток, проходящий через трансформатор тока при к. з определяется по формуле:')
        te.p('I<sub>1макс.</sub> = 1,1 &middot; I<sub>с.з.</sub> / k<sub>сх</sub>,')
        te.p('где I<sub>с.з.</sub> – максимальный первичный ток срабатывания защиты')
        te.p('k<sub>сх</sub> – коэффициент схемы (для схемы соединения ТТ полная звезда – составляет 1)')
        te.p('1,1 – коэффициент, учитывающий возможное уменьшение вторичного тока на 10% из-за погрешностей '
                  'трансформатора тока')
        te.p('Коэффициент k<sub>a</sub> учитывающий влияние переходных процессов, принимается равным:')
        te.p('для всех защит, имеющих выдержку времени 0,5 с и больше k<sub>a</sub> = 1;')
        te.p(' для максимальных токовых зашит и отсечек с выдержкой времени меньше 0,5 с '
                  'k<sub>a</sub> = 1,2&divide;1,3.')
        te.h3('Проверка ТТ на предельно допустимую погрешность')
        te.p('Выполняется для проверки по условиям повышенной вибрации контактов реле направления мощности или '
                  'реле тока (для электромеханических реле), а также для проверки по условиям предельно допустимой для '
                  'реле направления мощности и направленных реле сопротивлений угловой погрешности – 50%')
        te.p('Проверка трансформаторов тока на предельно допустимую погрешность выполняется для максимального тока '
                  'короткого замыкания в зоне действия защиты')
        te.p('Максимальная расчетная кратность ТТ при коротком замыкании в зоне действия защиты определяется по '
                  'формуле: K<sub>макс.внутр</sub> = I<sub>макс.внутр</sub> / I<sub>H1</sub>,')
        te.p('где I<sub>макс.внутр</sub> – максимальный расчетный ток короткого замыкания в зоне действия защиты;')
        te.p('I<sub>H1</sub> – номинальный первичный ток ТТ')
        te.p('Обобщенный параметр A<sub>расч</sub>, определяющий величину токовой погрешности по превышению '
                  'предельно допустимой кратности тока в классе точности 10Р определяется по формуле: '
                  'A<sub>расч</sub> = K<sub>макс.внутр</sub> / K<sub>10доп</sub>,')
        te.p('где K<sub>10доп</sub> – предельно допустимая кратность тока в классе точности 10P')
        te.p('Токовая погрешность ТТ не превышает предельно допустимого значения при выполнении условия: '
                  'A<sub>расч</sub> < A. ')
        te.p('Предельно допустимая токовая погрешность при коротком замыкании в зоне действия защиты для '
                  'микропроцессорных реле составляет 50%, этой величине соответствует значение параметра A=2,6')
        te.h3('Проверка по условию отсутствия опасных перенапряжений во вторичных цепях ТТ')
        te.p('Напряжение во вторичных цепях ТТ при максимальном токе короткого замыкания определяется по формуле: '
                  'U<sub>TTрасч</sub> = I<sub>макс.внутр</sub> / K<sub>TT</sub> &middot; Z<sub>н.факт.расч</sub>')
        te.p('где K<sub>ТТ</sub> – коэффициент трансформации трансформатора тока')
        te.p('Значение напряжения на вторичных обмотках ТТ не должно превышать испытательного напряжения 1000 В. '
                  'Трансформаторы тока удовлетворяют указанному требованию при выполнении условия: '
                  'U<sub>ТТрасч</sub> < 1000 В')

    @property
    def r_cab(self):
        return self.p * self.length * self.k_circuit / self.s

    @property
    def s_real(self):
        return sum([LOADS_DATA[l][1] / LOADS_DATA[l][2] * self.i2 for l in self.loads])

    @property
    def r_ustr(self):
        return self.s_real / self.i2 ** 2

    @property
    def z_nagr3ph(self):
        return self.r_cont + self.r_ustr + self.r_cab

    @property
    def z_nagr1ph(self):
        return self.r_cont + self.r_ustr + self.r_cab * 2

    @property
    def r_nagr3ph(self):
        return self.z_nagr3ph

    @property
    def r_nagr1ph(self):
        return self.z_nagr1ph

    @property
    def x_nagr3ph(self):
        return 0

    @property
    def x_nagr1ph(self):
        return 0

    @property
    def cos_nagr1ph(self):
        return self.r_nagr1ph / self.z_nagr1ph

    @property
    def cos_nagr3ph(self):
        return self.r_nagr3ph / self.z_nagr3ph

    @property
    def sin_nagr1ph(self):
        return self.x_nagr1ph / self.z_nagr1ph

    @property
    def sin_nagr3ph(self):
        return self.x_nagr3ph / self.z_nagr3ph

    @property
    def x_nagr3ph(self):
        return math.sqrt(self.z_nagr3ph **2 - self.r_nagr3ph ** 2)

    @property
    def x_nagr1ph(self):
        return math.sqrt(self.z_nagr1ph **2 - self.r_nagr1ph ** 2)

    @property
    def zn(self):
        '''
        Возвращает номинальное полное сопротивление ТТ
        :return:
        '''
        return  self.sn / self.i2 ** 2

    def _a(self, casesc: CaseSC, kz3ph: bool = True):
        '''
        Параметр режима А по формуле 9 ГОСТ Р 58669—2019 при однофазном КЗ
        :return:
        '''
        r_nagr = self.r_nagr3ph if kz3ph else self.r_nagr1ph
        x_nagr = self.x_nagr3ph if kz3ph else self.x_nagr1ph
        zreal = math.sqrt((self.r2 + r_nagr) ** 2 + (self.x2 + x_nagr) ** 2)
        zn = self.zn
        z = math.sqrt((self.r2 + zn * self.cos) ** 2 + (zn * math.sin(math.acos(self.cos))) ** 2)
        ikz = casesc.isc3ph_sum if kz3ph else casesc.isc1ph_sum
        return self.i1 * self.kn * z / ikz / zreal

    def a1ph(self, casesc: CaseSC):
        '''
        Параметр режима А по формуле 9 ГОСТ Р 58669—2019 при однофазном КЗ
        :return:
        '''
        if casesc.isc1:
            zreal = math.sqrt((self.r2 + self.r_nagr1ph) ** 2 + (self.x2 + self.x_nagr1ph) ** 2)
            zn = self.zn
            z = math.sqrt((self.r2 + zn * self.cos) ** 2 + (zn * math.sin(math.acos(self.cos))) ** 2)
            a1ph = self.i1 * self.kn * z / casesc.isc1ph_sum / zreal
            return a1ph

    def a3ph(self, casesc: CaseSC):
        '''
        Параметр режима А по формуле 9 ГОСТ Р 58669—2019 при трёхфазном КЗ
        :return:
        '''
        zreal = math.sqrt((self.r2 + self.r_nagr3ph) ** 2 + (self.x2 + self.x_nagr3ph) ** 2)
        zn = self.zn
        z = math.sqrt((self.r2 + zn * self.cos) ** 2 + (zn * math.sin(math.acos(self.cos))) ** 2)
        isum = casesc.isc3ph_sum
        return self.i1 * self.kn * z / isum / zreal

    def _t_saturation(self, casesc: CaseSC, kz3ph: bool = True):
        '''
        приближённая оценка времени до насыщения ТТ по выражению 6 ГОСТ Р 58669—2019 и Б.47 ПНСТ 283-2018
        :return: время в мс
        '''
        if not kz3ph and not casesc.isc1:
            return
        check = self._a(casesc, kz3ph) * (1 - self.kr)
        if check and (check <= 1):
            raise MethodNotReliable(f'Условие 8 ГОСТ Р 58669—2019 и Б.49 ПНСТ 283-2018 не выполняется. '
                             f'Формулу 6 ГОСТ Р 58669—2019 и Б.47 ПНСТ 283-2018 нельзя применять, '
                             f'левая часть условия 8 равна {check} для {self.name}')
        sat = self._saturation(casesc, kz3ph)
        if sat == False:
            raise NotSaturation(f'Условие 7 ГОСТ Р 58669—2019 и Б.48 ПНСТ 283-2018 не выполняется. '
                             f'Насыщение не происходит для {self.name}')
        w = 2 * math.pi * 50
        t_eq = casesc.t_eq3ph if kz3ph else casesc.t_eq1ph
        t_eq /= 1000
        return t_eq * math.log((w * t_eq) / (w * t_eq - check + 1)) * 1000

    def t_saturation1ph(self, casesc: CaseSC):
        '''
        приближённая оценка времени до насыщения ТТ при однофазном КЗ
        :return: время в мс
        '''
        return self._t_saturation(casesc, False)

    def t_saturation3ph(self, casesc: CaseSC):
        '''
        приближённая оценка времени до насыщения ТТ при трёхфазном КЗ
        :return: время в мс
        '''
        return self._t_saturation(casesc, True)

    def _saturation(self, casesc: CaseSC, kz3ph: bool = True):
        '''
        Возвращает True если проверка по условию 7 ГОСТ Р 58669—2019 (Б.48 ПНСТ 283-2018) покажет наличие насыщения
        :return:
        '''
        a = self.a3ph(casesc) if kz3ph else self.a1ph(casesc)
        if a:
            t_eq = casesc.t_eq3ph if kz3ph else casesc.t_eq1ph
            return a * (1 - self.kr) < 100 * math.pi * t_eq / 1000 + 1

    def saturation1ph(self, casesc: CaseSC):
        '''
        Возвращает True если есть насыщение при однофазном КЗ
        :return:
        '''
        return self._saturation(casesc, False)

    def saturation3ph(self, casesc: CaseSC):
        '''
        Возвращает True если есть насыщение при трёхфазном КЗ
        :return:
        '''
        return self._saturation(casesc, True)

    def k_p_r(self, t: float, casesc: CaseSC, kz3ph: bool = True):
        '''
        Метод для построения кривой зависимости Кп.р. от времени согласно Г.21 ГОСТ Р 58669—2019
        :param t: время в сек
        :param ikz:
        :return:
        '''
        if not kz3ph and not casesc.isc1:
            return
        sum_i = 0
        cos_alfa = 1
        alfa = math.acos(cos_alfa) #угол фактического сопротивления нагрузки которую считаем активной
        sin_alfa = math.sin(alfa)
        cos_v = math.cos(self.v)
        sin_v = math.sin(self.v)
        w = 100 * math.pi
        ikz = casesc.isc3 if kz3ph else casesc.isc1
        isum = casesc.isc3ph_sum if kz3ph else casesc.isc1ph_sum
        trig2 = cos_alfa * sin_v - math.sin(w * t + alfa + self.v)
        for i in ikz:
            i_pu = i.isc / isum
            tp = i.ts / 1000
            trig = sin_alfa * cos_v * math.exp(- t / tp) + cos_alfa * cos_v * w * tp * (1 - math.exp(- t / tp))
            sum_i +=  i_pu * trig
        sum_i += trig2
        return sum_i

    def k_p_rPNST(self, t: float, casesc: CaseSC, kz3ph: bool = True):
        '''
        Метод для построения кривой зависимости Кп.р. от времени согласно Б.42 (Б.51) ПНСТ 283-2018
        :param t: время в сек
        :param kz3ph: если флаг True то расчёт производится для трёхфазных КЗ а если False то для однофазных
        :return:
        '''
        if not kz3ph and not casesc.isc1:
            return
        w = 100 * math.pi
        t_eq = casesc.t_eq3ph if kz3ph else casesc.t_eq1ph
        t_eq /= 1000
        return w * t_eq * (1 - math.exp(- t / t_eq)) - math.sin(w * t)

    def t_sat_from_k_p_r_by_a(self, casesc: CaseSC, kz3ph: bool = True, gost: bool = True):
        '''
        Метод ищет на графике Кп.р. значение времени до насыщения соответствующее параметру режима А
        :param kz3ph:
        :param gost:
        :return: время в мс
        '''
        if not kz3ph and not casesc.isc1:
            return
        a = self.a3ph(casesc) if kz3ph else self.a1ph(casesc)
        a = a * (1 - self.kr)
        last_k_p_r = 0
        last_t = 0
        for t in range(0, 1000):
            t /= 1000
            k_p_r = self.k_p_r(t, casesc, kz3ph) if gost else self.k_p_rPNST(t, casesc, kz3ph)
            if a < k_p_r:
                return ((t - last_t) / (k_p_r - last_k_p_r) * (a - last_k_p_r) + last_t) * 1000
            last_k_p_r = k_p_r
            last_t = t


    def check(self, te: TextEngine):
        te.h3(self.name)
        te.p('Для расчета релейной обмотки ТТ 10 кВ приняты следующие исходные данные:')
        te.ul(f'трансформатор тока {self.model}')
        te.ul(f'номинальный ток первичной обмотки ТТ - {te.m("I_{H1} = ")}{self.i1} А;')
        te.ul(f'номинальный ток вторичной обмотки ТТ - {te.m("I_{H2} = ")}{self.i2} А;')
        te.ul(f'односекундный ток термической стойкости {self.i_term} кА;')
        # # <p>- ТТ устанавливаются в {% if cell.phases==3 %}
        # # трех
        # # {% elif cell.phases==2 %}
        # # двух
        # # {% endif %}
        # # фазах;</p>
        te.ul(f'максимальный расчетный ток короткого замыкания в зоне действия защиты - {self.ikz_max} А;')
        te.ul(f'максимальная токовая уставка срабатывания зашиты - {self.isz_max} А;')
        te.p('нагрузкой токовых релейных цепей являются:')
        zsum = 0
        psum = 0
        for z in self.loads:
            l = LOADS_DATA[z][1] / LOADS_DATA[z][2] * self.i2
            te.ul(f'{l[0]} с потребляемой мощностью {l[1]} ВА и сопротивлением {l[2]}')
            zsum += l[2]
            psum += l[1]
        te.p('переходное сопротивление контактов, принимается равным 0,05 Ом;')
        te.p(f'минимальное сечение кабельной линии от релейной обмотки трансформатора тока составляет '
                  f'{self.conductor_section} мм2;')
        te.p(f'максимальная длина кабельной линии от релейной обмотки трансформатора тока до конечного потребителя '
                  f'составляет не более {self.conductor_lenght} м')

        te.h3('Проверка на допустимый длительный ток, ток термической и динамической стойкости')
        te.p(f'Максимальный рабочий ток через первичную обмотку ТТ составляет {self.imax }A. Значит принятые к '
                  f'установке ТТ не будут перегружены')
        te.p(f'Максимальный ток КЗ {self.ikz_max} А меньше тока односекундной термической стойкости {self.i_term} кА '
                  f'и тока динамической стойкости {self.i_din} кА')
        te.p(f'Кратность тока при КЗ {self.ikz_max} / {self.i1} = {self.ikz_max/self.i1} < 40 а значит термическая '
                  f'двухсекундная стойкость для цифровых защит обеспечивается')

        te.h3('Расчет мощности релейной обмотки трансформаторов тока')
        r = 0.0175 * self.conductor_lenght / self.conductor_section
        te.math(r'R_{КАБ} = ρ \cdot \frac{l}{S} = 0,0175 \cdot \frac{'+self.conductor_lenght+r'}{'+
                     self.conductor_section+'} = '+r+' Ом')
        te.p('Суммарное сопротивление нагрузки для цепей РЗА и потребляемая мощность от релейной обмотки '
                  'трансформатора тока в режиме отсутствия напряжения на шинках управления составит:')
        te.math(r'Z_{СУММ} = ' + f'{zsum:.3f} + {r:.3f}Ом')
        zsum += r
        te.math(f'S = {self.i2}^2 \\cdot {zsum} = {self.i2**2*zsum} ВА')
        # <p>Следовательно, мощность вторичной релейной обмотки устанавливаемого
        # трансформатора тока выбираем {{ cell.Snom }} ВА.</p>
        # <h3>Расчет мощности измерительной обмотки трансформаторов тока.</h3>
        # {% set r_izm=0.0175*cell.conductor.lenght/cell.conductor.section %}
        # <p>R<sub>КАБ</sub>=ρ⋅<sup>l</sup> &frasl; <sub>S</sub> = 0,0175&middot;<sup>{{ cell.conductor.lenght }}</sup> &frasl;
        # <sub>{{ cell.conductor.section }}</sub> = {{ '%.3f' | format(r_izm) }} Ом.</p>
        # <p>Суммарное сопротивление нагрузки для цепей измерения и потребляемая мощность от измерительной обмотки трансформатора тока составит:</p>
        # {% set Zsum_izm = (cell.apparats_in_tt_izm.power | sum)/25 + r_izm %}
        # <p>Z<sub>СУММ</sub> = {{ '%.3f' | format(r_izm) }}
        # {% for pow in cell.apparats_in_tt_izm.power %}
        # + {{ pow/25 }}
        # {% endfor %}={{ '%.3f' | format(Zsum_izm) }} Ом
        # </p>
        # <p>W = 5<sup>2</sup> &middot; {{ '%.3f' | format(Zsum_izm) }} = {{ '%.3f' | format(Zsum_izm*25) }} ВА.</p>
        # <p>Следовательно, мощность вторичной измерительной обмотки устанавливаемого
        # трансформатора тока выбираем {{ cell.Snomizm }} ВА.</p>
        # {% if 'apparats_in_tt_uchet' in cell %}
        # <h3>Расчет мощности обмотки для учёта электроэнергии трансформаторов тока.</h3>
        # {% set r_uchet=0.0175*cell.conductor.lenght/cell.conductor.section %}
        # <p>R<sub>КАБ</sub>=ρ⋅<sup>l</sup> &frasl; <sub>S</sub> = 0,0175&middot;<sup>{{ cell.conductor.lenght }}</sup> &frasl;
        # <sub>{{ cell.conductor.section }}</sub> = {{ '%.3f' | format(r_uchet) }} Ом.</p>
        # <p>Суммарное сопротивление нагрузки для цепей измерения и потребляемая мощность от измерительной обмотки трансформатора тока составит:</p>
        # {% set Zsum_uchet = (cell.apparats_in_tt_uchet.power | sum)/25 + r_uchet %}
        # <p>Z<sub>СУММ</sub> = {{ '%.3f' | format(r_uchet) }}
        # {% for pow in cell.apparats_in_tt_uchet.power %}
        # + {{ pow/25 }}
        # {% endfor %}={{ '%.3f' | format(Zsum_uchet) }} Ом
        # </p>
        # <p>W = 5<sup>2</sup> &middot; {{ '%.3f' | format(Zsum_uchet) }} = {{ '%.3f' | format(Zsum_uchet*25) }} ВА.</p>
        # <p>Следовательно, мощность вторичной измерительной обмотки устанавливаемого
        # трансформатора тока выбираем {{ cell.Snom_uchet }} ВА.</p>
        # {% endif %}
        # <h3>Проверка ТТ на 10 % погрешность.</h3>
        # <p>Для номинальной мощности вторичной релейной обмотки ТТ равной {{ cell.Snom }} ВА, номинальной предельной кратности
        # обмотки ТТ равной {{ cell.Knom }}, класса точности 5Р и мощности нагрузки вторичной обмотки
        # {{ '%.3f' | format(Zsum*25) }} ВА по кривым предельной кратности допустимая кратность составит:</p>
        # <p>K<sub>макс.</sub>= {{ '%.1f' | format(Kpk(Zsum * 25, cell.Knom)) }}</p>
        # <p>Фактическая кратность при максимальной токовой уставке срабатывания зашиты К = {{ cell.i_to }} / {{ cell.I1n }} =
        # {{ '%.1f' | format(cell.i_to/cell.I1n) }}, условие выполняется.</p>
        # <h3>Проверка ТТ на предельно допустимую погрешность.</h3>
        # <p>Выполняется для проверки по условиям повышенной вибрации контактов реле
        # направления мощности или реле тока (для электромеханических реле), а также для проверки по
        # условиям предельно допустимой для реле направления мощности и направленных реле
        # сопротивлений угловой погрешности – 50%.
        # Так как в качестве защиты используется микропроцессорный терминал без функций
        # направления мощности и направленных реле сопротивлений, то по данному критерию проверка
        # ТТ не производится.</p>
        # <h3>Проверка по условию отсутствия опасных перенапряжений во вторичных цепях ТТ.</h3>
        # <p>U<sub>ТТрасч</sub> = {{ '%.1f' | format(sc.ikss_ka[cell.i_kz_max_index]*1000) }} /
        # {{ cell.I1n }} &middot; 5 &middot; {{ '%.3f' | format(Zsum) }} =
        # {{ '%.1f' | format(sc.ikss_ka[cell.i_kz_max_index]*1000*5/cell.I1n*Zsum) }} < 1000 В, условие выполняется.</p>
        # <h3>Выбранные параметры ТТ</h3>
        # <p>В ячейках {{ cell.name }} устанавливаются {{ cell.phases }} ТТ со следующими параметрами: номинальное напряжение 10кВ,
        # номинальный ток {{ cell.I1n }}/5, наибольшее рабочее напряжение 12 кВ, класс точности релейной обмотки 5P, номинальная
        # мощность релейной обмотки {{ cell.Snom }} ВА, коэффициент предельной кратности релейной обмотки {{ cell.Knom }}, класс
        # точности измерительной обмотки 0,5, номинальная мощность измерительной обмотки {{ cell.Snomizm }} ВА,
        # номинальный коэффициент безопасности приборов К<sub>Бном</sub> вторичной измерительной обмотки - 5
        # {% if 'apparats_in_tt_uchet' in cell %}
        # ,класс точности обмотки для учёта 0,5S, номинальная мощность обмотки для учёта {{ cell.Snom_uchet }} ВА,
        # номинальный коэффициент безопасности приборов К<sub>Бном</sub> вторичной обмотки для учёта - 5
        # {% endif %}.</p>
        # {% endfor %}
        # <h2>Итоговые характеристики для выбранных трансформаторов тока.</h2>
        # <table>
        # <tr>
        # <th>Место установки</th>
        # <th>Присоединение</th>
        # <th>Ктт</th>
        # <th>Тип вторичной обмотки</th>
        # <th>Предельная кратность</th>
        # <th>Мощность, ВА</th>
        # </tr>
        # {% for cell in select_tt %}
        # <tr>
        # <td>{{ cell.name_object }}</td>
        # <td>{{ cell.name }}</td>
        # <td>{{ cell.I1n }}/5</td>
        # <td>Релейная - класс точности 5Р</td>
        # <td>Номинальная предельная кратность {{ cell.Knom }}</td>
        # <td>{{ cell.Snom }}</td>
        # </tr>
        # <tr>
        # <td>{{ cell.name_object }}</td>
        # <td>{{ cell.name }}</td>
        # <td>{{ cell.I1n }}/5</td>
        # <td>Измерительная - класс точности 0,5</td>
        # <td>Номинальный коэффициент безопасности приборов 5</td>
        # <td>{{ cell.Snomizm }}</td>
        # </tr>
        # {% if 'apparats_in_tt_uchet' in cell %}
        # <tr>
        # <td>{{ cell.name_object }}</td>
        # <td>{{ cell.name }}</td>
        # <td>{{ cell.I1n }}/5</td>
        # <td>Учёт - класс точности 0,5S</td>
        # <td>Номинальный коэффициент безопасности приборов 5</td>
        # <td>{{ cell.Snom_uchet }}</td>
        # </tr>
        # {% endif %}
        # {% endfor %}
        # </table>
        # {% endblock %}

    def for_table(self, te: TextEngine, casesc: CaseSC):
        s_real = self.s_real
        r_cab = self.r_cab
        s2ta = self.s2ta if self.s2ta else 0.2 * self.sn
        sqrt2 = math.sqrt(2)
        if casesc.isc1:
            ikz_max1ph_i = casesc.isc1ph_sum
            s_calc1ph = self.i2 ** 2 * (2 * r_cab + self.r_cont) + s_real
            k_calc1ph = self.ka * ikz_max1ph_i / self.alfa / self.i1
            s_dop1ph = self.kn * ( self.sn + s2ta) / k_calc1ph - s2ta
            k_dop1ph = self.kn * ( self.sn + s2ta) / (s2ta + s_calc1ph)
            umax1ph = sqrt2 * self.ku * ikz_max1ph_i / self.i2 / self.i1 * s_calc1ph
            s_calc1ph = f'{s_calc1ph:.2f}'
            k_calc1ph = f'{k_calc1ph:.2f}'
            s_dop1ph = f'{s_dop1ph:.2f}'
            k_dop1ph = f'{k_dop1ph:.2f}'
            umax1ph = f'{umax1ph:.2f}'
            ikz_max1ph_i = f'{casesc.isc1ph_sum:.2f}'
        else:
            s_calc1ph = '-'
            ikz_max1ph_i = '-'
            k_calc1ph = '-'
            s_dop1ph = '-'
            k_dop1ph = '-'
            umax1ph = '-'
        isc3ph = casesc.isc3ph_sum
        s_calc3ph = self.i2 ** 2 * (r_cab + self.r_cont) + s_real
        k_calc3ph = self.ka * isc3ph / self.alfa / self.i1
        s_dop3ph = self.kn * ( self.sn + s2ta) / k_calc3ph - s2ta
        k_dop3ph = self.kn * ( self.sn + s2ta) / (s2ta + s_calc3ph)
        umax3ph = sqrt2 * self.ku * isc3ph / self.i2 / self.i1 * s_calc3ph
        te.table_row(self.name, self.accuracy, 'РЗА (f=10%)', self.i1, self.i2, self.sn, self.kn,
                     ikz_max1ph_i, f'{isc3ph:.2f}', self.s, self.length, f'{s_real:.2f}',
                     self.r_cont, self.ka, self.alfa, '-', f'{r_cab:.2f}', s_calc1ph, s_dop1ph,
                     f'{s_calc3ph:.2f}', f'{s_dop3ph:.2f}', k_calc1ph, k_dop1ph, f'{k_calc3ph:.2f}',
                     f'{k_dop3ph:.2f}', umax1ph, f'{umax3ph:.2f}')

    def ts(self, te: TextEngine):
        rn_kz3 = self._r_cab()
        rn_kz1 = 2 * rn_kz3
        t_eq = sum([ikz.i * ikz.T for ikz in self.ikz3]) / sum([ikz.i for ikz in self.ikz3])
        print(rn_kz3,rn_kz1, t_eq)

    def calc_q(self, te: TextEngine):
        r_ustr = self._r_ustr()
        te.table_row(self.name, f'{r_ustr:.2f}',
          f'{self.p * self.length * self.k_circuit / (self.sn / self.i2 ** 2 - r_ustr - self.r_cont):.2f}')

    def calc_s(self, te: TextEngine):
        r_cab = self.r_cab
        r_ustr = self.r_ustr
        s_nagr = (r_cab + r_ustr + self.r_cont) * self.i2 ** 2
        te.table_row(self.name, self.length, self.s, f'{r_cab:.2f}', self.k_circuit, f'{r_ustr:.2}', f'{s_nagr:.2f}')

    @staticmethod
    def _t2str(t):
        if t is None:
            return '-'
        suffix = ''
        if t < 15:
            suffix = '(П3)'
        return f'{t:.2f}{suffix}'

    def time_to_saturation(self, te: TextEngine, casesc: CaseSC, t3ph, t3phkr, t1ph ='П0', t1phkr ='П0'):
        te.h2(f'Трансформатор тока {self.name}')
        te.p(f'Режим: {casesc.name}')
        te.table_name('Паспортные данные трансформатора тока (ТТ)')
        te.table_head('Параметр',	'Значение',	'Ед. изм.',	'Расшифровка')
        te.table_row('I1ном', self.i1, 'A', 'Номинальный первичный ток ТТ')
        te.table_row('I2ном', self.i2, 'A', 'Номинальный втоичный ток ТТ')
        te.table_row('R2', self.r2, 'Ом', 'Активное сопротивление вторичной обмотки ТТ')
        te.table_row('X2', self.x2, 'Ом', 'Индуктивное сопротивление вторичной обмотки ТТ')
        te.table_row('Sн.ном', self.sn, 'ВА', 'Номинальная мощность вторичной нагрузки ТТ')
        te.table_row('cos(jн.ном)', self.cos, '-', 'Косинус номинального значения угла сопротивления нагрузки ТТ')
        te.table_row('ε', self.e, '%', 'Полная погрешность ТТ')
        te.table_row('Кном', self.kn, '-', 'Номинальная предельная кратность')
        te.table_row('Кп.р.ном', 1, '-', 'Номинальный коэффициент переходного режима (для трансформаторов классов '
                                         'точности Р и TPX если он не установлен принимается равным 1)')

        te.table_name('Данные по нагрузке трансформатора тока')
        te.table_head('Параметр',	'Значение',	'Ед. изм.',	'Расшифровка')
        te.table_row('r', self.p, 'Ом·мм2/м', 'Удельное сопротивление проводника')
        te.table_row('l', self.length, 'м', 'Длина контрольного кабеля ')
        te.table_row('s', self.s, 'мм2', 'Площадь поперечного сечения жилы контрольного кабеля')
        te.table_row('Rпр', f'{self.r_cab:.2f}', 'Ом', 'Активное сопротивление контрольного кабеля')
        te.table_row('Zрф', self.r_ustr, 'Ом', 'Суммарное сопротивление устройств релейной защиты')
        te.table_row('Zро', 0, 'Ом', 'Суммарное сопротивление устройств релейной защиты, включенных в цепь общего провода')

        te.table_name('Результаты расчета суммарной вторичной нагрузки ТТ')
        te.table_head('Параметр',	'Значение',	'Ед. изм.',	'Расшифровка')
        te.table_row('Zн.расч1', f'{self.z_nagr1ph:.2f}', 'Ом', 'Рассчитанное сопротивление нагрузки ТТ при однофазном КЗ')
        te.table_row('Zн.расч3', f'{self.z_nagr3ph:.2f}', 'Ом', 'Рассчитанное сопротивление нагрузки ТТ при трёхфазном КЗ')

        te.table_name('Данные по токам короткого замыкания (КЗ)')
        te.table_head('Параметр',	'Значение',	'Ед. изм.',	'Расшифровка')
        if casesc.isc1:
            ikz1 = [f'{i.isc:.1f}' for i in casesc.isc1]
            ikz1 = '; '.join(ikz1) if ikz1 else '-'
            te.table_row('Iкз1', ikz1, 'A', 'Значения токов в ветвях, питающих точку однофазного КЗ (отделяются символом ;)')
            tkz1 = [f'{i.ts:.1f}' for i in casesc.isc1]
            tkz1 = '; '.join(tkz1) if tkz1 else '-'
            te.table_row('Ткз1', tkz1, 'мс', 'Постоянные времени затухания апериодических составляющих токов в ветвях '
                                             'при однофазном КЗ (отделяются символом ;)')
        ikz3 = [f'{i.isc:.1f}' for i in casesc.isc3]
        ikz3 = '; '.join(ikz3) if ikz3 else '-'
        te.table_row('Iкз3', ikz3, 'A', 'Значения токов в ветвях, питающих точку трёхфазного КЗ (отделяются символом ;)')
        tkz3 = [f'{i.ts:.1f}' for i in casesc.isc3]
        tkz3 = '; '.join(tkz3) if tkz3 else '-'
        te.table_row('Ткз3', tkz3, 'мс', 'Постоянные времени затухания апериодических составляющих токов в ветвях '
                                         'при трёхфазном КЗ (отделяются символом ;)')
        if casesc.isc1:
            ikz1ph_sum = f'{casesc.isc1ph_sum:.1f}'
            t_eq1ph = f'{casesc.t_eq1ph:.1f}'
        else:
            ikz1ph_sum = 'П0'
            t_eq1ph = 'П0'
        te.table_name('Результаты расчета суммарных токов и эквивалентных постоянных времени близкого КЗ')
        te.table_head('Параметр',	'Значение',	'Ед. изм.',	'Расшифровка')
        te.table_row('Iкз1сум', ikz1ph_sum, 'A', 'Рассчитанный суммарный ток однофазного близкого КЗ')
        te.table_row('Tp.экв1', t_eq1ph, 'мс', 'Рассчитанная эквивалентная постоянная времени однофазного КЗ')
        te.table_row('Iкз3сум', f'{casesc.isc3ph_sum:.1f}', 'A', 'Рассчитанный суммарный ток трёхфазного близкого КЗ')
        te.table_row('Tp.экв3', f'{casesc.t_eq3ph:.1f}', 'мс', 'Рассчитанная эквивалентная постоянная времени трёхфазного КЗ')

        te.table_name('Данные по остаточной намагниченности трансформатора тока')
        te.table_head('Параметр',	'Значение',	'Ед. изм.',	'Расшифровка')
        te.table_row('Kr', self.kr, '-', 'Коэффициент остаточной намагниченности')

        te.table_name('Промежуточные результаты при расчете по паспортным данным трансформатора тока (ТТ)')
        te.table_head('Параметр',	'Значение',	'Ед. изм.',	'Расшифровка')
        a1ph = self.a1ph(casesc)
        a1phkr = f'{a1ph * (1 - self.kr):.2f}' if a1ph else '-'
        a1ph = f'{a1ph:.2f}' if a1ph else '-'
        te.table_row('Acs1', a1ph, '-', 'Параметр режима при однофазном КЗ')
        te.table_row('cosPHIsc1', self.cos_nagr1ph, '-', 'Косинус угла вторичной нагрузки ТТ при однофазном КЗ')
        te.table_row('sinPHIsc1', self.sin_nagr1ph, '-', 'Синус угла вторичной нагрузки ТТ при однофазном КЗ')
        te.table_row('Acs1kr', a1phkr, '-', 'Параметр режима при однофазном КЗ')
        a3ph = self.a3ph(casesc)
        te.table_row('Acs3', f'{a3ph:.2f}', '-', 'Параметр режима при трёхфазном КЗ')
        te.table_row('cosPHIsc3', self.cos_nagr3ph, '-', 'Косинус угла вторичной нагрузки ТТ при трёхфазном КЗ')
        te.table_row('sinPHIsc3', self.sin_nagr3ph, '-', 'Синус угла вторичной нагрузки ТТ при трёхфазном КЗ')
        te.table_row('Acs3kr', f'{a3ph * (1 - self.kr):.2f}', '-', 'Параметр режима при трёхфазном КЗ')

        x = []
        y = []
        z = []
        y1 = []
        z1 = []
        for tm in range(1, 200):
            tm /= 1000
            x.append(tm)
            y.append(self.k_p_r(tm, casesc, True))
            z.append(self.k_p_rPNST(tm, casesc, True))
            y1.append(self.k_p_r(tm, casesc, False))
            z1.append(self.k_p_rPNST(tm, casesc, False))
        fig, ax = plt.subplots()
        ax.plot(x, y, label='Кп.р. ГОСТ 3-х ф.КЗ')
        ax.plot(x, z, label='Кп.р. ПНСТ 3-х ф.КЗ')
        ax.plot(x, y1, label='Кп.р. ГОСТ 1-х ф.КЗ')
        ax.plot(x, z1, label='Кп.р. ПНСТ 1-х ф.КЗ')
        ax.legend()
        ax.grid()
        num = random.randint(1, 9999999)
        plt.savefig(f'{num}.png')
        te.image(f'{num}.png', 'Графики Кп.р.(t)', 500)

        x = []
        y = []
        z = []
        y1 = []
        z1 = []
        for tm in range(1, 25):
            tm /= 1000
            x.append(tm)
            y.append(self.k_p_r(tm, casesc, True))
            z.append(self.k_p_rPNST(tm, casesc, True))
            if casesc.isc1:
                y1.append(self.k_p_r(tm, casesc, False))
                z1.append(self.k_p_rPNST(tm, casesc, False))
        fig, ax = plt.subplots()
        ax.plot(x, y, label='Кп.р. ГОСТ')
        ax.plot(x, z, label='Кп.р. ПНСТ')
        if casesc.isc1:
            ax.plot(x, y1, label='Кп.р. ГОСТ 1-х ф.КЗ')
            ax.plot(x, z1, label='Кп.р. ПНСТ 1-х ф.КЗ')
        ax.legend()
        ax.grid()
        num = random.randint(1, 9999999)
        plt.savefig(f'{num}.png')
        te.image(f'{num}.png', 'Графики Кп.р.(t)', 500)
        plt.close()

        kr = self.kr
        self.kr = 0
        te.table_name('Результаты расчёта в соответствии с ГОСТ Р 58669-2019 при однофазном КЗ')
        te.table_head('Условия по остаточной намагниченности', 'Аналитический метод',
                      'Графический метод по паспортным данным (Тр.экв)', 'Графический метод по паспортным данным (ΣI)')
        if casesc.isc1:
            if self.saturation1ph(casesc):
                t1 = self._t2str(self.t_saturation1ph(casesc))
                t2 = t1ph
                t3 = f'{self.t_sat_from_k_p_r_by_a(casesc, False, True):.2f}'
            else:
                t1 = t2 = t3 = 'П1'
        else:
            t1 = t2 = t3 = 'П0'
        te.table_row('При отсутствии остаточной намагниченности', t1, t2, t3)
        self.kr = kr
        if casesc.isc1:
            if self.saturation1ph(casesc):
                t1 = self._t2str(self.t_saturation1ph(casesc))
                t2 = t1phkr
                t3 = f'{self.t_sat_from_k_p_r_by_a(casesc, False, True):.2f}'
            else:
                t1 = t2 = 'П1'
        else:
            t1 = t2 = t3 = 'П0'
        te.table_row(f'При наличии остаточной намагниченности {self.kr * 100}%', t1, t2, t3)

        self.kr = 0
        te.table_name('Результаты расчёта в соответствии с ГОСТ Р 58669-2019 при трёхфазном КЗ')
        te.table_head('Условия по остаточной намагниченности', 'Аналитический метод',
                      'Графический метод по паспортным данным (Тр.экв)', 'Графический метод по паспортным данным (ΣI)')
        if self.saturation3ph(casesc):
            try:
                t1 = self._t2str(self.t_saturation3ph(casesc))
            except MethodNotReliable as e:
                print(e)
                t1 = 'П3'
            t2 = t3ph
            t3 = f'{self.t_sat_from_k_p_r_by_a(casesc, True, True):.2f}'
        else:
            t1 = t2 = t3 = 'П1'
        te.table_row('При отсутствии остаточной намагниченности', t1, t2, t3)
        self.kr = kr
        if self.saturation3ph(casesc):
            try:
                t1 = self._t2str(self.t_saturation3ph(casesc))
            except MethodNotReliable as e:
                print(e)
                t1 = 'П3'
            t2 = t3phkr
            t3 = f'{self.t_sat_from_k_p_r_by_a(casesc, True, True):.2f}'
        else:
            t1 = t2 = t3 = 'П1'
        te.table_row(f'При наличии остаточной намагниченности {self.kr * 100}%', t1, t2, t3)

        te.table_name('Результаты расчёта в соответствии с ПНСТ 283-2018 при однофазном КЗ')
        te.table_head('Условия по остаточной намагниченности', 'Аналитический метод',
                      'Графический метод по паспортным данным (Тр.экв)', 'Графический метод по паспортным данным (ΣI)')
        self.kr = 0
        if casesc.isc1:
            if self.saturation1ph(casesc):
                t1 = self._t2str(self.t_saturation1ph(casesc))
                t3 = f'{self.t_sat_from_k_p_r_by_a(casesc, False, False):.2f}'
            else:
                t1 = t3 = 'П1'
        else:
            t1 = t3 = 'П0'
        te.table_row('При отсутствии остаточной намагниченности', t1, t3, t3)

        self.kr = kr
        if casesc.isc1:
            if self.saturation1ph(casesc):
                t1 = self._t2str(self.t_saturation1ph(casesc))
                t3 = f'{self.t_sat_from_k_p_r_by_a(casesc, False, False):.2f}'
            else:
                t1 = t3 = 'П1'
        else:
            t1 = t3 = 'П0'
        te.table_row(f'При наличии остаточной намагниченности {self.kr * 100}%', t1, t3, t3)

        te.table_name('Результаты расчёта в соответствии с ПНСТ 283-2018 при трёхфазном КЗ')
        te.table_head('Условия по остаточной намагниченности', 'Аналитический метод',
                      'Графический метод по паспортным данным (Тр.экв)', 'Графический метод по паспортным данным (ΣI)')
        self.kr = 0
        if self.saturation3ph(casesc):
            try:
                t1 = self._t2str(self.t_saturation3ph(casesc))
            except MethodNotReliable as e:
                print(e)
                t1 = 'П3'
            t3 = f'{self.t_sat_from_k_p_r_by_a(casesc, True, False):.2f}'
        else:
            t1 = t3 = 'П1'
        te.table_row('При отсутствии остаточной намагниченности', t1, t3, t3)
        self.kr = kr
        if self.saturation3ph(casesc):
            try:
                t1 = self._t2str(self.t_saturation3ph(casesc))
            except MethodNotReliable as e:
                print(e)
                t1 = 'П3'
            t3 = f'{self.t_sat_from_k_p_r_by_a(casesc, True, False):.2f}'
        else:
            t1 = t3 = 'П1'
        te.table_row(f'При наличии остаточной намагниченности {self.kr * 100}%', t1, t3, t3)


class CTs(Element):
    cts: list[CT]

    def for_table(self, te: TextEngine):
        te.table_name('Проверка параметров ТТ на допустимую погрешность')
        te.table_head(
            'Обозначение ТТ',	'Класс точности обмотки трансформатора тока',
            'Наименование присоединения и защиты',	'Ном. первичный ток ТТ, I1тт (А)',
            'Ном. вторичный ток ТТ, I2тт (А)',	'Ном. втор. нагрузка ТТ, Sном (ВА)',
            'Ном. предельная кратность ТТ, Kном',	'Расчётный ток 1ф. КЗ, Iрасч.кз(1) (А)',
            'Расчетный ток 3ф. КЗ, Iрасч.КЗ(3) (А)',	'Сечение жил кабеля, Sкаб (мм2)',
            'Длина кабеля, Lкаб (м)',	'Потребление устройств, Sуст (ВА)',
            'Сопротивление соед. контактов, Rконт (Ом)',	'Переходный коэфф., kа',	'Коэффициент "альфа"',
            'Расчетный коэффициент А', 'Сопротивление жилы кабеля, Rкаб (Ом)',
            'Расчетная нагрузка на ТТ при 1ф. КЗ, Sнагр.расч.(1) (ВА)',
            'Допустимая нагрузка на ТТ при 1ф. КЗ, Sнагр.доп.(1) (ВА)',
            'Расчетная нагрузка на ТТ при 3ф. КЗ, Sнагр.расч.(3) (ВА)',
            'Допустимая нагрузка на ТТ при 3ф. КЗ, Sнагр.доп.(3) (ВА)',
            'Расчетная предельная кратность при 1ф. КЗ, Красч(1)',
            'Допустимая предельная кратность при 1ф. КЗ, Кдоп(1)',
            'Расчетная предельная кратность при 3ф. КЗ, Красч(3)',
            'Допустимая предельная кратность при 3ф. КЗ, Кдоп(3)',
            'Напряж. на зажимах втор. обм. ТТ при 1ф. КЗ, Uмакс(1) (В)',
            'Напряж. на зажимах втор. обм. ТТ при 3ф. КЗ, Uмакс(3) (В)'
        )

    def calc_q(self, te: TextEngine):
        te.table_name('Расчет сечения жил кабелей токовых цепей обмоток ТТ для измерений')
        te.table_head('Вторичная обмотка ТТ', 'Rустр, Ом', 'q расч, мм2')
        for ct in self.cts:
            ct.calc_q(te)

    def calc_s(self, te: TextEngine):
        te.table_name('Расчет нагрузки вторичных обмоток')
        te.table_head('Вторичная обмотка', 'l,м', 'q прин, мм2', 'Rкаб, Ом', 'Kсх', 'Rустр, Ом', 'Sнагр.ТТ,ВА')
        for ct in self.cts:
            ct.calc_s(te)

    def time_to_saturation(self, te: TextEngine):
        '''
        Выполняет расчёт времни до насыщения для ТТ и выводит результат в текстовый движок
        :param te: текстовый движок
        :param tgraph: список кортежей со значениями времени до насыщения полученными по графикам приложения Б ГОСТ Р 58669-2019
        (при однофазном КЗ, при однофазном КЗ с остаточным намагничиванием, при трёхфазном КЗ, при трёхфазном КЗ с остаточным
        намагничиванием)
        :param tas: список имён ТТ для которых нужно выполнить расчёт. При значении по умолчанию выполняет расчёт для всех
        :return:
        '''
        te.h1('Определение времени до насыщения ТТ')
        te.p('Расчет производится в соответствии с ГОСТ Р 58669-2019 и ПНСТ 283-2018.')
        te.p('При оформлении результатов расчета приняты следующие условные обозначения:')
        te.ul('Столбец Tр.экв - результаты расчета (времени до насыщения) при использовании эквивалентной постоянной времени затухания свободной апериодической составляющей тока, затухающей по экспоненциальному закону, которой заменяют сумму свободных апериодических составляющих, имеющих неодинаковые начальные значения и постоянные времени затухания.')
        te.ul('Столбец ∑I - результаты расчета (времени до насыщения) по сумме воздействий апериодических составляющих токов в отдельных ветвях (без использования Tр.экв).')
        te.ul('П0 - Не введены необходимые исходные данные.')
        te.ul('П1 - Насыщение магнитопровода отсутствует (время до насыщения равно бесконечности).')
        te.ul('П2 - Эксплуатация ТТ в указанных условиях недопустима, так как ток предельной кратности меньше действующего тока КЗ.')
        te.ul('П3 - Аналитический метод дает недостоверное время до насыщения при указанных условиях, следует ориентироваться на расчет графическим методом по паспортным данным.')
        te.ul('П4 - Для использования данного метода ВАХ ТТ должна быть снята до значений тока намагничивания, соответствующего полной погрешности ТТ (то есть не менее чем до 0,1 (0,05) расчетной кратности тока КЗ).')
        te.ul('П5 - Метод не применим при указанных условиях.')
        te.ul('П6 - Расчет не выполняется в соответствии с введенными исходными данными.')
        te.ul('П7 - Время до насыщения больше 0,12 с.')
        te.ul('П8 - Для трансформатора с указанной характеристикой намагничивания данный метод не применим.')

    def select(self, name):
        for ct in self.cts:
            if ct.name == name:
                return ct