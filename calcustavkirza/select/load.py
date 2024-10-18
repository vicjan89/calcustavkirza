import math


from textengines.interfaces import TextEngine


from calcustavkirza.classes import Element

equipment = {    # name,                 power VA
    'mr771vt': ('Вход напряжения МР771', 0.25),
    'ss301': ('Вход напряжения счётчика СС-301', 1.5)
}

class Load(Element):
    length: float # length of cable
    s: float # wire cross-sectional area
    equipment: list[str] | None = None # list of equipment connected to instrument transformer

    def add(self, equipment_code):
        if self.equipment is None:
            self.equipment = []
        self.equipment.append(equipment_code)

    def data(self, te: TextEngine):
        te.table_name('Данные о подключенной нагрузке')
        te.table_head('Подключенное устройство', 'Мощность потребления при номинальных величинах, ВА')
        ssum = 0
        for eqpt in self.equipment:
            device, power = equipment[eqpt]
            te.table_row(device, power)
            ssum += power
        te.table_row('Итого', ssum)
        te.p(f'Нагрузка подключена медным кабелем сечением {self.s} мм² длиной {self.length} м.')
        return ssum

    @property
    def r_cable(self):
        return 0.0175 * self.length / self.s

    def metodology(self, te: TextEngine):
        te.p('Сопротивление кабельной линии от трансформатора напряжения до конечного потребителя находим по формуле:')
        te.math(r'R_{\text{КАБ}} = \rho \cdot \frac{l}{S} ,')
        te.ul('где '+te.m(r'\rho')+' – удельное сопротивление меди равное 0,0175 ' +
              te.m(r'\text{Ом} \cdot \frac{\text{мм}^2}{\text{м}};'))
        te.ul('l – длина контрольного кабеля, м; ')
        te.ul('S – сечение контрольного кабеля, мм2')
