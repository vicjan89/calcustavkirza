import math

from textengines.interfaces import TextEngine


from calcustavkirza.classes import Element


class Cable(Element):
    brand: str = ''
    s: float # сечение мм.кв.
    s_screen: float | None = None # сечение экрана кабеля, мм.кв.
    ith: float # допустимый ток односекундного КЗ для жилы
    ith_screen: float | None = None # допустимый ток односекундного КЗ для экрана

    def passort_data(self):
        s_screen = self.s_screen if self.s_screen else 'нет'
        ith_screen = self.ith_screen if self.ith_screen else 'нет'
        return self.name, self.brand, self.s, s_screen, self.ith, ith_screen

    def check_ith(self, isc: float, t: float, isc_screen: float, t_screen: float):
        '''
        Проверяет кабель на термическую стойкость к токам КЗ
        :param te:
        :param isc: ток КЗ в А
        :param t: время отключения защитами + полное время отключения выключателя
        :param isc_screen: ток КЗ для проверки экрана в А
        :param t: время отключения защитами + полное время отключения выключателя для проверки экрана
        :return:
        '''
        if self.ith_screen:
            ith_screen_real = self.ith_screen / math.sqrt(t_screen)
        else:
            ith_screen_real = 'нет'
        return self.name, isc, t, f'{self.ith / math.sqrt(t):.0f}', f'{isc_screen:.0f}', t_screen, f'{ith_screen_real:.0f}'

class Cables(Element):
    cables: list[Cable]


    def check_ith(self, te: TextEngine, cases: list[tuple[int, dict[str, float]]]):
        te.h1('Проверка кабелей на термическую стойкость')
        te.table_name('Паспортные данные кабелей')
        te.table_head('Место подключения', 'Марка', 'Сечение жилы, мм.кв.', 'Сечение экрана, мм.кв.',
                      'Допустимый ток односекундного КЗ, А', 'Допустимый тока односекундного КЗ экрана, А')
        for cable in self.cables:
            te.table_row(*cable.passort_data())
        te.p('При отличии времени отключения максимального тока от одной секунды допустимый ток пересчитывается по '
             'формуле:')
        te.math(r'I_{\text{доп.}} = \frac{I_{\text{доп.}}}{\sqrt{t}}')
        te.table_name('Проверка на термическую стойкость')
        te.table_head('Место подключения', 'Ток КЗ, А', 'Время КЗ, сек', 'Допустимый ток, А',
                      'Ток повреждения для проверки экрана, А', 'Время отключения повреждения для проверки экрана, сек',
                      'Допустимый ток экрана, А')
        for index_cable, case in cases:
            te.table_row(*self.cables[index_cable].check_ith(**case))