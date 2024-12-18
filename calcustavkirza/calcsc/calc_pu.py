import dataclasses
import math


from textengines.interfaces import TextEngine


from calcustavkirza.classes import Element

@dataclasses.dataclass
class Pu:
    '''
    Операции по переводу в и из относительных единиц
    '''
    v_kv: float # базовое напряжение
    s_mva: float = 1. # базовая мощность

    @property
    def i_ka(self) -> float:
        '''
        Базовый ток
        :return:
        '''
        return self.s_mva / self.v_kv / math.sqrt(3)

    @property
    def z_ohm(self) -> float:
        '''
        Базовое сопротивление
        :return:
        '''
        return self.v_kv ** 2 / self.s_mva

    @property
    def vph_kv(self):
        return self.v_kv / math.sqrt(3)

    def __truediv__(self, other):
        if not isinstance(other, (float, int)):
            raise ArithmeticError("Правый операнд должен быть типом int или float")
        return Pu(s_mva=self.s_mva, v_kv=self.v_kv / other)

    def write(self, te: TextEngine):
        te.table_name(f'Базисные значения для выполнения расчётов в относительных единицах при напряжении '
                      f'{self.v_kv:.2f}кВ')
        te.table_head('Наименование', 'Обозначение', 'Расчётная формула', 'Числовые значения в формуле', 'Величина')
        te.table_row('Полная мощность базовая, МВА', 'Sб', '', self.s_mva, self.s_mva)
        te.table_row('Ток базовый, кА', 'Iб', '', f'{self.i_ka:.3f}', f'{self.i_ka:.3f}')
        te.table_row('Сопротивление базовое, Ом', 'Zб', '', f'{self.z_ohm:.3f}', f'{self.z_ohm:.3f}')
