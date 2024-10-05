import math
import cmath
import traceback
import random
from typing import Callable

from pydantic import BaseModel, field_validator, ConfigDict
import matplotlib.pyplot as plt


from calcustavkirza.classes import Element
from calcustavkirza.Isc import CaseSC
from calcustavkirza.Characteristic import Characteristic
from textengines.interfaces import TextEngine

LOADS_DATA = [  # устройство, мощность потребления, ток при котором измерена мощность
    ['токовые входа микропроцессорного терминала', 0.5, 5],#0
    ['токовые цепи измерительного преобразователя', 1, 5],#1
    ['токовые цепи счётчика электрической энергии', 0.5, 5],#2
    ['реле РНТ-567', 5, 5],  #obsidian\work\factory_documentation\ЧЭАЗ\РНТ-565_566_567.djvu
    ['ION', 0.0625, 10], #https://download.schneider-electric.com/files?p_Doc_Ref=7ML12-0266-01&p_enDocType=User+guide&p_File_Name=7ML12-0266-01.pdf
    ['счётчик АЛЬФА А1800', 0.003, 5], #obsidian\work\factory_documentation\Учёт электроэнергии\Шкаф АИИСКУЭ бл.6.pdf
    ['терминал защит МР5 ПО50 БЭМН', 0.25, 5],#6
    ['токовые цепи счётчика электрической энергии СС-301', 1, 5],#7 https://strumen.com/upload/iblock/c1b/%D0%9F%D0%B0%D1%81%D0%BF%D0%BE%D1%80%D1%82%20%D0%93%D1%80%D0%B0%D0%BD-%D0%AD%D0%BB%D0%B5%D0%BA%D1%82%D1%80%D0%BE%20%D0%A1%D0%A1-301.pdf
    ['токовые цепи амперметра аналогового EQ7_', 1.2, 5],  #8
    ['токовые цепи терминала автоматики управления AHF', 0.043, 5],  #9
    ['токовые цепи амперметра цифрового SETRON PAC 32', 0.115, 5],  #10
]

class NotSaturation(ValueError):
    ...

class MethodNotReliable(ValueError):
    ...

