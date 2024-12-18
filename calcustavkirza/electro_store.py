from typing import Protocol
from abc import abstractmethod
from dataclasses import dataclass

from textengines.interfaces import TextEngine

class ModelStore(Protocol):

    @property
    @abstractmethod
    def class_name(self):
        ...


class PrisStore(Protocol):

    @property
    @abstractmethod
    def name(self):
        ...

    @property
    @abstractmethod
    def note(self):
        ...

    @property
    @abstractmethod
    def prots(self) -> list[ModelStore]:
        ...

class ProjectStore(Protocol):

    @property
    @abstractmethod
    def res_sc(self) -> tuple[tuple[dict], tuple[dict]]:
        ...

    @abstractmethod
    def prises(self, order: str) -> list[PrisStore]:
        '''

        Args:
            order(str): name field for the order

        Returns:
            generator: generator for the Pris objects
        '''
        ...
@dataclass
class GenStore(Protocol):
    std_type: str
    vn_kv: float
    cos_phi: float
    sn_mva: float
    p_mw: float
    xdss_pu: float
    t3: float
    t1: float


@dataclass
class CTwStore(Protocol):
    i1: int
    i2: int
    accuracy: str # название класса точности
    accuracy_value: float # полная погрешность в долях от номинального тока
    sn: int
    r2: float
    x2: float
    cos: float
    kn: int

@dataclass
class CTStore(Protocol):
    mark: str
    i1: int
    ctw: list[CTwStore]
    i_term: float
    i_din: float

@dataclass
class DiffGenStore(Protocol):
    '''
    Дифзащита генератора на терминале ЭКРА в шкафу ШЭ1113
    '''
    isz: float
    isc: float # ток внешнего КЗ в А

@dataclass
class IscStore(Protocol):
    u: float #линейное напряжение сети в вольтах
    i: float | None = None #ток КЗ в амперах
    t: float | None = None #постоянная времени в мс
    a: float  | None = None #угол тока КЗ в градусах
    i1: float | None = None
    a1: float | None = None
    i2: float | None = None
    a2: float | None = None
    i0: float | None = None
    a0: float | None = None
    kcd: float = 1 #коэффициент токораспределения

@dataclass
class TrafoStore(Protocol):
    std_type: str
    vn_hv_kv: float
    vn_lv_kv: float
    sn_mva: float
    vk_percent: float

@dataclass
class TrafoSplitWStore(TrafoStore, Protocol):
    vk_llv_percent: float
