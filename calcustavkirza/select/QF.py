import json
from importlib import resources


from store.store import JsonStorage
from textengines.interfaces import TextEngine


from calcustavkirza.classes import Element
from calcustavkirza.functions import create_from_charact, create_time_independent, charact_IEC60255_151type, mix_charact


class QF(Element):
    model: str #марка согласно каталога производителя
    inom: int #номинальный ток
    ir: float | None = None #уставка long-time защиты
    tr: float | None = None #уставка по времени long-time защиты
    isd: float | None = None #уставка short-time защиты если равен 0 то ступень выведена
    tsd: float | None = None #уставка по времени short-time защиты
    ii: float | None = None #уставка отсечки если равен 0 то ступень выведена
    icu: float | None = None #номинальная предельная отключающая способность кА
    ics: float | None = None #номинальная отключающая способность кА
    ui: int | None = None #номинальное напряжение изоляции
    ue: int | None = None #номинальное рабочее напряжение

    @property
    def ira(self):
        return self.inom * self.ir

    @property
    def isda(self):
        return self.ira * self.isd

    @property
    def iia(self):
        return self.ira * self.ii

    def __str__(self):
        match self.isd:
            case None:
                isd = ''
                tsd = ''
            case 0:
                isd = ' Isd=OFF'
                tsd = ''
            case _:
                isd = f' Isd={self.isd}'
                tsd = f' tsd={self.tsd}'
        tr = f' tr={self.tr}' if self.tr is not None else ''
        ii = self.ii if self.ii else 'OFF'
        return f'{self.name} {self.model} In={self.inom}A Ir={self.ir}{tr}{isd}{tsd} Ii={ii}'

    def select(self, te: TextEngine, u: float, inagr: float, ikzmax: float):
        te.table_row(self.name, self.model, inagr, self.inom, u, self.ui, ikzmax, self.ics)

    def kch(self, te: TextEngine, ikzmin: float):
        if self.isd:
            isda = self.isda
            kchisd = ikzmin/self.isda*1000
            if (kchisd < 1.25 and self.inom >100) or (kchisd < 1.4 and self.inom <=100): #ПУЭ п.1.7.79
                raise ValueError(f'Кч для ступени Isd мал и равен {kchisd}')
            kchisd = f'{kchisd:.2f}'
        else:
            isda = '-'
            kchisd = '-'
        te.table_row(self.name, ikzmin, self.ira, f'{ikzmin/self.ira*1000:.2f}', isda,
                     kchisd, self.iia, f'{ikzmin/self.iia*1000:.2f}')

class QFs(Element):
    qfs: list[QF]
    u: list[float]
    inagr: list[float]
    ikzmax: list[float]
    ikzmin: list[float]

    def select(self, te: TextEngine):
        te.p('Выбор модульных автоматических выключателей производится по следующим условиям:')
        te.ul('номинальное напряжение изоляции автоматического выключателя должно соответствовать напряжению сети:')
        te.math(r'U_{\text{изоляции}} \geq U_{\text{сети}}')
        te.ul('номинальный ток автоматического выключателя должен соответствовать длительному (расчетному) току электроприемника или линии:')
        te.math(r'I_{\text{Н}} \geq I_{\text{дл}}')
        te.ul('номинальная отключающая способность должна превышать максимальный ток короткого замыкания проходящий '
              'через автоматический выключатель:')
        te.math(r'I_{cs} \geq I_{\text{МАКС.КЗ}}')
        te.table_name('Выбор автоматических выключателей')
        te.table_head('Место установки', 'Модель', 'Ток нагрузки,А', 'Номинальный ток автомата,А',
                      'Напряжение сети,кВ', 'Номинальное напряжение изоляции,кВ', 'Максимальный ток КЗ,кА',
                      'Номинальная отключающая способность,кА')
        for index, qf in enumerate(self.qfs):
            qf.select(te, u=self.u[index], inagr=self.inagr[index], ikzmax=self.ikzmax[index])
        te.p('Проверка чувствительности расцепителей автоматического выключателя осуществляется по результату расчёта '
             'коэффициента чувствительности:')
        te.math(r'K_{\text{ч}} = \frac{I_{\text{МИН.КЗ}}}{I_{\text{сраб.расцеп.}}}')
        te.p('Зчачения рассчитанных коэффициентов чувствительности должны соответствовать требованиям пункта 1.7.79 ПУЭ.')
        te.table_name('Проверка чувствительности при минимальныx токах КЗ в точке подключения АФК к сети')
        te.table_head('Место установки', 'Iкз,А', 'Ir,A', 'Кч', 'Isd,A', 'Кч', 'Ii,A', 'Кч')
        for index, qf in enumerate(self.qfs):
            qf.kch(te, ikzmin=self.ikzmin[index])


class MicroLogic5(QF):

    def get_charact(self):
        charcsmin = []
        charcsmax = []
        if self.isd:
            isd = self.ir * self.isd * self.inom
            charcsmin.append(create_time_independent(isd*0.9, self.tsd*0.9))
            charcsmax.append(create_time_independent(isd*1.1, self.tsd*1.1))
        if self.ii:
            ii = self.inom * self.ii
            charcsmin.append(create_time_independent(ii*0.9, 0))
            charcsmax.append(create_time_independent(ii*1.1, 0))
        charcsmin.append(charact_IEC60255_151type(self.inom, self.ir/1.3, self.tr, 'VIT'))
        charcsmax.append(charact_IEC60255_151type(self.inom, self.ir, self.tr, 'VIT'))
        return mix_charact(charcsmin), mix_charact(charcsmax)

