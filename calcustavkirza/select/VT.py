import math

from textengines.interfaces import TextEngine

from calcustavkirza.classes import Element
from calcustavkirza.select.load import Load

class VTwinding(Element):
    u: float
    accuracy: float
    s: int
    smax: int
    uk: float

class VT(Element):
    name: str
    model: str
    location: str
    u1: float
    winding: list[VTwinding]

    def data(self, te: TextEngine):
        te.h2(f'Проверка параметров и выбор ТН {self.name}')
        te.h3('Для проверки параметров выбран трансформатор напряжения со следующими характеристиками:')
        te.ul(f'Место установки: {self.location}')
        te.ul(f'модель трансформатора: {self.model}')
        te.ul(f'Класс напряжения: {self.u1:.1f} В')
        # te.ul(f'Наибольшее рабочее напряжение {self.u1max} В')
        te.ul(f'Номинальное первичное напряжение {self.u1:.1f} В')
        te.table_name('Данные вторичных обмоток')
        te.table_head('Номинальное напряжение, В', 'Класс точности', 'Номинальная мощность, ВА')
        for wind in self.winding:
            te.table_row(f'{wind.u:.1f}', wind.accuracy, wind.s)

    def check_load(self, te: TextEngine, loads: list[Load], u2permissible: float):
        '''
        :param u2permissible:
        :type float:
        '''
        te.h3('Расчёт мощности нагрузки обмоток трансформатора напряжения.')
        total_load = []
        i = []
        for num, load in enumerate(loads):
            tl = load.data(te)
            total_load.append(tl)
            i.append(tl / self.winding[num].u)

        te.p('Ток в фазе находим по формуле:')
        te.math(r'I_{\text{НАГР}} = \frac{S_{\text{НАГР}}}{U_{\text{ф}}}, А')
        te.ul(' где ' + te.m(r'S_{\text{НАГР}}') + ' – мощность наиболее нагруженной фазы, ВА,')
        te.ul(' ' + te.m(r'U_{\text{ф}}') + ' – номинальное напряжение фазы, В.')
        loads[0].metodology(te)
        te.p('Величина падения напряжения до наиболее отдаленного потребителя находим по формуле:')
        te.math(r'\Delta U = I_{\text{НАГР}} \cdot 2 \cdot R_{\text{КАБ}} < \Delta U_{\text{ДОП}}')

        te.table_name('Расчет по допустимому падению напряжения')
        te.table_head('Ток в фазе, A', 'Сопротивление кабеля до нагрузки, Ом', 'Падение напряжения, В',
                      'Падение напряжения, %', 'Допустимое падение напряжения, %')
        for num, load in enumerate(loads):
            du = i[num] * load.r_cable * 2
            te.table_row(f'{i[num]:.4f}', f'{load.r_cable * 2:.4f}', f'{du:.4f}',
                         f'{du / self.winding[num].u * 100:.2f}%', u2permissible)
        # te.p('Требования к классу точности ТН для цепей учёта а также к допустимому падению напряжения определены '
        #           'в соответствии с ТКП 339-2022 (33240).')

    def check_sc(self, te: TextEngine, loads: list[Load]):
        te.h3('Расчёт токов короткого замыкания')
        te.p('Сопротивление ТН при коротком замыканиии определяем по формуле:')
        te.math(r'Z_{\text{ТН}} = \frac{U_{k} \cdot U_{ph}^2}{100 \cdot S_n}')
        te.ul(f'где {te.m(r"U_{k}")} - напряжение короткого замыкания ТН, %')
        te.ul(f'{te.m("S_n")} - пределная мощность ТН, ВА')
        te.ul(f'{te.m("U_{ph}")} - номинальное напряжение обмотки ТН, В')
        te.p('Ток короткого замыкания определяем по формуле:')
        te.math(r'I_{\text{КЗ}} = \frac{U_{ph}}{\sqrt{Z_{\text{ТН}}^2 + (r_{\text{КАБ}} \cdot 2)^2}}')
        te.ul(f'где {te.m(r"r_{\text{КАБ}}")} - сопротивление жилы кабеля до нагрузки, Ом')
        te.table_name('Расчёт токов короткого замыкания')
        te.table_head('Напряжение КЗ, %', 'Сопротивление ТН, Ом', 'Сопротивление кабеля, Ом',
                      'Ток КЗ на зажимах ТН, А', 'Ток КЗ в наиболее удалённой точке, А')
        for num, wind in enumerate(self.winding):
            zsc = wind.uk * wind.u ** 2 / wind.smax / 100
            r_cable = loads[num].r_cable * 2
            isc_max = wind.u / zsc
            isc_min = wind.u / math.sqrt(zsc ** 2 + r_cable **  2)
            te.table_row(wind.uk, f'{zsc:.3f}', f'{r_cable:.3f}', f'{isc_max:.1f}', f'{isc_min:.1f}')



    def check_group(self):
        te.h1('Выбор и проверка трансформаторов напряжения')
        te.h2(f'Проверка параметров и выбор ТН {self.name}')
        te.h3('Для проверки параметров выбран трансформатор напряжения со следующими характеристиками:')
        te.ul(f'Место установки {self.location}')
        te.ul(f'модель трансформатора {self.model}')
        te.ul(f'Класс напряжения {self.u1} В')
        te.ul(f'Наибольшее рабочее напряжение {self.u1max} В')
        te.ul(f'Номинальное первичное напряжение {self.u1} В')
        for num, wind in enumerate(self.winding):
            te.ul(f'Номинальное вторичное напряжение обмотки {num + 1} - {wind.u} В')
        te.ul(f'Напряжение на выводах «разомкнутого треугольника» дополнительных вторичных обмоток при замыкании '
              f'одной из фаз сети на землю {self.ud2}В')
        te.ul(f'Класс точности основной вторичной обмотки {self.u2accuracy}')
        te.ul(f'Номинальная мощность основной вторичной обмотки {self.u2s} ВА')
        te.ul(
            f'Класс точности дополнительной вторичной обмотки соединённой по схеме "разомкнутого треугольника" {self.u2daccuracy}')
        te.ul(f'Номинальная мощность вторичной обмотки соединённой по схеме "разомкнутого треугольника" {self.u2ds} ВА')

        te.h3('Расчёт мощности нагрузки основной вторичной обмотки трансформатора напряжения.')
        te.table_name('Исходные данные для основной обмотки')
        u2ssum = self.table_load(self.u2load, te)
        te.table_name('Исходные данные для дополнительной вторичной обмотки соединённой по схеме "разомкнутого треугольника"')
        ud2ssum = self.table_load(self.ud2load, te)

        te.h3('Расчет по допустимому падению напряжения')
        te.p('Ток в наиболее нагруженной фазе вторичной обмотки ТН «звезда»:')
        te.math(r'I_{\text{НАГР}} = \frac{\sqrt{3} \cdot S_{\text{НАГР}}}{U_{\text{мф}}}, А')
        i = u2ssum * math.sqrt(3) / self.u2
        te.math(r'I_{\text{НАГР}} = \frac{\sqrt{3} \cdot ' + f'{u2ssum}' + r'}{' + str(self.u2) + '} = ' +
                f'{i:.4f}  A')
        te.ul(' где ' + te.m(r'S_{\text{НАГР}}') + ' – мощность наиболее нагруженной фазы, ВА,')
        te.ul(' ' + te.m(r'U_{\text{мф}}') + ' – номинальное междуфазное напряжение, В.')
        te.p('Сопротивление кабельной линии от трансформатора напряжения до конечного потребителя составляет:')
        te.math(r'R_{\text{КАБ}} = \rho \cdot \frac{l}{S} ,')
        r = 0.0175 * self.lenght / self.s
        te.math(r'R_{\text{КАБ}} = 0.0175 \cdot \frac{' + str(self.lenght) + '}{' + str(self.s) + '} = ' +
                f'{r:.4f}' + r' \text{Ом}')
        te.ul('где ' + te.m(r'\rho') + ' – удельное сопротивление меди равное 0,0175 ' +
              te.m(r'\text{Ом} \cdot \frac{\text{мм}^2}{\text{м}};'))
        te.ul('l – длина контрольного кабеля, м; ')
        te.ul('S – сечение контрольного кабеля, мм2')
        te.p('Величина падения напряжения до наиболее отдаленного потребителя в обмотке ТН «звезда»:')
        te.math(r'\Delta U = \sqrt{3} \cdot I_{\text{НАГР}} \cdot R_{\text{КАБ}} < \Delta U_{\text{ДОП}}')
        u2perm = math.sqrt(3) * i * r / self.u2 * 100
        te.p('Результат расчёта:')
        te.math(r'\Delta U = \sqrt{3} \cdot ' + f'{i:.3f}' + r' \cdot ' + f'{r:.3f} = {u2perm:.4f}' + r' \% < ' +
                f'{self.u2permissible}' + r' \%')
        te.p('Требования к классу точности ТН для цепей учёта а также к допустимому падению напряжения определены '
             'в соответствии с ТКП 339-2022 (33240).')
