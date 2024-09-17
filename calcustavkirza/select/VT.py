import math


from textengines.interfaces import TextEngine


from calcustavkirza.classes import Element


class VT(Element):
    name: str
    model: str
    location: str
    u1: float
    u2: float
    ud2: float
    u1max: int
    u2accuracy: float
    u2daccuracy: float | str
    u2s: int
    u2ds: int
    u2load: list[tuple]
    ud2load: list[tuple]
    lenght: float # длина кабеля до потребителя
    s: float # сечение кабеля до потребителя
    u2permissible: float # допустимое падение напряжения


    def check(self, te: TextEngine):
        te.h1('Выбор и проверка трансформаторов напряжения')
        te.h2(f'Проверка параметров и выбор ТН {self.name}')
        te.h3('Для проверки параметров выбран трансформаторов напряжения со следующими характеристиками:')
        te.ul(f'Место установки {self.location}')
        te.ul(f'модель трансформатора {self.model}')
        te.ul(f'Класс напряжения {self.u1} В')
        te.ul(f'Наибольшее рабочее напряжение {self.u1max} кВ')
        te.ul(f'Номинальное линейное первичное напряжение {self.u1} В')
        te.ul(f'Номинальное линейное вторичное напряжение {self.u2} В')
        te.ul(f'Напряжение на выводах «разомкнутого треугольника» дополнительных вторичных обмоток при замыкании '
                   f'одной из фаз сети на землю {self.ud2}В')
        te.ul(f'Класс точности основной вторичной обмотки {self.u2accuracy}')
        te.ul(f'Номинальная мощность основной вторичной обмотки {self.u2s} ВА')
        te.ul(f'Класс точности дополнительной вторичной обмотки соединённой по схеме "разомкнутого треугольника" {self.u2daccuracy}')
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
        te.math(r'I_{\text{НАГР}} = \frac{\sqrt{3} \cdot ' + f'{u2ssum}' + r'}{' + str(self.u2) +'} = ' +
                     f'{i:.4f}  A')
        te.ul(' где ' + te.m(r'S_{\text{НАГР}}') + ' – мощность наиболее нагруженной фазы, ВА,')
        te.ul(' ' + te.m(r'U_{\text{мф}}') + ' – номинальное междуфазное напряжение, В.')
        te.p('Сопротивление кабельной линии от трансформатора напряжения до конечного потребителя составляет:')
        te.math(r'R_{\text{КАБ}} = \rho \cdot \frac{l}{S} ,')
        r = 0.0175 * self.lenght / self.s
        te.math(r'R_{\text{КАБ}} = 0.0175 \cdot \frac{' + str(self.lenght) + '}{' + str(self.s) + '} = ' +
                     f'{r:.4f}' + r' \text{Ом}')
        te.ul('где '+te.m(r'\rho')+' – удельное сопротивление меди равное 0,0175 ' +
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


    def table_load(self, load: list[tuple], te: TextEngine):
        te.table_head('Устройство подключенное к ТН', 'Мощность потребления (для обмотки звезда на одну фазу), ВА')
        ssum = 0
        for device, power in load:
            te.table_row(device, power)
            ssum += power
        te.table_row('Итого', ssum)
        return ssum
