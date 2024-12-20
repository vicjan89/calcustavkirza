import math


from textengines.interfaces import TextEngine


from calcustavkirza.classes import Element


class ImbalanceSVG(Element):
    c: float #номинальная ёмкость одного конденсатора в батарее
    N: int = 1 #количество последовательных рядов конденсаторов
    n: int = 1 #количество последовательных рядов конденсаторных элементов
    M: int = 1 #количество параллельных рядов конденсаторов
    m: int = 1 #количество параллельных рядов конденсаторных элементов
    u: float #номинальное напряжение сети
    isz: float #ток срабатывания
    isz_note: str = ''
    isz_alarm: float #ток срабатывания на сигнал
    t: float = 1.
    t_alarm: float = 10. #выдержка времени действия на сигнал
    t_note: str = ''
    kn: float = 1.5
    kch: float = 1.5 #коэффициент чувствительности
    name: str = 'Небалансная защита по току нейтрали БСК/ФКУ (ANSI 60/50)'
    name_short: str = 'НБЗ'

    def calc_ust(self, te: TextEngine, *args):
        te.table_name(self.name)
        te.table_head('Наименование величины', 'Расчётная формула, обозначение', 'Результат расчёта', widths=(3,2,1))
        i_imb = (self.u * 1000 / math.sqrt(3) * 100 * math.pi * self.c / 1_000_000 * self.M / self.N /
                 (4 * (self.N * (self.M * (self.n - 1) + 1)) - 3))
        te.table_row('Ток небаланса, протекающий в проводнике, соединяющем средние точки двух полуветвей фазы',
                     te.m( r'I_{\text{НБ.РАСЧ}} = \frac{U_{\text{НОМ}} \cdot \omega \cdot C_1 \cdot M}'
                         r'{\sqrt{3} \cdot N \cdot (4 \cdot (N \cdot (M \cdot (n - 1) + 1)) - 3) \cdot 1000}'),
                     f'{i_imb:.1f}')
        te.table_row('Ёмкость одного конденсаторного элемента, мкФ', te.m('C_1'), self.c)
        te.table_row('Количество последовательных рядов конденсаторов', te.m('N'), self.N)
        te.table_row('Количество последовательных рядов конденсаторных элементов', te.m('n'), self.n)
        te.table_row('Количество параллельных рядов конденсаторов', te.m('M'), self.M)
        te.table_row('Количество параллельных рядов конденсаторных элементов', te.m('m'), self.m)
        te.table_row('Номинальное напряжение, кВ', te.m(r'U_{\text{НОМ}}'), self.u)
        te.table_row('Коэффициент чувствительности', te.m(r'K_{\text{ч}}'), self.kch)
        isz_otkl = i_imb / self.kch
        te.table_row('Ток срабатывания ступени на отключение',
                     te.m(r'I_{\text{СР}} = \frac{I_{\text{НБ.РАСЧ}}}{K_{\text{ч}}}'),
                     f'{isz_otkl:.1f}')
        te.table_row(f'Принимаем первичный ток срабатывания защиты с действием на отключение {self.isz_note} '
                     f'равным (требуется уточнение '
                     f'на этапе наладки по результатам измерений для отстройки от небаланса нормального режима), А',
                     te.m(r'I_{\text{СР.ОТКЛ}}'), self.isz)
        te.table_row(f'Время срабатывания защиты на отключение (требуется уточнение на этапе наладки по '
                     f'результатам измерений для отстройки от переходного режима), с {self.t_note}', 'tср.откл', self.t)

        te.table_row('Ток срабатывания ступени на сигнал', te.m(r'I_{\text{СР}} = 0.6 \cdot I_{\text{СР.ОТКЛ}}'),
                     f'{0.6 * isz_otkl:.1f}')
        te.table_row(f'Принимаем первичный ток срабатывания защиты с действием на сигнал равным (требуется '
                     f'уточнение на этапе наладки по результатам измерений для отстройки от небаланса нормального '
                     f'режима), А', te.m(r'I_{\text{СР.СИГН}}'), self.isz_alarm)
        te.table_row(f'Время срабатывания защиты на отключение (требуется уточнение на этапе наладки по '
                     f'результатам измерений для отстройки от переходного режима), с', 'tср.сигн', self.t_alarm)

    def table_settings(self, te: TextEngine):
        te.table_row(self.name, f'{self.isz} A', self.t, self.isz_note)
        te.table_row(self.name, f'{self.isz_alarm} A', self.t_alarm, self.isz_note)
