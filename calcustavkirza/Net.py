import math

import pandapower as pp
from pandapower import pandapowerNet
import pandapower.shortcircuit as sc
from pandas import DataFrame
from pydantic import ConfigDict


from pandapowertools.functions import define_c
from calcustavkirza.classes import Element
from res import Res_sc_line, Res_sc_trafo, Res_sc_bus, Res_sc, Res_pf_line, Res_pf_trafo, Res_pf


class Net(Element):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    net: pandapowerNet | None = None
    modes: dict | None = None
    res_sc: Res_sc | None = None
    res_sc_bus: Res_sc_bus | None = None
    res_pf: Res_pf | None = None
    res_mci: Res_pf | None = None
    res_c: Res_pf | None = None
    index_magnetizing_current_inrush: list | None = None
    translate: dict = {'3ph': '3-фаз',
                 '2ph': '2-фаз',
                 'max': 'максимальный режим',
                 'min': 'минимальный режим'}
    index_t: list = []
    index_t3w: list = []
    index_eg: list = []
    index_eg_c: int = 0

    def create(self):
        self.te.h1('Схема замещения сети и расчёт токов нагрузки и короткого замыкания')
        self.te.p('Для выбора уставок устройств релейной защиты и автоматики производится расчет токов коротких '
                  'замыканий. Методика расчета токов КЗ позволяет определить значение периодической составляющей '
                  'полного тока КЗ для начального момента времени. Расчет производится в именованных единицах. '
                  'Сопротивления элементов схемы замещения приведены к номинальному напряжению. Расчетные режимы - '
                  'максимальный и минимальный режим системы. Расчёт произведен с применением стандарта IEC 60909.')
        # Создание расчётной сети PandaPower
        for i, item in self.net.ext_grid.sort_index().iterrows():
            self.te.h2(f'Эквивалент энергосистемы подключенный к {self.net.bus.at[item["bus"], "name"]}')
            u_bus = self.net.bus.at[item['bus'], 'vn_kv']
            i_kz_max = item['s_sc_max_mva'] / u_bus / math.sqrt(3)
            i_kz_min = item['s_sc_min_mva'] / u_bus / math.sqrt(3)
            self.te.p('Энергосистема представлена источником напряжения:')
            self.te.ul(f'в максимальном режиме ток трёхфазного короткого замыкания в точке подключения эквивалента '
                       f'энергосистемы {i_kz_max:.2f}A')
            self.te.ul(f'в максимальном режиме внутреннее сопротивление эквивалента энергосистемы определяется по '
                       f'формуле:')
            self.te.math(r'Z_C = \frac{c \cdot U}{I_{kz max} \cdot \sqrt 3} = '+
                         f'{define_c(u_bus, "max", 10)*u_bus / i_kz_max / math.sqrt(3):.4f}  Om')
            self.te.p(
                f'где {self.te.m("c")} - коэффициент коррекции напряжения. Для минимального режима в сетях до 1кВ равен '
                f'0.95 а выше 1кВ - равен 1. Для максимального режима равен 1.1')
            self.te.ul(f'в минимальном режиме ток трёхфазного короткого замыкания в точке подключения эквивалента '
                       f'энергосистемы {i_kz_min:.2f}A')
            self.te.ul(f'в минимальном режиме внутреннее сопротивление эквивалента энергосистемы определяется по '
                       f'формуле:')
            self.te.math(r'Z_C = \frac{c \cdot U^2}{I_{kz min} \cdot \sqrt 3} = '+
                         f'{define_c(u_bus, "min", 10)*u_bus / i_kz_min / math.sqrt(3):.4f}  Om')
        if not self.net.line.empty:
            self.te.h2('Расчет сопротивлений линий электропередач')
            self.te.p('Сопротивления кабельных и воздушных линий определяем по формулам:')
            self.te.math(r'R = R_{OhmPerKm} \cdot l')
            self.te.math(r'X = X_{OhmPerKm} \cdot l')
            self.te.ul(f'где {self.te.m("R_{OhmPerKm}")} - удельное активное сопротивление линии, Ом / км,')
            self.te.ul(f'{self.te.m("X_{OhmPerKm}")} - удельное реактивное сопротивление линии, Ом / км,')
            self.te.ul('l - длина линии, км.')
            self.te.table_name('Результат расчёта сопротивлений линий электропередач')
            self.te.table_head('Наименование', 'Марка', 'Длина,км', 'Удельное сопротивление,Ом/км', 'Сопротивление,Ом',
                               widths=(3,3,1,2,2))
            for i, item in self.net.line.sort_index().iterrows():
                try:
                    name1 = self.net.bus.at[item['from_bus'], 'name']
                except KeyError:
                    ...
                if not name1:
                    name1 = ''
                try:
                    name2 = self.net.bus.at[item['to_bus'], 'name']
                except KeyError:
                    ...
                if not name2:
                    name2 = ''
                name = name1 + ' - ' + name2
                r = item["r_ohm_per_km"]
                x = item["x_ohm_per_km"]
                l = item['length_km']
                self.te.table_row(name, item['std_type'], l, f'{r}+j{x}', f'{r*l:.3f}+j{x*l:.3f}')
        self.te.h2('Расчет сопротивлений трансформаторов')
        self.te.p('Полное сопротивление трансформатора определяем по формуле:')
        self.te.math(r'Z_{hl} = \frac{U_{k,hl} \cdot U_{nl}^2}{100 \cdot S_n \cdot K_T}')
        self.te.ul(f'где {self.te.m(r"U_{k,hl}")} - напряжение короткого замыкания трансформатора высокое-низкое '
                   f'напряжение (паспортные данные), %')
        self.te.ul(f'{self.te.m("S_n")} - номинальная мощность трансформатора, МВА')
        self.te.ul(f'{self.te.m("U_{nl}")} - номинальное напряжение обмотки низкого напряжения трансформатора, кВ.')
        self.te.p('Активное и реактивное сопротивления трансформатора определяем по формулам:')
        self.te.math(r'R_T = \frac{K_T \cdot P_K \cdot U_{nl}^2}{S_n^2 \cdot 1000} = \frac{U_{kr,hl} \cdot U_{nl}^2 '
                     r'\cdot K_T}{100 \cdot S_n}')
        self.te.math(r'X_T = \sqrt{Z_{hl}^2 - R_T^2}')
        self.te.ul(f'где {self.te.m("P_K")} - потери короткого замыкания (паспортные данные), Вт,')
        self.te.ul(
            f'{self.te.m(r"U_{kr,hl}")} - активная составляющая напряжения короткого замыкания. Определяется как ' +
            self.te.m(r"100 \cdot P_K / S_n") + ' %')
        self.te.ul(f'{self.te.m("K_T")} - коэффициент коррекции определяемый по формуле:')
        self.te.math(r'K_T = \frac{0.95 \cdot c}{1 + 0.6 \cdot \frac{U_{kx,hl}}{100}}')
        self.te.ul(f'где {self.te.m(r"U_{kx,hl}")} - реактивная составляющая напряжения короткого замыкания '
                   f'трансформатора. Определяется по формуле:')
        self.te.math(r'U_{kx,hl} = \sqrt{U_{k,hl}^2 - U_{kr,hl}^2}')
        if not self.net.trafo3w.empty:
            self.te.table_name('Паспортные данные для трёхобмоточных трансформаторов схемы замещения')
            self.te.table_head('Наименование', 'Марка', self.te.m(r'S_n,mva'), self.te.m(r'P_K,kW'), self.te.m(r'U_{k,hl}'),
                               self.te.m(r'U_{nl},kV'), self.te.m('P_{KZ},kW'), widths=(1,2,1,1,1,1,1))
            for i, t in self.net.trafo3w.sort_index().iterrows():
                k = max(t['sn_hv_mva'], t['sn_mv_mva']) / min(t['sn_hv_mva'], t['sn_mv_mva'])
                vk = t['vk_hv_percent'] * k
                pk = t['vkr_hv_percent'] /100 * t['sn_hv_mva']*1000
                self.te.table_row(t['name'], t['std_type'], t['sn_hv_mva'],
                                  f"{pk:.1f}",
                                  vk,
                                  t['vn_lv_kv'], t['vkr_hv_percent'] * t['sn_hv_mva'] * 10)
            self.te.table_name('Результат расчётов для трёхобмоточных трансформаторов схемы замещения приведенные к напряжению обмоток НН')
            self.te.table_head('Наименование', self.te.m(r'U_{kr,hl}'), self.te.m(r'U_{kx,hl}'), self.te.m('K_T'),
                               self.te.m('R_T'), self.te.m('X_T'), self.te.m('Z_T'))
            for i, t in self.net.trafo3w.sort_index().iterrows():
                k = max(t['sn_hv_mva'], t['sn_mv_mva']) / min(t['sn_hv_mva'], t['sn_mv_mva'])
                vk = t['vk_hv_percent'] * k
                vkr = t['vkr_hv_percent'] * k
                ukx = math.sqrt(vk**2 - vkr**2)
                kt = 0.95 * 1.1 / (1 + 0.6 * ukx / 100)
                z = vk * t['vn_lv_kv'] ** 2 / 100 / t['sn_hv_mva'] / kt
                r = kt * vkr * t['vn_lv_kv'] ** 2 / 100 / t['sn_hv_mva']
                self.te.table_row(t['name'], f'{t["vkr_hv_percent"]}', f'{ukx:.3f}',
                                  f'{kt:.3f}', f'{r:.3f}', f'{math.sqrt(z**2 - r**2):.3f}', f'{z:.3f}')
        if not self.net.trafo.empty:
            self.te.table_name('Паспортные данные для двухобмоточных трансформаторов схемы замещения')
            self.te.table_head('Наименование', 'Марка', self.te.m(r'S_n,mva'), self.te.m(r'P_K,kW'), self.te.m(r'U_{k,hl}'),
                               self.te.m(r'U_{nh},kV'), self.te.m('P_{KZ},kW'), widths=(3,4,3,3,2,2,3))
            for i, t in self.net.trafo.sort_index().iterrows():
                self.te.table_row(t['name'], t['std_type'], t['sn_mva'], f'{t["vkr_percent"] /100 * t["sn_mva"]*1000:.3f}',
                                  t['vk_percent'],
                                  t['vn_hv_kv'], f"{t['vkr_percent'] * t['sn_mva'] * 10:.3f}")
            self.te.table_name('Результат расчётов для двухобмоточных трансформаторов схемы замещения приведенные к '
                               'напряжению обмотки ВН')
            self.te.table_head('Наименование', self.te.m(r'U_{kr,hl}'), self.te.m(r'U_{kx,hl}'), self.te.m('K_T'),
                               self.te.m('R_T'), self.te.m('X_T'), self.te.m('Z_T'))
            for i, t in self.net.trafo.sort_index().iterrows():
                ukx = math.sqrt(t['vk_percent'] ** 2 - t['vkr_percent'] ** 2)
                kt = 0.95 * 1.1 / (1 + 0.6 * ukx / 100)
                z = t['vk_percent'] * t['vn_hv_kv'] ** 2 / 100 / t['sn_mva'] / kt
                r = kt * t['vkr_percent'] * t['vn_hv_kv'] ** 2 / 100 / t['sn_mva']
                self.te.table_row(t['name'], f'{t["vkr_percent"]}', f'{ukx:.3f}',
                                  f'{kt:.3f}', f'{r:.3f}', f'{math.sqrt(z ** 2 - r ** 2):.3f}', f'{z:.3f}')
        if not self.net.impedance.empty:
            self.te.h2('Сопротивления токоограничивающих реакторов')
            self.te.p('Реактивное сопростивление токоограничевающего реактора задано в паспортных данных. Активное '
                       'сопротивление рассичтано по значению потерь активной мощности в реакторе')
            self.te.table_name('Значения сопротивлений токоограничивающих реакторов')
            self.te.table_head('Место подключения', 'Марка', 'r,Ом', 'x,Ом',
                               widths=(3,2,1,2))
            for i, item in self.net.impedance.sort_index().iterrows():
                name_from = self.net.bus.loc[item['from_bus'], 'name'].ljust(28)
                name_to = self.net.bus.loc[item['to_bus'], 'name'].rjust(28)
                u2 = self.net.bus.loc[item['from_bus'], 'vn_kv'] ** 2
                zb = u2 / item['sn_mva']
                rpu = item['rtf_pu']
                xpu = item['xtf_pu']
                self.te.table_row(f'{name_from} - {name_to}', item['name'], f'{rpu * zb:.3f}', f'{xpu * zb:.3f}')
        if not self.net.load.empty:
            raise NotImplementedError


    # def get_sc_by_mode(self, index_bus: int, mode_name: str) -> float:
    #     return self.res_sc.res[mode_name].ikss_ka[index_bus] * 1000
    #
    # def get_sc_min(self, index_bus: list[int], modes: list[str] = None) -> float:
    #     '''
    #     Возвращает минимальный ток короткого замыкания для шины из указанных режимов
    #     :param index_bus: список индексов шин среди которых ищем минимальный ток
    #     :param modes: список режимов среди которых ищем ток
    #     :return: кортеж из тока КЗ в амперах, имени режима, индекса шины с минимальным током КЗ
    #     '''
    #     first = True
    #     for mode_name, res in self.res_sc.res.items():
    #         if not modes or mode_name in modes:
    #             for index in index_bus:
    #                 if first:
    #                     i_kz_min = res.ikss_ka[index]
    #                     mode_min = mode_name
    #                     bus_index = index
    #                     first = False
    #                 else:
    #                     if i_kz_min >= res.ikss_ka[index]:
    #                         i_kz_min = res.ikss_ka[index]
    #                         mode_min = mode_name
    #                         bus_index = index
    #     return i_kz_min * 1000, mode_min, bus_index
    #
    # def get_sc_max(self, index_bus: list[int], modes: list[str] = None) -> float:
    #     '''
    #     Возвращает максимальный ток короткого замыкания для шины из указанных режимов
    #     :param index_bus: список индексов шин среди которых ищем максимальный ток
    #     :param modes: список режимов среди которых ищем ток
    #     :return: кортеж из тока КЗ в амперах, имени режима, индекса шины с максимальным током КЗ
    #     '''
    #     first = True
    #     for mode_name, res in self.res_sc.res.items():
    #         if not modes or mode_name in modes:
    #             for index in index_bus:
    #                 if first:
    #                     i_kz_max = res.ikss_ka[index]
    #                     mode_max = mode_name
    #                     bus_index = index
    #                     first = False
    #                 else:
    #                     if i_kz_max <= res.ikss_ka[index]:
    #                         i_kz_max = res.ikss_ka[index]
    #                         mode_max = mode_name
    #                         bus_index = index
    #     return i_kz_max * 1000, mode_max, bus_index
    #
    # def get_sc_3ph_min(self, index_bus: int) -> float:
    #     return min([res.ikss_ka[index_bus] for mode_name, res in self.res_sc.res.items() if '3ph' in mode_name]) * 1000
    #
    # def create_mode_magnetizing_current_inrush(self, k: float):
    #     for i, l in self.net.load.iterrows():
    #         l.in_service = False
    #     for i, tr in self.net.trafo.iterrows():
    #         self.index_magnetizing_current_inrush.append(pp.create_load(self.net, tr.hv_bus, p_mw=tr.sn_mva * k))
    #     for i, tr in self.net.trafo3w.iterrows():
    #         self.index_magnetizing_current_inrush.append(pp.create_load(self.net, tr.hv_bus, p_mw=tr.sn_hv_mva * k))
    #
    # def delete_mode_magnetizing_current_inrush(self):
    #     pp.toolbox.drop_elements(self.net, element_type='load', element_index=self.index_magnetizing_current_inrush)
    #     for i, l in self.net.load.iterrows():
    #         l.in_service = True
    #
    # def create_mode_calc_c(self, bus_index: int):
    #     for i, tr in self.net.trafo.iterrows():
    #         if tr.in_service:
    #             self.index_t.append(i)
    #             self.net.trafo.loc[i, 'in_service'] = False
    #     for i, tr in self.net.trafo3w.iterrows():
    #         if tr.in_service:
    #             self.index_t3w.append(i)
    #             self.net.trafo3w.loc[i, 'in_service'] = False
    #     for i, eg in self.net.ext_grid.iterrows():
    #         if eg.in_service:
    #             self.index_eg.append(i)
    #             self.net.ext_grid.loc[i, 'in_service'] = False
    #     self.index_eg_c = pp.create_ext_grid(self.net, bus_index)
    #
    # def delete_mode_calc_c(self):
    #     pp.toolbox.drop_elements(self.net, 'ext_grid', self.index_eg_c)
    #     self.net.trafo.loc[self.index_t, 'in_service'] = True
    #     self.net.trafo3w.loc[self.index_t3w, 'in_service'] = True
    #     self.net.ext_grid.loc[self.index_eg, 'in_service'] = True
    #     self.index_t = []
    #     self.index_t3w = []
    #     self.index_eg = []
    #
    # def calc_pf_mode(self, mode_name):
    #     tolerance = 1e-8
    #     self.make_mode(mode_name)
    #     for i in range(15):
    #         try:
    #             pp.runpp(self.net, tolerance_mva=tolerance, switch_rx_ratio=1)
    #             print(f'PowerFlow calculated witn tolerance {tolerance}')
    #             break
    #         except pp.powerflow.LoadflowNotConverged:
    #             tolerance *= 10
    #     else:
    #         print(f'PowerFlow not calculated with tolerance {tolerance}')
    #
    # def calc_pf_modes(self):
    #     for mode_name, mode in self.modes.items():
    #         self.calc_pf_mode(mode_name)
    #         self.res_pf.line.update(f'{mode_name}', self.net.res_line)
    #         self.res_pf.trafo.update(f'{mode_name}', self.net.res_trafo)
    #         self.res_pf.switch.update(f'{mode_name}', self.net.res_switch)
    #
    # def calc_mci_modes(self):
    #     self.create_mode_magnetizing_current_inrush(4)
    #     for mode_name, mode in self.modes.items():
    #         self.calc_pf_mode(mode_name)
    #         self.res_mci.line.update(f'{mode_name}', self.net.res_line)
    #         self.res_mci.trafo.update(f'{mode_name}', self.net.res_trafo)
    #         self.res_mci.switch.update(f'{mode_name}', self.net.res_switch)
    #     self.delete_mode_magnetizing_current_inrush()
    #
    # def get_pf_max(self, index_line: int):
    #     return max([max((res.i_from_ka[index_line], res.i_to_ka[index_line])) for mode_name, res in self.res_pf.items()]) * 1000
    #
    # def get_pf_min(self, index_line: int):
    #     return min([min((res.i_from_ka[index_line], res.i_to_ka[index_line])) for mode_name, res in self.res_pf.items()]) * 1000
    #
    # def get_posl_prot_imax(self, code_name: str):
    #     isz = 0
    #     t = None
    #     name = None
    #     for pris in self.select_setting:
    #         for prot in pris['protection']:
    #             current_code_name = prot.get('code_name', False)
    #             if current_code_name == code_name:
    #                 if prot['isz'] > isz:
    #                     isz = prot['isz']
    #                     t = prot['t']
    #                     name = f'{pris["name_object"]} {pris["name"]} МТЗ {prot.get("suffix", "")}'
    #     return isz, name
    #
    # def get_posl_protect_imax(self, protection: dict):
    #     code_name = protection['posl']
    #     u_current_bus: float = self.net.bus.vn_kv[protection['bus']]
    #     isz = 0
    #     name = None
    #     for pris in self.select_setting:
    #         for prot in pris['protection']:
    #             current_code_name = prot.get('code_name', False)
    #             if current_code_name == code_name:
    #                 if prot['isz'] > isz:
    #                     isz = prot['isz']
    #                     name = f'{pris["name_object"]} {pris["name"]} МТЗ {prot.get("suffix", "")}'
    #                     u_bus: float = self.net.bus.vn_kv[prot['bus']]
    #     return isz * u_bus / u_current_bus, name
    #
    # def get_posl_prot_tmax(self, protection: dict):
    #     code_name = protection['posl']
    #     t = 0
    #     name = None
    #     for pris in self.select_setting:
    #         for prot in pris['protection']:
    #             current_code_name = prot.get('code_name', False)
    #             if current_code_name == code_name:
    #                 if prot['t'] > t:
    #                     t = prot['t']
    #                     name = f'{pris["name_object"]} {pris["name"]} МТЗ {prot.get("suffix", "")}'
    #     return t, name
    #
    # def get_sc_min_line(self, et: str, index: int, side: str):
    #     i_kz_min = 1000000
    #     for mode in self.res_sc.res:
    #         # if self.net.res_sc[mode].at[]
    #         i_kz_min = self.net.res_sc.res[mode]