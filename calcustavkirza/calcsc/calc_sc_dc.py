from textengines.interfaces import TextEngine

from calcustavkirza.classes import Element, Doc
from calcustavkirza.select.QF import QF

class Line(Element):
    ro: float = 0.0172 # удельное сопротивление материала проводника
    l: float # длина кабеля в метрах
    s: float = 2.5 # сечение жилы кабеля в мм²

    @property
    def r(self):
        return self.ro * self.l / self.s * 2

class CalcScDcDoc(Doc):

    def write(self, te: TextEngine):
        te.h2('Методика расчёта тока КЗ')
        te.p('Ток короткого замыкания:')
        te.math(r'I_{\text{КЗ}} = \frac{E_{\text{расч}} \cdot n \cdot K_c}{R_{\text{сумм}}}')
        te.ul(f'где {te.m(r"E_{\text{расч}}", "Eрасч")} - ЭДС одного элемента аккумуляторной батареи (АКБ)'
              f'в конце разряда, В;')
        te.ul('n - количество элементов  АКБ;')
        te.ul('Kc=(0.59-0.79) - коэффициент снижения тока КЗ, учитывающий сопротивление дуги в месте КЗ (определяется '
              'по экспериментальной зависимости Кс=f(Rкз));')
        te.ul('Rсумм - сопротивление петли короткого замыкания')
        te.p('Rсумм = Rаб + Rош + Rк + Rкаб')
        te.ul('где Rаб - сопротивление АКБ;')
        te.ul('Rош - сопротивление ошиновки АКБ;')
        te.ul('Rк - сопротивление переходных контактов автоматов и рубильников;')
        te.ul('Rкаб - суммарное сопротивление жилы кабеля от АКБ до удалённой нагрузки и обратно;')
        te.p('Коэффициент чувствительности:')
        te.math(r'K_{\text{Ч}} = \frac{I_{\text{КЗ}}}{I_{\text{ср_защ}}}')
        te.ul(f'где {te.m(r"I_{\text{ср_защ}}", "Iср_защ")} - ток срабатывания защитного аппарата (автоматического выключателя) '
              f'или номинальный ток предохранителя.')
        te.p('Кч - должен быть больше 1.4 для электромагнитных расцепителей автоматических выключателей с номинальным '
             'током до 100А')

    def table(self, te: TextEngine):
        te.h2('Расчёт тока КЗ')
        te.p(f'Аккумуляторная батарея: {self.n} элементов с внутренним сопротивлением {self.r} Ом и полным '
             f'сопротивлением {self.n}·{self.r} = {self.n * self.r:.5f} и ЭДС в конце разряда '
             f'{self.umin} В на элемент и полным ЭДС {self.n * self.umin:.1f}')
        te.table_name('Расчёт сопротивлений проводников петли КЗ')
        te.table_head('Участок сети', 'Удельное сопротивление, Ом·мм²/m', 'Длина кабеля, м',
                      'Сечение жилы кабеля, мм²', 'Rкаб, Ом')
        for line in self.lines:
            te.table_row(line.name, line.ro, line.l, line.s, f'{line.r:.5f}')
        r_total = sum([line.r for line in self.lines])
        te.table_row('Итого', '', '', '', f'{r_total:.5f}')
        te.table_name('Сопротивление элементов защитных аппаратов')
        te.table_head('Схеммное обозначение', 'Rк, Ом')
        rk = 0
        for qf in self.qfs:
            te.table_row(qf.name, qf.rk)
            rk += qf.rk
        r_total += rk
        te.table_row('Итого', rk)
        r_total += self.r * self.n
        isc = self.umin * self.n * self.kc / r_total
        te.math(r'I_{\text{КЗ}} = \frac{' + str(self.umin) + r' \cdot ' + str(self.n) + r' \cdot ' + str(self.kc) +
                '}{' + f'{r_total:.5f}' + '} = ' + f'{isc:.1f} A')
        return isc



class CalcScDc(Element):
    umin: float = 2. # напряжение на элементе в конце разряда
    n: int # количество элементов АКБ
    r: float = 0.000239 # сопротивление внутреннее элемента АКБ
    kc: float = 0.59 # коэффициент снижения тока КЗ из-за дуги
    lines: list[Line]
    qfs: list[QF] # список автоматов в цепи

