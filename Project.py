from itertools import groupby

from pydantic import ConfigDict

from calcustavkirza.classes import Element
from calcustavkirza.Pris import Pris
from select.CT import CT


def num2str_list(l: list) -> list:
    res = []
    for i in l:
        if isinstance(i, float):
            res.append(f'{i:.2f}')
        elif isinstance(i, int):
            res.append(str(i))
        elif i is None:
            res.append('')
        else:
            res.append(i)
    return res

class Project(Element):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    res_sc_min: dict
    res_sc_max: dict
    pris: list[Pris] | None = None
    ct: list[CT] | None = None

    def add_context(self, **kwargs):
        super().add_context(**kwargs)
        self.net.add_context(**kwargs)
        if self.pris:
            for pr in self.pris:
                pr.add_context(**kwargs, net=self.net)

    def table_settings_bmz(self):
        self.te.table_grid_name('Таблица уставок РЗА РП 10кВ Водозабор-Коммунальный и ПС 110кВ Сталь')
        self.te.table_grid_head('Функция РЗА', 'Параметр', *[p.name for p in self.pris])
        table_row_data = []
        for n, pris_rza in enumerate(self.pris):
            for p in pris_rza.table_settings_bmz():
                table_row_data.append([n] + p)
        table_row_data.sort(key=lambda x: x[1] + ''.join(x[2]))
        for key, items in groupby(table_row_data, key=lambda x: x[1] + ''.join(x[2])):
            first = True
            items = list(items)
            repeat = True
            while repeat:
                remainder = []
                while items:
                    item = items[-1]
                    if first:
                        name = item[1]
                        row = [item[2]] + [''] * len(self.pris)
                        first = False
                    if not row[item[0] + 1]:
                        row[item[0] + 1] = item[-1]
                        items.pop()
                    else:
                        remainder.append(items.pop())
                    if all(row) or not items:
                        # fill empty strings
                        if not all(row):
                            for n, i in enumerate(row):
                                if not i:
                                    row[n] = [''] * len(row[0])
                        row = list(zip(*row))
                        if len(row) == 1:
                            self.te.table_grid_row(name, *num2str_list(row[0]))
                        elif len(row) == 2:
                            self.te.table_grid_row(name, *num2str_list(row[0]), rowspan=(0,))
                            self.te.table_grid_row('', *num2str_list(row[1]))
                        elif len(row) > 2:
                            self.te.table_grid_row(name, *num2str_list(row[0]), rowspan=(0,))
                            for r in row[1: -1]:
                                self.te.table_grid_row('', *num2str_list(r), rowspan=(0,))
                            self.te.table_grid_row('', *num2str_list(row[-1]))
                        first = True
                if remainder:
                    items = remainder
                else:
                    repeat = False

    def table_settings_bmz2(self):
        num = (len(self.pris) + 1)
        self.te.table_grid_name('Таблица уставок РЗА РП 10кВ Водозабор-Коммунальный и ПС 110кВ Сталь',
                                widths=[1] * num)
        self.te.table_grid_head('Параметр', *[p.name for p in self.pris])
        table_row_data = []
        for n, pris_rza in enumerate(self.pris):
            for p in pris_rza.table_settings_bmz():
                table_row_data.append([n] + p)
        table_row_data.sort(key=lambda x: x[1] + ''.join(x[2]), reverse=True)
        for key, items in groupby(table_row_data, key=lambda x: x[1] + ''.join(x[2])):
            first = True
            items = list(items)
            repeat = True
            while repeat:
                remainder = []
                while items:
                    item = items[-1]
                    if first:
                        name = item[1]
                        self.te.table_grid_row_colspan(name, widths=[50]*(len(self.pris) + 1))
                        row = [item[2]] + [''] * len(self.pris)
                        first = False
                    if not row[item[0] + 1]:
                        row[item[0] + 1] = item[-1]
                        items.pop()
                    else:
                        remainder.append(items.pop())
                    if all(row) or not items:
                        # fill empty strings
                        if not all(row):
                            for n, i in enumerate(row):
                                if not i:
                                    row[n] = [''] * len(row[0])
                        row = list(zip(*row))
                        for r in row:
                            if any([i != '' and i is not None for i in r[1:]]):
                                self.te.table_grid_row(*num2str_list(r))
                        first = True
                if remainder:
                    items = remainder
                else:
                    repeat = False

    def calc_ust(self):
        # if self.calc_load:
        #     self.te.h2('Расчёт значений токов нагрузок')
        #     self.net.calc_pf_modes()
        #     self.te.table_name('Результат расчёта для линий')
        #     self.te.table_head('Линия', *self.net.res_pf.line.head)
        #     for name, row in self.net.res_pf.line:
        #         row = [f'{r:.1f}' for r in row]
        #         self.te.table_row(name, *row)
        #     self.te.table_name('Результат расчёта для трансформаторов')
        #     self.te.table_head('Трансформатор', *self.net.res_pf.trafo.head)
        #     for name, row in self.net.res_pf.trafo:
        #         row = [f'{r:.1f}' for r in row]
        #         self.te.table_row(name, *row)
        #     self.te.table_name('Результат расчёта для коммутационных аппаратов')
        #     self.te.table_head('Аппарат', *self.net.res_pf.switch.head)
        #     for name, row in self.net.res_pf.switch:
        #         for i in range(len(row)):
        #             row[i] = f'{row[i]:.1f}' if not isna(row[i]) else ' '
        #         self.te.table_row(name, *row)
        #
        # if self.calcmci:
        #     self.te.h2('Расчёт значений бросков токов намагничивания')
        #     self.net.calc_mci_modes()
        #     self.te.table_name('Результат расчёта для линий с коэффициентом 4')
        #     mode_names = self.net.res_mci.line.head
        #     self.te.table_head('Линия', *mode_names)
        #     for name, row in self.net.res_mci.line:
        #         row = [f'{r:.1f}' for r in row]
        #         self.te.table_row(name, *row)
        #

        if self.pris:
            self.te.h1('Выбор уставок РЗА')
            if self.pris:
                for p in self.pris:
                    p.calc_ust(self.res_sc_min)
            # if self.ct:
            #     self.te.h1('Выбор трансформаторов тока')
            #     self.ct[0].metods()
            #     self.te.h2('Проверка параметров и выбор мощности релейных обмоток трансформаторов тока (ТТ)')
            #     for ct in self.ct:
            #         ct.calc_ust()
            # self.te.h1('Таблица уставок')
            # if self.table_settings == 'bmz':
            #     self.table_settings_bmz2()
            # else:
            #     for p in self.pris:
            #         p.table_settings()

        self.te.h1('Расчётная схема сети')

        # self.te.h1('Графики селективности')
        # char_pkt200 = [(i*2, t) for i, t in char_pkt100]
        # char_pkt200_spred = [(i*1.2*2, t) for i, t in char_pkt160]
        # compose_selectivity_map(self.pris[0:1], [(create_from_charact(char_pkt200), create_from_charact(char_pkt200_spred))],
        #                         ['ПКТ-104 200А'], 500, 6000, 'source_old\s_map0', time_max=2)
        # self.te.image(image_path='s_map0.png', name='Карта селективности при КЗ за предохранителями трансформаторов '
        #                                             '2500кВА (диапазон токов 3831.5 - 5089.2 A)')
        #
        # char_pkt160_spred = [(i*1.2, t) for i, t in char_pkt160]
        # compose_selectivity_map([self.pris[0], self.pris[4]], [(create_from_charact(char_pkt160), create_from_charact(char_pkt160_spred))],
        #                         ['ПКТ-103 160А'], 400, 6000, 'source_old\s_map1', time_max=2)
        # self.te.image(image_path='s_map1.png', name='Карта селективности при КЗ за предохранителями трансформаторов '
        #                                             '1600кВА (диапазон токов 3610.6 - 4782.7 A)')
        #
        # char_pkt100_spred = [(i*1.2, t) for i, t in char_pkt100]
        # compose_selectivity_map([self.pris[0], self.pris[4], self.pris[8], self.pris[10]], [(create_from_charact(char_pkt100), create_from_charact(char_pkt100_spred))],
        #                         ['ПКТ-103 100А'], 45, 6000, 'source_old\s_map2', time_max=2)
        # self.te.image(image_path='s_map2.png', name='Карта селективности при КЗ за предохранителями трансформаторов '
        #                                             '1000кВА (диапазон токов 3455 - 4568.4 A)')

