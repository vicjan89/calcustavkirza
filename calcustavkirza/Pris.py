from calcustavkirza.select.devices import Device, Terminal
from textengines.interfaces import TextEngine

from calcustavkirza.classes import Element, Doc
from calcustavkirza.protections.MTZ import MTZ
from calcustavkirza.protections.TO import TO
from calcustavkirza.protections.EF import EF
from calcustavkirza.protections.LZSH import LZSH
from calcustavkirza.protections.BFP import BFP
from calcustavkirza.protections.ControlBFP import ControlBFP
from calcustavkirza.protections.EFdir import EFdir
from calcustavkirza.protections.AutoReclose import AutoReclose
from calcustavkirza.protections.Avr import Avr
from calcustavkirza.protections.voltage import Voltage
from calcustavkirza.protections.overload import OverLoad
from calcustavkirza.protections.T3WPDIF import T3WPDIF
from calcustavkirza.protections.DZSH import DZSH
from calcustavkirza.protections.ZMQPDIS import ZMQPDIS
from calcustavkirza.protections.EF4PTOC import EF4PTOC
from calcustavkirza.protections.TOSVG import TOSVG
from calcustavkirza.protections.MTZSVG import MTZSVG1, MTZSVG2
from calcustavkirza.Net import Net


class CT(Element):
    mark: str
    i1: int
    i2: int

    def i1toi2(self, i1):
        return i1 / self.i1 * self.i2

class VT(Element):
    mark: str
    u1: int | float
    u2: int

    def u1tou2(self, u1):
        return u1 / self.u1 * self.u2

class BusGroupDoc(Doc):

    def ap_generate(self, te: TextEngine):
        te.table_name(f'Перечень нагрузок {self.name}')
        te.table_head('Наименование', 'Мощность, ВА', 'Количество', 'Мощность всего, ВА')
        power_consumption_total = 0
        for bus in self.buses.all():
            for device_set in bus.devices.all():
                quantity = device_set.quantity * bus.parent.quantity
                total = device_set.device.power_consumption * quantity
                te.table_row(f'{bus.parent}: {bus.name} {device_set.device.name} {device_set.device.parameters}',
                             device_set.device.power_consumption,
                             quantity,
                             total)
                power_consumption_total += total
        te.table_row('Итого', '', '', power_consumption_total)


class BusGroup(Element):
    ...


class BusDoc(Doc):
    ...

class Bus(Element):
    devices: list[Device] | None = None
    terminals: list[Terminal] | None = None