class CT(Element):
    '''
    model_config = ConfigDict(arbitrary_types_allowed=True)
    model: str = ''
    i1: int
    i2: int
    accuracy: str | None = None
    sn: int | None = None # номинальная вторичная нагрузка, ВА
    r2: float = 4 #активное сопротивление вторичной обмотки
    x2: float = 0 #реактивное сопротивление вторичной обмотки
    cos: float = 0.8 #косинус номинального значения угла сопротивления нагрузки
    s2ta: float | None = None #нагрузка на ТТ, обусловленная сопротивлением его вторичной обмотки R2ТТ (ориентировочно принимается 0,2·Sном)
    imax: float | None = None #ток нагрузки максимальный протекающий через ТТ. Если на задан то принимаем номинальный ток ТТ
    kn: int | None = None # номинальная предельная кратность
    kpk: Callable | None = None #функция возвращающая значение предельной кратности и принимающая фактическое сопротивление нагрузки токовых цепей
    k_circuit: float = 1 #коэффициент схемы соединений токовых цепей
    kr: float = 0.86 #коэффициент остаточной намагниченности
    kprn: float = 1 #коэффициент переходного режима номинальный (для ТТ класса Р равен 1 согласно примечания к Б.39 ПНСТ 283-2018)
    i_term: float | None = None #термическая стойкость ТТ
    i_din: float | None = None #динамическая стойкость ТТ
    ikz_max: int | None = None # short circuit current in A
    isz_max: float | None = None # short circuit current in A
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
    vach: Characteristic | None = None # класс характеристик применительно для ВАХ
    '''
    model_config = ConfigDict(arbitrary_types_allowed=True)
    model: str = ''
    i1: int
    i2: int
    accuracy: str | None = None
    sn: int | None = None # номинальная вторичная нагрузка, ВА
    r2: float = 4 #активное сопротивление вторичной обмотки
    x2: float = 0 #реактивное сопротивление вторичной обмотки
    cos: float = 0.8 #косинус номинального значения угла сопротивления нагрузки
    s2ta: float | None = None #нагрузка на ТТ, обусловленная сопротивлением его вторичной обмотки R2ТТ (ориентировочно принимается 0,2·Sном)
    imax: float | None = None #ток нагрузки максимальный протекающий через ТТ. Если на задан то принимаем номинальный ток ТТ
    kn: int | None = None # номинальная предельная кратность
    kpk: Callable | None = None #функция возвращающая значение предельной кратности и принимающая фактическое сопротивление нагрузки токовых цепей
    k_circuit: float = 1 #коэффициент схемы соединений токовых цепей
    kr: float = 0.86 #коэффициент остаточной намагниченности
    kprn: float = 1 #коэффициент переходного режима номинальный (для ТТ класса Р равен 1 согласно примечания к Б.39 ПНСТ 283-2018)
    i_term: float | None = None #термическая стойкость ТТ
    i_din: float | None = None #динамическая стойкость ТТ
    ikz_max: int | None = None # short circuit current in A
    isz_max: float | None = None # short circuit current in A
    p: float = 0.0175 #удельное сопротивление
    length: float #длина кабеля токовых цепей в метрах
    s: float = 2.5 #сечение жилы кабеля токовых цепей в мм квадратных
    r_cont: float = 0.1 #сопротивление соединительных контактов
    loads: list | None = None
    cases: list[CaseSC] | None = None
    ka: float = 1.4 #коэффициент, учитывающий влияние апериодической составляющей тока КЗ (1,4 – для защит без выдержки времени, 1 – для защит с выдержкой времени)
    alfa: float = 0.9 #коэффициент, учитывающий возможное отклонение действительной характеристики данного ТТ от типовой
    ku: float = 1.85 #ударный коэффициент (для расчёта напряжения на зажимах ТТ)
    v: float = 0 #фаза периодической составляющей в момент КЗ в радианах
    vach: Characteristic | None = None # класс характеристик применительно для ВАХ

    @field_validator('accuracy')
    @classmethod
    def validate_accuracy(cls, v: str | None) -> str | None:
        if v is None:
            return v
        values = ('10P', '5P', '10PR', '5PR', '0.5', '0.5S', '0.2', '0.2S', '1')
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
                  te.m(r'I_{H1} \geq I_{\text{макс.}}') + 'Номинальный ток вторичной обмотки принимается равным 1 А или 5 А')
        te.p('По термической односекундной стойкости ток в цепи измерения тока терминала не должен превышать значения' +
                  te.m(r'100⋅I_{H2}') + ' (при двухсекундной - не более ' + te.m(r'40 \cdot I_{H2}') +
                  '). Поэтому для ТТ '
                  'используемых для подключения терминалов защит, для которых максимальное время ликвидации КЗ в зоне '
                  'действия защиты составляет менее 1 с (с учетом отказа основной защиты и ликвидации КЗ в результате '
                  'действия резервных или смежных защит защищаемого элемента), должно выполняться условие ' +
                  te.m(r'I_{H1} \geq \frac{I_{\text{кз.макс.}}}{100}'))
        te.p('Для ТТ используемых для подключения терминалов защит, для которых максимальное время ликвидации КЗ '
                  'в зоне действия защиты составляет более 1 с, но менее 2 с (с учетом отказа основной защиты и '
                  'ликвидации КЗ в результате действия резервных или смежных защит защищаемого элемента), должно '
                  'выполняться условие' + te.m(r'I_{H1} \geq \frac{I_{\text{кз.макс.}}}{40}'))
        te.p(te.m(r'I_{\text{кз.макс}}')+' - максимально возможное значение тока КЗ проходящего через обмотку '
                  'рассматриваемого ТТ')
        te.h3('Проверка по термической стойкости')
        te.p('Проверка трансформатора тока на термическую стойкость при КЗ заключается в сравнении найденного '
             'при расчетных условиях интеграла Джоуля Вкз с его допустимым для проверяемого ТТ значением Втер.доп. '
             'Трансформатор тока удовлетворяет условию  термической стойкости, если выполняется следующее условие:')
        te.math(r'B_{\text{ТЕР.ДОП}} = I_{\text{ТЕР}}^2 \cdot 1\text{сек}')
        te.math(r'B_{\text{КЗ}} = I_{\text{КЗ}}^2 \cdot t_{\text{ОТКЛ}}')
        te.math(r'B_{\text{КЗ}} \leq B_{\text{ТЕР.ДОП}}')

        te.h3('Проверка по динамической стойкости')
        te.p('Проверка трансформатора тока на динамическую стойкость при КЗ заключается в сравнении тока динамической '
             'стойкости с ударным током короткого замыкания.'
             'Трансформатор тока удовлетворяет условию  термической стойкости, если выполняется следующее условие:')
        te.math(r'I_{\text{ДИН}} \geq \chi \cdot \sqrt{2} \cdot I_{\text{КЗ}}')
        te.ul(f'где {te.m(r"\chi")} - ударный коэффициент')

        te.h3('Расчет мощности обмоток трансформаторов тока')
        te.p('Суммарное сопротивление нагрузки составляет: ')
        te.math(r'Z_{\text{СУММ}} = Z_{\text{КАБ}} + Z_{\text{ПОТР}} + Z_{\text{КОН}},')
        te.p('где ' + te.m(r'Z_{\text{КАБ}}') + ' - сопротивление кабельной линии от трансформатора тока до конечного потребителя; ')
        te.p(te.m(r'Z_{\text{ПОТР}}') + ' -сопротивление подключенной нагрузки;')
        te.p(te.m(r'Z_{\text{КОН}}') + ' - переходное сопротивление контактов, принимается равным 0,05 Ом при количестве '
                                      'подключенных устройств три и менее и 0,1 Ом при количестве приборов более трех')
        te.p('Соротивление кабельной линии от трансформатора тока до конечного потребителя составляет: ')
        te.math(r'R_{\text{КАБ}} = \rho \cdot \frac{l}{S},')
        te.p('где ρ – удельное сопротивление меди равное 0,0175 Ом⋅мм2/м;')
        te.p('l – длина контрольного кабеля, м; ')
        te.p('S – сечение контрольного кабеля, мм2')
        te.p('Мощность обмотки трансформатора тока должна составлять не менее: ')
        te.math(r'W = I^2_{H2} \cdot Z_{\text{СУММ}},')
        te.p('где '+te.m(r'I_{H2}')+' - номинальный ток вторичной обмотки ТТ')

        te.h3('Проверка ТТ на 10 % погрешность')
        te.p('Расчетная проверка на 10 % погрешность выполняется для максимального тока внешнего короткого '
                  'замыкания с учетом фактического значения сопротивления нагрузки '+te.m(r'Z_{\text{н.факт.расч.}}'))
        te.p('Сопротивление нагрузки ТТ при трехфазном (двухфазном) коротком замыкании (схема соединения ТТ полная '
                  'звезда) определяется формулой:')
        te.math(r'Z_{\text{н.факт.расч.}} = \rho \cdot \frac {l}{S} + R_{\text{реле}} + R_{\text{пер}},')
        te.p('где '+te.m(r'R_{\text{реле}}')+' – сопротивление подключённых к токовым цепям реле защиты, Ом')
        te.p(te.m(r'R_{\text{пер}}')+' – сопротивление контактов, принимается равным 0,05 Ом при количестве подключенных '
                  'устройств три и менее и 0,1 Ом при количестве приборов более трех')
        te.p('При схеме соединения ТТ в неполную звезду сопротивление нагрузки ТТ определяется формулой (при '
                  'двухфазном коротком замыкании):')
        te.math(r'Z_{\text{н.факт.расч.}} = 2 \cdot \rho \cdot \frac {l}{S} + R_{\text{реле}} + R_{\text{пер}},')
        te.p('Предельно допустимая кратность тока '+te.m(r'K_{\text{10доп}}')+' в заданном классе точности при фактической '
                  'расчетной нагрузке определяется по кривым предельной кратности на основе '+
             te.m(r'Z_{\text{н.факт.расч.}}'))
        te.p('При отсутствии кривых предельной кратности '+te.m(r'K_{\text{10доп}}')+' определяется по формуле:')
        te.math(r'K_{\text{10доп}} = K_{10} \cdot '
                r'\frac{\sqrt{(r_2 + \cos \phi \cdot Z_{\text{НОМ}})^2 + (\sin \phi \cdot Z_{\text{НОМ}})^2}}'
                r'{r_2 + Z_{\text{н.факт.расч.}}}')
        te.p('где '+te.m('r_2')+' - сопротивление вторичной обмотки ТТ')
        te.p(te.m(r'\cos \phi')+' - коэффициент мощности номинальной вторичной нагрузки ТТ')
        te.p(te.m(r'Z_{\text{НОМ}}')+' - номинальная вторичное сопротивление ТТ (без учета сопротивления рассеяния '
                                     'вторичной обмотки ТТ)')
        te.p('Максимальная расчетная кратность ТТ при внешнем коротком замыкании определяется по формуле: ')
        te.math(r'K_{\text{макс.расч}} = \frac{I_{\text{макс.расч}}}{I_{H1}},')
        te.p('где '+te.m(r'I_{\text{макс.расч}}')+' – максимальный расчетный ток;')
        te.p(te.m('I_{H1}')+' – номинальный первичный ток ТТ')
        te.p('Полная погрешность ТТ не превышает 10 % при выполнении условия: ')
        te.math(r'K_{\text{10доп}} > K_{\text{макс.расч}}')
        te.p('В общем случае максимальный расчетный ток определяется по формуле:')
        te.math(r'I_{\text{макс.расч.}} = k_a \cdot I_{\text{1макс.}},')
        te.p('где '+te.m(r'I_{\text{1макс.}}')+' - максимальный ток, проходящий через трансформатор тока при к. з. в таких точках '
                  'защищаемой сети, где увеличение погрешностей трансформатора тока сверх допустимой может вызвать '
                  'неправильное действие защиты;')
        te.p(te.m('k_a')+' - коэффициент, учитывающий влияние на быстродействующие защиты переходных процессов '
                  'при к. з., которые сопровождаются прохождением апериодических составляющих в токе к. з.')
        te.p('В случае использования обычных токовых защит (МТЗ с независимой выдержкой времени, ТО) максимальный '
                  'ток, проходящий через трансформатор тока при к. з определяется по формуле:')
        te.math(r'I_{\text{1макс.}} = 1.1 \cdot \frac{I_{\text{с.з.}}}{k_{\text{сх}}},')
        te.p('где '+te.m(r'I_{\text{с.з.}}')+' – максимальный первичный ток срабатывания защиты')
        te.p(te.m(r'k_{\text{сх}}')+' – коэффициент схемы (для схемы соединения ТТ полная звезда – составляет 1)')
        te.p('1,1 – коэффициент, учитывающий возможное уменьшение вторичного тока на 10% из-за погрешностей '
                  'трансформатора тока')
        te.p('Коэффициент '+te.m('k_a')+' учитывающий влияние переходных процессов, принимается равным:')
        te.ul('для всех защит, имеющих выдержку времени 0,5 с и больше '+te.m('k_a = 1;'))
        te.ul(' для максимальных токовых зашит и отсечек с выдержкой времени меньше 0,5 с '+
                  te.m(r'k_a = 1,2 ... 1,4.'))

        te.h3('Проверка ТТ на предельно допустимую погрешность')
        te.p('Выполняется для проверки по условиям повышенной вибрации контактов реле направления мощности или '
                  'реле тока (для электромеханических реле), а также для проверки по условиям предельно допустимой для '
                  'реле направления мощности и направленных реле сопротивлений угловой погрешности – 50%')
        te.p('Проверка трансформаторов тока на предельно допустимую погрешность выполняется для максимального тока '
                  'короткого замыкания в зоне действия защиты')
        te.p('Максимальная расчетная кратность ТТ при коротком замыкании в зоне действия защиты определяется по '
                  'формуле:')
        te.math(r'K_{\text{макс.внутр}} = \frac{I_{\text{макс.внутр}}}{I_{H1}},')
        te.p('где '+te.m(r'I_{\text{макс.внутр}}')+' – максимальный расчетный ток короткого замыкания в зоне действия защиты;')
        te.p(te.m(r'I_{H1}')+' – номинальный первичный ток ТТ')
        te.p('Обобщенный параметр '+te.m(r'A_{\text{расч}}')+', определяющий величину токовой погрешности по превышению '
                  'предельно допустимой кратности тока в классе точности 10Р определяется по формуле:')
        te.math(r'A_{\text{расч}} = \frac{K_{\text{макс.внутр}}}{K_{\text{10доп}}},')
        te.p('где '+te.m(r'K_{\text{10доп}}')+' – предельно допустимая кратность тока в классе точности 10P')
        te.p('Токовая погрешность ТТ не превышает предельно допустимого значения при выполнении условия: '+
                  te.m(r'A_{\text{расч}} < A.'))
        te.p('Предельно допустимая токовая погрешность при коротком замыкании в зоне действия защиты для '
                  'электромеханических реле тока составляет 50%, для статических реле тока - 80%, для реле направления '
             'мощности РБМ-177,178 - 20%, РБМ-171,172 - 30%, статических реле мощности - 50%. Для микропроцессорных '
             'защит проверку производить не требуется.')

        te.h3('Проверка по условию отсутствия опасных перенапряжений во вторичных цепях ТТ')
        te.p('Напряжение во вторичных цепях ТТ при максимальном токе короткого замыкания определяется по формуле:')
        te.math(r'U_{\text{TTрасч}} = K_{\text{У}} \cdot \frac{I_{\text{макс.внутр}}}{K_{TT}} \cdot Z_{\text{н.факт.расч}}')
        te.p('где '+te.m(r'K_{TT}')+' – коэффициент трансформации трансформатора тока')
        te.p(te.m(r'K_{\text{У}}') + f' - ударный коэффициент равный {self.ku}')
        te.p('Значение напряжения на вторичных обмотках ТТ не должно превышать испытательного напряжения 1000 В. '
                  'Трансформаторы тока удовлетворяют указанному требованию при выполнении условия:')
        te.math(r'U_{\text{ТТрасч}} < 1000 В')

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
    def s_nagr3ph(self):
        return self.i2 ** 2 * self.z_nagr3ph

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

    @property
    def kn_real3ph(self):
        zn = self.sn / (self.i2 ** 2)
        sin_phi = math.sin(math.acos(self.cos))
        return self.kn * math.sqrt((self.r2 + self.cos * zn) ** 2 + (sin_phi * zn) ** 2) / (self.r2 + self.z_nagr3ph)

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
        for t in range(0, 10000):
            t /= 1000
            k_p_r = self.k_p_r(t, casesc, kz3ph) if gost else self.k_p_rPNST(t, casesc, kz3ph)
            if a < k_p_r:
                return ((t - last_t) / (k_p_r - last_k_p_r) * (a - last_k_p_r) + last_t) * 1000
            last_k_p_r = k_p_r
            last_t = t
        print('error')

    def check_table(self, t: float):
        '''
        :param t: time of protection plus time open CB
        '''
        i_din = self.i_din if self.i_din else 'нет'
        yield (self.name, self.model, self.i_term, i_din, f'{self.i_term**2:.2f}', f'{self.ikz_max / 1000:.2f}', t,
               f'{(self.ikz_max / 1000) ** 2 * t:.2f}', self.ku,
               f'{self.ikz_max / 1000 * math.sqrt(2) * self.ku:.2f}')
        z_nagr3ph = self.z_nagr3ph
        yield (self.name, self.accuracy, self.sn, f'{self.r_ustr:.2f}', self.length, self.s, f'{z_nagr3ph:.2f}',
               f'{self.s_nagr3ph:.2f}')
        if self.kn:
            if ('P' in self.accuracy or 'PR' in self.accuracy) or self.accuracy == '1':
                data = (f'{self.kn_real3ph:.2f}', self.isz_max, f'{self.isz_max * 1.1:.0f}',
                        f'{self.isz_max * 1.1 / self.i1:.2f}')
            else:
                data = 'нет', 'нет', 'нет', 'нет'
            yield (self.name, self.kn, self.r2, *data)
        else:
            yield None
        if self.vach:
            i2sc = self.ikz_max / self.i1 * self.i2
            u2sc = i2sc * (self.z_nagr3ph + self.r2)
            i0sc = self.vach.get_a_by_b(u2sc)
            yield self.name, i2sc, self.z_nagr3ph, u2sc, f'{i0sc:.3f}', f'{i0sc / i2sc * 100:.2f}'
        else:
            yield None

        usc = self.ku * self.ikz_max * self.i2 / self.i1 * z_nagr3ph
        yield (self.name, f'{self.i1}/{self.i2}', f'{self.imax:.0f}', f'{self.imax / self.i1 * 100:.0f}',
               f'{z_nagr3ph:.2f}', self.ikz_max, f'{usc:.1f}')

    def check(self, te: TextEngine):
        te.h2(self.name)
        te.p('Для расчета обмотки ТТ приняты следующие исходные данные:')
        if self.model:
            te.ul(f'трансформатор тока {self.model}')
        te.ul('номинальный ток первичной обмотки ТТ '+ te.m("I_{H1} =")+f' {self.i1} А;')
        te.ul('номинальный ток вторичной обмотки ТТ '+ te.m("I_{H2} =")+f' {self.i2} А;')
        if self.accuracy in ('10P', '10PR', '5P', '5PR'):
            te.ul(f'односекундный ток термической стойкости {self.i_term} кА;')
            te.ul(f'максимальный расчетный ток короткого замыкания в зоне действия защиты - {self.ikz_max} А;')
            te.ul(f'максимальная токовая уставка срабатывания зашиты - {self.isz_max} А;')
        te.p('нагрузкой токовых релейных цепей являются:')
        zsum = 0
        psum = 0
        for num_load in self.loads:
            p = LOADS_DATA[num_load][1] / LOADS_DATA[num_load][2] * self.i2
            z = p / (self.i2 ** 2)
            te.ul(f'{LOADS_DATA[num_load][0]} с потребляемой мощностью {p} ВА и сопротивлением {z:.2f} Ом')
            zsum += z
            psum += p
        te.p('переходное сопротивление контактов, принимается равным 0,05 Ом;')
        te.p(f'минимальное сечение кабельной линии от релейной обмотки трансформатора тока составляет '
                  f'{self.s} мм2;')
        te.p(f'максимальная длина кабельной линии от релейной обмотки трансформатора тока до конечного потребителя '
                  f'составляет не более {self.length} м')

        if self.accuracy in ('10P', '10PR', '5P', '5PR'):
            te.h3('Проверка на допустимый длительный ток, ток термической и динамической стойкости')
            imax = self.imax if self.imax else self.i1
            te.p(f'Максимальный рабочий ток через первичную обмотку ТТ составляет {imax }A. Значит принятые к '
                      f'установке ТТ не будут перегружены')
            te.p(f'Максимальный ток КЗ {self.ikz_max} А меньше тока односекундной термической стойкости {self.i_term} кА '
                      f'и тока динамической стойкости {self.i_din} кА')
            ksc = self.ikz_max/self.i1
            if ksc < 100:
                te.p(f'Кратность тока при КЗ {self.ikz_max} / {self.i1} = {ksc:.1f}')
                if ksc < 40:
                    te.p('Значит термическая двухсекундная стойкость для цифровых защит обеспечивается (менее 40 крат)')
                else:
                    te.p('Значит термическая односекундная стойкость для цифровых защит обеспечивается (менее 100 крат)')
            else:
                te.p(f'Кратность вторичного тока трансформатора тока при КЗ не может значительно превысить значение '
                     f'предельной кратности равной {self.kn}. Поэтому из-за насыщения сердечника трансформатора тока '
                     f'термическая двухсекундная стойкость для цифровых защит при максимальной кратности 40 будет '
                     f'обсеспечена.')
        te.h3('Расчет мощности обмотки трансформаторов тока')
        r = 0.0175 * self.length / self.s
        te.math(r'R_{КАБ} = ρ \cdot \frac{l}{S} = 0,0175 \cdot \frac{'+f'{self.length}'+r'}{'+
                     f'{self.s}'+'} = '+f'{r:.3f}'+' Ом')
        te.p('Суммарное сопротивление нагрузки для цепей РЗА и потребляемая мощность от релейной обмотки '
                  'трансформатора тока в режиме отсутствия напряжения на шинках управления составит:')
        te.math(r'Z_{СУММ} = ' + f'{zsum:.3f} + {r:.3f} = {zsum+r:.3f} Ом')
        zsum += r
        sreal = self.i2**2*zsum
        te.math(f'S = {self.i2}^2 \\cdot {zsum:.3f} = {sreal:.2f} ВА')
        if sreal <= self.sn:
            te.p(f'Следовательно, мощность вторичной релейной обмотки устанавливаемого трансформатора тока выбираем {self.sn} ВА.')
        else:
            te.warning('Мощности выбранного трансформатора тока недостаточно')

        if self.accuracy in ('10P', '10PR', '5P', '5PR'):
            te.h3('Проверка ТТ на 10 % погрешность')
            if self.kpk:
                te.p(f'Для номинальной мощности вторичной релейной обмотки ТТ равной {self.sn} ВА, номинальной предельной кратности '
                     f'обмотки ТТ равной {self.kn}, класса точности {self.accuracy} и мощности нагрузки вторичной обмотки '
                     f'{self.s_real:.3f} ВА по кривым предельной кратности допустимая кратность составит:')
                te.math(r'K_{\text{макс.}} = ' + f'{self.knfact}')
            else:
                zn = self.sn/(self.i2**2)
                te.math(r'Z_{\text{НОМ}} = \frac{W_{\text{НОМ}}}{I_{H2}^2} ='+f'{zn:.2f}'+r'\text{Ом}')
                sin_phi = math.sin(math.acos(self.cos))
                k10dop = self.kn * math.sqrt((self.r2 + self.cos * zn)**2 + (sin_phi * zn)**2) / (self.r2 + zsum)
                te.math(r'K_{\text{10доп}} ='+f'{self.kn}'+r' \cdot \frac{\sqrt{('+f'{self.r2} + {self.cos} \\cdot {zn})^2 + '
                       f'({sin_phi:.2f} \\cdot {zn})^2'+r'}}{'+f'{self.r2} + {zsum:.3f}'+'} = '+
                        f'{k10dop:.1f}')
            kreal = self.isz_max/self.i1
            te.p(f'Фактическая кратность при максимальной токовой уставке срабатывания зашиты К = {self.isz_max} / {self.i1}'
                 f' = {kreal:.1f})')
            if self.kpk and self.knfact < self.kn or not self.kpk and kreal < self.kn:
                 te.p('Условие выполняется.')
            else:
                te.warning('Условие не выполняется.')

            te.h3('Проверка ТТ на предельно допустимую погрешность')
            te.p('Выполняется для проверки по условиям повышенной вибрации контактов реле направления мощности или реле тока'
                 ' (для электромеханических реле), а также для проверки по условиям предельно допустимой для реле '
                 'направления мощности и направленных реле сопротивлений угловой погрешности – 50%. Так как в качестве '
                 'защиты используется микропроцессорный терминал без функций направления мощности и направленных реле '
                 'сопротивлений, то по данному критерию проверка ТТ не производится.')

            te.h3('Проверка по условию отсутствия опасных перенапряжений во вторичных цепях ТТ.')
            usc = self.ku * self.ikz_max * self.i2 / self.i1 * zsum
            te.math(r'U_{\text{TTрасч}} = '+f'{self.ku}'+r' \cdot \frac{'+f'{self.ikz_max} \\cdot {self.i2}'+r'}{'+f'{self.i1}'+r'} \cdot'+
                    f' {zsum:.3f} = {usc:.1f} < 1000 B')
            if usc < 1000:
                te.p('Условие выполняется.')
            else:
                te.warning(f'Напряжение выше нормы: {usc:.1f} > 1000 B')
        te.h3('Выбранные параметры ТТ')
        txt_kn = 'коэффициент предельной кратности релейной обмотки' if self.accuracy in (
            '10P', '10PR', '5P', 'PR') else 'коэффициент безопасности приборов'
        te.p(f'номинальный ток {self.i1}/{self.i2}, класс точности обмотки {self.accuracy}, номинальная мощность '
              f'обмотки {self.sn} ВА, {txt_kn} {self.kn}')

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

    def _graph(self, te: TextEngine, t_limit: int, casesc: CaseSC, suffix: str):
        x = []
        y = []
        z = []
        y1 = []
        z1 = []
        for tm in range(1, t_limit):
            tm /= 1000
            x.append(tm)
            y.append(self.k_p_r(tm, casesc, True))
            z.append(self.k_p_rPNST(tm, casesc, True))
            if casesc.isc1:
                y1.append(self.k_p_r(tm, casesc, False))
                z1.append(self.k_p_rPNST(tm, casesc, False))
        fig, ax = plt.subplots()
        ax.plot(x, y, label='Кп.р. ГОСТ 3-х ф.КЗ')
        ax.plot(x, z, label='Кп.р. ПНСТ 3-х ф.КЗ')
        if casesc.isc1:
            ax.plot(x, y1, label='Кп.р. ГОСТ 1-х ф.КЗ')
            ax.plot(x, z1, label='Кп.р. ПНСТ 1-х ф.КЗ')
        ax.legend()
        ax.grid()
        namefile = f'{self.name}_{casesc.name}'
        namefile = namefile.replace(' ', '_')
        namefile = namefile.replace('.', '_')
        namefile = namefile.replace('(', '_')
        namefile = namefile.replace(')', '_')
        plt.savefig(namefile + suffix + '.png')
        te.image(namefile + suffix + '.png', 'Графики Кп.р.(t)', 500)
        plt.close()

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
            t_graph_big = self.t_sat_from_k_p_r_by_a(casesc, True, True)
            t3 = f'{t_graph_big:.2f}'
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
            t_graph_small = self.t_sat_from_k_p_r_by_a(casesc, True, True)
            t3 = f'{t_graph_small:.2f}'
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

        self._graph(te, int(t_graph_big * 1.2), casesc, '_big')
        self._graph(te, int(t_graph_small * 1.2), casesc, '_small')

    def row_data(self):
        return self.name, self.model, f'{self.i1}/{self.i2}', self.accuracy, self.sn, self.kn, self.i_term, self.i_din

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

    def check(self, te: TextEngine):
        te.h1('Расчётная проверка трансформаторов тока')
        self.cts[0].metods(te)
        for ct in self.cts:
            ct.check(te)

    def check_table(self, te: TextEngine, t: list[float]):
        '''
        :param t: list of time protection
        '''
        te.h1('Расчётная проверка трансформаторов тока')
        self.cts[0].metods(te)
        te.h2('Проверка трансформаторов тока')
        gens_data = [ct.check_table(t[num]) for num, ct in enumerate(self.cts)]
        te.table_name('Проверка на стойкость к токам КЗ')
        te.table_head('Место установки', 'Модель', 'Односекундный ток термической стойкости, кА',
                      'Ток динамической стойкости, кА', 'Номинальный тепловой импульс, кА²·сек', 'Ток КЗ, кА',
                      'Время отключения, сек', 'Тепловой импульс, кА²·сек', 'Ударный коэффициент', 'Ударный ток КЗ, кА')
        for gen in gens_data:
            te.table_row(*next(gen))
        te.table_name('Проверка мощности обмоток')
        te.table_head('Место установки', 'Класс точности', 'Мощность обмотки, ВА', 'Сопротивление приборов, Ом', 'Длина кабеля, м',
                      'Сечение жилы кабеля, мм.кв', 'Полное сопротивление нагрузки, Ом', 'Мощность фактической нагрузки, ВА')
        for gen in gens_data:
            te.table_row(*next(gen))

        rows = []
        for gen in gens_data:
            data = next(gen)
            if data:
                rows.append(data)
        if rows:
            te.table_name('Проверка на 10% погрешность')
            te.table_head('Место установки', 'Кп (Fs)', 'Сопротивление вторичной обмотки, Ом', 'K10доп',
                          'Ток срабатывания защиты максимальный, А', 'Iмакс.расч, А', 'Kмакс.рас')
            for row in rows:
                te.table_row(*row)

        rows = []
        for gen in gens_data:
            data = next(gen)
            if data:
                rows.append(data)
        if rows:
            te.table_name('Проверка на 10% погрешность по реальной ВАХ')
            te.table_head('Место установки', 'Ток вторичный КЗ, А', 'Сопротивление нагрузки, Ом',
                          'Напряжение на нагрузке, В', 'Ток намагничивания по ВАХ, А', 'Погрешность, %')
            for row in rows:
                te.table_row(*row)
        te.table_name('Проверка по току нагрузки и условию отсутствия опасных перенапряжений во вторичных цепях ТТ')
        te.table_head('Место установки', 'Ктт', 'Ток нагрузки максимальный, А', 'Загрузка, %', 'Полное сопротивление нагрузки, Ом',
                      'Iмакс.кз, А', 'Напряжение, В')
        for gen in gens_data:
            data = next(gen)
            if data:
                te.table_row(*data)
        te.h2('Выбранные трансформаторы тока')
        self.data(te)

    def data(self, te: TextEngine):
        te.table_name('Выбранные трансформаторы тока с параметрами обмоток')
        te.table_head('Место установки', 'Марка', 'Ктт', 'Класс точности', 'Мощность обмотки, ВА', 'Kп (Fs)',
                      'Односекундный ток термической стойкости, кА', 'Ток динамической стойкости, кА')
        for ct in self.cts:
            te.table_row(*ct.row_data())
