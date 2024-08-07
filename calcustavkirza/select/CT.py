from pydantic import BaseModel


from calcustavkirza.classes import Element
from textengines.interfaces import TextEngine

class Ikz(BaseModel):
    name: str #наименование ветви
    i: float #ток КЗ
    T: float #постоянная времени


class CT(Element):
    model: str
    i1: int
    i2: int
    i_term: int | None = None
    ikz_max: int | None = None
    isz_max: float | None = None
    length: float #длина кабеля токовых цепей в метрах
    s: float = 2.5 #сечение жилы кабеля токовых цепей в мм квадратных
    loads: list | None = None
    loads_data: list = [['токовые входа микропроцессорного герминала', 0.25, 0.01],
                        ['токовые цепи измерительного преобразователя', 1, 0.04],
                        ['токовые цепи счётчика электрической энергии', 0.5, 0.02]]
    ikz3: list[Ikz] #список трёхфазных токов КЗ
    ikz1: list[Ikz] | None = None #список однофазных токов КЗ

    def metods(self):
        self.te.h2('Методика выполнения расчётов')
        self.te.h3('Проверка коэффициента трансформации релейных обмоток трансформаторов тока')
        self.te.p('Номинальный ток первичной обмотки ТТ должен быть больше максимально возможного тока нагрузки: ' +
                  self.te.m('I<sub>Н1</sub>≥I<sub>макс.</sub>') + 'Номинальный ток вторичной обмотки принимается равным 1 А или 5 А')
        self.te.p('По термической односекундной стойкости ток в цепи измерения тока терминала не должен превышать значения' +
                  self.te.m('100⋅I<sub>H2</sub>') + ' (при двухсекундной - не более ' + self.te.m('40⋅I<sub>H2</sub>') +
                  '. Поэтому для ТТ '
                  'используемых для подключения терминалов защит, для которых максимальное время ликвидации КЗ в зоне '
                  'действия защиты составляет менее 1 с (с учетом отказа основной защиты и ликвидации КЗ в результате '
                  'действия резервных или смежных защит защищаемого элемента), должно выполняться условие ' +
                  self.te.m('I<sub>H1</sub> ≥ <sup>Iкз.макс.</sup>&frasl;<sub>100</sub>'))
        self.te.p('Для ТТ используемых для подключения терминалов защит, для которых максимальное время ликвидации КЗ '
                  'в зоне действия защиты составляет более 1 с, но менее 2 с (с учетом отказа основной защиты и '
                  'ликвидации КЗ в результате действия резервных или смежных защит защищаемого элемента), должно '
                  'выполняться условие  I<sub>H1</sub> ≥ <sup>Iкз.макс.</sup>&frasl;<sub>40</sub>')
        self.te.p('I<sub>кз.макс</sub> - максимально возможное значение тока КЗ проходящего через обмотку '
                  'рассматриваемого ТТ')
        self.te.h3('Расчет мощности обмоток трансформаторов тока')
        self.te.p('Суммарное сопротивление нагрузки составляет: '
                  'Z<sub>СУММ</sub>=Z<sub>КАБ</sub>+Z<sub>ПОТР</sub>+Z<sub>КОН</sub>,')
        self.te.p('где Z<sub>КАБ</sub> - сопротивление кабельной линии от трансформатора тока до конечного потребителя; '
                  'Z<sub>ПОТР</sub> -сопротивление подключенной нагрузки; Z<sub>КОН</sub> - переходное сопротивление '
                  'контактов, принимается равным 0,05 Ом при количестве подключенных устройств три и менее и 0,1 Ом при '
                  'количестве приборов более трех')
        self.te.p('Сопротивление кабельной линии от трансформатора тока до конечного потребителя составляет: '
                  'R<sub>КАБ</sub>=ρ⋅<sup>l</sup>&frasl;<sub>S</sub>, где ρ – удельное сопротивление меди равное '
                  '0,0175 Ом⋅<sup>мм2</sup>&frasl;<sub>м</sub>; l – длина контрольного кабеля, м; '
                  'S – сечение контрольного кабеля, мм2')
        self.te.p('Мощность обмотки трансформатора тока должна составлять не менее: '
                  'W=I<sup>2</sup><sub>H2</sub>⋅Z<sub>СУММ</sub>,')
        self.te.p('где I<sub>Н2</sub> - номинальный ток вторичной обмотки ТТ')
        self.te.h3('Проверка ТТ на 10 % погрешность')
        self.te.p('Расчетная проверка на 10 % погрешность выполняется для максимального тока внешнего короткого '
                  'замыкания с учетом фактического значения сопротивления нагрузки Z<sub>н.факт.расч.</sub>')
        self.te.p('Сопротивление нагрузки ТТ при трехфазном (двухфазном) коротком замыкании (схема соединения ТТ полная '
                  'звезда) определяется формулой:')
        self.te.p('Z<sub>н.факт.расч.</sub>=ρ⋅<sup>l</sup>&frasl;<sub>S</sub>+R<sub>реле</sub>+R<sub>пер</sub>,')
        self.te.p('где ρ – удельное сопротивление меди равное 0,0175 Ом⋅<sup>мм2</sup>&frasl;<sub>м</sub>; l – длина '
                  'контрольного кабеля, м; S – сечение контрольного кабеля, мм2')
        self.te.p('R<sub>реле</sub> – сопротивление подключённых к токовым цепям реле защиты, Ом')
        self.te.p('R<sub>пер</sub> – сопротивление контактов, принимается равным 0,05 Ом при количестве подключенных '
                  'устройств три и менее и 0,1 Ом при количестве приборов более трех')
        self.te.p('При схеме соединения ТТ в неполную звезду сопротивление нагрузки ТТ определяется формулой (при '
                  'двухфазном коротком замыкании):')
        self.p('Z<sub>н.факт.расч.</sub>=2&middot;ρ⋅<sup>l</sup>&frasl;<sub>S</sub>+R<sub>реле</sub>+R<sub>пер</sub>,')
        self.te.p('Предельно допустимая кратность тока K<sub>10доп</sub> в заданном классе точности при фактической '
                  'расчетной нагрузке определяется по кривым предельной кратности на основе Z<sub>н.факт.расч.</sub>')
        self.te.p('Максимальная расчетная кратность ТТ при внешнем коротком замыкании определяется по формуле: '
                  'K<sub>макс.внеш</sub>=I <sub>макс.внеш</sub>/I<sub>H1</sub>,')
        self.te.p('где I<sub>макс.внеш</sub> – максимальный расчетный ток;')
        self.te.p('I<sub>H1</sub> – номинальный первичный ток ТТ')
        self.te.p('Полная погрешность ТТ не превышает 10 % при выполнении условия: '
                  'K<sub>10доп</sub> > K<sub>макс.расч</sub>')
        self.te.p('В общем случае максимальный расчетный ток определяется по формуле:')
        self.te.p('I<sub>макс.расч.</sub> = k<sub>a</sub>&middot;I<sub>1макс.</sub>, где')
        self.te.p('I<sub>1макс.</sub> - максимальный ток, проходящий через трансформатор тока при к. з. в таких точках '
                  'защищаемой сети, где увеличение погрешностей трансформатора тока сверх допустимой может вызвать '
                  'неправильное действие защиты;')
        self.te.p('k<sub>a</sub> - коэффициент, учитывающий влияние на быстродействующие защиты переходных процессов '
                  'при к. з., которые сопровождаются прохождением апериодических составляющих в токе к. з.')
        self.te.p('В случае использования обычных токовых защит (МТЗ с независимой выдержкой времени, ТО) максимальный '
                  'ток, проходящий через трансформатор тока при к. з определяется по формуле:')
        self.te.p('I<sub>1макс.</sub> = 1,1 &middot; I<sub>с.з.</sub> / k<sub>сх</sub>,')
        self.te.p('где I<sub>с.з.</sub> – максимальный первичный ток срабатывания защиты')
        self.te.p('k<sub>сх</sub> – коэффициент схемы (для схемы соединения ТТ полная звезда – составляет 1)')
        self.te.p('1,1 – коэффициент, учитывающий возможное уменьшение вторичного тока на 10% из-за погрешностей '
                  'трансформатора тока')
        self.te.p('Коэффициент k<sub>a</sub> учитывающий влияние переходных процессов, принимается равным:')
        self.te.p('для всех защит, имеющих выдержку времени 0,5 с и больше k<sub>a</sub> = 1;')
        self.te.p(' для максимальных токовых зашит и отсечек с выдержкой времени меньше 0,5 с '
                  'k<sub>a</sub> = 1,2&divide;1,3.')
        self.te.h3('Проверка ТТ на предельно допустимую погрешность')
        self.te.p('Выполняется для проверки по условиям повышенной вибрации контактов реле направления мощности или '
                  'реле тока (для электромеханических реле), а также для проверки по условиям предельно допустимой для '
                  'реле направления мощности и направленных реле сопротивлений угловой погрешности – 50%')
        self.te.p('Проверка трансформаторов тока на предельно допустимую погрешность выполняется для максимального тока '
                  'короткого замыкания в зоне действия защиты')
        self.te.p('Максимальная расчетная кратность ТТ при коротком замыкании в зоне действия защиты определяется по '
                  'формуле: K<sub>макс.внутр</sub> = I<sub>макс.внутр</sub> / I<sub>H1</sub>,')
        self.te.p('где I<sub>макс.внутр</sub> – максимальный расчетный ток короткого замыкания в зоне действия защиты;')
        self.te.p('I<sub>H1</sub> – номинальный первичный ток ТТ')
        self.te.p('Обобщенный параметр A<sub>расч</sub>, определяющий величину токовой погрешности по превышению '
                  'предельно допустимой кратности тока в классе точности 10Р определяется по формуле: '
                  'A<sub>расч</sub> = K<sub>макс.внутр</sub> / K<sub>10доп</sub>,')
        self.te.p('где K<sub>10доп</sub> – предельно допустимая кратность тока в классе точности 10P')
        self.te.p('Токовая погрешность ТТ не превышает предельно допустимого значения при выполнении условия: '
                  'A<sub>расч</sub> < A. ')
        self.te.p('Предельно допустимая токовая погрешность при коротком замыкании в зоне действия защиты для '
                  'микропроцессорных реле составляет 50%, этой величине соответствует значение параметра A=2,6')
        self.te.h3('Проверка по условию отсутствия опасных перенапряжений во вторичных цепях ТТ')
        self.te.p('Напряжение во вторичных цепях ТТ при максимальном токе короткого замыкания определяется по формуле: '
                  'U<sub>TTрасч</sub> = I<sub>макс.внутр</sub> / K<sub>TT</sub> &middot; Z<sub>н.факт.расч</sub>')
        self.te.p('где K<sub>ТТ</sub> – коэффициент трансформации трансформатора тока')
        self.te.p('Значение напряжения на вторичных обмотках ТТ не должно превышать испытательного напряжения 1000 В. '
                  'Трансформаторы тока удовлетворяют указанному требованию при выполнении условия: '
                  'U<sub>ТТрасч</sub> < 1000 В')


    def check(self):
        self.te.h3(self.name)
        self.te.p('Для расчета релейной обмотки ТТ 10 кВ приняты следующие исходные данные:')
        self.te.ul(f'трансформатор тока {self.model}')
        self.te.ul(f'номинальный ток первичной обмотки ТТ - {self.te.m("I_{H1} = ")}{self.i1} А;')
        self.te.ul(f'номинальный ток вторичной обмотки ТТ - {self.te.m("I_{H2} = ")}{self.i2} А;')
        self.te.ul(f'односекундный ток термической стойкости {self.i_term} кА;')
        # # <p>- ТТ устанавливаются в {% if cell.phases==3 %}
        # # трех
        # # {% elif cell.phases==2 %}
        # # двух
        # # {% endif %}
        # # фазах;</p>
        self.te.ul(f'максимальный расчетный ток короткого замыкания в зоне действия защиты - {self.ikz_max} А;')
        self.te.ul(f'максимальная токовая уставка срабатывания зашиты - {self.isz_max} А;')
        self.te.p('нагрузкой токовых релейных цепей являются:')
        zsum = 0
        psum = 0
        for z in self.loads:
            l = self.loads_data[z]
            self.te.ul(f'{l[0]} с потребляемой мощностью {l[1]} ВА и сопротивлением {l[2]}')
            zsum += l[2]
            psum += l[1]
        self.te.p('переходное сопротивление контактов, принимается равным 0,05 Ом;')
        self.te.p(f'минимальное сечение кабельной линии от релейной обмотки трансформатора тока составляет '
                  f'{self.conductor_section} мм2;')
        self.te.p(f'максимальная длина кабельной линии от релейной обмотки трансформатора тока до конечного потребителя '
                  f'составляет не более {self.conductor_lenght} м')

        self.te.h3('Проверка на допустимый длительный ток, ток термической и динамической стойкости')
        self.te.p(f'Максимальный рабочий ток через первичную обмотку ТТ составляет {self.imax }A. Значит принятые к '
                  f'установке ТТ не будут перегружены')
        self.te.p(f'Максимальный ток КЗ {self.ikz_max} А меньше тока односекундной термической стойкости {self.i_term} кА '
                  f'и тока динамической стойкости {self.i_din} кА')
        self.te.p(f'Кратность тока при КЗ {self.ikz_max} / {self.i1} = {self.ikz_max/self.i1} < 40 а значит термическая '
                  f'двухсекундная стойкость для цифровых защит обеспечивается')

        self.te.h3('Расчет мощности релейной обмотки трансформаторов тока')
        r = 0.0175 * self.conductor_lenght / self.conductor_section
        self.te.math(r'R_{КАБ} = ρ \cdot \frac{l}{S} = 0,0175 \cdot \frac{'+self.conductor_lenght+r'}{'+
                     self.conductor_section+'} = '+r+' Ом')
        self.te.p('Суммарное сопротивление нагрузки для цепей РЗА и потребляемая мощность от релейной обмотки '
                  'трансформатора тока в режиме отсутствия напряжения на шинках управления составит:')
        self.te.math(r'Z_{СУММ} = ' + f'{zsum:.3f} + {r:.3f}Ом')
        zsum += r
        self.te.math(f'S = {self.i2}^2 \cdot {zsum} = {self.i2**2*zsum} ВА')
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

    def ts(self, te: TextEngine):
        rn_kz3 = 0.0175 * self.length / self.s
        rn_kz1 = 2 * rn_kz3
        t_eq = sum([ikz.i * ikz.T for ikz in self.ikz3]) / sum([ikz.i for ikz in self.ikz3])
        print(rn_kz3,rn_kz1, t_eq)