import math
from itertools import groupby
from typing import Any

from pydantic import ConfigDict
from textengines.interfaces import TextEngine

from calcustavkirza.classes import Element
from calcustavkirza.Pris import Pris
from calcustavkirza.select.CT import CT, ct_metods
from calcustavkirza.select.DC import DC
from calcustavkirza.classes import Element, Doc
from store.store import JsonStorage
from calcustavkirza.electro_store import ProjectStore


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

class Project:

    def __init__(self, project_store: ProjectStore, te: TextEngine):
        self.project_store = project_store
        self.te = te

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

    def calc_settings(self):
        res_sc_max, res_sc_min = self.project_store.res_sc
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

        self.te.h1('Расчёт и выбор уставок РЗА')
        prises = [Pris(te, pris_store, res_sc_min, res_sc_max) for pris_store in self.project_store.prises(order='name')]
        for pris in prises:
            pris.calc_settings()
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


    def ap_general_part(self, te: TextEngine):
        te.h1('Общие сведения')
        te.p(f'В данном разделе проекта приводятся решения по организации {self.volume}.')
        te.p('Проектная документация разработана на основании:')
        docs = [f'{doc.name};' for doc in self.localdocs.all()]
        if docs:
            docs[-1] = f'{docs[-1][0:-1]}.'
        for doc in docs:
            te.ul(doc)
        te.h2('Перечень нормативных документов')
        te.p('Технические решения, принятые в данном разделе архитектурного проекта, отвечают требованиям следующих '
             'руководящих и нормативных документов:')
        docs = [f'{doc.code} "{doc.name}";' for doc in self.normativedocs.all()]
        if docs:
            docs[-1] = f'{docs[-1][0:-1]}.'
        for doc in docs:
            te.ul(doc)
        te.h1('Общие положения по выполнению РЗА')
        te.p('Решения по выполнению комплекса РЗА разрабатывались с учетом требований ПУЭ, норм технологического '
             'проектирования и других нормативных документов, действующих на момент разработки данного проекта.')
        te.p('Комплексы РЗА должны выполняться в соответствии с действующими в РБ нормативными материалами и '
             'обеспечивать предъявляемые к ним требования по надежности, быстродействию, селективности и чувствительности.')
        te.p('Повышение надежности РЗА защищаемых элементов обеспечивается:')
        if self.protection_terminal_reservation:
            te.ul('установкой на каждом защищаемом элементе двух комплексов защит;')
            te.ul('разделением комплексов защит по цепям переменного тока, переменного напряжения и оперативного постоянного тока;')
            te.ul('размещение устройств, резервирующих друг друга, в разных шкафах.')
            te.p('Разделение по цепям переменного тока предполагает подключение комплексов РЗА, резервирующих друг друга, к '
                 'разным вторичным обмоткам трансформаторов тока. Цепи переменного тока выполняются отдельными '
                 'экранированными кабелями проложенными, по возможности в разных кабельных каналах.')
        te.ul('использованием УРОВ;')
        te.ul('выполнением дальнего резервирования.')
        if self.operating_current_distribution_cabinet:
            te.p('Каждое устройство РЗА питается от отдельного автоматического выключателя в шкафу распределения '
                 'оперативного постоянного тока.')
        te.p('Так как выключатели имеют два электромагнита отключения, действие устройств РЗА '
             'выполняется на оба электромагнита. Наличие двух электромагнитов отключения снижает общее количество '
             'отказов выключателей, а также увеличивает надежность отключения КЗ. ' +
             ('Питание схем управления электромагнитов отключения по цепям постоянного оперативного тока осуществляется от разных ' +
              ('аккумуляторных батарей' if self.two_batteries else 'секций ЩПТ') +
              ' через шкафы распределения оперативного постоянного тока. Цепи отключения от каждого ' 
              'устройства РЗА выполняются отдельными экранированными кабелями, проложенными по возможности в разных ' 
              'кабельных каналах.' if self.operating_current_distribution_cabinet else ''))
        te.p('Во всех цепях, прямо или косвенно действующие на отключение или пуск УРОВ присоединения, должны '
             'предусматриваться переключающие устройства.')
        te.p('Во всех микропроцессорных (МП) устройствах РЗА предусмотрена светодиодная сигнализация.')
        te.p('Все устройства РЗА должны быть выполнены на микропроцессорной элементной базе')
        te.p('Для работы с МП устройствами РЗА на ПС предусматривается поставка программного обеспечения, техническая '
             'документация на русском языке и необходимые кабели для подключения ноутбука к терминалам защит.')
        te.p('При установке МП устройств на подстанции должны быть выполнены все регламентированные требования по '
             'электромагнитной совместимости и помехозащищенности.')
        te.p('Во всех цепях дискретных входов и высокоомных реле, выходящих за пределы шкафа, должны быть предусмотрены '
             'шунтирующие резисторы для снижения импульсных помех и наводок. Номинальное сопротивление шунтирующих '
             'резисторов должно обеспечивать нормальную работу устройства контроля изоляции сети оперативного тока.')
        te.p(f'Прокладки кабелей связей и схема подключения терминалов защит в сеть приведены в разделе  '
             f'СЕАВ.{self.code}-АСУ.')

    def ap_voltage_circuits(self, te: TextEngine):
        te.h1('Организация цепей напряжения')
        te.p('Для организации цепей напряжения в РУ 10 кВ устанавливаются:')
        te.ul('трехфазный ТН на каждой секции шин 10 кВ;')
        if self.vt_section_input:
            te.ul('трехфазный ТН на ошиновке каждой обмотки 10 кВ трансформатора (устанавливается в ячейке ввода 10 кВ).')
        te.p('Шинный ТН 10 кВ имеет 3 вторичные обмотки: 1-ая используется для учета; 2-ая – для защиты и измерения; '
             '3-ая – для защиты нулевой последовательности. 1-ая и 2-ая вторичные обмотки подключаются по схеме '
             '«звезда», 3-ая – по схеме «разомкнутый треугольник». В обмотках, соединенных в звезду, заземляется '
             'фаза «B». В обмотке, соединенной в разомкнутый треугольник, заземляется фаза «K». Заземление '
             'выполняется в ячейке ТН.')
        if self.vt_section_input:
            te.p('ТН, устанавливаемый до ввода 10 кВ, аналогичен шинному, но имеет 2 вторичные обмотки: 1-ая '
                 'используется для резервирования цепей защиты и измерения, а также для терминала АВР-10; 2-ая – для '
                 'контроля 3U0. 1-ая вторичная обмотка подключаются по схеме «звезда», 2-ая – по схеме «разомкнутый '
                 'треугольник».')
        te.p('Для обеспечения безопасности при работах в цепях напряжения предусматривается установка испытательных '
             'блоков. Для защиты вторичных цепей от КЗ предусматривается установка во всех незаземленных фазах '
             'автоматических выключателей. Данные коммутационные аппараты предусматриваются отдельно для каждой из '
             'обмоток ТН и устанавливаются в релейных отсеках ячеек, в которых установлен ТН. Предусматривается контроль '
             'положения данных аппаратов посредством вспомогательных контактов. Сигналы о положении защитных автоматов '
             'ТН секций шин 10 кВ передаются в терминалы автоматики ТН 10 кВ соответствующих секций.' +
             ' Сигналы о положении защитных автоматов ТН, устанавливаемых до вводов 10 кВ, передаются в терминалы РЗА '
             'вводов 10 кВ соответствующих секций.' if self.vt_section_input else '')
        te.p('Цепи напряжения ТН-10 кВ прокладываются шинками по всем ячейкам КРУ 10 кВ.' +
             (' Предусматривается резервирование цепей напряжения между шинным ТН и ТН, установленным до ввода 10 кВ.' if
             self.vt_section_input else 'Резервирование цепей напряжения не предусматривается.'))

    def ap_avr(self, te: TextEngine):
        if self.un % 10:
            un = f'{self.un}'
        else:
            un = f'{self.un:.0f}'
        te.h1(f'АВР {un} кВ')
        te.p(f'Для организации логики автоматического включения резерва {un} кВ используются микропроцессорные терминалалы '
             f'вводов на секции, секционного выключателя и трансформаторов напряжения.')
        te.p(f'В нормальном режиме работы секционный выключатель отключен. Пуск АВР происходит при '
             f'выполнении всех последующих условий:')
        te.ul(f'отсутствие напряжения на контролируемой секции шин {un} кВ и наличие напряжения на соседней '
              f'секции шин. Отсутствие напряжения на своей секции и наличие напряжения на соседней секции принимается '
              f'«сухими контактом» от терминала автоматики ТН-{un} кВ соответствующей секции;')
        te.ul('отсутствие запрещающих факторов (работа ЛЗШ, УРОВ, ЗДЗ);')
        te.ul('введенное положение переключателя АВР.')
        te.p('После пуска АВР начинается отсчёт выдержки времени АВР, по истечении которой происходит отключение '
             'вводного выключателя секции шин и включение секционного выключателя. Автоматический возврат схемы '
             'производится в случае появления напряжения со стороны питания вводного выключателя на секцию шин. '
             'При этом производится с выдержкой времени отключение секционного выключателя и включение вводного выключателя.')
        te.p('Микропроцессорные терминалы ТН формируют сигналы пуска АВР только после проверки исправности цепей ТН '
             '(включенное положение автоматического выключателя ТН, отсутствие напряжения обратной последовательности).')

    def ap_generate(self, te: TextEngine):
        un = str(self.un) if self.un % 1 else f'{self.un:.0f}'
        self.ap_general_part(te)
        self.ap_voltage_circuits(te)
        if self.avr:
            self.ap_avr(te)
        if self.pris:
            for pris in self.pris.all():
                pris.ap_generate(te)
        if self.zdz:
            te.h1(f'Дуговая защита ячеек РУ-{un}')
            te.p(f'Для защиты ячеек РУ-{un} кВ от коротких замыканий, сопровождаемых открытой электрической дугой, '
                 f'предусматривается установка оптоволоконной дуговой защиты для каждой секции шин {un} кВ. '
                 f'Оптоволоконная дуговая защита предусматривается в виде отдельного независимого комплекса дуговой '
                 f'защиты, имеющего в своем составе центральный терминал, модули дуговой защиты и оптические датчики. '
                 f'Оптические датчики подключаются к модулям дуговой защиты. Оптические датчики устанавливаются в '
                 f'отсеке сборных шин, отсеке выкатного элемента и кабельном отсеке ячеек {un} кВ. Модули '
                 f'дуговой защиты выполняют следующие функции:')
            te.ul(f'контроль наличия электрической дуги в ячейках РУ-{un} кВ посредством оптических датчиков;')
            te.ul('контроль целостности оптоволокна, соединяющего оптические датчики и модули дуговой защиты;')
            te.ul('замыкание собственных выходных реле для воздействия в различные цепи.')
            te.p('Дуговая защита действует по следующему алгоритму:')
            te.ul(f'при срабатывании оптического датчика в любом отсеке отходящего присоединения {un} кВ, '
                  f'ввода {un} кВ или СВ {un} кВ производится его отключение без контроля по току;')
            te.ul(f'при превышении тока через ввод {un} кВ или СВ {un} кВ больше заданной уставки пуска ЗДЗ '
                  f'и сработанном датчике дуговой защиты любого присоединения {un} кВ производится отключение '
                  f'ввода {un} кВ или СВ {un} кВ соответственно.')
        if self.rzn:
            te.h1(f'Организация защиты от ОЗЗ в сети {un} кВ')
            if self.rp:
                tznp_cb = (f' Данная резервная защита  на {self.name} выполняется измерительными органами вводов {un} кВ '
                          f'подключенными к их трансформаторам тока нулевой последовательности с действием на отключение секционного '
                          f'выключателя {un} кВ с меньшей выдержкой времени и на отключение собственного вводного '
                          f'выключателя с большей выдержкой времени. ')
            else:
                tznp_cb = (f' Данная резервная защита выполняется отдельными токовыми ступенями в устройствах '
                 f'защиты вводов 10 кВ и секционных выключателей и по токовым цепям подключается к ТТ в цепи '
                 f'заземляющего резистора. В терминале РЗА СВ {un} кВ защита от ОЗЗ выполняется ненаправленной с '
                 f'действием на отключение выключателя. В терминале РЗА ввода {un} кВ защита от ОЗЗ выполняется '
                 f'ненаправленной с действием на отключение выключателя. Время срабатывания данной защиты отстраивается от времени '
                 f'срабатывания защиты от ОЗЗ на отходящих присоединениях и СВ-{un}.')
            te.p(f'На {self.name_ss} организуется резистивное заземление нейтрали сети {un} кВ. Для этих целей на '
                 f'каждую секцию шин {un} кВ устанавливается заземляющий резистор сопротивлением {self.rzn} Ом. '
                 f'Селективность защит нулевой последовательности присоединений определяется тем, что активная '
                 f'составляющая тока ОЗЗ протекает через повреждённое присоединение и присоединение заземляющего '
                 f'резистора, в то время как через остальные присоединения протекает собственный ёмкостный ток нулевой '
                 f'последовательности, от которого защита присоединения отстраивается. Защита от ОЗЗ для присоединений '
                 f'отходящих линий {un} кВ, подключенных к сборным шинам через выключатель, выполняется '
                 f'ненаправленной (при малом емкостном токе линии) или направленной, реагирующей на активную '
                 f'составляющую тока (при большом емкостном токе линии), с действием на отключение выключателя. Опорным '
                 f'напряжением для определения направления является измеренное напряжение нулевой последовательности. '
                 f'Защита от ОЗЗ для присоединений заземляющего резистора выполняется направленной, реагирующей на '
                 f'емкостную составляющую тока, с действием на отключение выключателя. Опорным напряжением для '
                 f'определения направления является измеренное напряжение нулевой последовательности. В случае отказа '
                 f'защит отходящих присоединений по отключению поврежденного присоединения, а также при ОЗЗ на '
                 f'сборных шинах и кабельных разделках предусматривается резервная защита от ОЗЗ с целью защиты '
                 f'резистора от термического повреждения и предотвращения длительной работы сети в режиме ОЗЗ с большим '
                 f'током повреждения.' + tznp_cb + 'Время срабатывания данной защиты отстраивается от времени '
                 f'срабатывания защиты от ОЗЗ на отходящих присоединениях. При работе данного вида '
                 f'защиты выполняется запрет АВР {un} кВ. ')
        te.h1('Управление коммутационными аппаратами')
        disc_contr = 'разъединителями и заземляющими ножами ' if self.disconnector_motor_control else ''
        te.p(f'Оперативное управление выключателями, {disc_contr}осуществляется из АСУ оперативным персоналом в режиме '
             f'дистанционного управления или с помощью ключей управления в режиме местного управления.')
