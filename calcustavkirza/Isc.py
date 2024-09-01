import math
import cmath


from calcustavkirza.classes import Element


class Isc(Element):
    i: float | None = None #ток КЗ
    t: float | None = None #постоянная времени в мс
    a: float  | None = None #угол тока КЗ в градусах
    u: float #линейное напряжение сети
    i1: float | None = None
    a1: float | None = None
    i2: float | None = None
    a2: float | None = None
    i0: float | None = None
    a0: float | None = None
    kcd: float = 1 #коэффициент токораспределения

    @property
    def isc(self):
        if self.i:
            return self.i * self.kcd
        i1 = cmath.rect(self.i1, math.radians(self.a1))
        i2 = cmath.rect(self.i2, math.radians(self.a2))
        i0 = cmath.rect(self.i0, math.radians(self.a0))
        i = i1 + i2 + i0 / 3
        self.i, a = cmath.polar(i)
        self.a = math.degrees(a)
        return self.i * self.kcd

    @property
    def alfa(self):
        if self.a:
            return self.a
        i1 = cmath.rect(self.i1, math.radians(self.a1))
        i2 = cmath.rect(self.i2, math.radians(self.a2))
        i0 = cmath.rect(self.i0, math.radians(self.a0))
        i = i1 + i2 + i0 / 3
        self.i, a = cmath.polar(i)
        self.a = math.degrees(a)
        return self.a

    @property
    def z(self):
        '''
        Рассчитывает сопротивление по току трёхфазного КЗ
        :param u: линейное напряжение сети
        :return: комплексное значение сопротивления в Ом
        '''
        return self.u / math.sqrt(3) / cmath.rect(self.i, math.radians(self.a)) / self.kcd

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

    @property
    def i1c(self):
        return cmath.rect(self.i1, math.radians(self.a1)) * self.kcd

    @property
    def i2c(self):
        return cmath.rect(self.i2, math.radians(self.a2)) * self.kcd

    @property
    def i0c(self):
        return cmath.rect(self.i0, math.radians(self.a0)) * self.kcd

class CaseSC(Element):
    isc1: list[Isc] | None = None
    isc3: list[Isc]

    @property
    def isc1ph_sum(self):
        if self.isc1:
            return sum([isc.isc for isc in self.isc1])

    @property
    def t_eq1ph(self):
        if self.isc1:
            return sum([isc.isc * isc.ts for isc in self.isc1]) / self.isc1ph_sum

    @property
    def isc3ph_sum(self):
        return sum([isc.isc for isc in self.isc3])

    @property
    def t_eq3ph(self):
        return sum([isc.isc * isc.ts for isc in self.isc3]) / self.isc3ph_sum

    @property
    def i1sum(self):
        isum = 0
        for i in self.isc1:
            isum += i.i1c
        return isum


    @property
    def i2sum(self):
        isum = 0
        for i in self.isc1:
            isum += i.i2c
        return isum

    @property
    def i0sum(self):
        isum = 0
        for i in self.isc1:
            isum += i.i0c
        return isum

    def set_kcd(self, kcd: float):
        if self.isc1:
            for i in self.isc1:
                i.kcd = kcd
        for i in self.isc3:
            i.kcd = kcd

class CasesSC(Element):
    cases: list[CaseSC]

    def select(self, name: str):
        for case in self.cases:
            if case.name == name:
                return case
