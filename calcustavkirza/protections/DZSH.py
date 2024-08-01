import math
import os


from textengines.interfaces import TextEngine


from calcustavkirza.classes import Element

class DZSH(Element):
    pris_base: str = '' #название присоединения приятого за базовое
    i1_base: int #первичный ток ТТ базистного присоединения
    i2_base: int #вторичный ток ТТ базистного присоединения
    e: float = 0.05 #погрешность ТТ
    Kots: float = 1.2 #рекомендация БЭМН
    Koverl: float = 2.5 #коэффициент перегрузки по рекоментации БЭМН
    i_kz_max: float #максимальный сквозной ток КЗ приведенный к высокой стороне
    i_kz_max_note: str = ''
    i_kz_min: float #минимальный ток КЗ приведенный к высокой стороне
    i_kz_min_note: str = ''
    i_nagr_max: float #максимальный ток нагрузки
    i_overload: float #максимальный ток перегркузки
    ib1: float #тормозной ток первого перегиба
    s2: float
    t_max: float #наибольшая задержка времени РЗА присоединений питающих шины
    dt: float = 0.3 #время запаса для расчёта времени контоля целостности ТТ
    id: float
    id_ots: float = 40 #уставка дифференциальной отсечки
    id_alarm: float | None = None #контроль дифтока в о.е.
    time_prot: bool = False
    name: str = 'Дифференциальная защита шин'
    name_short: str = 'ДЗШ'

    def calc_ust(self, te: TextEngine, res_sc_min: list, res_sc_max: list):
        te.table_name(self.name)
        te.table_head('Наименование величины', 'Расчётная формула, обозначение', 'Результат расчёта', widths=(3,2,1))
        te.table_row(f'Максимальный ток КЗ {self.i_kz_max_note}, А', te.m(r'I_{\text{КЗ.МАКС}}'), self.i_kz_max)
        te.table_row(f'Минимальный ток КЗ {self.i_kz_min_note}, А', te.m(r'I_{\text{КЗ.МИН}}'), self.i_kz_min)
        ktt = self.i1_base / self.i2_base
        te.table_row(f'Принимаем за базисное присоединение {self.pris_base}',
                     te.m(r'K_{\text{ТТ.БАЗ}} = \frac{'+str(self.i1_base)+r'}{'+str(self.i2_base)+r'}'),
                          ktt)
        id = self.Kots * self.i_nagr_max / self.i1_base
        f_inom_ktt = r'I_{\text{НОМ}} \cdot K_{\text{ТТ.БАЗ}}'
        te.table_row('Рассчитаем уставку '+te.m(r'I_{\text{Д>}}'),
                     te.m(r'I_{\text{Д}} = K_{\text{ОТС}} \cdot \frac{I_{\text{МАКС.НАГР}}}{'+f_inom_ktt+'}'),
                     f'{id:.2f}')
        te.table_row('Номинальный вторичный ток, A', te.m(r'I_{\text{НОМ}}'), self.i2_base)
        te.table_row('Максимальный ток нагрузки, А', te.m(r'I_{\text{МАКС.НАГР}}'), self.i_nagr_max)
        te.table_row('Коэффициент отстройки', te.m(r'K_{\text{ОТС}}'), self.Kots)
        ib1 = self.Kots * 2 * self.i_overload / self.i1_base
        te.table_row('Рассчитаем '+te.m(r'I_{\text{Б1}}'), te.m(r'K_{\text{ОТС}} \cdot '
                                                                r'\frac{2I_{\text{МАКС.ПЕРЕГР.}}}{'+f_inom_ktt+'}'),
                     f'{ib1:.2f}')
        te.table_row('Максимальный ток перегрузки, А', te.m(r'I_{\text{МАКС.ПЕРЕГР.}}'), self.i_overload)
        f1 = math.atan2(self.Kots * (self.Koverl * self.e * self.i_kz_max / self.i1_base - id),
                        self.i_kz_max / self.i1_base - ib1)
        te.table_row('Рассчитаем угол наклона участа торможения' + te.m(r'f_1'),
                     te.m(r'\arctan(K_{\text{ОТС}} \frac{K_{\text{ПЕР}} \cdot \varepsilon \cdot '
                          r'I^*_{\text{КЗ.ВНЕШ}} - I_{\text{Д>}}}{I^*_{\text{ТОРМ.РАСЧ}} - I_{\text{Б1}}})'),
                     f'{math.degrees(f1):.1f}')
        te.table_row('Коэффициент перегрузки', te.m(r'K_{\text{ПЕР}}'), self.Koverl)
        te.table_row('Погрешность ТТ', te.m(r'\varepsilon'), self.e)
        te.table_row('Максимальный ток внешнего КЗ, о.е.', te.m(r'I^*_{\text{КЗ.ВНЕШ}} = \frac{I_{\text{КЗ.ВНЕШ}}}{'+
                                                          f_inom_ktt+'}}'), f'{self.i_kz_max / self.i1_base:.1f}')
        te.table_row('Максимальный ток внешнего КЗ, A', te.m(r'I_{\text{КЗ.ВНЕШ}}'), self.i_kz_max)
        te.table_row('Максимальный тормозной ток при внешнем КЗ, о.е.',
                     te.m(r'I^*_{\text{ТОРМ.РАСЧ}} = \frac{I_{\text{ТОРМ.РАСЧ}}}{'+
                                                                f_inom_ktt+'}}'), f'{self.i_kz_max / self.i1_base:.1f}')
        te.table_row('Максимальный тормозной ток при внешнем КЗ, A', te.m(r'I_{\text{ТОРМ.РАСЧ}}'), self.i_kz_max)
        te.table_row('Принимаем угол наклона участка торможения', te.m(r'f_1'), self.s2)
        te.table_row('Ток срабатывания дифференциальной отсечки принимаем', te.m(r'I_{\text{Д>>}}'),
                     self.id_ots)
        ib = self.i_kz_min / self.i1_base
        if ib <= ib1:
            id_fact = id
        else:
            id_fact = math.tan(f1) * (self.i_kz_min / self.i1_base - ib1) + id
        kch = self.i_kz_min / self.i1_base / id_fact
        te.table_row('Проверка чувствительности ДЗШ' + te.m(r'K_{\text{Ч}}'),
                     te.m(r'\frac{I^*_{\text{ДИФ.МИН}}}{I^*_{\text{СР.РАСЧ}}}'), f'{kch:.1f}')
        i_kz_min_pe = self.i_kz_min / self.i1_base
        te.table_row('Дифференциальный ток при минимальном токе КЗ в зоне ДЗШ ' + te.m(r'I^*_{\text{ДИФ.МИН}}'),
                     te.m(r'\frac{I_{\text{КЗ.МИН}}}{'+f_inom_ktt+r'} = \frac{'+str(self.i_kz_min)+'}{'+
                          str(self.i2_base)+r'\cdot'+str(ktt)+'}'), f'{i_kz_min_pe}')
        te.table_row('Ток срабатывания ДЗШ по характеристике при тормозном токе',
                     te.m(r'I_{\text{ТОРМ.РАСЧ}} = \frac{I_{\text{КЗ.МИН}}}{'+f_inom_ktt+'} = '+str(i_kz_min_pe)),
                     f'{id_fact:.2f}')
        id_alarm = 1.5 * self.e * self.i_overload / self.i1_base
        f_id_min = te.m(r'I_{\text{Д.МИН}}')
        te.table_row('Рассчитаем уставку контроля целостности цепей ТТ ' + f_id_min,
                     te.m(r'K_{\text{ОТС}} \cdot \varepsilon \frac{I_{\text{МАКС.ПЕРЕГР}}}{'+f_inom_ktt+
                          r'} K_{\text{ОТС}} = 1.5'),
                     f'{id_alarm:.2f}')
        te.table_row('Принимаем уставку', f_id_min, self.id_alarm)
        te.table_row(r'Рассчитаем уставку времени для контроля целостности цепей ТТ' + te.m(r'T_{\text{КЦ}}'),
                     te.m(r'T_{\text{МАКС.РЗА}} + \Delta T_{\text{ЗАП}} = ' + f'{self.t_max} + {self.dt}'),
                     self.t_max + self.dt)

    def table_settings(self, te: TextEngine):
        te.table_row(self.name, te.m(r'I_{\text{Д>}}'), self.id, '')
        te.table_row(self.name, te.m(r'I_{\text{Б1}}'), self.ib1, '')
        te.table_row(self.name, te.m(r'f_1'), self.s2, '')
        te.table_row(self.name, te.m(r'I_{\text{Д>>}}'), self.id_ots, '')
        te.table_row(self.name, te.m(r'I_{\text{Д.МИН}}'), self.id_alarm, '')
