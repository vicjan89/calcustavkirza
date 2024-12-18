import math
import os

from textengines.interfaces import TextEngine

from calcustavkirza.calcsc.gen import Gen
from calcustavkirza.calcsc.Isc import Isc
from calcustavkirza.electro_store import DiffGenStore, GenStore, CTwStore


class DiffGen:
    '''
    Дифзащита генератора на терминале ЭКРА в шкафу ШЭ1113
    '''

    def __init__(self, te: TextEngine, store: DiffGenStore, gen_store: GenStore, system_store: IscStore,
                 ctw_l_store: CTwStore, ctw_n_store: CTwStore, pu: Pu, *args, **kwargs):
        self.te = te
        self.store = store
        self.gen = Gen(te, gen_store, pu)
        self.system = Isc(te, system_store, pu)
        self.ctw_l = ctw_l_store
        self.ctw_n = ctw_n_store

    def calc_settings(self):
        self.te.h2('Продольная дифференциальная защита генератора (I∆G)')
        self.te.p('Функция продольной дифференциальной защиты генератора предназначена для защиты генератора от '
                  'многофазных КЗ в обмотке статора и на его выводах, а также от двойных замыканий на землю в цепях '
                  'генераторного напряжения.')
        self.te.p('Защита выполняется трехфазной, т.к. такое исполнение позволяет обеспечить чувствительность к двойным '
                  'замыканиям на землю.')
        self.te.p('Защита от междуфазных коротких замыканий выполняется без выдержки времени с действием на отключение '
                  'генератора, развозбуждение и остановку турбоагрегата.')
        self.te.p('Уставки защиты задаются в относительных единицах, относительно базисного тока. В качестве базисного '
                 'тока принимается номинальный ток генератора. Номинальный ток генератора должен задаваться для каждого '
                 'плеча защиты.')
        self.te.p('Номинальный ток генератора для каждого плеча защиты определяется по формуле:')
        self.te.math(r'I_{\text{ном 1(2)}} = \frac{I_{\text{ном.г}}}{K_{\text{сх.ген 1(2)}}}')
        inom = self.gen.in_ka * 1000
        self.te.ul(f'где Iном.г = {inom} А - номинальный ток генератора;')
        self.te.ul(f'Kсх.ген 1(2) - коэффичиент, учитывающий схему соединения обмоток генератора (равен {self.gen.k_sсh};')
        self.te.p('Номинальный ток со стороны линейных выводов генератора:')
        self.te.math(r'I_{\text{ном1}} = \frac{'+inom+'}{'+self.gen.k_sch+'}')
        self.te.p('Номинальный ток со стороны нулевых выводов генератора:')
        self.te.math(r'I_{\text{ном1}} = \frac{'+inom+'}{'+self.gen.k_sch+'}')
        self.te.p('Базисный ток каждого плеча защиты определяется по формуле:')
        self.te.math(r'I_{\text{баз 1(2)}} = \frac{I_{\text{ном1(2)}}·K_{\text{сх}}}{K_{TT}},')
        self.te.ul('где Ксх - коэффициент, учитывающий схему соединения обмоток трансформаторов тока;')
        self.te.ul('Kтт - коэффициент трансформации трансформаторов тока.')
        self.te.p('Базисный ток со стороны линейных выводов генератора:')
        ibase_l = inom / self.ctw_l.i1 * self.ctw_l.i2
        self.te.math(r'I_{\text{баз.Г}} = \frac{'+inom+'}{'+self.ctw_l.i1+'/'+self.ctw_l.i2+'} = '+ibase_l+' A')
        self.te.p('Базисный ток со стороны нулевых выводов генератора:')
        ibase_n = inom / self.ctw_n.i1 * self.ctw_n.i2
        self.te.math(r'I_{\text{баз.НГ}} = \frac{'+inom+'}{'+self.ctw_n.i1+'/'+self.ctw_n.i2+'} = '+ibase_n+' A')
        self.te.p('Расчет уставок целесообразно выполнять в первичных величинах.')
        self.te.h3('Начальный ток срабатывания')
        self.te.p('Уставка определяется по условию отстройки защиты от тока небаланса номинального режима по формуле:')
        self.te.math(r'I_{\text{ср}} = K_{\text{отс}}·I_{\text{нб}},')
        self.te.ul('где Котс = 1.2 - коэффициент отстройки, учитывающий погрешность работы защиты и необходимый запас;')
        self.te.ul('Iнб - ток небаланса нормального (номинального) режима, в о.е., определяемый по формуле:')
        self.te.math(r'I_{\text{нб}} = (K_{\text{одн}}·ε_{TT}+∆f_{\text{выр}})·I_{\text{ном.Г}},')
        self.te.ul('где Kодн - коэффициент однотипности;')
        self.te.ul('εтт - полная погрешность трансформаторов тока;')
        self.te.ul('∆fвыр - относительная погрешность выравнивания токов плеч.')
        accuracy = max(self.ctw_l.accuracy_value, self.ctw_n.accuracy_value)
        inb = accuracy + 0.02
        self.te.math(r'I_{\text{нб}} = (1·'+accuracy+f'+0.02)·1 = {inb} о.е.,')
        self.te.math(r'I_{\text{ср}}≥1.2·'+f'{inb} = {1.2*inb:.2f} о.е.')
        self.te.p(f'Значение начального тока срабатывания дифференциальной защиты генератора принимается равным Iср = '
                  f'{self.store.isz} о.е')
        self.te.p('Коэффициент торможения первого наклонного участка выбирается по условию отстройки защиты от '
                  'максимальных токов небаланса, вызванных погрешностями ТТ при внешних трехфазных КЗ или АХ по формуле:')
        self.te.math(r'K_{T1} = \frac{K_{\text{отс}}·I_{\text{нб.макс}}}{I_T},')
        self.te.ul('где Котс = 2 - коэффициент	отстройки,	учитывающий	погрешность	защиты, приближенность расчета токов '
                   'КЗ и необходимый запас;')
        self.te.ul('Iт – ток торможения в рассматриваемом режиме;')
        self.te.ul('Iнб.макс – максимальный ток небаланса при внешнем трехфазном КЗ или АХ, определяемый по формуле:')
        self.te.math(r'I_{\text{нб.макс}} = (K_{\text{ап}}·K_{\text{одн}}·ε_{TT}+∆f_{\text{выр}})·I_{\text{скв}},')
        self.te.ul('где Kап = 2 – коэффициент, учитывающий наличие апериодической составляющей тока;')
        self.te.ul('Kодн - коэффициент однотипности;')
        self.te.ul('εтт - полная погрешность трансформаторов тока;')
        self.te.ul('∆fвыр - относительная погрешность выравнивания токов плеч.')
        self.te.ul('Iскв – максимальный сквозной ток.')
        self.te.p('Максимальный сквозной ток определяется как максимальный из двух значений:')
        self.te.ul(f'ток в цепи генератора при внешнем трехфазном КЗ на выводах генератора Iвн.кз = {self.store.isc} A.')
        self.te.ul('ток IАХ в цепи генератора при асинхронном ходе (несинхронном включении генератора).')
        self.te.math(r'I_{AX} = \frac{E^"_{\text{Г}}+E_{\text{экв.с}}}{x^"_d+x_{\text{экс.с}}},')
        self.te.ul(f'где E" = {self.gen.ess} кB - сверхпереходная ЭДС генератора;')
        self.te.ul(f'Eэкв.с = {self.system.e} кB - эквивалентная ЭДС «системы»;')
        self.te.ul(f'xd" = {self.gen.x1_ohm} Ом - сверхпереходное сопротивление генератора;')
        self.te.ul(f'xэкв.с = {self.system.z_abs} - эквивалентное сопротивление «системы»;')
        iax = (self.gen.ess + self.system.z_abs) / (self.gen.x1_ohm + self.system.z_abs)
        self.te.math(r'I_{AX} = \frac{'+self.gen.ess + f'+{self.system.e}' + r'}{' + self.gen.x1_ohm + r'+' +
                     self.system.z_abs + '} = ' + f'{iax:.2f} A')

    def table_settings(self):
        te.table_row(self.name, te.m(r'I_{\text{Д>}}'), self.id, '')
        te.table_row(self.name, te.m(r'I_{\text{Б1}}'), self.ib1, '')
        te.table_row(self.name, te.m(r'f_1'), self.s2, '')
        te.table_row(self.name, te.m(r'I_{\text{Д>>}}'), self.id_ots, '')
        te.table_row(self.name, te.m(r'I_{\text{Д.МИН}}'), self.id_alarm, '')
