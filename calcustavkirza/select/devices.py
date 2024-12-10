from typing import Any

from textengines.interfaces import TextEngine

from calcustavkirza.classes import Element, Doc

class DeviceDoc(Doc):
    ...


class Device(Element):
    power_consumption_ac: float | None = None # мощность потребления по цепи питания в Вт
    power_consumption_dc: float | None = None # мощность потребления по цепи питания в Вт

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        if self.power_consumption_ac is None:
            self.power_consumption = float(input("Enter your power consumption DC, W: "))
        if self.power_consumption_dc is None:
            self.power_consumption_dc = float(input("Enter your power consumption DC, W: "))

    @property
    def power_consumption_ac_total(self) -> float:
        return self.power_consumption

class DI(Element):
    number: str | None = None
    power_consumption: float = 0.33 # мощность потребления по цепи питания в Вт

class DO(Element):
    number: str | None = None
    power_consumption: float = 0.44 # мощность потребления по цепи питания в Вт

class Terminal(Device):
    di: list[DI] | None = None
    do: list[DO] | None = None


    def add_di(self, di: DI | None) -> None:
        if self.di is None:
            self.di = []
        self.di.append(di)

    def add_do(self, do: DO | None) -> None:
        if self.do is None:
            self.do = []
        self.do.append(do)

    @property
    def power_consumption_total(self) -> float:
        power = self.power_consumption
        # power += sum(d.power_consumption for d in self.di)
        # power += sum(d.power_consumption for d in self.do)
        return power

    @property
    def power_consumption_iter(self):
        yield self.name, self.power_consumption
        # for di in self.di:
        #     yield 'Дискретный вход терминала защит', di.power_consumption
        # for do in self.do:
        #     yield 'Релейный выход терминала защит', do.power_consumption
