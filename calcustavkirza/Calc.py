import math


from pandapower import pandapowerNet
from textengines.interfaces import TextEngine


from calcustavkirza.classes import Element
from pandapowertools.net import Net


class Calc(Element):
    calc1ph_trans: bool = False
    calcmci: bool = False
    calc_load: bool = False
    transDY: bool = False

    def do(self, te: TextEngine, res_sc: list[list], res_c: dict | None = None):
        te.h1('Расчёт параметров электрической сети')
        if self.calc_load:
            te.h2('Расчёт значений токов нагрузок')
            te.table_name('Результат расчёта для линий')
            te.table_head('Линия', *self.net.res_pf.line.head)
            for name, row in self.net.res_pf.line:
                row = [f'{r:.1f}' for r in row]
                te.table_row(name, *row)
            te.table_name('Результат расчёта для трансформаторов')
            te.table_head('Трансформатор', *self.net.res_pf.trafo.head)
            for name, row in self.net.res_pf.trafo:
                row = [f'{r:.1f}' for r in row]
                te.table_row(name, *row)
            te.table_name('Результат расчёта для коммутационных аппаратов')
            te.table_head('Аппарат', *self.net.res_pf.switch.head)
            for name, row in self.net.res_pf.switch:
                for i in range(len(row)):
                    row[i] = f'{row[i]:.1f}' if not isna(row[i]) else ' '
                te.table_row(name, *row)

        if self.calcmci:
            te.h2('Расчёт значений бросков токов намагничивания')
            self.net.calc_mci_modes()
            te.table_name('Результат расчёта для линий с коэффициентом 4')
            mode_names = self.net.res_mci.line.head
            te.table_head('Линия', *mode_names)
            for name, row in self.net.res_mci.line:
                row = [f'{r:.1f}' for r in row]
                te.table_row(name, *row)

        te.h2('Расчет значений токов короткого замыкания')
        te.p('Расчет максимальных значений токов трехфазного короткого замыкания выполнялся по формуле:')
        te.math(r'I^{(3)}_K = \frac{c \cdot U_n}{ \sqrt{3} \cdot Z_{∑max}}')
        te.ul(f'где {te.m("U_n")} - номинальное линейное напряжение в месте КЗ,')
        te.ul(f'{te.m("Z_{∑max}")} - суммарное эквивалентное сопротивление до рассматриваемой точки КЗ для максимального режима работы энергосистемы.')
        te.ul(f'{te.m("c")} - коэффициент коррекции напряжения. Для минимального режима в сетях до 1кВ равен '
                   f'0.95 а выше 1кВ - равен 1. Для максимального режима равен 1.1')
        te.ul('Расчет минимальных значений токов двухфазного короткого замыкания выполнялся по формуле:')
        te.math(r'I^{(2)}_K = \frac{c \cdot U_n}{2 \cdot Z_{∑min}}')
        te.ul(f'где {te.m("U_n")} - номинальное линейное напряжение в месте КЗ,')
        te.ul(f'{te.m("Z_{∑min}")} - суммарное эквивалентное сопротивление до рассматриваемой точки КЗ для минимального режима работы энергосистемы.')
        te.p(f'При определении {te.m("Z_∑")} суммируются все сопротивления на пути протекания тока короткого '
                  f'замыкания. Сопротивления предварительно приводятся к напряжению, для которого рассчитывается ток '
                  f'короткого замыкания по формуле приведения:')
        te.math(r'Z_1 = Z_2 \cdot \biggl(\frac{U_1}{U_2}\biggr)^2')
        te.ul(f'где {te.m("U_2")} - номинальное напряжение трансформатора к которому подключен элемент с '
                   f'{te.m("Z_2")}')
        te.ul(f'{te.m("U_1")} - номинальное напряжение трансформатора к которому приводится сопротивление '
                   f'{te.m("Z_2")}')
        te.table_name('Результат расчёта токов КЗ для всех узлов (в скобках ток, приведенный к стороне ВН)')
        head = [mode[0] for mode in res_sc]
        te.table_head('Узел', *head)
        buses = sorted([(key, value[0]) for key, value in res_sc[0][1].items()], key=lambda x: x[1])
        for i, name in buses:
            row = [f'{data[1][i][1]:.3f}' for data in res_sc]
            te.table_row(name, *row)
        if self.transDY:
            te.p('Оценка уровня токов однофазного короткого замыкания за трансформаторами со схемой '
                      'соединения обмоток "треугольник-звезда с нулём" выполнена с учётом того, что сопротивление нулевой '
                      'последовательности таких трансформаторов равно сопротивлению прямой последовательности и '
                      'соответственно ток однофазного короткого замыкания на выводах 0.4 кВ практически равен току '
                      'трёхфазного короткого замыкания.Приведение тока однофазного короткого замыкания к стороне высокого '
                      'напряжения трансформатора осуществляется по формуле:')
            te.math(r'I_{hv}^{k1} = \frac{I_{lv}^{k1}}{\sqrt{3} \cdot n_T}')
            te.ul(f'где {te.m("I_{lv}^{k1}")} - ток однофазного короткого замыкания на выводах обмотки низкого '
                       f'напряжения трансформатора')
            te.ul(f'{te.m("I_{hv}^{k1}")} - ток однофазного короткого замыкания на выводах обмотки низкого '
                       f'напряжения трансформатора приведенный к напряжению обмотки высокого напряжения трансформатора')
            te.ul(f'{te.m("n_T")} - коэффициент трансформации трансформатора')

        if self.calc1ph_trans:
            te.table_name('Результат расчёта токов однофазного КЗ за трансформаторами звезда-звезда Iкз=Uф/(1/3 z(1)т)')
            te.table_head('Трансформатор', 'Марка', '1/3 z(1)т', 'Iкз(1)', 'Iкз(1)*2/3/nт (привед. к ВН)')
            for n, tr in self.net.net.trafo.iterrows():
                z, u_lv, u_hv = get_z1_trafo(tr)
                i = u_lv/math.sqrt(3)/z
                te.table_row(tr['name'], tr['std_type'], z, f'{i:.1f}', f'{i/u_hv*u_lv*2/3:.1f}')

        if res_c:
            te.h2('Расчет значений токов однофазного замыкания на землю')
            te.p(f'Расчет токов однофазного замыкания на землю выполнен для случая замыкания на землю: {res_c[0]}. '
                      f'Полученные токи используются для отстройки ТЗНП от собственных ёмкостных токов. '
                      f'Расчёт ёмкостного тока замыкания на землю выполнялся по формуле:')
            te.math(r'I^{(1)} = \sqrt{3} \cdot U_n \cdot \omega \cdot C \cdot 10^{-6}')
            te.ul(f'где {te.m("U_n")} - номинальное линейное напряжение в месте замыкания, кВ')
            te.ul(te.m(r"\omega")+' - угловая частота равная ' + te.m(r"2 \cdot \pi \cdot f"))
            te.ul('f - частота в сети равная 50 Гц;')
            te.ul('C - ёмкость кабеля, нФд.')

            te.table_name('Результат расчёта для линий')
            te.table_head('Линия', 'Ёмкостный ток, А')
            for name, ic in res_c[1].items():
                te.table_row(name, f'{ic:.3f}')


        te.p('Расчёты выполнены с применением языка программирования Python и библиотеки PandaPower(© Copyright '
                  '2016 - 2024 by Fraunhofer IEE and University of Kassel) распространяемой по свободной лицензии BSD.')
