'''Classes for save and get information about result calculation in PandaPower'''
class Res:

    def __init__(self, names: list):
        self.res = dict()
        self.names = names

    def update(self, mode, res):
        self.res[mode] = res

    @property
    def head(self):
        return [mode for mode in self.res]

    def __iter__(self):
        self.i = 0
        self.l = len(self.res[self.head[0]])
        return self


class Res_sc_line(Res):

    def get_max(self, index: int):
        '''
        Возвращает максимальный ток короткого замыкания для линии для всех режимов
        :param index: индекс линии для которой ищем максимальный ток
        :return: ток КЗ в амперах
        '''
        imax = 0
        for mode_name, res in self.res.items():
            i = res.loc[index, 'ikss_ka'].max()
            if i > imax:
                imax = i
        return imax * 1000

    def get_min(self, index: int):
        '''
        Возвращает минимальный ток короткого замыкания для линии для всех режимов
        :param index: индекс линии для которой ищем минимальный ток
        :return: ток КЗ в амперах
        '''
        imin = 0
        for mode_name, res in self.res.items():
            i = res.loc[index, 'ikss_ka']
            i = i[i > 0].min()
            if not imin:
                imin = i
            if i and i < imin:
                imin = i
        return imin * 1000

    def __next__(self):
        if self.i == self.l:
            raise StopIteration
        row = []
        for value in self.res.values():
            row.append(value.iloc[self.i]*1000)
        return self.names[self.i], *row

class Res_sc_trafo(Res):

    def get_max(self, index: int):
        '''
        Возвращает максимальный ток короткого замыкания для трансформаторов для всех режимов
        :param index: индекс трансформатора для которого ищем максимальный ток
        :return: ток КЗ в амперах
        '''
        i_kz_max = 0
        for mode_name, res in self.res.items():
            print(res.loc[(index,)])

    def __next__(self):
        if self.i == self.l:
            raise StopIteration
        row = []
        for value in self.res.values():
            row.append(value.iloc[self.i]*1000)
        return self.names[self.i], *row

class Res_sc_bus(Res):

    def __next__(self):
        if self.i == self.l:
            raise StopIteration
        row = []
        for value in self.res.values():
            row.append(value.iloc[self.i]['ikss_ka'] * 1000)
        name = self.names[self.i]
        self.i += 1
        return name, row

    def get_max(self, index: int):
        '''
        Возвращает максимальный ток короткого замыкания для шины для всех режимов
        :param index: индекс шины для которой ищем максимальный ток
        :return: ток КЗ в амперах
        '''
        imax = 0
        for mode_name, res in self.res.items():
            i = res.loc[index, 'ikss_ka'].max()
            if i > imax:
                imax = i
        return imax * 1000

class Res_sc:

    def __init__(self, name_line, name_trafo):
        self.line = Res_sc_line(name_line)
        self.trafo = Res_sc_trafo(name_trafo)

    def get_max(self, loc: dict):
        if loc['type'] == 'line':
            return self.line.get_max(loc['index'])
        if loc['type'] == 'trafo':
            return self.trafo.get_max(loc['index'])

    def get_min(self, loc: dict):
        if loc['type'] == 'line':
            return self.line.get_min(loc['index'])
        if loc['type'] == 'trafo':
            return self.trafo.get_min(loc['index'])

class Res_pf_line(Res):

    def get_max(self, index: int):
        '''
        Возвращает максимальный ток нагрузки для линии для всех режимов
        :param index: индекс линии для которой ищем максимальный ток
        :return: ток КЗ в амперах
        '''
        imax = 0
        for mode_name, res in self.res.items():
            i = res.loc[index, 'i_ka']
            if i > imax:
                imax = i
        return imax * 1000

    def __next__(self):
        if self.i == self.l:
            raise StopIteration
        row = []
        for value in self.res.values():
            row.append(value.iloc[self.i]['i_ka']*1000)
        name = self.names[self.i]
        self.i += 1
        return name, row

class Res_pf_trafo(Res):

    def get_max(self, index: int):
        '''
        Возвращает максимальный ток нагрузки для трансформатора для всех режимов
        :param index: индекс трансформатора для которого ищем максимальный ток
        :return: ток КЗ в амперах
        '''
        imax = 0
        for mode_name, res in self.res.items():
            i = res.loc[index, 'i_hv_ka']
            if i > imax:
                imax = i
        return imax * 1000

    def __next__(self):
        if self.i == self.l:
            raise StopIteration
        row = []
        for value in self.res.values():
            row.append(value.iloc[self.i]['i_hv_ka']*1000)
        name = self.names[self.i]
        self.i += 1
        return name, row

class Res_pf_switch(Res):

    def get_max(self, index: int):
        '''
        Возвращает максимальный ток нагрузки для коммутационного аппарата для всех режимов
        :param index: индекс трансформатора для которого ищем максимальный ток
        :return: ток КЗ в амперах
        '''
        imax = 0
        for mode_name, res in self.res.items():
            i = res.loc[index, 'i_ka']
            if i > imax:
                imax = i
        return imax * 1000

    def __next__(self):
        if self.i == self.l:
            raise StopIteration
        row = []
        for value in self.res.values():
            row.append(value.iloc[self.i]['i_ka']*1000)
        name = self.names[self.i]
        self.i += 1
        return name, row

class Res_pf:

    def __init__(self, name_line, name_trafo, name_switch):
        self.line = Res_pf_line(name_line)
        self.trafo = Res_pf_trafo(name_trafo)
        self.switch = Res_pf_switch(name_switch)

    def get_max(self, loc: dict):
        if loc['type'] == 'line':
            return self.line.get_max(loc['index'])
        if loc['type'] == 'trafo':
            return self.trafo.get_max(loc['index'])
        if loc['type'] == 'switch':
            return self.switch.get_max(loc['index'])
