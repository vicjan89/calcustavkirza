import math


from textengines.interfaces import TextEngine


from calcustavkirza.classes import Element


class ZMQPDIS_step(Element):
    condition: int #условие выбора
    R1: float | None = None #активное сопротивление прямой последовательности
    X1: float | None = None #реактивное сопротивление прямой последовательности
    R0: float | None = None #активное сопротивление нулевой последовательности
    X0: float | None = None #реактивное сопротивление нулевой последовательности
    RFPP: float
    RFPE: float | None = None
    note: str = ''#примечание (куда действует)
    calc_z0: bool = True #нужно ли считать уставку для однофазных КЗ
    prot_sogl: str = '' #наименование поледующей защиты для согласования
    Rs: float | None = None #активное сопротивление для согласования
    Xs: float | None = None #реактивное сопротивление для согласования
    R0s: float | None = None #активное сопротивление нулевой последовательности для согласования
    X0s: float | None = None #реактивное сопротивление нулевой последовательности для согласования
    t: float | None = None #время срабатывания ступени
    tau: float | None = None #время срабатывания автоматического ускорения ступени
    Kch: float | None = None #коэффициент чувствительности для ступени
    Ks: float | None = None #коэффициент согласования для ступени
    dir: bool = True #прямонаправленная ступень, если False то обратнонаправленная
    psd: bool = True #блокировка от качания введена
    # ikz: float | None = None #минимальный ток КЗ при междуфазных КЗ
    kPP: float = 3 #коэффициент для определения RFPP
    kPE: float = 4.5 #коэффициент для определения RFPE

    def calc_ust(self, te: TextEngine, zm, res_sc_min: list, res_sc_max: list):
        match self.condition:
            case 1:
                R1 = zm.Kots * zm.Rl
                te.table_row(f'Активное сопротивление прямой последовательности {self.name} ступени по условию отстройки от КЗ в конце '
                             'защищаемой линии, Ом',
                             f'R1 = Kотс * Rl = {zm.Kots} * {zm.Rl}', f'{R1:.2f}')
                X1 = zm.Kots * zm.Xl
                te.table_row(f'Реактивное сопротивление прямой последовательности {self.name} ступени по условию отстройки от КЗ в конце '
                             'защищаемой линии, Ом',
                             f'X1 = Kотс * Xl = {zm.Kots} * {zm.Xl}', f'{X1:.2f}')
                if self.calc_z0:
                    x0 = zm.X0l
                    if zm.Xm:
                        x0 = zm.X0l - zm.Xm ** 2 / zm.X0l
                    te.table_row(f'Активное сопротивление нулевой последовательности {self.name} ступени по условию отстройки от КЗ в конце '
                                 'защищаемой линии, Ом',
                                 f'R0 = Kотс * R0l = {zm.Kots} * {zm.R0l}', f'{zm.Kots * zm.R0l:.2f}')
                    te.table_row(f'Реактивное сопротивление нулевой последовательности {self.name} ступени по условию отстройки от КЗ в конце '
                                 'защищаемой линии, Ом',
                                 f'X0 = Kотс * X0э = {zm.Kots} * {x0}', f'{zm.Kots * x0:.2f}')
                    te.table_row('Реактивное эвивалентное сопротивление нулевой последовательности, Ом',
                                 te.m(r'X0э = Xl - \frac{X^2_m}{Xl}'), f'{x0:.2f}')
            case 2:
                Ks = self.Ks if self.Ks else zm.Ks
                sign_char = ' + ' if self.dir else ' - '
                sign2_char = ' * ' if self.dir else ' / '
                if self.dir:
                    R1 = (self.Rs + zm.Rl) * Ks
                    X1 = (self.Xs + zm.Xl) * Ks
                else:
                    R1 = (self.Rs - zm.Rl) / Ks
                    X1 = (self.Xs - zm.Xl) / Ks
                te.table_row(f'Активное сопротивление прямой последовательности {self.name} ступени по согласованию '
                             f' с последующей защитой {self.prot_sogl}, Ом',
                             f'R1 = Kсогл * R1согл = ({self.Rs}{sign_char}{zm.Rl}){sign2_char}{Ks}', f'{R1:.2f}')
                te.table_row(f'Реактивное сопротивление прямой последовательности {self.name} ступени по согласованию '
                             f'с последующей защитой {self.prot_sogl}, Ом',
                             f'X1 = Kсогл * X1согл = ({self.Xs}{sign_char}{zm.Xl}){sign2_char}{Ks}', f'{X1:.2f}')
                if self.calc_z0:
                    if self.dir:
                        R0 = (self.R0s + zm.R0l) * Ks
                        X0 = (self.X0s + zm.X0l) * Ks
                    else:
                        R0 = (self.R0s - zm.R0l) / Ks
                        X0 = (self.X0s - zm.X0l) / Ks
                    te.table_row(f'Активное сопротивление нулевой последовательности {self.name} ступени по согласованию '
                                 f'с последующей защитой {self.prot_sogl}, Ом',
                                 f'R0 = Kсогл * R0согл = ({self.R0s}{sign_char}{zm.R0l}){sign2_char}{Ks}', f'{R0:.2f}')
                    te.table_row(f'Реактивное сопротивление нулевой последовательности {self.name} ступени по согласованию '
                                 f'с последующей защитой {self.prot_sogl}, Ом',
                                 f'X0 = Kсогл * X0согл = ({self.X0s}{sign_char}{zm.X0l}){sign2_char}{Ks}', f'{X0:.2f}')
            case 3:
                Kch = self.Kch if self.Kch else zm.Kch
                R1 = Kch * zm.Rl
                te.table_row(f'Активное сопротивление прямой последовательности {self.name} ступени по условию чувствительности при КЗ'
                             ' в конце защищаемой линии, Ом',
                             f'R1 = Kч * Rl = {Kch} * {zm.Rl}', f'{R1:.2f}')
                X1 = Kch * zm.Xl
                te.table_row(f'Реактивное сопротивление прямой последовательности {self.name} ступени по условию '
                             f'чувствительности при КЗ в конце защищаемой линии, Ом',
                             f'X1 = Kч * Xl = {Kch} * {zm.Xl}', f'{X1:.2f}')
                if self.calc_z0:
                    x0 = zm.X0l
                    if zm.Xm:
                        x0 = zm.X0l + zm.Xm
                    te.table_row(f'Активное сопротивление нулевой последовательности {self.name} ступени по условию чувствительности при КЗ'
                                 ' в конце защищаемой линии, Ом',
                                 f'R0 = Kч * R0l = {Kch} * {zm.R0l}', f'{Kch * zm.R0l:.2f}')
                    te.table_row(f'Реактивное сопротивление нулевой последовательности {self.name} ступени по условию чувствительности при '
                                 'КЗ в конце защищаемой линии, Ом',
                                 f'X0 = Kч * X0э = {Kch} * {x0}', f'{Kch * x0:.2f}')
                    te.table_row('Реактивное эвивалентное сопротивление нулевой последовательности, Ом',
                                 te.m(r'X0э = Xl + X_m'), f'{x0:.2f}')
        # Rd = 2500 * 3.5 / self.ikz
        # te.table_row('Сопротивление дуги', 'Rd', f'{Rd:.2f}')
        # te.table_row('', 'RFPE', f'{1.2 * (3 + Rd + 3 * 3) / (1 + zm.R0l / zm.Rl):.2f}')
        # Z1 = math.sqrt((R1 + Rd) ** 2 + X1 ** 2)
        # fr = math.atan2(X1, R1 + Rd)
        # fl = math.atan2(zm.X0l, zm.R0l)
        # te.table_row('', 'RFPP', 1.2 * Z1 * math.sin(fl - fr) / math.sin(fl))
        te.table_row('Активное сопротивление в месте КЗ для междуфазных КЗ',
                     te.m(r'RFPP \leq ' + str(self.kPP) + r' \cdot ' + f'{X1:.2f}' + ' = ' + f'{self.kPP*X1:.2f}'),
                     self.RFPP)
        if self.RFPE is not None:
            te.table_row('Активное сопротивление в месте КЗ для однофазных КЗ',
                         te.m(r'RFPE \leq ' + str(self.kPE) + r' \cdot ' + f'{X1:.2f}' + ' = ' + f'{self.kPE*X1:.2f}'),
                         self.RFPE)
        if self.R1:
            te.table_row(f'Принимаем активное сопротивление прямой последовательности {self.name} ступени, Ом',
                         'R1', f'{self.R1}')
        if self.X1:
            te.table_row(f'Принимаем реактивное сопротивление прямой последовательности {self.name} ступени, Ом',
                         'X1', f'{self.X1}')
        if self.R0:
            te.table_row(f'Принимаем активное сопротивление нулевой последовательности {self.name} ступени, Ом',
                         'R0', f'{self.R0}')
        if self.X0:
            te.table_row(f'Принимаем реактивное сопротивление нулевой последовательности {self.name} ступени, Ом',
                         'X0', f'{self.X0}')
        note = [self.note] if self.note else []
        if not self.dir:
            note.append('обратнонаправленная')
        if not self.psd:
            note.append('не блокируется при качаниях')
        note = ', '.join(note)
        if self.t is not None:
            note = f'({note})'
            te.table_row(f'Время срабатывания {self.name} ступени {note}, сек', 't', self.t)
        else:
            te.table_row(f'{self.name} ступень {note}', '', '')
        if self.tau is not None:
            te.table_row(f'Время срабатывания автоматического ускорения {self.name} ступени, сек',
                         te.m(r't_{\text{АУ}}'), self.tau)


