import math

import pandapower as pp
from pandapower import pandapowerNet
import pandapower.shortcircuit as sc
from pandapowertools import net
from pandas import DataFrame
from pydantic import ConfigDict
from textengines.interfaces import TextEngine


from pandapowertools.functions import define_c
from calcustavkirza.classes import Element
from res import Res_sc_line, Res_sc_trafo, Res_sc_bus, Res_sc, Res_pf_line, Res_pf_trafo, Res_pf


class Net(Element):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    net: pandapowerNet | None = None

    def create(self, te: TextEngine, line_c: bool = False):
        te.h1('Схема замещения сети')
        te.p('Для выбора уставок устройств релейной защиты и автоматики производится расчет токов коротких '
                  'замыканий. Методика расчета токов КЗ позволяет определить значение периодической составляющей '
                  'полного тока КЗ для начального момента времени. Расчет производится в именованных единицах. '
                  'Сопротивления элементов схемы замещения приведены к номинальному напряжению. Расчетные режимы - '
                  'максимальный и минимальный режим системы. Расчёт произведен с применением стандарта IEC 60909.')
        for i, item in self.net.ext_grid.sort_index().iterrows():
            if item['bus'] in self.net.bus_geodata.index:
                te.h2(f'Эквивалент энергосистемы подключенный к {self.net.bus.at[item["bus"], "name"]}, {item["name"]}')
                u_bus = self.net.bus.at[item['bus'], 'vn_kv']
                i_kz_max = item['s_sc_max_mva'] / u_bus / math.sqrt(3)
                i_kz_min = item['s_sc_min_mva'] / u_bus / math.sqrt(3)
                te.p('Энергосистема представлена источником напряжения:')
                te.ul(f'в максимальном режиме ток трёхфазного короткого замыкания в точке подключения эквивалента '
                           f'энергосистемы {i_kz_max:.2f}кA')
                te.ul(f'в максимальном режиме внутреннее сопротивление эквивалента энергосистемы определяется по '
                           f'формуле:')
                te.math(r'Z_C = \frac{c \cdot U}{I_{kz max} \cdot \sqrt 3} = '+
                             f'{define_c(u_bus, "max", 10)*u_bus / i_kz_max / math.sqrt(3):.4f}  Om')
                te.p(
                    f'где {te.m("c")} - коэффициент коррекции напряжения. Для минимального режима в сетях до 1кВ равен '
                    f'0.95 а выше 1кВ - равен 1. Для максимального режима равен 1.1')
                te.ul(f'в минимальном режиме ток трёхфазного короткого замыкания в точке подключения эквивалента '
                           f'энергосистемы {i_kz_min:.2f}кA')
                te.ul(f'в минимальном режиме внутреннее сопротивление эквивалента энергосистемы определяется по '
                           f'формуле:')
                te.math(r'Z_C = \frac{c \cdot U}{I_{kz min} \cdot \sqrt 3} = '+
                             f'{define_c(u_bus, "min", 10)*u_bus / i_kz_min / math.sqrt(3):.4f}  Om')

        if not self.net.line.empty:
            rows = []
            for i, item in self.net.line.sort_values(by='from_bus').iterrows():
                if item['from_bus'] in self.net.bus_geodata.index and item['to_bus'] in self.net.bus_geodata.index:
                    if item['std_type']:
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
                        parallel = item['parallel']
                        count = f' {parallel}шт.' if parallel > 1 else ''
                        rows.append((name, f'{item['std_type']}{count}', l, f'{r}+j{x}', f'{r*l/parallel:.3f}+j{x*l/parallel:.3f}'))
            if rows:
                te.h2('Расчет сопротивлений линий электропередач')
                te.p('Сопротивления кабельных и воздушных линий определяем по формулам:')
                te.math(r'R = R_{OhmPerKm} \cdot l')
                te.math(r'X = X_{OhmPerKm} \cdot l')
                te.ul(f'где {te.m("R_{OhmPerKm}")} - удельное активное сопротивление линии, Ом / км,')
                te.ul(f'{te.m("X_{OhmPerKm}")} - удельное реактивное сопротивление линии, Ом / км,')
                te.ul('l - длина линии, км.')
                te.table_name('Результат расчёта сопротивлений линий электропередач')
                te.table_head('Наименование', 'Марка', 'Длина,км', 'Удельное сопротивление,Ом/км', 'Сопротивление,Ом',
                              widths=(3, 3, 1, 2, 2))
                for row in rows:
                    te.table_row(*row)
                if line_c:
                    te.table_name('Паспортные данные по ёмкости линий электропередач')
                    te.table_head('Наименование', 'Марка', 'Длина,км', 'Удельная ёмкость,нФ/км', 'Ёмкость,нФ',
                                  widths=(3, 3, 1, 2, 2))
                    for i, item in self.net.line.iterrows():
                        from_bus = item['from_bus']
                        to_bus = item['to_bus']
                        if from_bus in self.net.bus_geodata.index and to_bus in self.net.bus_geodata.index:
                            if item['std_type']:
                                name1 = self.net.bus.at[from_bus, 'name']
                                name2 = self.net.bus.at[to_bus, 'name']
                                name = name1 + ' - ' + name2
                                c = item["c_nf_per_km"]
                                l = item['length_km']
                                te.table_row(name, item['std_type'], l, c, f'{l * c:.2f}')
        rows3w_pasp = []
        rows3w_calc = []
        if not self.net.trafo3w.empty:
            for i, t in self.net.trafo3w.sort_index().iterrows():
                if all([t[side] in self.net.bus_geodata.index for side in ('hv_bus', 'mv_bus', 'lv_bus')]):
                    k = max(t['sn_hv_mva'], t['sn_mv_mva']) / min(t['sn_hv_mva'], t['sn_mv_mva'])
                    vk_hl = t['vk_hv_percent'] * k
                    pk = t['vkr_hv_percent'] /100 * t['sn_hv_mva']*1000
                    std_type = t['std_type'] if t['std_type'] else ''
                    rows3w_pasp.append((t['name'], std_type, t['sn_hv_mva'],
                                      f"{pk:.1f}",
                                      vk_hl,
                                      t['vn_lv_kv'], t['vkr_hv_percent'] * t['sn_hv_mva'] * 10))
            for i, t in self.net.trafo3w.sort_index().iterrows():
                if all([t[side] in self.net.bus_geodata.index for side in ('hv_bus', 'mv_bus', 'lv_bus')]):
                    k = max(t['sn_hv_mva'], t['sn_mv_mva']) / min(t['sn_hv_mva'], t['sn_mv_mva'])
                    vk_hl = t['vk_hv_percent'] * k
                    vkr = t['vkr_hv_percent'] * k
                    vk_ml = t['vk_mv_percent'] * k
                    vk_hm = t['vk_lv_percent'] * k
                    vt1 = (vk_hl + vk_hm - vk_ml) / 2
                    vt2 = (vk_ml + vk_hm - vk_hl) / 2
                    vt3 = (vk_ml + vk_hl - vk_hm) / 2
                    vt0 = vt1 + vt2 * vt3 / (vt2 + vt3)
                    ukx = math.sqrt(vk_hl**2 - vkr**2)
                    kt = 0.95 * 1.1 / (1 + 0.6 * ukx / 100)
                    z = vk_hl * t['vn_hv_kv'] ** 2 / 100 / t['sn_hv_mva'] / kt
                    z0 = vt0 * t['vn_hv_kv'] ** 2 / 100 / t['sn_hv_mva'] / kt
                    r = kt * vkr * t['vn_hv_kv'] ** 2 / 100 / t['sn_hv_mva']
                    rows3w_calc.append((t['name'], f'{t["vkr_hv_percent"]}', f'{ukx:.3f}',
                                      f'{kt:.3f}', f'{r:.3f}', f'{math.sqrt(z**2 - r**2):.3f}', f'{z:.3f}', f'{z0:.3f}'))
        rowsw_pasp = []
        rowsw_calc = []
        if not self.net.trafo.empty:
            for i, t in self.net.trafo.sort_index().iterrows():
                if all([t[side] in self.net.bus_geodata.index for side in ('hv_bus', 'lv_bus')]):
                    rowsw_pasp.append((t['name'], t['std_type'], t['sn_mva'], f'{t["vkr_percent"] /100 * t["sn_mva"]*1000:.3f}',
                                      t['vk_percent'],
                                      t['vn_hv_kv'], f"{t['vkr_percent'] * t['sn_mva'] * 10:.3f}"))
            for i, t in self.net.trafo.sort_index().iterrows():
                if all([t[side] in self.net.bus_geodata.index for side in ('hv_bus', 'lv_bus')]):
                    ukx = math.sqrt(t['vk_percent'] ** 2 - t['vkr_percent'] ** 2)
                    kt = 0.95 * 1.1 / (1 + 0.6 * ukx / 100)
                    z = t['vk_percent'] * t['vn_hv_kv'] ** 2 / 100 / t['sn_mva'] / kt
                    r = kt * t['vkr_percent'] * t['vn_hv_kv'] ** 2 / 100 / t['sn_mva']
                    rowsw_calc.append((t['name'], f'{t["vkr_percent"]}', f'{ukx:.3f}',
                                      f'{kt:.3f}', f'{r:.3f}', f'{math.sqrt(z ** 2 - r ** 2):.3f}', f'{z:.3f}'))
        if rowsw_pasp or rows3w_pasp:
            te.h2('Расчет сопротивлений трансформаторов')
            te.p('Полное сопротивление трансформатора определяем по формуле:')
            te.math(r'Z_{hl} = \frac{U_{k,hl} \cdot U_{nl}^2}{100 \cdot S_n \cdot K_T}')
            te.ul(f'где {te.m(r"U_{k,hl}")} - напряжение короткого замыкания трансформатора высокое-низкое '
                  f'напряжение (паспортные данные), %')
            te.ul(f'{te.m("S_n")} - номинальная мощность трансформатора, МВА')
            te.ul(f'{te.m("U_{nl}")} - номинальное напряжение обмотки низкого напряжения трансформатора, кВ.')
            te.p('Активное и реактивное сопротивления трансформатора определяем по формулам:')
            te.math(r'R_T = \frac{K_T \cdot P_K \cdot U_{nl}^2}{S_n^2 \cdot 1000} = \frac{U_{kr,hl} \cdot U_{nl}^2 '
                    r'\cdot K_T}{100 \cdot S_n}')
            te.math(r'X_T = \sqrt{Z_{hl}^2 - R_T^2}')
            te.ul(f'где {te.m("P_K")} - потери короткого замыкания (паспортные данные), Вт,')
            te.ul(
                f'{te.m(r"U_{kr,hl}")} - активная составляющая напряжения короткого замыкания. Определяется как ' +
                te.m(r"100 \cdot P_K / S_n") + ' %')
            te.ul(f'{te.m("K_T")} - коэффициент коррекции определяемый по формуле:')
            te.math(r'K_T = \frac{0.95 \cdot c}{1 + 0.6 \cdot \frac{U_{kx,hl}}{100}}')
            te.ul(f'где {te.m(r"U_{kx,hl}")} - реактивная составляющая напряжения короткого замыкания '
                  f'трансформатора. Определяется по формуле:')
            te.math(r'U_{kx,hl} = \sqrt{U_{k,hl}^2 - U_{kr,hl}^2}')
            if rows3w_pasp:
                te.table_name('Паспортные данные для трёхобмоточных трансформаторов схемы замещения')
                te.table_head('Наименование', 'Марка', te.m(r'S_n,mva'), te.m(r'P_K,kW'), te.m(r'U_{k,hl}'),
                              te.m(r'U_{nl},kV'), te.m('P_{KZ},kW'), widths=(1, 2, 1, 1, 1, 1, 1))
                for row in rows3w_pasp:
                    te.table_row(*row)
                te.table_name('Результат расчётов для трёхобмоточных трансформаторов схемы замещения приведенные к '
                              'напряжению обмоток ВН')
                te.table_head('Наименование', te.m(r'U_{kr,hl}'), te.m(r'U_{kx,hl}'), te.m('K_T'),
                              te.m('R_T'), te.m('X_T'), te.m('Z_T'), te.m(r'Z_0'))
                for row in rows3w_calc:
                    te.table_row(*row)
            if rowsw_pasp:
                te.table_name('Паспортные данные для двухобмоточных трансформаторов схемы замещения')
                te.table_head('Наименование', 'Марка', te.m(r'S_n,mva'), te.m(r'P_K,kW'), te.m(r'U_{k,hl}'),
                              te.m(r'U_{nh},kV'), te.m('P_{KZ},kW'), widths=(3, 7, 3, 3, 2, 2, 3))
                for row in rowsw_pasp:
                    te.table_row(*row)
                te.table_name('Результат расчётов для двухобмоточных трансформаторов схемы замещения приведенные к '
                              'напряжению обмотки ВН')
                te.table_head('Наименование', te.m(r'U_{kr,hl}'), te.m(r'U_{kx,hl}'), te.m('K_T'),
                              te.m('R_T'), te.m('X_T'), te.m('Z_T'))
                for row in rowsw_calc:
                    te.table_row(*row)

        if not self.net.impedance.empty or any(self.net.line['std_type'].isna()):
            rows = []
            for i, item in self.net.impedance.sort_index().iterrows():
                if item['from_bus'] in self.net.bus_geodata.index and item['to_bus'] in self.net.bus_geodata.index:
                    name_from = self.net.bus.loc[item['from_bus'], 'name'].ljust(28)
                    name_to = self.net.bus.loc[item['to_bus'], 'name'].rjust(28)
                    u2 = self.net.bus.loc[item['from_bus'], 'vn_kv'] ** 2
                    zb = u2 / item['sn_mva']
                    rpu = item['rtf_pu']
                    xpu = item['xtf_pu']
                    rows.append((f'{name_from} - {name_to}', item['name'], f'{rpu * zb:.3f}', f'{xpu * zb:.3f}'))
            for i, item in self.net.line.sort_index().iterrows():
                if item['from_bus'] in self.net.bus_geodata.index and item['to_bus'] in self.net.bus_geodata.index:
                    if item['std_type'] is None:
                        name_from = self.net.bus.loc[item['from_bus'], 'name'].ljust(28)
                        name_to = self.net.bus.loc[item['to_bus'], 'name'].rjust(28)
                        r = item["r_ohm_per_km"]
                        x = item["x_ohm_per_km"]
                        l = item['length_km']
                        parallel = item['parallel']
                        name = item['name'] if item['name'] else ''
                        rows.append((f'{name_from} - {name_to}', name,
                                     f'{r * l / parallel:.3f}', f'{x * l / parallel:.3f}'))
            if rows:
                te.h2('Сопротивления токоограничивающих реакторов')
                te.p('Реактивное сопростивление токоограничевающего реактора задано в паспортных данных. Активное '
                     'сопротивление рассичтано по значению потерь активной мощности в реакторе')
                te.table_name('Значения сопротивлений токоограничивающих реакторов')
                te.table_head('Место подключения', 'Марка', 'r,Ом', 'x,Ом',
                              widths=(3, 2, 1, 2))
                for row in rows:
                    te.table_row(*row)

        if not self.net.load.empty:
            raise NotImplementedError
