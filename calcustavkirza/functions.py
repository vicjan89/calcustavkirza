import json
import math
import cmath
import os

from store.store import JsonStorage


import pandapower as pp
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patheffects
from matplotlib.font_manager import FontProperties
from matplotlib.collections import LineCollection, PatchCollection
from matplotlib.ticker import FixedLocator, FixedFormatter
from matplotlib.pyplot import close
import pandapower.plotting as plot
from pandapower.plotting.plotting_toolbox import get_color_list, get_linewidth_list
from matplotlib.patches import Circle
from pandas import DataFrame


def Kpk(s: float, k_nom: int) -> float:
    '''
    Рассчитывает допустимую предельную кратность трансформатора тока
    :param s: фактическая мощность на вторичной обмотке
    :param k_nom: номер характеристики (Кном=10, Кном=15 или Кном=20)
    :return: фактическая предельная кратность для фактической мощности
    '''
    characteristic = (
        (1, 47, 57, 57),
        (2.5, 35, 45, 48),
        (5, 25, 34, 38),
        (10, 15, 23, 28),
        (15, 11, 16, 22),
        (20, 9, 13, 18)
    )
    k_nom_dict = {10: 1, 15: 2, 20: 3}
    for i in range(len(characteristic)-1):
        if characteristic[i][0] <= s <= characteristic[i+1][0]:
            return characteristic[i][k_nom_dict[k_nom]] - (s - characteristic[i][0]) / (characteristic[i+1][0] - characteristic[i][0]) *\
                (characteristic[i][k_nom_dict[k_nom]] - characteristic[i+1][k_nom_dict[k_nom]])

def create_from_charact(characteristic: tuple | list):
    '''
    Создаёт функцию работающую по заданной характеристике с аппроксимацией
    :param char: характеристика в виде кортежа пар значений входных и выходных
    :return: функцию
    '''
    def a_s_charact(ikz: float) -> float:
        '''
        Возвращает время перегорания предохранителя ПКТ согласно переданной характеристике characteristic
        :param ikz: ток короткого замыкания
        :return: время перегорания предохранителя
        '''
        if ikz < characteristic[0][0]:
            return None
        for i in range(len(characteristic)-1):
            if characteristic[i][0] <= ikz <= characteristic[i+1][0]:
                return characteristic[i][1] - (ikz - characteristic[i][0]) / (characteristic[i+1][0] - characteristic[i][0]) *\
                    (characteristic[i][1] - characteristic[i+1][1])
    return a_s_charact

def make_spread_iec_charact(char_iec, inom):
    '''
    Возвращает кортеж из двух характеристик ограничивающих предели разброса реальной характеристики
    :param char_iec:
    :param inom:
    :return:
    '''
    char_iec_min = [(k * inom, min_value) for k, min_value, max_value in char_iec]
    char_iec_max = [(k * inom, max_value) for k, min_value, max_value in char_iec]
    iec_min = create_from_charact(char_iec_min)
    iec_max = create_from_charact(char_iec_max)
    return (iec_min, iec_max)


def create_time_dependent(isz: float, k: int):
    '''
    Создаёт функцию работающую по заданной формулой характеристике
    :param isz: ток срабатывания
    :param k: коэффициент, характеризующий вид зависимой характеристики
    :return: функцию
    '''
    def a_s_charact(ikz: float) -> float:
        '''
        Возвращает время срабатывания защиты
        :param ikz: ток короткого замыкания
        :return: время
        '''
        if ikz < isz:
            return None
        return k / 100 / (ikz/isz - 0.6)

    return a_s_charact

def create_time_independent(isz: float, tsz: float):
    '''
    Создаёт функцию ступени защиты с независимой от тока временной характеристикой с заданными параметрами срабатывания
    :param isz: ток срабатывания
    :param tsz: время срабатывания
    :return: функция ступени защит
    '''
    def time_independent(ikz: float) -> float:
        '''
        Функция ступени защиты с независимой от тока временной характеристикой
        :param ikz: ток короткого замыкания
        :return: время срабатывания защиты
        '''
        if ikz < isz:
            return 1000
        else:
            return tsz

    return time_independent

def mix_charact(charact: list | tuple):
    '''
    Создаёт функцию возвращающую наименьшее время полученное из всех входных функций по заданному току
    :param charact: кортеж функций
    :return: итоговую функцию
    '''
    def a_s_charact(ikz: float) -> float:
        '''
        Возвращает наименьшее время срабатывания защит
        :param ikz: ток короткого замыкания
        :return: время
        '''
        t = None
        for func in charact:
            t_current = func(ikz)
            if t_current is not None:
                if t is not None:
                    if t > t_current:
                        t = t_current
                else:
                    t = t_current
        return t

    return a_s_charact