class ZMQPDIS(Element):
    Rl: float #активное сопротивление линии
    Xl: float #реактивное сопротивление линии
    Rd: float #сопротивление дуги (определяется по таблице)
    Rper: float = 5 #переходное сопротивление (опеределяется по методике стр.18)
    R0l: float #активное сопротивление линии нулевой последовательности
    X0l: float #реактивное сопротивление линии нулевой последовательности
    Xm: float = 0 #реактивное сопротивление взаимоиндукции нулевой последовательности
    Kch: float = 1.25#коэффициент чувствительности
    Ks: float = 0.8#коэффициент согласования
    Kots: float = 0.85#коэффициент отстройки
    X1: float #уставка ОКП
    X0: float #уставка ОКП
    X1max: float #максимальная уставка ступеней
    R1max: float #максимальная уставка ступеней
    R0max: float #максимальная уставка ступеней
    RFPPmax: float #максимальная уставка ступеней
    RFPEmax: float #максимальная уставка ступеней
    X0max: float #максимальная уставка ступеней
    RFFwPP: float #ОКП уставка
    RFRvPP: float #ОКП уставка
    RFFwPE: float #ОКП уставка
    RFRvPE: float
    RldFw: float
    RldRv: float
    ARGRld: float
    IminOpPP: float
    IminOpPE: float

    steps: list[ZMQPDIS_step]
    name: str = 'Дистанционная защита'
    name_short: str = 'ДЗ'

    def calc_ust(self, te: TextEngine, res_sc_min: list, res_sc_max: list):
        te.table_name(self.name)
        # X0l = self.X0l - self.Xm ** 2 / self.X0l
        te.table_head('Наименование величины', 'Расчётная формула, обозначение', 'Результат расчёта', widths=(3,2,1))
        te.table_row('Активное сопротивление линии, Ом',
                     'Rl', self.Rl)
        te.table_row('Реактивное сопротивление линии, Ом',
                     'Xl', self.Xl)
        te.table_row('Активное сопротивление линии нулевой последовательности, Ом',
                     'R0l', self.R0l)
        te.table_row('Реактивное сопротивление линии нулевой последовательности, Ом',
                     'X0l', self.X0l)
        te.table_row('Реактивное сопротивление взаимоиндукции линии, Ом',
                     'Xm', self.Xm)
        te.table_row('Коэффициент чувствительности', 'Kч', self.Kch)
        te.table_row('Коэффициент согласования', 'Kсогл', self.Ks)
        te.table_row('Коэффициент отстройки', 'Kотс', self.Kots)
        for step in self.steps:
            step.calc_ust(te, self, res_sc_min, res_sc_max)
        te.table_row('ОКП (PHS)', f'X1 = 2 * Xmax = 2 * {self.X1max} = {2 * self.X1max:.2f}', self.X1)
        te.table_row('ОКП (PHS)', f'X0 = 1.3 * X0max = 1.3 * {self.X0max} = {1.3 * self.X0max:.2f}', self.X0)
        te.table_row('ОКП (PHS)', f'RFFwPP = 1.2 * (R1max + RFPPmax) = 1.2 * ({self.R1max} + {self.RFPPmax}) '
                                  f'= {1.2 * (self.R1max + self.RFPPmax):.2f}', self.RFFwPP)
        # te.table_row('ОКП (PHS)', f'RFFwPE(RFRvPE) = 1.2 * ((2*R1max + R0max)/3 + RFPEmax) = 1.2 * ((2 * {self.R1max} + {self.R0max})/3 + {self.RFPEmax}) '
        #                           f'= {1.2 * ((2 * self.R1max + self.R0max) / 3 + self.RFPEmax):.2f}', self.RFFwPE)
        te.table_row('ОКП (PHS)', f'RFRvPP, Ом', self.RFRvPP)
        te.table_row('ОКП (PHS)', f'RFFwPE, Ом', self.RFFwPE)
        te.table_row('ОКП (PHS)', f'RFRvPE, Ом', self.RFRvPE)
        te.table_row('ОКП (PHS)', f'RldFw, Ом', self.RldFw)
        te.table_row('ОКП (PHS)', f'RldRv, Ом', self.RldRv)
        te.table_row('ОКП (PHS)', f'ARGRld, °', self.ARGRld)
        te.table_row('ОКП (PHS)', f'IminOpPP, %', self.IminOpPP)
        te.table_row('ОКП (PHS)', f'IminOpPE, %', self.IminOpPE)