# В КРУЭ 110 кВ на шкафах управления выполняется мнемосхема подстанции с ключами управления для элементов присоединений
# 110 кВ и индикацией положения коммутационных аппаратов.
        te.p(f'Ключи управления выключателями присоединений {un} кВ и лампочки индикации положения коммутационных '
             f'аппаратов располагаются на дверях релейных отсеков соответствующих ячеек.')
        te.p('Команды включения выключателей обрабатываются терминалами защиты и автоматики соответствующих '
             'присоединений, в которых выполняется контроль всех параметров выключателя и дополнительных условий '
             'включения.')
        te.p('Отключение выключателей происходит через два соленоида отключения, запитанных от разных автоматических '
             'выключателей шинок управления.')
# Управление приводами РПН трансформаторов в нормальном режи-ме работы осуществляется в автоматическом режиме устройствами
# АРН. Оперативное управление данными приводами осуществляется из АРМ оперативного персонала в режиме дистанционного
# управления или с помощью ключей управления в режиме ручного управления. Ключи управления приводами РПН трансформаторов
# располагаются в шкафу с терми-налами АРН. Команды ручного управления приводами РПН обрабатыва-ются терминалами АРН,
# в которых выполняется контроль всех парамет-ров привода РПН.
        te.p(f'Оперативное управление выкатными элементами и заземляющими ножами ячеек КРУ {un} кВ осуществляется '
             f'по месту.')
        te.p('Управление заземляющими ножами и выкатными элементами возможно только при наличии разрешающего сигнала '
             'от оперативной блокировки.')

        te.h1('Оперативная блокировка')
        te.p('Оперативная блокировка элементов распредустройства выполняется заводом-изготовителем ячеек распредустройства.')
        te.p('Механическая блокировка непосредственного действия не требует питания и реализует сделующие функции:')
        te.ul('блокировка выкатывания тележки выключателя при включенном выключателе;')
        te.ul('отключение выключателя при попытке выкатывания тележки;')
        te.ul('блокировка включения линейного заземляющего ножа при вкаченной тележке выключателя.')
        te.p('Электромагнитная блокировка питается от ШОТ и выполняет сделующие функции:')
        te.ul('блокировка оперирования заземляющими ножами сборных шин при нахождении хотя-бы одной выкатной тележки '
              'в рабочем положении;')
        te.ul('блокировка вкатывания тележек выключателей при включенных заземляющих ножах сборных шин;')
        te.ul('блокировка оперирования заземляющими ножами секционной перемычки при нахождении при рабочем положении '
              'тележки СР')
        te.ul('блокировка вкатывания тележки СР при включенных заземляющих ножах секционной перемычки;')
        te.p('Распределение оперативного тока электромагнитной блокировки выполняется посредством кроссовых шинок '
              'проложенным в релейных отсеках ячеек распредустройства.')

        for dc in self.dc.all():
            dc.ap_generate(te)

        first = True
        data_for_table_check_sc_term = {}
        data_for_table_check_sc_din = {}
        js = JsonStorage(self.path_res_sc[:-5])
        res_sc = None
        for pris in self.pris.filter(ctpris__isnull=False):
            if first:
                te.h1('Выбор и проверка трансформаторов тока')
                first = False
                ct_metods(te)
                te.h2('Проверка трансформаторов тока')
            res_sc = None
            for ctpris in pris.ctpris.all():
                if pris.i_kz_max_index:
                    if not res_sc:
                        res_sc = js.read()
                    isc =res_sc[0][1][str(pris.i_kz_max_index)][1]
                else:
                    isc = pris.ikz_max
                pris_for_table_check_sc_term = (ctpris.ct.mark, ctpris.ct.i_term, round(isc,1), pris.tsz, pris.isz_max,
                                                pris.tsz2)
                pris_for_table_check_sc_din = (ctpris.ct.mark, ctpris.ct.i_din, round(isc,1), pris.ku)
                if pris_for_table_check_sc_term in data_for_table_check_sc_term:
                    data_for_table_check_sc_term[pris_for_table_check_sc_term].append(pris.name)
                else:
                    data_for_table_check_sc_term[pris_for_table_check_sc_term] = [pris.name]
                if pris_for_table_check_sc_din in data_for_table_check_sc_din:
                    data_for_table_check_sc_din[pris_for_table_check_sc_din].append(pris.name)
                else:
                    data_for_table_check_sc_din[pris_for_table_check_sc_din] = [pris.name]
        if data_for_table_check_sc_term:
            te.table_name('Проверка ТТ на стойкость к термическому действию токов КЗ')
            te.table_head('Место установки/ модель', 'Односекундный ток термической стойкости, кА',
                          'Номинальный тепловой импульс, кА²·сек', 'Ток КЗ, кА',
                          'Время отключения, сек', 'Тепловой импульс, кА²·сек', widths=(3, 1, 1, 1, 1, 1))
            for data, name in data_for_table_check_sc_term.items():
                impuls_nom = f'{data[1] ** 2:.1f}' if data[1] else 'Нет данных'
                impuls_real = f'{(data[2] / 1000) ** 2 * data[3]:.1f}' if data[3] and data[2] else 'Нет данных'
                impuls_real2 = f'{(data[4] / 1000) ** 2 * data[5]:.1f}' if data[4] and data[5] else None
                pris_names = ', '.join(name) + f' {data[0]}'
                te.table_row(pris_names, data[1], impuls_nom, f'{data[2] / 1000:.2f}', data[3],
                             impuls_real)
                if impuls_real2:
                    te.table_row(pris_names, data[1], impuls_nom, f'{data[4] / 1000:.2f}', data[5],
                                 impuls_real2)
        if data_for_table_check_sc_din:
            te.table_name('Проверка ТТ на стойкость к динамическому действию токов КЗ')
            te.table_head('Место установки/ модель', 'Ток динамической стойкости, кА', 'Ток КЗ, кА',
                          'Ударный коэффициент', 'Ударный ток КЗ, кА', widths=(3, 1, 1, 1, 1))
            for data, name in data_for_table_check_sc_din.items():
                isc_udarn = f'{data[2] / 1000 * data[3] * math.sqrt(2):.1f}' if data[3] and data[2] else 'Нет данных'
                te.table_row(', '.join(name) + f' {data[0]}', data[1], f'{data[2] / 1000:.1f}', data[3],
                             isc_udarn)

        data_for_table_check_power_ct = {}
        data_for_table_check_errors = {}
        data_for_table_check_ir_umax = {}
        data_total = {}
        for pris in self.pris.filter(ctpris__isnull=False):
            for ctpris in pris.ctpris.all():
                wind_total = []
                for ctload in ctpris.loadct.all():
                    power_total = 0.
                    power_names = []
                    for deviceset in ctload.deviceset.all():
                        power_names.append(f'{deviceset.device.name} ({deviceset.device.power_consumption_ct}x{deviceset.quantity})')
                        power_total += deviceset.device.power_consumption_ct * deviceset.quantity
                    pris_for_table_check_power_ct = (ctload.ctw.accuracy, ctload.ctw.sn, power_total, ', '.join(power_names))
                    if pris_for_table_check_power_ct in data_for_table_check_power_ct:
                        data_for_table_check_power_ct[pris_for_table_check_power_ct].append(pris.name)
                    else:
                        data_for_table_check_power_ct[pris_for_table_check_power_ct] = [pris.name]
                    if ctload.ctw.accuracy in ('5P', '10P'):
                        zn = ctload.ctw.sn / (ctload.ctw.i2 ** 2)
                        z_real = power_total / (ctload.ctw.i2 ** 2)
                        sin_phi = math.sin(math.acos(ctload.ctw.cos))
                        kn_real =  ctload.ctw.kn * math.sqrt((ctload.ctw.r2 + ctload.ctw.cos * zn) ** 2 + (sin_phi * zn) ** 2) / (
                                ctload.ctw.r2 + z_real)
                        i_max_calc = pris.isz_max * 1.1 / pris.k_circuit
                        pris_for_table_check_errors = (ctload.ctw.kn, ctload.ctw.r2, pris.isz_max, kn_real,
                                                       i_max_calc, ctload.ctw.i1, ctload.ctw.accuracy, ctload.ctw.sn)
                        if pris_for_table_check_errors in data_for_table_check_errors:
                            data_for_table_check_errors[pris_for_table_check_errors].append(pris.name)
                        else:
                            data_for_table_check_errors[pris_for_table_check_errors] = [pris.name]
                    if pris.i_kz_max_index:
                        if not res_sc:
                            res_sc = js.read()
                        isc = res_sc[0][1][str(pris.i_kz_max_index)][1]
                    pris_for_table_check_ir_umax = (ctload.ctw.i1, ctload.ctw.i2, pris.imax,
                                                    power_total / (ctload.ctw.i2 ** 2), pris.imax, isc, pris.k_circuit,
                                                    ctload.ctw.accuracy)
                    if pris_for_table_check_ir_umax in data_for_table_check_ir_umax:
                        data_for_table_check_ir_umax[pris_for_table_check_ir_umax].append(pris.name)
                    else:
                        data_for_table_check_ir_umax[pris_for_table_check_ir_umax] = [pris.name]
                    wind_total.append((ctload.ctw.i1, ctload.ctw.i2, ctload.ctw.accuracy, ctload.ctw.sn, ctload.ctw.kn))
                pris_total = (ctpris.ct.mark, ctpris.ct.i1, ctpris.ct.i_term, ctpris.ct.i_din, tuple(wind_total))
            if pris_total in data_total:
                data_total[pris_total].append(pris.name)
            else:
                data_total[pris_total] = [pris.name]
        if data_for_table_check_power_ct:
            te.table_name('Проверка мощности обмоток')
            te.table_head('Место установки', 'Класс точности / мощность обмотки, ВА', 'Мощности нагрузок, Вт',
                          widths=(2, 1, 3))
            for data, name in data_for_table_check_power_ct.items():
                te.table_row(', '.join(name), f'{data[0]} / {data[1]}', f'{data[3]} = {data[2]}')

        if data_for_table_check_errors:
            te.table_name('Проверка обмоток ТТ на 10% погрешность')
            te.table_head('Место установки (класс точности /мощность)', 'Кп/ Fs',
                          'Сопротивление вторичной обмотки, Ом', 'K10доп', 'Ток срабатывания защиты максимальный, А',
                          'Iмакс. расч,А', 'Kмакс. рас', widths=(2, 1, 1, 1, 1, 1, 1))
            for data, name in data_for_table_check_errors.items():
                te.table_row(', '.join(name) + f' ({data[6]} / {data[7]})', data[0], data[1], f'{data[3]:.1f}',
                             data[2], f'{data[4]:.1f}', f'{data[4] / data[5]:.1f}')
        if data_for_table_check_ir_umax:
            te.table_name('Проверка обмоток по току нагрузки и условию отсутствия опасных перенапряжений во вторичных цепях ТТ')
            te.table_head('Место установки (Ктт, кл.точ.)', 'Ток нагрузки максимальный, А', 'Загрузка, %',
                          'Полное сопротивление нагрузки, Ом', 'Iмакс.кз, А', 'Напряжение, В', widths=(3, 1, 1, 1, 1, 1))
            for data, name in data_for_table_check_ir_umax.items():
                te.table_row(', '.join(name) + f' ({data[0]}/{data[1]}, {data[7]})', data[2], f'{data[2]/data[0]*100:.1f}%',
                             f'{data[3]:.3f}', f'{data[5]:.1f}', f'{data[5] / data[0] * data[1] * data[6] * data[3]:.1f}')

        te.h2('Выбранные трансформаторы тока')
        te.table_name('Выбранные трансформаторы тока с параметрами обмоток')
        # te.table_head('Место установки', 'Марка', 'Ктт', 'Класс точности', 'Мощность обмотки, ВА', 'Kп (Fs)',
        te.table_head('Место установки', 'Марка', 'Номи- нальный ток, А',
                      'Ктт; класс точности; мощность обмотки, ВА; Kп/Fs',
                      'Ток терми- ческой стойкости (1сек), кА', 'Ток динами- ческой стойкости, кА',
                      widths=(3, 1, 1, 3, 1, 1))
        for data, name in data_total.items():
            winds_data = [f'({w[0]}/{w[1]}; {w[2]}; {w[3]}; {w[4]})' for w in data[4]]
            te.table_row(', '.join(name), data[0], data[1], ', '.join(winds_data), data[2], data[3])


        first = True
        data_for_check_du = {}
        for pris in self.pris.filter(vtpris__isnull=False):
            if first:
                te.h1('Выбор и проверка трансформаторов напряжения')
                first = False
            for vtpris in pris.vtpris.all():
                # pris_for_table_check_sc_term = (ctpris.ct.mark, ctpris.ct.i_term, round(isc,1), pris.tsz)
                # pris_for_table_check_sc_din = (ctpris.ct.mark, ctpris.ct.i_din, round(isc,1), pris.ku)
                te.h2(f'Проверка параметров и выбор для места установки: {pris.name}')
                te.h3('Проверка по мощности обмоток')
                te.p('Для проверки параметров выбран трансформатор напряжения со следующими характеристиками:')
                te.ul(f'модель трансформатора: {vtpris.vt.name} {vtpris.vt.mark}')
                te.ul(f'Класс напряжения: {vtpris.vt.u1} кВ')
                te.ul(f'Наибольшее рабочее напряжение: {vtpris.vt.u1max} кВ')
                te.ul(f'Номинальное первичное напряжение: {vtpris.vt.u1} кВ')
                for num, loadvt in enumerate(vtpris.loadvt.all()):
                    match loadvt.vtw.schema:
                        case 'C':
                            note = ' при однофазном замыкании на землю'
                        case 'I':
                            note = ''
                        case _:
                            note = ' линейное'
                    te.ul(f'Номинальное вторичное напряжение обмотки {num + 1}{note} - {loadvt.vtw.u2} В')
                    te.ul(f'Номитальная мощность обмотки {num + 1} при классе точности {loadvt.vtw.accuracy} - {loadvt.vtw.sn} ВА')
                    te.ul(f'Схема соединения для обмотки {num + 1}: {loadvt.vtw.schema_str}')
                    power_total = 0.
                    power_names = []
                    for deviceset in loadvt.deviceset.all():
                        power_names.append(f'{deviceset.device.name} ({deviceset.device.power_consumption_vt}x{deviceset.quantity})')
                        power_total += deviceset.device.power_consumption_vt * deviceset.quantity
                    te.ul(f'Нагрузкой обмотки {num + 1} являются: {', '.join(power_names)} = {power_total:.2f} ВА')
                    if power_total <= loadvt.vtw.sn:
                        te.p(f'Обмотка {num + 1} не перегружена и будет работать в своём классе точности '
                             f'{loadvt.vtw.accuracy}')
                    else:
                        te.warning(f'Обмотка {num + 1} перегружена')
                    wind_for_check_du = (vtpris.vt.name, vtpris.vt.mark, power_total, loadvt.vtw.u2, loadvt.length,
                                               loadvt.s, loadvt.du2permissible, loadvt.vtw.accuracy,
                                         loadvt.vtw.schema_str, num + 1)
                    if wind_for_check_du in data_for_check_du:
                        data_for_check_du[wind_for_check_du].append(pris.name)
                    else:
                        data_for_check_du[wind_for_check_du] = [pris.name]
        if data_for_check_du:
            te.h3('Проверка по допустимому падению напряжения')
            te.p('Расчёт тока в наиболее нагруженной фазе обмотки производим по формуле:')
            te.math(r'I_{\text{НАГР}} = \frac{\sqrt{3} \cdot S_{\text{НАГР}}}{U_{\text{мф}}}, А')
            te.ul(' где ' + te.m(r'S_{\text{НАГР}}') + ' – мощность наиболее нагруженной фазы, ВА,')
            te.ul(' ' + te.m(r'U_{\text{мф}}') + ' – номинальное междуфазное напряжение, В.')
            te.p('Сопротивление кабельной линии от трансформатора напряжения до конечного потребителя составляет:')
            te.math(r'R_{\text{КАБ}} = \rho \cdot \frac{l}{S} ,')
            te.ul('где ' + te.m(r'\rho') + ' – удельное сопротивление меди равное 0,0175 ' +
                  te.m(r'\text{Ом} \cdot \frac{\text{мм}^2}{\text{м}};'))
            te.ul('l – длина контрольного кабеля, м; ')
            te.ul('S – сечение контрольного кабеля, мм2')
            te.p('Величина падения напряжения до наиболее отдаленного потребителя в обмотке ТН:')
            te.math(r'\Delta U = \sqrt{3} \cdot I_{\text{НАГР}} \cdot R_{\text{КАБ}} < \Delta U_{\text{ДОП}}')
            te.p('Результат расчёта')
            for data, name in data_for_check_du.items():
                te.p(', '.join(name) + f' обмотка {data[9]} класса точности {data[7]} со схемой соединения {data[8]}')
                i = data[2] * math.sqrt(3) / data[3]
                te.math(r'I_{\text{НАГР}} = \frac{\sqrt{3} \cdot ' + f'{data[2]:.2f}' + r'}{' + str(data[3]) + '} = ' +
                        f'{i:.4f}  A')
                r = 0.0175 * data[4] / data[5]
                te.math(r'R_{\text{КАБ}} = 0.0175 \cdot \frac{' + str(data[4]) + '}{' + str(data[5]) + '} = ' +
                        f'{r:.4f}' + r' \text{Ом}')
                u2perm = math.sqrt(3) * i * r / data[3] * 100
                te.math(r'\Delta U = \sqrt{3} \cdot ' + f'{i:.3f}' + r' \cdot ' + f'{r:.3f} = {u2perm:.4f}' + r' \% < ' +
                        f'{data[6]}' + r' \%')
            te.p('Требования к классу точности ТН для цепей учёта а также к допустимому падению напряжения определены '
                 'в соответствии с ТКП 339-2022 (33240).')


    def tt_generate(self, te: TextEngine):
        te.h1('Перечень шкафов и оборудования')
        te.table_name('Перечень шкафов и оборудования')
        te.table_head('№', 'Наименование оборудования', 'Количество, шт. (компл.)', 'Пункт тех.требований',
                      widths=(1,10,3,2))
        n1 = 1
        for bus_group in self.bus_group.all():
            for bus in bus_group.buses.all():
                for device_set in bus.devices.all():
                    if device_set.cabinet:
                        ref = te.ref(device_set.device.requirements.name) if device_set.device.requirements else ''
                        te.table_row(n1, device_set.device.name, device_set.quantity, ref)
                        for sub_device_set in device_set.chield_device_set.all():
                            ref = te.ref(sub_device_set.device.requirements.name) if sub_device_set.device.requirements else ''
                            te.table_row('', f'-{sub_device_set.device.name}', sub_device_set.quantity, ref)

        te.h1('Общие технические требования')
        te.p('Электрооборудование должно соответствовать требованиям технических нормативно-правовых актов, действующим '
             'на территории Республики Беларусь.')
        te.p('Предлагаемое оборудование должно быть новым (не бывшим в употреблении); конструкции узлов и агрегатов '
             'должны быть ранее опробованными и положительно зарекомендовавшими себя в условиях промышленной эксплуатации.')
        te.p('Все поставляемое оборудование должно быть сертифицировано и иметь:')
        te.ul('Сертификат соответствия о проведении обязательной сертификации на соответствие требованиям пожарной безопасности;')
        te.ul('Сертификат соответствия ТР ТС 004/2011 «О безопасности низковольтного оборудования»;')
        te.ul('Сертификат соответствия ТР ТС 020/2011 «Электромагнитная совместимость технических средств».')
        te.p('Все средства измерений должны иметь действующие свидетельства о поверке в Республике Беларусь, а также '
             'внесены в государственный реестр средств измерений Республики Беларусь.')
        te.p('Любые несоответствия электрооборудования требованиям ТЗ и техническим нормативно-правовым актам, '
             'действующим на территории Республики Беларусь, устраняются за счет поставщика.')
        te.p('Места и способы установки надписей поставщик шкафов согласовывает с Генпроектировщиком и Заказчиком.')
        te.p('Проектные схемы шкафов с устройствами РЗА должны быть выполнены проектной организацией.')
        te.p('Принципиальные чертежи (схемы) шкафов с устройствами РЗА могут быть выполнены либо проектной организацией, '
             'либо могут быть предложены как типовые (уже разработанные) поставщиком шкафов и устройств РЗА.')
        te.p('В случае разработки схем поставщиком оборудования, поставщик обязан предоставить в проектную организацию '
             'информацию, согласованную заказчиком, по шкафам (принципиальные схемы, клеммные ряды, спецификация '
             'оборудования) не позднее 3-х месяцев до окончания срока проектирования. В связи с этим, при заключении '
             'контракта, должно быть учтено время, необходимое для изготовления шкафов РЗА.')
        te.p('В случае разработки схем проектной организацией, изготовление шкафов с устройствами РЗА и ПА должно '
             'производиться по чертежам задания заводу-изготовителю, согласованным заказчиком. В связи с этим, при '
             'заключении контракта, должно быть учтено время, необходимое для разработки строительного проекта и '
             'задания заводу-изготовителю, что определит реальный срок изготовления шкафов РЗА. Необходимое время на '
             'разработку схем задания заводу - не более 3-х месяцев.')
        te.p('В комплект поставки на все поставляемое оборудование должно вхо-дить:')
        te.ul('подробная техническая и эксплуатационная документация на русском языке;')
        te.ul('документация по монтажу, техническому обслуживанию и ремонту на русском языке;')
        te.ul('подробный перечень деталей и узлов на каждый вид оборудования с указанием заказных номеров на детали и узлы;')
        te.ul('программное обеспечение необходимое для проведения технического обслуживания и диагностики работы оборудования;')
        te.ul('на все поставляемые терминалы РЗА одного производителя программное обеспечение для задания уставок и '
             'конфигурирования свободно программируемой логики должно быть единым;')
        te.ul('интерфейсные кабели, необходимые для подключения ноутбука к терминалам защит.')

        te.h2('Общие технические требования к устройствам РЗА')
        te.p('Настоящие технические требования предъявляются ко всем устройствам РЗА данного проекта.')
        te.p('Для всех поставляемых устройств РЗА требуется предоставление всех технических данных в соответствии с '
             'общими техническими требованиями и техническими требованиями к отдельным устройствам РЗА.')
        te.p('Достоверность представленной в опросных листах информации должна подтверждаться технической документацией '
             'на предлагаемые устройства и оборудование РЗА. К рассмотрению принимается документация на технически '
             'грамотном русском языке в полной версии, соответствующая объему поставки завода-производителя '
             'предлагаемых устройств и оборудования РЗА.')
        te.p('Все указанные ниже терминалы РЗА должны быть выполнены на микропроцессорной базе, выполнять функции '
             'дистанционного и телеуправления, блокировки в согласованном объеме, обеспечивать информационное '
             'взаимодействие с техническими средствами автоматизированной системы управления технологическим процессом '
             '(ТМ), обеспечивать выходы в схему сигнализации и др.')
        if self.diff_terminals:
            te.p('Терминалы РЗА, выполняющие дублирующие функции (1-й комплекс, 2- комплекс) должны быть разных '
                 'фирм-производителей или разного алгоритма работы.')
        te.p('Терминалы РЗА должны выполняться с конфигурируемой пользователем логикой, обеспечивающей взаимодействие '
             'как между различными функциями защиты, управления и контроля, так и между этими функциями и внешними '
             'устройствами защит, управления и контроля в других терминалах.')
        te.p('Для каждого предложенного терминала РЗА, не имеющегося в эксплуатации у Заказчика, должны быть предложены '
             'рекомендации и методики расчета уставок и/или программы (программ) расчета на технически грамотном '
             'русском языке, оформленные в соответствии с действующими в РБ нормативно-техническими документами.')
        te.p('Состав защит должен соответствовать требованиям «Правил устройств электроустановок». Каждая система защит '
             'конкретного электрооборудования должна иметь аппаратное резервирование, должна быть независима по цепям '
             'оперативного постоянного тока, входным и выходным цепям, цепям сигнализации и контроля.')
        te.p('Терминалы РЗА должны отвечать следующим требованиям:')
        te.ul('модульное аппаратное исполнение;')
        te.ul('обеспечение независимой работы исправных модулей при отказах или неисправности в соседних модулях;')
        te.ul('возможность задания уставок через интерфейс человек-машина (ИЧМ);')
        te.ul('интерфейс пользователя (ИЧМ) должен быть русифицирован;')
        te.ul('мощность процессора терминала защит должна быть достаточной для выполнения всех логических функций;')
        te.ul('полностью цифровая обработка сигнала;')
        te.ul('непрерывный самоконтроль аппаратной части и программного обеспечения;')
        te.ul('возможность задания параметров, запись и считывание уставок с помощью персонального компьютера (ПК);')
        te.ul('отображение на экране дисплея измеренных значений;')
        te.ul('отображение на экране дисплея событий, параметров, уставок и др. в удобном для просмотра виде;')
        te.ul('регистрация анормальных режимов;')
        te.ul('длительный ресурс работы;')
        te.ul('хранение информации (уставки, журналы событий, аварийные осциллограммы) в энергонезависимой флэш-памяти;')
        te.ul('согласованная связь с подстанционным управлением;')
        te.ul('все устройства РЗА должны предусматривать возможность синхронизации времени с помощью внешнего приемника '
              'или при помощи ТМ объекта.')
        te.p('Устройства РЗА должны соответствовать требованиям СТП 09110.35.250-12.')
        te.h2('Общие технические требования к релейным отсекам')
        te.p('Все релейные отсеки распределительного устройства должны быть выполнены в металлическом корпусе с '
             'клеммными коробками в скомпонованном виде, если не указано иное. Все межблочные связи в отсеках должны '
             'быть выполнены при заводской сборке.')
        te.p('Релейные отсеки должны комплектоваться всей необходимой сигнальной и переключающей аппаратурой. Объем '
             'указанной аппаратуры определяется производителем шкафов и согласовывается с заказчиком и проектной организацией.')
        te.p('Комплектующие изделия: реле, клеммы, испытательные блоки, переключатели и т.п. должны соответствовать '
             'требованиям действующих НТД.')
        te.p('Релейные отсеки должны соответствовать требованиям СТП 33243.10.179-16 «Требования к устройствам и '
             'оборудованию устанавливаемых в релейных отсеках высоковольтных ячеек» и другим ТНПА действующим на '
             'территории Республики Беларусь.')
        te.table_name('Технические требования к релейным отсекам')
        te.table_head('№ п/п', 'Параметр и его характеристика', 'Требования',
                      'Предлагаемые технические характеристики (заполняется участником торгов)', widths=(1,10, 3, 2))
        te.table_row(1, 'Способ обслуживания', 'Отдносторонее')
        te.table_row(2, 'Номинальное напряжение цепей управления, В', 'DC 220')
        te.table_row(3, 'Обогрев, наличие',	'Да')
        te.table_row(4, 'Освещение, наличие',	'Да')
        te.table_row(5, 'Сервисные цепи, наличие',	'Да')
        te.table_row(6, 'Номинальное напряжение цепей обогрева, освещения, сервисных цепей, В',	'AC 220')
        te.table_row(7, 'Запирающие устройства, наличие',	'Да')
        te.h1('Технические требования к устройствам РЗА')
        for requirement in self.requirements.all():
            requirement.tt_generate(te)

