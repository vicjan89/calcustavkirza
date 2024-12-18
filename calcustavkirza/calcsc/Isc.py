import math
import cmath


from textengines.interfaces import TextEngine


from calcustavkirza.classes import Element
from calcustavkirza.calcsc.calc_pu import Pu
from calcustavkirza.functions import complex2polar_str
from calcustavkirza.electro_store import IscStore


class ClassIscStore(Element):
    i: float | None = None #ток КЗ в амперах
    t: float | None = None #постоянная времени в мс
    a: float  | None = None #угол тока КЗ в градусах
    u: float #линейное напряжение сети в вольтах
    i1: float | None = None
    a1: float | None = None
    i2: float | None = None
    a2: float | None = None
    i0: float | None = None
    a0: float | None = None
    kcd: float = 1 #коэффициент токораспределения

class Isc:

    def __init__(self, te: TextEngine, store: IscStore, pu: Pu):
        self.te = te
        self.store = store
        self.pu = pu

    @property
    def isc(self):
        '''
        Модуль тока КЗ
        '''
        if self.i:
            return self.i * self.kcd
        i1 = cmath.rect(self.i1, math.radians(self.a1))
        i2 = cmath.rect(self.i2, math.radians(self.a2))
        i0 = cmath.rect(self.i0, math.radians(self.a0))
        i = i1 + i2 + i0 / 3
        return abs(i) * self.kcd

    @property
    def alfa(self):
        '''
        Угол в градусах тока КЗ
        '''
        if self.a:
            return self.a
        if self.i1 and self.i2 and self.i0:
            i1 = cmath.rect(self.i1, math.radians(self.a1))
            i2 = cmath.rect(self.i2, math.radians(self.a2))
            i0 = cmath.rect(self.i0, math.radians(self.a0))
            i = i1 + i2 + i0 / 3
            return math.degrees(cmath.phase(i))
        if self.t:
            r = self.u / math.sqrt(3) / self.i / math.sqrt(1 + self.t ** 2 * 10000 * math.pi ** 2)
            x = self.t * 100 * math.pi * r
            return math.degrees(cmath.phase(self.u / math.sqrt(3) / complex(r, x)))
        raise ValueError('Нет исходных данных для вычисления угла тока')

    @property
    def z(self):
        '''
        Рассчитывает сопротивление по току трёхфазного КЗ
        :param u: линейное напряжение сети
        :return: комплексное значение сопротивления в Ом в котором исключны отрицательные значения
        '''
        z = self.u / math.sqrt(3) / cmath.rect(self.isc, math.radians(self.alfa)) / self.kcd
        return complex(abs(z.real), abs(z.imag))

    @property
    def z_abs(self):
        '''

        Returns:
            float: модуль сопротивления
        '''
        return abs(self.z)

    @property
    def ts(self):
        '''
        Рассчитывает постоянную времени по сопротивлению если она не задана
        :param u: линейное напряжение сети
        :return: постоянная времени в мс
        '''
        if self.t:
            return  self.t
        z = self.z
        t = abs(z.imag / 100 / math.pi / z.real * 1000)
        self.t = t
        return t

    @property
    def ic(self):
        return cmath.rect(self.isc, math.radians(self.alfa))
        # return complex(abs(ic.real), abs(ic.imag))

    @ic.setter
    def ic(self, value):
        self.i, self.a = cmath.polar(value)
        self.a = math.degrees(self.a)

    @property
    def s_sc_mva(self):
        return self.ic * self.u * math.sqrt(3) / 1_000_000

    @property
    def i1c(self):
        return cmath.rect(self.i1, math.radians(self.a1)) * self.kcd

    @i1c.setter
    def i1c(self, value):
        self.i1, a = cmath.polar(value)
        self.a1 = math.degrees(a)

    @property
    def i2c(self):
        return cmath.rect(self.i2, math.radians(self.a2)) * self.kcd

    @i2c.setter
    def i2c(self, value):
        self.i2, a = cmath.polar(value)
        self.a2 = math.degrees(a)

    @property
    def i0c(self):
        return cmath.rect(self.i0, math.radians(self.a0)) * self.kcd

    @i0c.setter
    def i0c(self, value):
        self.i0, a = cmath.polar(value)
        self.a0 = math.degrees(a)

    def write3ph(self, te: TextEngine):
        te.table_row(self.name, f'{self.isc:.0f}', f'{self.alfa:.3f}°')

    def write1ph(self, te: TextEngine):
        te.table_row(self.name, f'{self.i1:.0f} {self.a1:.3f}°', f'{self.i2:.0f} {self.a2:.3f}°',
                     f'{self.i0:.0f} {self.a0:.3f}°')

    def __str__(self):
        return f'{self.isc:.3f}A {self.alfa:.3f}°'

    @property
    def z2str(self):
        z = self.z
        return f'{z.real:.3f}+j{z.imag:.3f} Ом'

    @property
    def e(self): # ЭДС системы
        return  self.store.u / math.sqrt(3)

    def __imul__(self, other):
        if not isinstance(other, int) and not isinstance(other, float):
            raise ArithmeticError("Правый операнд должен быть типом int или float")
        if self.i:
            self.i *= other
        if self.i1 and self.i2 and self.i0:
            self.i1 *= other
            self.i2 *= other
            self.i0 *= other
        return self

    def __itruediv__(self, other):
        '''
        Деление на число
        '''
        if not isinstance(other, int) and not isinstance(other, float):
            raise ArithmeticError("Правый операнд должен быть типом int или float")
        if self.i:
            self.i /= other
        if self.i1 and self.i2 and self.i0:
            self.i1 /= other
            self.i2 /= other
            self.i0 /= other
        return self


    def __add__(self, other):
        if not isinstance(other, Isc):
            raise ArithmeticError("Правый операнд должен быть типом Isc")
        if self.u != other.u:
            raise ArithmeticError('У токов разные напряжения')
        isc = Isc(u=self.u)
        if self.i and other.i:
            isc.ic = self.ic + other.ic
        elif self.i1 and self.i2 and self.i0 and other.i1 and other.i2 and other.i0:
            i1 = self.i1c + other.i1c
            i2 = self.i2c + other.i2c
            i0 = self.i0c + other.i0c
            isc.i1c = i1
            isc.i2c = i2
            isc.i0c = i0
        else:
            raise ArithmeticError('Операнды заданы разными способами')
        return isc

    def write(self):
        self.te.table_name(f'Технические данные: {self.name}')
        self.te.table_head('Наименование', 'Обозначение', 'Расчётная формула', 'Числовые значения в формуле',
                      'Величина')
        self.te.table_row('Ток трёхфазного короткого замыкания, кА', 'Iкз3', '', f'{self.ic/1000:.3f}',
                     complex2polar_str(self.ic/1000))
        z_ohm = self.u/math.sqrt(3)/self.ic
        z_ohm = complex(abs(z_ohm.real), abs(z_ohm.imag))
        self.te.table_row('Сопротивление прямой последовательности, Ом', 'x1c', 'Eлин/(√3·Iкз3)',
                     f'{self.u}/(√3·{self.ic:.3f})', f'{z_ohm:.3f} ({complex2polar_str(z_ohm)})')
        z_s_pu = z_ohm / self.pu.z_ohm
        z_s_pu = complex(abs(z_s_pu.real), abs(z_s_pu.imag))
        self.te.table_row('Сопротивление прямой последовательности приведенное к базовому сопротивлению, о.е.', 'x1c',
                     'x1c/Zб', f'{z_ohm:.3f}/{self.pu.z_ohm:.3f}', f'{z_s_pu:.5f} ({complex2polar_str(z_s_pu)})')
        esys_pu = self.u/self.pu.v_kv/1000
        self.te.table_row('ЭДС системы, о.е.', 'Ec*', 'Uc/Uб', f'{self.u/1000:.3f}/{self.pu.v_kv:.3f}', f'{esys_pu:.3f}')
        return esys_pu, z_s_pu