# Для Водозабор-Коммунальный
#         char_pkt10_spred = [(i * 1.2, t) for i, t in char_pkt10]
#         compose_selectivity_map(self.pris[6:7], [(create_from_charact(char_pkt10), create_from_charact(char_pkt10_spred))],
#                                 ['ПКТ-10 10А тр-ров 100кВА скважин '], 30, 300, 'source_old\s_map1')
#         self.te.image(image_path='s_map1.png', name='Селективность с предохранителями трансформатора скважин')
#
#         char_pkt100_spred = [(i * 1.2, t) for i, t in char_pkt100]
#         compose_selectivity_map(self.pris[2:3]+self.pris[6:8], [(create_from_charact(char_pkt100), create_from_charact(char_pkt100_spred))],
#                                 ['ПКТ-10 100А Т СТО 630кВА'], 30, 9500, 'source_old\s_map2')
#         self.te.image(image_path='s_map2.png', name='Селективность с предохранителями трансформатора СТО')
#
#         compose_selectivity_map(self.pris[7:8],
#                                 [make_spread_iec_charact(char_a37, 500/10.5*0.4*2/3),
#                                               create_time_independent(5000/10.5*0.4*2/3, 0)],
#                                 ['А3796П ввода 0.4кВ тр-ра 7TU0\n(тепловой расцепитель)',
#                                  'А3796П ввода 0.4кВ тр-ра 7TU0\n(электромагнитный расцепитель)'],
#                                              20, 600, 'source_old\s_map3', 40)
#         self.te.image(image_path='s_map3.png',
#                       name='Селективность с автоматами вводов 0.4кВ трансформаторов РП Водозабор при однофазных КЗ')
#
#         compose_selectivity_map(self.pris[7:8],
#                                 [make_spread_iec_charact(char_a37, 500/10.5*0.4),
#                                  create_time_independent(5000/10.5*0.4, 0)],
#                                 ['А3796П ввода 0.4кВ тр-ра 7TU0\n(тепловой расцепитель)',
#                                  'А3796П ввода 0.4кВ тр-ра 7TU0\n(электромагнитный расцепитель)'],
#                                 20, 600, 'source_old\s_map4', 20)
#         self.te.image(image_path='s_map4.png',
#                       name='Селективность с автоматами вводов 0.4кВ трансформаторов РП Водозабор при междуфазных КЗ')
