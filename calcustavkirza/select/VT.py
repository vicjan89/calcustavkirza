import math

from calcustavkirza.classes import Element


class SelectVT(Element):
    name: str
    model: str
    location: str
    u1: int
    u2: int
    ud2: int
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


    def select(self):
        self.te.h1('Выбор и проверка трансформаторов напряжения')
        self.te.h2(f'Проверка параметров и выбор ТН {self.name}')
        self.te.h3('Для проверки параметров выбран трансформаторов напряжения со следующими характеристиками:')
        self.te.ul(f'Место установки {self.location}')
        self.te.ul(f'модель трансформатора {self.model}')
        self.te.ul(f'Класс напряжения {self.u1} В')
        self.te.ul(f'Наибольшее рабочее напряжение {self.u1max} кВ')
        self.te.ul(f'Номинальное линейное первичное напряжение {self.u1} В')
        self.te.ul(f'Номинальное линейное вторичное напряжение {self.u2} В')
        self.te.ul(f'Напряжение на выводах «разомкнутого треугольника» дополнительных вторичных обмоток при замыкании '
                   f'одной из фаз сети на землю {self.ud2}В')
        self.te.ul(f'Класс точности основной вторичной обмотки {self.u2accuracy}')
        self.te.ul(f'Номинальная мощность основной вторичной обмотки {self.u2s} ВА')
        self.te.ul(f'Класс точности дополнительной вторичной обмотки соединённой по схеме "разомкнутого треугольника" {self.u2daccuracy}')
        self.te.ul(f'Номинальная мощность вторичной обмотки соединённой по схеме "разомкнутого треугольника" {self.u2ds} ВА')

        self.te.h3('Расчёт мощности нагрузки основной вторичной обмотки трансформатора напряжения.')
        self.te.table_name('Исходные данные для основной обмотки')
        u2ssum = self.table_load(self.u2load)
        self.te.table_name('Исходные данные для дополнительной вторичной обмотки соединённой по схеме "разомкнутого треугольника"')
        ud2ssum = self.table_load(self.ud2load)

        self.te.h3('Расчет по допустимому падению напряжения')
        self.te.p('Ток в наиболее нагруженной фазе вторичной обмотки ТН «звезда»:')
        self.te.math(r'I_{\text{НАГР}} = \frac{\sqrt{3} \cdot S_{\text{НАГР}}}{U_{\text{мф}}}, А')
        i = u2ssum * math.sqrt(3) / self.u2
        self.te.math(r'I_{\text{НАГР}} = \frac{\sqrt{3} \cdot ' + f'{u2ssum}' + r'}{' + str(self.u2) +'} = ' +
                     f'{i:.4f}  A')
        self.te.ul(' где ' + self.te.m(r'S_{\text{НАГР}}') + ' – мощность наиболее нагруженной фазы, ВА,')
        self.te.ul(' ' + self.te.m(r'U_{\text{мф}}') + ' – номинальное междуфазное напряжение, В.')
        self.te.p('Сопротивление кабельной линии от трансформатора напряжения до конечного потребителя составляет:')
        self.te.math(r'R_{\text{КАБ}} = \text{?} \cdot \frac{l}{S} ,')
        r = 0.0175 * self.lenght / self.s
        self.te.math(r'R_{\text{КАБ}} = 0.0175 \cdot \frac{' + str(self.lenght) + '}{' + str(self.s) + '} = ' +
                     f'{r:.4f}' + r' \text{Ом}')
        self.te.ul('где ? – удельное сопротивление меди равное 0,0175 ' +
                   self.te.m(r'\text{Ом} \cdot \frac{\text{мм}^2}{\text{м}};'))
        self.te.ul('l – длина контрольного кабеля, м; ')
        self.te.ul('S – сечение контрольного кабеля, мм2')
        self.te.p('Величина падения напряжения до наиболее отдаленного потребителя в обмотке ТН «звезда»:')
        self.te.math(r'?U = \sqrt{3} \cdot I_{\text{НАГР}} \cdot R_{\text{КАБ}} < ?U_{\text{ДОП}}')
        u2perm = math.sqrt(3) * i * r / self.u2 * 100
        self.te.p('Результат расчёта:')
        self.te.math(r'?U = \sqrt{3} \cdot ' + f'{i:.3f}' + ' \cdot ' + f'{r:.3f} = {u2perm:.4f}' + r' \% < ' +
                     f'{self.u2permissible}' + ' \%')
        self.te.p('Требования к классу точности ТН для цепей учёта а также к допустимому падению напряжения определены '
                  'в соответствии с ТКП 339-2022 (33240).')


    def table_load(self, load: list[tuple]):
        self.te.table_head('Устройство подключенное к ТН', 'Мощность потребления (для обмотки звезда на одну фазу), ВА')
        ssum = 0
        for device, power in load:
            self.te.table_row(device, power)
            ssum += power
        self.te.table_row('Итого', ssum)
        return ssum
