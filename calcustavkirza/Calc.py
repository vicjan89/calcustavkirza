from pandapower import pandapowerNet


from calcustavkirza.classes import Element
from pandapowertools.net import Net


class Calc(Element):
    res_sc: list[list]
    calc1ph: bool | str = False
    calc1ph_trans: bool = False
    calcmci: bool = False
    calc_load: bool = False
    transDY: bool = False

    def do(self):
        if self.calc_load:
            self.te.h2('Расчёт значений токов нагрузок')
            self.te.table_name('Результат расчёта для линий')
            self.te.table_head('Линия', *self.net.res_pf.line.head)
            for name, row in self.net.res_pf.line:
                row = [f'{r:.1f}' for r in row]
                self.te.table_row(name, *row)
            self.te.table_name('Результат расчёта для трансформаторов')
            self.te.table_head('Трансформатор', *self.net.res_pf.trafo.head)
            for name, row in self.net.res_pf.trafo:
                row = [f'{r:.1f}' for r in row]
                self.te.table_row(name, *row)
            self.te.table_name('Результат расчёта для коммутационных аппаратов')
            self.te.table_head('Аппарат', *self.net.res_pf.switch.head)
            for name, row in self.net.res_pf.switch:
                for i in range(len(row)):
                    row[i] = f'{row[i]:.1f}' if not isna(row[i]) else ' '
                self.te.table_row(name, *row)

        if self.calcmci:
            self.te.h2('Расчёт значений бросков токов намагничивания')
            self.net.calc_mci_modes()
            self.te.table_name('Результат расчёта для линий с коэффициентом 4')
            mode_names = self.net.res_mci.line.head
            self.te.table_head('Линия', *mode_names)
            for name, row in self.net.res_mci.line:
                row = [f'{r:.1f}' for r in row]
                self.te.table_row(name, *row)

        self.te.h2('Расчет значений токов короткого замыкания')
        self.te.p('Расчет максимальных значений токов трехфазного короткого замыкания выполнялся по формуле:')
        self.te.math(r'I^{(3)}_K = \frac{c \cdot U_n}{ \sqrt{3} \cdot Z_{∑max}}')
        self.te.ul(f'где {self.te.m("U_n")} - номинальное линейное напряжение в месте КЗ,')
        self.te.ul(f'{self.te.m("Z_{∑max}")} - суммарное эквивалентное сопротивление до рассматриваемой точки КЗ для максимального режима работы энергосистемы.')
        self.te.ul(f'{self.te.m("c")} - коэффициент коррекции напряжения. Для минимального режима в сетях до 1кВ равен '
                   f'0.95 а выше 1кВ - равен 1. Для максимального режима равен 1.1')
        self.te.ul('Расчет минимальных значений токов двухфазного короткого замыкания выполнялся по формуле:')
        self.te.math(r'I^{(2)}_K = \frac{c \cdot U_n}{2 \cdot Z_{∑min}}')
        self.te.ul(f'где {self.te.m("U_n")} - номинальное линейное напряжение в месте КЗ,')
        self.te.ul(f'{self.te.m("Z_{∑min}")} - суммарное эквивалентное сопротивление до рассматриваемой точки КЗ для минимального режима работы энергосистемы.')
        self.te.p(f'При определении {self.te.m("Z_∑")} суммируются все сопротивления на пути протекания тока короткого '
                  f'замыкания. Сопротивления предварительно приводятся к напряжению, для которого рассчитывается ток '
                  f'короткого замыкания по формуле приведения:')
        self.te.math(r'Z_1 = Z_2 \cdot \biggl(\frac{U_1}{U_2}\biggr)^2')
        self.te.ul(f'где {self.te.m("U_2")} - номинальное напряжение трансформатора к которому подключен элемент с '
                   f'{self.te.m("Z_2")}')
        self.te.ul(f'{self.te.m("U_1")} - номинальное напряжение трансформатора к которому приводится сопротивление '
                   f'{self.te.m("Z_2")}')
        self.te.table_name('Результат расчёта токов КЗ для всех узлов (в скобках ток, приведенный к стороне ВН)')
        head = [mode[0] for mode in self.res_sc]
        self.te.table_head('Узел', *head)
        buses = sorted(list(self.res_sc[0][1].keys()))
        for i in buses:
            row = [f'{data[1][i][1]:.3f}' for data in self.res_sc]
            self.te.table_row(self.res_sc[0][1][i][0], *row)
        if self.transDY:
            self.te.p('Оценка уровня токов однофазного короткого замыкания за трансформаторами 10 / 0.4 кВ со схемой '
                      'соединения обмоток "треугольник-звезда с нулём" выполнена с учётом того, что сопротивление нулевой '
                      'последовательности таких трансформаторов равно сопротивлению прямой последовательности и '
                      'соответственно ток однофазного короткого замыкания на выводах 0.4 кВ практически равен току '
                      'трёхфазного короткого замыкания.Приведение тока однофазного короткого замыкания к стороне высокого '
                      'напряжения трансформатора осуществляется по формуле:')
            self.te.math(r'I_{hv}^{k1} = \frac{I_{lv}^{k1}}{\sqrt{3} \cdot n_T}')
            self.te.ul(f'где {self.te.m("I_{lv}^{k1}")} - ток однофазного короткого замыкания на выводах обмотки низкого '
                       f'напряжения трансформатора')
            self.te.ul(f'{self.te.m("I_{hv}^{k1}")} - ток однофазного короткого замыкания на выводах обмотки низкого '
                       f'напряжения трансформатора приведенный к напряжению обмотки высокого напряжения трансформатора')
            self.te.ul(f'{self.te.m("n_T")} - коэффициент трансформации трансформатора')

        if self.calc1ph_trans:
            self.te.table_name('Результат расчёта токов однофазного КЗ за трансформаторами звезда-звезда Iкз=Uф/(1/3 z(1)т)')
            self.te.table_head('Трансформатор', 'Марка', '1/3 z(1)т', 'Iкз(1)', 'Iкз(1)*2/3/nт (привед. к ВН)')
            for n, tr in self.net.net.trafo.iterrows():
                z, u_lv, u_hv = get_z1_trafo(tr)
                i = u_lv/math.sqrt(3)/z
                self.te.table_row(tr['name'], tr['std_type'], z, f'{i:.1f}', f'{i/u_hv*u_lv*2/3:.1f}')

        if self.calc1ph:
            self.te.h2('Расчет значений токов однофазного замыкания на землю')
            self.te.p(f'Расчет токов однофазного замыкания на землю выполнен для случая замыкания на землю {self.calc1ph}'
                      f' с выведенными из работы резисторами заземления нейтрали. Полученные токи используются для '
                      f'отстройки ТЗНП от собственных ёмкостных токов. '
                      f'Расчёт ёмкостного тока замыкания на землю выполнялся по формуле:')
            self.te.math(r'I^{(1)} = \sqrt{3} \cdot U_n \cdot \omega \cdot C \cdot 10^{-6}')
            self.te.ul(f'где {self.te.m("U_n")} - номинальное линейное напряжение в месте замыкания, кВ')
            self.te.ul(self.te.m(r"\omega")+' - угловая частота равная ' + self.te.m("2 \cdot \pi \cdot f"))
            self.te.ul('f - частота в сети равная 50 Гц;')
            self.te.ul('C - ёмкость кабеля, нФд.')

            self.te.table_name('Паспортные данные линий электропередач')
            self.te.table_head('Наименование', 'Марка', 'Длина,км', 'Удельная ёмкость,нФ/км', 'Ёмкость,нФ',
                               widths=(3,3,1,2,2))
            for i, item in self.net.net.line.iterrows():
                name1 = self.net.net.bus.at[item['from_bus'], 'name']
                name2 = self.net.net.bus.at[item['to_bus'], 'name']
                name = name1 + ' - ' + name2
                c = item["c_nf_per_km"]
                l = item['length_km']
                self.te.table_row(name, item['std_type'], l, c, f'{l*c:.2f}')

            self.net.create_mode_calc_c(0)
            for mode_name, mode in self.modes.items():
                self.net.calc_pf_mode(mode_name)
                self.net.res_c.line.update(f'{mode_name}', self.net.net.res_line)
            self.net.delete_mode_calc_c()
            self.te.table_name('Результат расчёта для линий')
            self.te.table_head('Линия', *self.net.res_c.line.head)
            for name, row in self.net.res_c.line:
                row_txt = []
                for r in row:
                    row_txt.append('' if isna(r) else f'{r*3:.2f}')
                self.te.table_row(name, *row_txt)


        self.te.p('Расчёты выполнены с применением языка программирования Python и библиотеки PandaPower(© Copyright '
                  '2016 - 2024 by Fraunhofer IEE and University of Kassel.)')