def make_selectivity_map(functions_list: list, labels: list, i_begin, i_end, name_file, time_max=1.5):
    '''
    Создаёт график в формате png с ампер-секундными характеристиками защит
    :param functions_list: список функций для характеристик
    :param labels: список подписей для характеристик
    :param i_begit: начальный ток графика
    :param i_end: конечный ток графика
    '''
    step = (i_end-i_begin)/300
    i_list = [i*step+i_begin for i in range(300)]
    fig, ax = plt.subplots()
    fig.set_figheight(7)
    fig.set_figwidth(8)
    for num, func in enumerate(functions_list):
        func_list = [func(i) for i in i_list]
        ax.plot(i_list, func_list, color=f'C{num}', label=labels[num])
    ax.set_xlabel("Iкз,A", fontsize=13)
    ax.set_ylabel("t,сек", fontsize=13)
    ax.set_ylim(ymin=0, ymax=time_max)
    ax.minorticks_on()
    ax.grid(which='major', lw=1)
    ax.grid(which='minor', lw=0.5)
    plt.legend()
    plt.savefig(name_file+'.png',  format="png", dpi=1000)
    close()

def make_selectivity_map_spread(functions_list: list, labels: list, i_begin, i_end, name_file, time_max=1.5):
    '''
    Создаёт график в формате png с ампер-секундными характеристиками защит
    :param functions_list: список функций для характеристик
    :param labels: список подписей для характеристик
    :param i_begit: начальный ток графика
    :param i_end: конечный ток графика
    '''
    step = (i_end-i_begin)/300
    i_list = [i*step+i_begin for i in range(300)]
    fig, ax = plt.subplots()
    for num, func in enumerate(functions_list):
        func_list_min = []
        func_list_max = []
        x = []
        for i in i_list:
            y1 = func[0](i)
            y2 = func[1](i)
            if y1 and y2:
                func_list_min.append(y1)
                func_list_max.append(y2)
                x.append(i)
        ax.fill_between(x=x, y1=func_list_min, y2=func_list_max, alpha=0.5, label=labels[num])
    ax.set_xlabel("Iкз,A", fontsize=13)
    ax.set_ylabel("t,сек", fontsize=13)
    ax.set_ylim(ymin=0, ymax=time_max)
    ax.minorticks_on()
    ax.grid(which='major', lw=1)
    ax.grid(which='minor', lw=0.5)
    plt.legend()
    plt.savefig(name_file+'.png',  format="png", dpi=1000)
    close()

def make_selectivity_map_all(functions_list: list, labels: list, i_nagr: list, i_begin, i_end, name_file, time_max=1.5, title=''):
    '''
    Создаёт график в формате png с ампер-секундными характеристиками защит
    :param functions_list: список функций для характеристик
    :param labels: список подписей для характеристик
    :param i_nagr: список токов нагрузки протекающих через защиту для сдвига характеристики
    :param i_begin: начальный ток графика
    :param i_end: конечный ток графика
    '''
    step = (i_end-i_begin)/300
    labels_with_cr = []
    for label in labels:
        for limit in (40, 80, 120, 160):
            if len(label) > limit:
                index = label[:limit].rfind(' ')
                label = label[:index] + '\n' + label[index+1:]
            else:
                break
        labels_with_cr.append(label)
    i_list = [i*step+i_begin for i in range(300)]
    fig, ax = plt.subplots(figsize=(7, 10))
    plt.title(title)
    for num, func in enumerate(functions_list):
        if isinstance(func, tuple):
            func_list_min = []
            func_list_max = []
            x = []
            for i in i_list:
                y1 = func[0](i + i_nagr[num])
                y2 = func[1](i + i_nagr[num])
                if y1 is not None and y2 is not None:
                    func_list_min.append(y1)
                    func_list_max.append(y2)
                    x.append(i)
            ax.fill_between(x=x, y1=func_list_min, y2=func_list_max, alpha=0.5, label=labels_with_cr[num], color=f'C{num}')
        else:
            func_list = [func(i + i_nagr[num]) for i in i_list]
            ax.plot(i_list, func_list, color=f'C{num}', label=labels_with_cr[num])
    ax.set_xlabel("Iкз,A", fontsize=13)
    ax.set_xlim(xmin=0, xmax=i_end)
    ax.set_yscale('log')
    ax.set_ylabel("t,сек", fontsize=13)
    ax.set_ylim(ymin=0, ymax=time_max)
    ax.minorticks_on()
    ax.grid(which='major', lw=1)
    ax.grid(which='minor', lw=0.5)
    lgd = plt.legend(loc='best') #, bbox_to_anchor=(0.5, -0.05))
    plt.savefig(name_file+'.png',  format="png", dpi=1000, bbox_extra_artists=(lgd,), bbox_inches='tight')
    close()