class PrisDoc:

    @property
    def power_consumption_total(self):
        power = sum([d.power_consumption_total for d in self.devices])
        power += sum([d.power_consumption_total for d in self.terminals])
        return power * self.quantity

    @property
    def power_consumption_iter(self):
        for dev in self.devices:
            yield dev.name, dev.power_consumption_total, self.quantity
        for terminal in self.terminals:
            for name, power in terminal.power_consumption_iter:
                yield name, power, self.quantity

    @property
    def _functions(self):
        if isinstance(self, Element):
            return [func[0] for name, func in self.__dict__.items() if name not in ('ct', 'vt') and isinstance(func, list)]
        else:
            res = []
            for name in self.__dir__():
                if name in ('to', 'mtz', 'avr', 'bfp', 'cbfp', 'ef', 'lzsh', 'overload', 'voltage'):
                    objs = getattr(self, name)
                    obj = list(objs.all())
                    if obj:
                        res.extend(obj)
            return res

    def ap_generate(self, te: TextEngine):
        if len(self._functions) or self.zdz or self.trip_ef or self.saon or self.achr or self.cb or self.terminal:
            te.h1(f'{self.name[0].capitalize()}{self.name[1:]}')
            te.p('Для выполнения функций РЗА предусматривается установка отдельного микропроцессорного терминала в релейном '
                 'отсеке соответствующей ячейки. Аппаратура РЗА выполняет следующие функции:')
            for func in self._functions:
                if func:
                    func.ap_generate(te)
            if self.zdz:
                te.ul('Отключение от дуговой защиты;')
            if self.trip_ef:
                te.ul('Отключение от ТЗНП;')
            if self.saon:
                te.ul('Отключение и включение от САОН-АСБС;')
            if self.achr:
                te.ul('Отключение от АЧР и включение от ЧАПВ;')
            if self.cb:
                te.ul('Управление выключателем 10 кВ с контролем всех его параметров. '
                      'Управление выключателем должно осуществляться с АРМ АСУТП в режиме '
                      'дистанционного управления и с кнопок терминала автоматики управления выключателем '
                      '(резервное управление). Включение (оперативное и автоматическое) должно производиться только через '
                      'схему терминалов автоматики. Схема управления выключателем должна обеспечивать отключающее действие '
                      'через два соленоида отключения. Устройство РЗА и соленоиды отключения должны быть запитаны от '
                      'отдельных автоматов оперативного тока;')
            if self.terminal:
                te.ul('Регистратор аварийных событий;')
                te.ul('Дополнительная конфигурируемая логика;')
                te.ul('Возможность ввода/вывода отдельных функций терминала;')
                te.ul('Функция внутреннего контроля и самодиагностики;')
                te.ul('Не менее 2-ух групп уставок;')

    def get_rza(self) -> tuple:
        return (self.to, self.mtz, self.lzsh, self.overload, self.bfp, self.cbfp, self.ef, self.efdir, self.apv, self.avr,
                self.voltage)


    def calc_ust(self, te: TextEngine, res_sc_min, res_sc_max):
        first = True
        for typ in ('dif', 'dzsh', 'zm', 'ef4', 'mtz', 'lzsh', 'to', 'bfp', 'cbfp', 'ef', 'efdir',
                    'apv', 'avr', 'voltage', 'overload'):
            if hasattr(self, typ):
                prots = getattr(self, typ)
                for p in prots.all():
                    if first:
                        te.h2(self.name)
                        if self.note:
                            te.p(self.note)
                        first = False
                    p.calc_ust(te=te, res_sc_min=res_sc_min, res_sc_max=res_sc_max)

    def table_settings(self, te: TextEngine):
        te.table_name(self.name)
        te.table_head('Функция РЗА', 'Величина срабатывания', 'Время срабатывания, сек', 'Примечание')
        for typ in (self.dif, self.dzsh, self.zm, self.ef4, self.mtz, self.lzsh, self.to, self.bfp, self.cbfp, self.ef, self.efdir,
                    self.apv, self.avr, self.voltage, self.overload):
            for p in typ:
                p.table_settings(te=te)

    def table_settings_bmz(self):
        res = []
        for protectiona_group in  self.get_rza():
            if protectiona_group:
                for prot in protectiona_group:
                    res.append(prot.table_settings_bmz())
        return res

    def get_protections(self):
        prot = []
        if self.mtz:
            prot.extend(self.mtz)
        if self.to:
            prot.extend(self.to)
        # if self.ef:
        #     prot.extend(self.ef)
        if self.lzsh:
            prot.extend(self.lzsh)
        # if self.bfp:
        #     prot.extend(self.bfp)
        # if self.efdir:
        #     prot.extend(self.efdir)
        return prot


class Pris(Element):
    loc: dict | None = None
    ct: list[CT] | None = None
    vt: list[VT] | None = None
    dif: list[T3WPDIF] | None = None
    dzsh: list[DZSH] | None = None
    zm: list[ZMQPDIS] | None = None
    ef4: list[EF4PTOC] | None = None
    mtz: list[MTZ] | None = None
    to: list[TO] | None = None
    ef: list[EF] | None = None
    lzsh: list[LZSH] | None = None
    bfp: list[BFP] | None = None
    cbfp: list[ControlBFP] | None = None
    efdir: list[EFdir] | None = None
    apv: list[AutoReclose] | None = None
    avr: list[Avr] | None = None
    voltage: list[Voltage] | None = None
    overload: list[OverLoad] | None = None
    zdz: bool | None = None # наличе ЗДЗ
    cb: bool | None = None # наличие выключателя
    trip_ef: bool | None = None # отключение от ТЗНП
    saon: bool | None = None # отключение от САОН-АСБС
    achr: bool | None = None # отключение от АЧР
    note: str = ''
    buses: list[Bus] | None = None # шинки питания устройств
    quantity: int | None = None # количество присоединений

    def model_post_init(self, __context) -> None:
        super().model_post_init(__context)
        if not self.quantity:
            self.quantity = int(input('Количество присоединений? '))


    def add_device(self, device: Device | list[Device]):
        if self.devices is None:
            self.devices = []
        if isinstance(device, list):
            self.devices.extend(device)
        else:
            self.devices.append(device)

    def add_terminal(self, terminal: Terminal | list[Terminal]):
        if self.terminals is None:
            self.terminals = []
        if isinstance(terminal, list):
            self.terminals.extend(terminal)
        else:
            self.terminals.append(terminal)
