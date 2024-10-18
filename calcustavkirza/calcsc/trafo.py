import math
import cmath


from textengines.interfaces import TextEngine
from calcustavkirza.calcsc.calc_pu import Pu


class Trafo:

    def __init__(self,
                 vn_hv_kv: float,
                 vn_lv_kv: float,
                 vk_percent: float,
                 sn_mva: float,
                 sbase_mva: float, # базовая мощность системы относительных единиц
                 std_type: str = '',
                 name: str = '',
                 ):
        self.vn_hv_kv = vn_hv_kv
        self.vn_lv_kv = vn_lv_kv
        self.vk_percent = vk_percent
        self.sn_mva = sn_mva
        self.std_type = std_type
        self.name = name
        self.sbase_mva = sbase_mva

    @property
    def z_hv(self):
        '''
        Сопротивление трансформатора приведенное в стороне ВН, Ом
        '''
        return complex(0, self.vk_percent / 100 * self.vn_hv_kv ** 2 / self.sn_mva)

    @property
    def z_lv(self):
        '''
        Сопротивление трансформатора приведенное в стороне НН, Ом
        '''
        return self.z_hv / self.vn_hv_kv ** 2 * self.vn_lv_kv ** 2

    @property
    def z_pu(self):
        return complex(0, self.vk_percent * self.sbase_mva / 100 / self.sn_mva)

    @property
    def n(self):
        return self.vn_hv_kv / self.vn_lv_kv

    @property
    def in_hv_ka(self):
        return self.sn_mva / math.sqrt(3) / self.vn_hv_kv

    @property
    def in_lv_ka(self):
        return self.sn_mva / math.sqrt(3) / self.vn_lv_kv

    def _write_part1(self, te: TextEngine):
        te.table_row('Напряжение короткого замыкания трансформатора ВН-НН, %', 'Ek', '', self.vk_percent,
                     self.vk_percent)

    def _write_z_windings_separately(self, te: TextEngine):
        ...

    def _write_in_lv(self, te: TextEngine):
        te.table_row('Номинальный ток трансформатора со стороны НН, А', 'Iт.ном.Нн',
                     'Sт.ном/(√3·Uт.ном.нн)', f'{self.sn_mva*1000}/(√3·{self.vn_lv_kv})', f'{self.in_lv_ka*1000:.0f}')

    def write(self, te: TextEngine):
        te.table_name(f'Технические данные трансформатора {self.name}')
        te.table_head('Наименование', 'Обозначение', 'Расчётная формула', 'Числовые значения в формуле', 'Величина')
        te.table_row('Тип трансформатора', self.std_type, '', '', '')
        te.table_row('Номинальная полная мощность трансформатора, МВА', 'Sт.ном', '', self.sn_mva, self.sn_mva)
        te.table_row('Номинальное напряжение обмотки ВН, кВ', 'Uт.ном.вн', '', self.vn_hv_kv, self.vn_hv_kv)
        te.table_row('Номинальное напряжение обмотки НН, кВ', 'Uт.ном.нн', '', self.vn_lv_kv, self.vn_lv_kv)
        self._write_part1(te)
        te.table_row('Сопротивление трансформатора между обмоткой ВН и обмоткой НН, приведенное к высшей стороне, '
                     'Ом', 'Xт.вн', 'Ek·Uт.ном.вн²/(100·Sт.ном)',
                     f'{self.vk_percent}·{self.vn_hv_kv}²/(100·{self.sn_mva})', f'{abs(self.z_hv):.3f}')
        te.table_row('Сопротивление трансформатора между обмоткой ВН и обмоткой НН, приведенное к низшей стороне, '
                     'Ом', 'Xт.нн', 'Ek·Uт.ном.нн²/(100·Sт.ном)',
                     f'{self.vk_percent}·{self.vn_lv_kv}²/(100·{self.sn_mva})', f'{abs(self.z_lv):.3f}')
        te.table_row('Сопротивление трансформатора между обмоткой ВН и обмоткой НН, приведенное к базовому '
                     'сопротивлению, о.е.', 'Xт*', 'Ek·Sб/(100·Sт.ном)',
                     f'{self.vk_percent}·{self.sbase_mva}/(100·{self.sn_mva})', f'{self.z_pu:.4f}')
        self._write_z_windings_separately(te)
        te.table_row('Номинальный ток трансформатора со стороны ВН, А', 'Iт.ном.вн',
                     'Sт.ном/(√3·Uт.ном.вн)', f'{self.sn_mva*1000}/(√3·{self.vn_hv_kv})', f'{self.in_hv_ka*1000:.0f}')
        self._write_in_lv(te)

class TrafoSplitW(Trafo):

    def __init__(self, vk_llv_percent: float, **kwargs):
        super().__init__(**kwargs)
        self.vk_llv_percent = vk_llv_percent

    @property
    def in_lv_ka(self):
        return self.sn_mva / math.sqrt(3) / self.vn_lv_kv

    def _write_part1(self, te: TextEngine):
        te.table_row('Напряжение короткого замыкания трансформатора ВН-НН1 (ВН-НН2), %', 'Ek', '', self.vk_percent,
                     self.vk_percent)
        te.table_row('Напряжение короткого замыкания между расщёплёнными обмотками трансформатора, %',
                     'Eк.нн1-нн2', '', self.vk_llv_percent, self.vk_llv_percent)

    def _write_z_windings_separately(self, te: TextEngine):
        te.table_row('Сопротивление трансформатора обмотки НН, приведенное к базовому сопротивлению, о.е.',
                     'Xтнн*', 'Ekнн1нн2·Sб/(100·Sт.ном)', f'{self.vk_llv_percent}·{self.sbase_mva}/(100·{self.sn_mva})',
                     f'{self.z_l:.4f}')
        te.table_row('Сопротивление трансформатора обмотки ВН, приведенное к базовому сопротивлению, о.е.',
                     'Xтвн*', 'Xт* - Xтнн*', f'{self.z_pu:.4f} - {self.z_l:.4f}', f'{self.z_h:.4f}')


    def _write_in_lv(self, te: TextEngine):
        te.table_row('Номинальный ток трансформатора со стороны НН, А', 'Iт.ном.Нн',
                     'Sт.ном/(2·√3·Uт.ном.нн)', f'{self.sn_mva * 1000}/(2·√3·{self.vn_lv_kv})', f'{self.in_lv_ka * 1000:.0f}')

    @property
    def z_h(self):
        '''
        Сопротивление одной обмотки ВН в о.е.
        '''
        return self.z_pu - self.z_l

    @property
    def z_l(self):
        '''
        Сопротивление одной обмотки НН в о.е.
        '''
        return complex(0, self.vk_llv_percent * self.sbase_mva / 100 / self.sn_mva) / 2