# class CaseSCStore(Element):
#     isc1: list[Isc] | None = None
#     isc3: list[Isc]

class CaseSC:
    def write(self, te: TextEngine):
        te.table_name(f'Технические данные о трёхфазных токах повреждения при {self.name}')
        te.table_head('Наименование ветви', 'Величина, A', 'Угол, °')
        for isc in self.isc3:
            isc.write3ph(te)
        isumc = self.isc3phc
        te.table_row('Сумма', f'{abs(isumc):.3f}', f'{math.degrees(cmath.phase(isumc)):.2f}')
        if self.isc1:
            te.table_name(f'Технические данные о симметричных составляющих токов однофазного КЗ при {self.name}')
            te.table_head('Наименование ветви', 'Ток прямой последовательности, A',
                          'Ток обратной последовательности, A', 'Утроенный ток нулевой последовательности, А')
            for isc in self.isc1:
                isc.write1ph(te)
            te.table_row('Сумма', complex2polar_str(self.i1c), complex2polar_str(self.i2c),
                         complex2polar_str(self.i0c))

    @property
    def isc3str(self):
        '''
        Ток трёхфазного КЗ в комплксной форме в виде строки с полярными значениями
        '''
        i, a = cmath.polar(self.isc3phc)
        return f'{i:.3f}A {math.degrees(a):.3f}°'

    @property
    def isc1str(self):
        '''
        Ток однофазного КЗ в комплксной форме в виде строки с полярными значениями
        '''
        i, a = cmath.polar(self.isc1phc)
        return f'{i:.3f}A {math.degrees(a):.3f}°'

    @property
    def isc1ph_sum(self):
        '''
        Алгебраическая сумма токов однофазного КЗ
        '''
        if self.isc1:
            return sum([isc.isc for isc in self.isc1])

    @property
    def t_eq1ph(self):
        '''
        Постоянная времени тока однофазного КЗ в миллисекунах полученная по методике ГОСТ
        '''
        if self.isc1:
            return sum([isc.isc * isc.ts for isc in self.isc1]) / self.isc1ph_sum

    @property
    def isc3ph_sum(self) -> float:
        '''
        Алгебраическая сумма токов трёхфазного КЗ
        '''
        return sum([isc.isc for isc in self.isc3])

    @property
    def isc3phc(self) -> complex:
        '''
        Возвращает комплексную сумму токов трёхфазного КЗ
        :return:
        '''
        return sum([isc.ic for isc in self.isc3])

    @property
    def isc1phc(self) -> complex:
        '''
        Возвращает комплексную сумму токов однофазного КЗ, исключив отрицательные значения реальной и мнимой частей
        :return:
        '''
        return self.i1c + self.i2c + self.i0c / 3

    @property
    def t_eq3ph(self):
        '''
        Постоянная времени тока трёхфазного КЗ в миллисекунах полученная по методике ГОСТ
        '''
        return sum([isc.isc * isc.ts for isc in self.isc3]) / self.isc3ph_sum

    @property
    def i1c(self) -> complex:
        '''
        Возвращает комплексную сумму токов прямой последовательности
        :return:
        '''
        isum = 0
        for i in self.isc1:
            isum += i.i1c
        return isum


    @property
    def i2c(self) -> complex:
        '''
        Возвращает комплексную сумму токов обратной последовательности
        :return:
        '''
        isum = 0
        for i in self.isc1:
            isum += i.i2c
        return isum

    @property
    def i0c(self) -> complex:
        '''
        Возвращает комплексную сумму токов нулевой последовательности
        :return:
        '''
        isum = 0
        for i in self.isc1:
            isum += i.i0c
        return isum

    def set_kcd(self, kcd: float):
        '''
        Устанавливает коэффициент распределения тока для всех составляющих токов однофазного и трёхфазного КЗ
        '''
        if self.isc1:
            for i in self.isc1:
                i.kcd = kcd
        for i in self.isc3:
            i.kcd = kcd

    def drop(self, index):
        '''
        Удаляет составляющую тока КЗ с индексом index как в трёзфазных токак так и в однофазных
        '''
        self.isc1.pop(index)
        self.isc3.pop(index)

# class CasesSCStore(Element):
#     cases: list[CaseSC]

class CasesSCStore:
    def select(self, name: str):
        for case in self.cases:
            if case.name == name:
                return case