class ChintNM8NEN(QF):
    '''
    Класс описывает автоматический выключатель CHINT NM8N с электронным расцепителем EN
    :param ir: дискретно одно из значений 0.4, 0.5, 0.7, 0.8, 0.9, 0.95, 1
    :param tr: дискретно одно из значений 3, 6, 12, 18
    :param isd: дискретно одно из значений 0 (OFF), 1.5, 2, 3, 4, 6, 8, 10
    :param tsd: дискретно одно из значений 0.1, 0.2, 0.3, 0.4
    :param ii: дискретно одно из значений 0 (OFF), 2, 3, 4, 6, 8, 10, 12
    '''

    def get_charact(self):
        '''
        Возвращает кортеж из функций для минимума и максимума времятоковых характеристик электронного расцепителя EN
        автоматического выключателя NM8N CHINT
        :return:
        '''
        avalible_values = (32, 63, 100, 160, 250, 400, 630, 800, 1000, 1250, 1600)
        if self.inom not in avalible_values:
            raise ValueError(f'value inom must be one of {avalible_values}')
        avalible_values = (0.4, 0.5, 0.7, 0.8, 0.9, 0.95, 1)
        if self.ir not in avalible_values:
            raise ValueError(f'value ir must be one of {avalible_values}')
        avalible_values = (3, 6, 12, 18)
        if self.tr not in avalible_values:
            raise ValueError(f'Value tr must be one of {avalible_values}')
        avalible_values = (0, 1.5, 2, 3, 4, 6, 8, 10)
        if self.isd not in avalible_values:
            raise ValueError(f'Value isd must be one of {avalible_values}')
        avalible_values = (0.1, 0.2, 0.3, 0.4)
        if self.tsd not in avalible_values:
            raise ValueError(f'Value tsd must be one of {avalible_values}')
        avalible_values = (0, 2, 3, 4, 6, 8, 10, 12)
        if self.ii not in avalible_values:
            raise ValueError(f'Value ii must be one of {avalible_values}')
        charcsmin = []
        charcsmax = []
        if self.isd:
            isd = self.ir * self.isd * self.inom
            charcsmin.append(create_time_independent(isd * 0.85, self.tsd * 0.8))
            charcsmax.append(create_time_independent(isd * 1.15, self.tsd * 1.2))
        if self.ii:
            ii = self.inom * self.ii
            charcsmin.append(create_time_independent(ii * 0.85, 0))
            charcsmax.append(create_time_independent(ii * 1.15, 0))
        js = JsonStorage(r'D:\PycharmProjects\calcustavkirza\calcustavkirza\select\characteristics\CHINT_NM8N_ENmin6s')
        data = [(i * self.inom, t / 6 * self.tr) for i, t in js.read()]
        charcsmin.append(create_from_charact(data))
        js = JsonStorage(r'D:\PycharmProjects\calcustavkirza\calcustavkirza\select\characteristics\CHINT_NM8N_ENmax6s')
        data = [(i * self.inom, t / 6 * self.tr) for i, t in js.read()]
        charcsmax.append(create_from_charact(data))
        return mix_charact(charcsmin), mix_charact(charcsmax)

class ChintNM8NTM(QF):
    '''
    Класс описывает автоматический выключатель CHINT NM8N с термомагнитным расцепителем TM
    :param ir: дискретно одно из значений 0.7, 0.8, 0.9, 1
    :param ii: дискретно одно из значений 5, 6, 7, 8, 9, 10, 12
    '''

    def get_charact(self):
        '''
        Возвращает кортеж из функций для минимума и максимума времятоковых характеристик термомагнитного расцепителя TM
        автоматического выключателя NM8N CHINT
        :return:
        '''
        avalible_values = (16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 180, 200, 225, 250, 315, 350, 400, 500, 630,
                           700, 800, 1000, 1250, 1600)
        if self.inom not in avalible_values:
            raise ValueError(f'value inom must be one of {avalible_values}')
        avalible_values = (0.7, 0.8, 0.9, 1)
        if self.ir not in avalible_values:
            raise ValueError(f'value ir must be one of {avalible_values}')
        avalible_values = (5, 6, 7, 8, 9, 10, 11, 12)
        if self.ii not in avalible_values:
            raise ValueError(f'Value ii must be one of {avalible_values}')
        charcsmin = []
        charcsmax = []
        ii = self.inom * self.ii
        charcsmin.append(create_time_independent(ii * 0.8, 0))
        charcsmax.append(create_time_independent(ii * 1.2, 0))
        with resources.open_text('calcustavkirza.select.characteristics', 'CHINT_NM8N_400HV_TM_min.json') as f:
            data = [(i * self.ira, t) for i, t in json.load(f)]
            charcsmin.append(create_from_charact(data))
        with resources.open_text('calcustavkirza.select.characteristics', 'CHINT_NM8N_400HV_TM_max.json') as f:
            data = [(i * self.ira, t) for i, t in json.load(f)]
            charcsmax.append(create_from_charact(data))
        return mix_charact(charcsmin), mix_charact(charcsmax)
