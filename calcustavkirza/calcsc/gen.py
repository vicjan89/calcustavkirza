import math


from textengines.interfaces import TextEngine


from calcustavkirza.classes import Element
from calcustavkirza.calcsc.calc_pu import Pu


class Gen:

    def __init__(self, te: TextEngine, store, pu: Pu):
        self.te = te
        self.store = store
        self.pu = pu

    @property
    def sn_mva(self):
        if self.store.sn_mva:
            return self.store.sn_mva
        return self.store.p_mw / self.store.cos_phi

    @property
    def p_mw(self):
        if self.store.p_mw:
            return self.store.p_mw
        return self.store.sn_mva * self.store.cos_phi

    @property
    def cos_phi(self):
        if self.store.cos_phi:
            return self.store.cos_phi
        return self.store.p_mw / self.store.sn_mva

    @property
    def sin_phi(self):
        return math.sin(math.acos(self.cos_phi))

    @property
    def zbase(self):
        return self.store.vn_kv ** 2 / self.sn_mva

    @property
    def x1_ohm(self):
        return self.store.xdss_pu * self.zbase

    @property
    def x1_pu(self):
        return self.store.xdss_pu * self.pu.s_mva / self.sn_mva

    @property
    def r1_ohm(self):
        return self.x1_ohm / 100 / math.pi / self.store.t3

    @property
    def r1_pu(self):
        return self.r1_ohm / self.pu.z_ohm

    @property
    def z1_pu(self):
        '''
        Полное сверхпереходное сопротивление в относительных единицах
        '''
        return complex(self.r1_pu, self.x1_pu)

    @property
    def in_ka(self):
        return self.sn_mva / self.store.vn_kv / math.sqrt(3)

    @property
    def vn_ph_kv(self):
        return self.store.vn_kv / math.sqrt(3)

    @property
    def ess(self):
        return math.sqrt((self.vn_ph_kv + self.in_ka * self.x1_ohm * self.sin_phi) ** 2 +
                         (self.in_ka * self.x1_ohm * self.cos_phi) ** 2)

    @property
    def ess_pu(self):
        return self.ess / self.pu.v_kv * math.sqrt(3)

    def write_source_data(self):
        self.te.table_name(f'Технические данные генератора')
        self.te.table_head('Наименование', 'Обозначение', 'Расчётная формула', 'Числовые значения в формуле', 'Величина')
        self.te.table_row('Тип генератора', self.store.std_type, '', '', '')
        self.te.table_row('Номинальное линейное напряжение генератора', 'Uг.ном', '', self.store.vn_kv, self.store.vn_kv)
        self.te.table_row('Коэффициент мощности', 'cosфном', '', f'{self.cos_phi:.2f}', f'{self.cos_phi:.2f}')
        self.te.table_row('Номинальная активная мощность генератора МВт', 'Pг.ном', '', f'{self.p_mw:.0f}',
                     f'{self.p_mw:.0f}')
        self.te.table_row('Номинальная полная мощность генератора, МВА', 'Sг.ном', '', f'{self.sn_mva:.3f}',
                     f'{self.sn_mva:.3f}')
        self.te.table_row('Сверхпереходное сопротивление генератора по продольной оси приведенное к номинальному '
                     'сопротивлению, о.е.', 'Xd"', '', self.store.xdss_pu, self.store.xdss_pu)
        self.te.table_row('Постоянная времени апериодической составляющей при трёхфазном коротком замыкании, сек',
                     'Ta3', '', self.store.t3, self.store.t3)
        self.te.table_row('Постоянная времени апериодической составляющей при однофазном коротком замыкании, сек',
                     'Ta1', '', self.store.t1, self.store.t1)

    def write_calculated_data(self):
        self.te.table_row('Номинальный первичный ток, соответствующий номинальной мощности генератора, кА', 'Iг.ном',
                     'Sг.ном/(√3·Uг.ном)', f'{self.sn_mva}/(√3·{self.store.vn_kv})', f'{self.in_ka:.3f}')
        self.te.table_row('Базисное сопротивление генератора (первичное), Ом', 'Zбаз', 'Uг.ном²/Sг.ном',
                     f'{self.store.vn_kv}²/{self.sn_mva}', f'{self.zbase:.3f}')
        self.te.table_row('Сверхпереходная ЭДС генератора по поперечной оси при нормальных условиях, кВ', 'Eф"',
                     '√(Uф + Iн·xd"·sinф)² + (Iн·xd"·cosф)²',
                     f'√({self.vn_ph_kv:.1f} + {self.in_ka:.3f}·{self.x1_ohm:.3f}·{self.sin_phi:.2f})² + '
                     f'({self.in_ka:.3f}·{self.x1_ohm:.3f}·{self.cos_phi:.2f})²', f'{self.ess:.3f}')
        self.te.table_row('Сверхпереходная ЭДС генератора по поперечной оси приведенная к базисному напряжению, о.е.',
                     'Eф"*', 'Eф"/(Uб·√3)', f'{self.ess:.3f}/({self.pu.v_kv}/√3)', f'{self.ess_pu:.3f}')
        self.te.table_row('Сверхпереходное сопротивление генератора приведенное к базисному сопротивлению, о.е.',
                     'xd"*', 'xd"·Sб/Sн', f'{self.store.xdss_pu:.3f}·{self.pu.s_mva}/{self.sn_mva:.3f}', f'{self.z1_pu:.4f}')

    def write_sc(self):
        self.te.table_name(f'Рассчёт токов трёхфазного короткого замыкания от генератора {self.store.name}')
        self.te.table_head('Наименование', 'Обозначение', 'Расчётная формула', 'Числовые значения в формуле', 'Величина')
        self.te.table_row('Сверхпереходное сопротивление генератора по продольной оси приведенное к базисному '
                     'сопротивлению, о.е.', 'Xd"', '', f'{xdss_b_pu:.3f}', f'{xdss_b_pu:.3f}')
        isc_pu = ess_b_pu/xdss_b_pu
        self.te.table_row('Ток короткого замыкания на выводах генератора, о.е.', 'Iкз*', 'Eф"* / xd"*',
                     f'{ess_b_pu:.3f} / {xdss_b_pu:.3f}', f'{isc_pu:.3f}')
        isc = isc_pu * pu.i_ka
        self.te.table_row('Ток короткого замыкания на выводах генератора, кА', 'Iкз', 'Iкз*·Iб',
                     f'{isc_pu:.3f} · {pu.i_ka:.3f}', f'{isc:.3f}')

class ClassGenStore:

    def __init__(self,
                 xdss_pu: float, # сверхпереходное индуктивное сопротивление продольное в относительных единицах
                 t3: float, # постоянная времени при трёхфазном КЗ в с
                 t1: float, # постоянная времени при однофазном КЗ в с
                 vn_kv: float,  # номинальное напряжение
                 pu: Pu,
                 sn_mva: float | None = None, # полная мощность в МВА
                 p_mw: float | None = None, # активная мощность в МВт
                 cos_phi: float | None = None, # номинальный коэффициент мощности
                 name: str = '',
                 std_type: str = '',
                 ):
        self.xdss_pu = xdss_pu
        self.t3 = t3
        self.t1 = t1
        self.vn_kv = vn_kv
        self._sn_mva = sn_mva
        self._p_mw = p_mw
        self._cos_phi = cos_phi
        self.name = name
        self.std_type = std_type
        self._in_ka = None
        self.pu = pu