class RequirementDeviceDoc(Doc):
    def tt_generate(self, te: TextEngine):
        te.h2(self.name)
        te.target(self.name)
        te.table_name(self.name)
        te.table_head('№ п/п', 'Параметр и его характеристика', 'Требования',
                      'Предлагаемые технические характеристики (заполняется участником торгов)', widths=(1,10, 3, 2))
        n1 = n2 = 1
        for requirement_set in self.requirement_set.all().order_by('order'):
            te.table_row(te.b(n1), te.b(requirement_set.name), '', '')
            for requirement in requirement_set.requirements.all():
                relation = f', {requirement.relation_verbose}' if requirement.relation_verbose != 'равно' else ''
                te.table_row(f'{n1}.{n2}', f'{requirement.name}{relation}', f'{requirement.value}', '')
                n2 += 1
            n1 += 1
            n2 = 1
        te.p('* Далее приводятся разъяснения по каждой позиции, по которой имеется частичное или полное несоответствие '
             'требованиям Заказчика')

# class Project(Element, ProjectDoc):
#     model_config = ConfigDict(arbitrary_types_allowed=True)
#     res_sc_min: dict | None = None
#     res_sc_max: dict | None = None
#     pris: list[Pris] | None = None
#     ct: list[CT] | None = None
#     vt_section_input: bool | None = None
#     protection_terminal_reservation: bool | None = None
#     operating_current_distribution_cabinet: bool | None = None
#     two_batteries: bool | None = None
#     avr: bool | None = None # наличие АВР
#     zdz: bool | None = None # наличие ЗДЗ (указать напряжение ячеек)
#     rzn: int | None = None # сопротивление резистора заземления нейтрали
#     name_ss: str | None = None # название питающей подстанции на которой заземлена нейтраль через резистор
#     un: float | None = None # номинальное напряжения сети
#     rp: bool | None = None # если True то защиты ОЗЗ описываются как для РП иначе как для подстанции
#     dc: DC | None = None
#
#     def model_post_init(self, __context: Any) -> None:
#         if self.vt_section_input is None:
#             self.vt_section_input = bool(input('Установить ТН на ввод на секцию шин?'))
#         if self.protection_terminal_reservation is None:
#             self.protection_terminal_reservation = bool(input('Выполнить ближнее резервирование?'))
#         if self.operating_current_distribution_cabinet is None:
#             self.operating_current_distribution_cabinet = bool(input('Добавить шкаф распределение оперативного тока?'))
#         if self.two_batteries is None:
#             self.two_batteries = bool(input('Установить вторую АКБ?'))
#         if self.iec_61850_8_1 is None:
#             self.iec_61850_8_1 = bool(input('Добавить поддержку протокола IEC 61850-8-1 ?'))
#         if self.avr is None:
#             self.avr = input('Добавить АВР (если да то введите напряжение для АВР в кВ)?')
#         if self.zdz is None:
#             self.zdz = input('Добавить ЗДЗ (укажите напряжение ячеек КРУ)?')
#         if self.rzn is None:
#             self.rzn = input('Добавить резистивно-заземлённую нейтраль сети (указать напряжение сети в кВ)?')
#         if self.dc is None:
#             self.dc = DC()
#
#     def add_pris(self, pris: Pris):
#         if self.pris is None:
#             self.pris = []
#         self.pris.append(pris)
#
#     @property
#     def power_consumption_total(self):
#         return sum([p.power_consumption_total for p in self.pris])
#
#     @property
#     def power_consumption_iter(self):
#         for p in self.pris:
#             for power_data in p.power_consumption_iter:
#                 yield power_data
#
#     @property
#     def power_consumption_agregate(self):
#         data = {}
#         for name, power, quantity in self.power_consumption_iter:
#             if name in data:
#                 if data[name][0] != power:
#                     raise ValueError('Одинаковые названия с разными мощностями')
#                 data[name][1] += quantity
#             else:
#                 data[name] = [power, quantity]
#         return data
#
