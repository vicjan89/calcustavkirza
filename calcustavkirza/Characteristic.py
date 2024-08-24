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
