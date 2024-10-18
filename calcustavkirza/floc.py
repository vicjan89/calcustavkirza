import tomllib
from dataclasses import dataclass
from math import radians, degrees
from cmath import rect, phase

version = 0.1

@dataclass
class Pris:
    name: str
    Ia: float
    fIa: float
    Ib: float
    fIb: float
    Ic: float
    fIc: float
    Ua: float
    fUa: float
    Ub: float
    fUb: float
    Uc: float
    fUc: float
    paral3I0: float
    f_paral3I0: float

    def calc(self):
        self.ia = rect(self.Ia, radians(self.fIa))
        self.ib = rect(self.Ib, radians(self.fIb))
        self.ic = rect(self.Ic, radians(self.fIc))
        self.ua = rect(self.Ua, radians(self.fUa))
        self.ub = rect(self.Ub, radians(self.fUb))
        self.uc = rect(self.Uc, radians(self.fUc))
        self.parali0 = rect(self.paral3I0, radians(self.f_paral3I0)) / 3
        self._3i0 = (self.ia + self.ib + self.ic)
        self.m3i0 = abs(self._3i0)
        self.i0 = self._3i0 / 3
        self._3u0 = (self.ua + self.ub + self.uc)
        self.m3u0 = abs(self._3u0)
        self.u0 = self._3u0 / 3
        out = f'{self.name}\n{self.__repr__()}\n{self.__str__()}\n'
        return out

    def __str__(self):
        return f'3U0={self._3u0:.2f} ({self.m3u0:.2f} {degrees(phase(self._3u0)):.1f}°) ' \
               f'3I0={self._3i0:.2f} ({self.m3i0:.2f} {degrees(phase(self._3u0)):.1f}°)'

@dataclass
class FLOC:
    R1: float
    X1: float
    R0: float
    X0: float
    Rm: float
    Xm: float
    Xo: float
    begin: Pris
    end: Pris
    L: float
    Lo: float

    def calc_2_9(self, p: Pris):
        return abs((p.uc / p.i0).imag / ((p.ic + self.k * p.i0) * self.Z1 / p.i0).imag)

    def calc_2_27(self, p: Pris):
        return abs((p.uc / p.i0).imag / ((p.ic + self.k * p.i0 + (self.Zm / self.Z1) *
                                                    p.parali0) * self.Z1 / p.i0).imag)

    def calc_1_11(self, begin, end):
        return (end.m3u0 - begin.m3u0 + end.m3i0 * self.mZ0 * self.L) / (begin.m3i0 + end.m3i0) / self.mZ0

    def calc(self):
        self.Z1 = complex(self.R1, self.X1)
        self.Z0 = complex(self.R0, self.X0)
        self.Zm = complex(self.Rm, self.Xm)
        self.k = (self.Z0 - self.Z1) / self.Z1

        out = f'{version=}\n'
        # 2.9
        out += f'По формуле 2.9 расстояние  {self.calc_2_9(self.begin):.3f} км от {self.begin.name}\n'
        out += f'По формуле 2.9 расстояние  {self.calc_2_9(self.end):.3f} км от {self.end.name}\n'

        #2.27
        out += f'По формуле 2.27 расстояние  {self.calc_2_27(self.begin):.3f} км от {self.begin.name}\n'
        out += f'По формуле 2.27 расстояние  {self.calc_2_27(self.end):.3f} км от {self.end.name}\n'

        #1.11
        self.mZ0 = abs(self.Z0)
        out += f'По формуле 1.11 расстояние  {self.calc_1_11(self.begin, self.end):.3f} км от {self.begin.name}\n'
        out += f'По формуле 1.11 расстояние  {self.calc_1_11(self.end, self.begin):.3f} км от {self.end.name}\n'


        #1.12
        self.mZm = abs(self.Zm)
        l4 = (self.end.m3u0 - self.begin.m3u0 + self.end.m3i0 * abs(self.Z0 + self.Zm) * self.L) / \
             (self.begin.m3i0 + self.end.m3i0) / abs(self.Z0 + self.Zm)
        l6 = (self.end.m3u0 - self.begin.m3u0 + self.end.m3i0 * (self.X0 + self.Xm) * self.L) / (self.begin.m3i0 + self.end.m3i0) / (self.X0 + self.Xm)

        #1.15
        x1 = (self.Lo + self.Xo / self.X0) * self.end.m3u0 - self.Xo * self.begin.m3u0 / self.X0 + (self.L * self.Xo + self.X0 * self.Lo * (self.L - self.Lo)) * self.end.m3i0
        x2 = self.end.m3u0 + self.Xo * self.begin.m3i0 + (self.Xo + self.X0 * (self.L - self.Lo)) * self.end.m3i0
        l5 = x1 / x2
        l3u0 = self.begin.m3u0 + self.X0 * self.Lo * self.begin.m3i0
        r3u0 = self.end.m3u0 + self.X0 * (self.L - self.Lo) * self.end.m3i0
        out += 'По критерию страницы 33:\n'
        if l3u0 > r3u0:
            out += 'Повреждение до отпайки\n'
        else:
            out += 'Повреждение после отпайки\n'

        out += f'По формуле 1.12 расстояние {l6:.3f} км от {self.begin.name}\n' \
               f'По формуле 1.15 расстояние {l5:.3f} км от {self.begin.name}'
        return out


with open("config.toml", "rb") as f:
    data = tomllib.load(f)

out = ''
begin = Pris(**data['begin'])
out += begin.calc()
end = Pris(**data['end'])
out += end.calc()
floc = FLOC(begin=begin, end=end, **data['settings'])
out += floc.calc()
with open('result.txt', 'w', encoding='utf-8') as file:
    file.write(out)