import math


class Characteristic:

    def __init__(self, name):
        self.name = name
        self.x = []
        self.y = []
        self.curve = []

    def addx(self, x: float, value: float):
        self.x.append((x, value))

    def addy(self, y: float, value: float):
        self.y.append((y, value))

    def addp(self, x: int, y: int):
        self.curve.append((x, y))

    @staticmethod
    def _approximate(c, collect):
        for coord, value in collect:
            if c <= coord:
                return (value - last_value) / (coord - last_coord) * (c - last_coord) + last_value
            last_coord = coord
            last_value = value

    def get(self):
        res = []
        for x, y in self.curve:
            vx = self._approximate(x, self.x)
            vy = self._approximate(y, self.y)
            res.append((vx, vy))
        return res

    def log10(self, c1: float, v1: float, c2: float, v2: float):
        '''
        Возвращает список координат логарифмической шкалы по основанию 10 добавляя декаду в начале и в конце
        :param c1: координата первого значения
        :param v1: первое значение кратно 10
        :param c2: координата второго значения
        :param v2: второе значение кратно 10
        :return:
        '''
        res = []
        count_decads = 0
        v2v1 = v2 / v1
        while (v2v1 - 1) > 0.01:
            count_decads += 1
            v2v1 = v2v1 / 10
        length_decad = (c2 - c1) / count_decads
        v1 /= 10
        c = c1 - length_decad
        for d in range(count_decads + 2):
            for k in range(1, 10):
                res.append((length_decad * math.log10(k) + c, (10 ** d) * v1 * k))
            c += length_decad
        return res