def compose_selectivity_map(prisos: list, characts, labels, i_begin, i_end, name_file, time_max=1.5):
    '''
    Компанует графики уставок и графики характеристик срабатывания защит
    :param prisos: список данных для присоединений
    :param characts: характеристики для отображения совместно с уставками
    :param labels: список подписей для характеристик
    :param i_begin: начальный ток графика
    :param i_end: конечный ток графика
    :param name_file: имя файла для сохранения графика
    :return:
    '''
    # prot_name = {'mtz': 'МТЗ', 'to_t': 'ТО с t', 'lzsh': 'ЛЗШ', 'to': 'ТО'}
    # time_prot = ('mtz', 'to_t', 'lzsh')
    # no_time_prot = ('to',)
    for pris in prisos:
        characts_for_mix = []
        names = []
        for z in pris.get_protections():
            if z.time_prot:
                if z.k:
                    characts_for_mix.append(create_time_dependent(z.isz, z.k))
                else:
                    characts_for_mix.append(create_time_independent(z.isz, z.t))
            else:
                characts_for_mix.append(create_time_independent(z.isz, 0))
            names.append(z.name)
        names = ','.join(names)
        names = f'({names})'
        characts.append(mix_charact(characts_for_mix))
        labels.append(f"{pris.name}\n{names}")
    make_selectivity_map_all(characts, labels, i_begin, i_end, name_file, time_max=time_max)


def plot_dzt_char(dzt: dict, name_file: str = None):
    ib1 = dzt['id']/math.tan(math.radians(dzt['f1']))
    ib2 = dzt['Kperegr']*2
    id2 = ib2*math.tan(math.radians(dzt['f1']))
    ib3 = ib2 + (dzt['ido'] - id2)/math.tan(math.radians(dzt['f2']))
    ib4 = int(ib3 + 3)
    torm = [0, ib1, ib2, ib3, ib4]
    x_ticks = [f'Iб1={ib1:.3f}', f'Iб2={ib2:.3f}', f'Iб3={ib3:.3f}', torm[-1]]
    y_ticks = [f'Id>={dzt["id"]}', f'Id>2={id2:.3f}', f'Id>>={dzt["ido"]}']
    dif = [dzt['id'], dzt['id'], id2, dzt['ido'], dzt['ido']]
    fig = plt.figure(figsize=(14, 8))
    ax = fig.add_subplot()
    ax.loglog(torm, dif, 'r')
    ax.minorticks_on()
    ax.xaxis.set_major_locator(FixedLocator(torm[1:]))
    ax.xaxis.set_major_formatter(FixedFormatter(x_ticks))
    ax.yaxis.set_major_locator(FixedLocator(dif[1:-1]))
    ax.yaxis.set_major_formatter(FixedFormatter(y_ticks))

    ax.xaxis.set_minor_locator(FixedLocator((1,2,4,5,6,7,8,9,10,11,12,13)))
    ax.xaxis.set_minor_formatter(FixedFormatter((1,2,4,5,6,7,8,9,10,11,12,13)))
    ax.yaxis.set_minor_locator(FixedLocator(range(1, int(dzt["ido"]))))
    ax.yaxis.set_minor_formatter(FixedFormatter(range(1, int(dzt["ido"]))))

    ax.grid(which='major', lw=1)
    ax.grid(which='minor', lw=0.5, linestyle=':')

    if name_file:
        plt.savefig(name_file + '.png', format="png", dpi=500)
    else:
        plt.show()

def get_z1_trafo(tr: DataFrame):
    '''
    Возвращает данные для расчёта тока однофазного КЗ за трансформатором 6...10.5/0.4кВ со схемой соединения обмоток
    звезда-звезда на основе таблицы из книги Шабада
    :param tr: данные трансформатора в формате Series pandas
    :return: кортеж из сопротивления петли фаза-ноль 1/3 z(1)т, номинального напряжения НН, номинального напряжения ВН
    в вольтах
    '''
    s = tr['sn_mva']
    u_hv = tr['vn_hv_kv']
    if 6 <= u_hv <= 10.5:
        z = {0.025: 1.04,
             0.04: 0.65,
             0.063: 0.41,
             0.1: 0.26,
             0.16: 0.16,
             0.25: 0.1,
             0.4: 0.065,
             0.63: 0.042,
             1: 0.027,
             1.6: 0.018}
        return z[s], tr['vn_lv_kv']*1000, u_hv*1000

def charact_IEC60255_151(ir, tr, k, c, a, i): #https://product-help.schneider-electric.com/ED/MTZ/Micrologic_X_User_Guide/EDMS/DOCA0102EN/DOCA0102xx/ProtectionFunctions/ProtectionFunctions-21.htm
    t6 = k / ((6 / 1.125) ** a - 1) + c
    ti = k / ((i / 1.125 / ir) ** a - 1) + c
    t = tr / t6 * ti
    return t if t > 0 else 10000

def charact_IEC60255_151type(inom, ir, tr, type: str):
    k, c, a = {'SIT': (0.14, 0, 0.02),
               'VIT': (13.5, 0, 1),
               'EIT': (80, 0, 2),
               'HVF': (80, 0, 4)}[type]
    def charact(i):
        i = i / inom / ir
        return charact_IEC60255_151(ir, tr, k, c, a, i)
    return charact
