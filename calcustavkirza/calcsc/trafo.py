import math
import cmath


from textengines.interfaces import TextEngine
from calcustavkirza.calcsc.calc_pu import Pu
from calcustavkirza.electro_store import TrafoStore

class ClassTrafoStore:

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

class ClassTrafoSplitWStore(ClassTrafoStore):

    def __init__(self, vk_llv_percent: float, **kwargs):
        super().__init__(**kwargs)
        self.vk_llv_percent = vk_llv_percent

class Trafo:

    def __init__(self, te: TextEngine, store: TrafoStore, pu: Pu, *args, **kwargs):
        self.te = te
        self.store = store
        self.pu = pu

    @property
    def z_hv(self):
        '''
        Сопротивление трансформатора приведенное в стороне ВН, Ом
        '''
        return complex(0, self.store.vk_percent / 100 * self.store.vn_hv_kv ** 2 / self.store.sn_mva)

    @property
    def z_lv(self):
        '''
        Сопротивление трансформатора приведенное в стороне НН, Ом
        '''
        return self.z_hv / self.store.vn_hv_kv ** 2 * self.store.vn_lv_kv ** 2

    @property
    def z_pu(self):
        return complex(0, self.store.vk_percent * self.pu.s_mva / 100 / self.store.sn_mva)

    @property
    def n(self):
        return self.store.vn_hv_kv / self.store.vn_lv_kv

    @property
    def in_hv_ka(self):
        return self.store.sn_mva / math.sqrt(3) / self.store.vn_hv_kv

    @property
    def in_lv_ka(self):
        return self.store.sn_mva / math.sqrt(3) / self.store.vn_lv_kv

    def _write_part1(self):
        self.te.table_row('Напряжение короткого замыкания трансформатора ВН-НН, %', 'Ek', '', self.store.vk_percent,
                     self.store.vk_percent)

    def _write_z_windings_separately(self):
        ...

    def _write_in_lv(self):
        self.te.table_row('Номинальный ток трансформатора со стороны НН, А', 'Iт.ном.Нн',
                     'Sт.ном/(√3·Uт.ном.нн)', f'{self.store.sn_mva*1000}/(√3·{self.store.vn_lv_kv})',
                          f'{self.in_lv_ka*1000:.0f}')

    def write_source_data(self):
        self.te.table_name(f'Технические данные трансформатора')
        self.te.table_head('Наименование', 'Обозначение', 'Расчётная формула', 'Числовые значения в формуле', 'Величина')
        self.te.table_row('Тип трансформатора', self.store.std_type, '', '', '')
        self.te.table_row('Номинальная полная мощность трансформатора, МВА', 'Sт.ном', '', self.store.sn_mva,
                     self.store.sn_mva)
        self.te.table_row('Номинальное напряжение обмотки ВН, кВ', 'Uт.ном.вн', '', self.store.vn_hv_kv,
                     self.store.vn_hv_kv)
        self.te.table_row('Номинальное напряжение обмотки НН, кВ', 'Uт.ном.нн', '', self.store.vn_lv_kv,
                     self.store.vn_lv_kv)
        self._write_part1()

    def write_calculated_data(self):
        self.te.table_row('Сопротивление трансформатора между обмоткой ВН и обмоткой НН, приведенное к высшей стороне, '
                     'Ом', 'Xт.вн', 'Ek·Uт.ном.вн²/(100·Sт.ном)',
                     f'{self.store.vk_percent}·{self.store.vn_hv_kv}²/(100·{self.store.sn_mva})', f'{abs(self.z_hv):.3f}')
        self.te.table_row('Сопротивление трансформатора между обмоткой ВН и обмоткой НН, приведенное к низшей стороне, '
                     'Ом', 'Xт.нн', 'Ek·Uт.ном.нн²/(100·Sт.ном)',
                     f'{self.store.vk_percent}·{self.store.vn_lv_kv}²/(100·{self.store.sn_mva})', f'{abs(self.z_lv):.3f}')
        self.te.table_row('Сопротивление трансформатора между обмоткой ВН и обмоткой НН, приведенное к базовому '
                     'сопротивлению, о.е.', 'Xт*', 'Ek·Sб/(100·Sт.ном)',
                     f'{self.store.vk_percent}·{self.pu.s_mva}/(100·{self.store.sn_mva})', f'{self.z_pu:.4f}')
        self._wriself.te_z_windings_separaself.tely()
        self.te.table_row('Номинальный ток трансформатора со стороны ВН, А', 'Iт.ном.вн', 'Sт.ном/(√3·Uт.ном.вн)',
                     f'{self.store.sn_mva*1000}/(√3·{self.store.vn_hv_kv})', f'{self.store.in_hv_ka*1000:.0f}')
        self._write_in_lv()

class TrafoSplitW(Trafo):

    def __init__(self, te: TextEngine, store, pu: Pu, *args, **kwargs):
        self.te = te
        self.store = store
        self.pu = pu

    @property
    def in_lv_ka(self):
        return self.store.sn_mva / math.sqrt(3) / self.store.vn_lv_kv

    def _write_part1(self):
        self.te.table_row('Напряжение короткого замыкания трансформатора ВН-НН1 (ВН-НН2), %', 'Ek', '',
                     self.store.vk_percent, self.store.vk_percent)
        self.te.table_row('Напряжение короткого замыкания между расщёплёнными обмотками трансформатора, %',
                     'Eк.нн1-нн2', '', self.store.vk_llv_percent, self.store.vk_llv_percent)

    def _write_z_windings_separately(self):
        self.te.table_row('Сопротивление трансформатора обмотки НН, приведенное к базовому сопротивлению, о.е.',
                     'Xтнн*', 'Ekнн1нн2·Sб/(100·Sт.ном)', f'{self.store.vk_llv_percent}·{self.pu.s_mva}/'
                                                          f'(100·{self.store.sn_mva})', f'{self.z_l:.4f}')
        self.te.table_row('Сопротивление трансформатора обмотки ВН, приведенное к базовому сопротивлению, о.е.',
                     'Xтвн*', 'Xт* - Xтнн*', f'{self.z_pu:.4f} - {self.z_l:.4f}', f'{self.z_h:.4f}')


    def _write_in_lv(self):
        self.te.table_row('Номинальный ток трансформатора со стороны НН, А', 'Iт.ном.Нн',
                     'Sт.ном/(2·√3·Uт.ном.нн)', f'{self.store.sn_mva * 1000}/(2·√3·{self.store.vn_lv_kv})',
                          f'{self.store.in_lv_ka * 1000:.0f}')

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
        return complex(0, self.store.vk_llv_percent * self.pu.s_mva / 100 / self.store.sn_mva) / 2
