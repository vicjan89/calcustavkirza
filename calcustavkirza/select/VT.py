import math

from calcustavkirza.classes import Element


class SelectVT(Element):
    name: str
    model: str
    location: str
    u1: int
    u2: int
    ud2: int
    u1max: int
    u2accuracy: float
    u2daccuracy: float | str
    u2s: int
    u2ds: int
    u2load: list[tuple]
    ud2load: list[tuple]
    lenght: float # ����� ������ �� �����������
    s: float # ������� ������ �� �����������
    u2permissible: float # ���������� ������� ����������


    def select(self):
        self.te.h1('����� � �������� ��������������� ����������')
        self.te.h2(f'�������� ���������� � ����� �� {self.name}')
        self.te.h3('��� �������� ���������� ������ ��������������� ���������� �� ���������� ����������������:')
        self.te.ul(f'����� ��������� {self.location}')
        self.te.ul(f'������ �������������� {self.model}')
        self.te.ul(f'����� ���������� {self.u1} �')
        self.te.ul(f'���������� ������� ���������� {self.u1max} ��')
        self.te.ul(f'����������� �������� ��������� ���������� {self.u1} �')
        self.te.ul(f'����������� �������� ��������� ���������� {self.u2} �')
        self.te.ul(f'���������� �� ������� ������������� ������������ �������������� ��������� ������� ��� ��������� '
                   f'����� �� ��� ���� �� ����� {self.ud2}�')
        self.te.ul(f'����� �������� �������� ��������� ������� {self.u2accuracy}')
        self.te.ul(f'����������� �������� �������� ��������� ������� {self.u2s} ��')
        self.te.ul(f'����� �������� �������������� ��������� ������� ���������� �� ����� "������������ ������������" {self.u2daccuracy}')
        self.te.ul(f'����������� �������� ��������� ������� ���������� �� ����� "������������ ������������" {self.u2ds} ��')

        self.te.h3('������ �������� �������� �������� ��������� ������� �������������� ����������.')
        self.te.table_name('�������� ������ ��� �������� �������')
        u2ssum = self.table_load(self.u2load)
        self.te.table_name('�������� ������ ��� �������������� ��������� ������� ���������� �� ����� "������������ ������������"')
        ud2ssum = self.table_load(self.ud2load)

        self.te.h3('������ �� ����������� ������� ����������')
        self.te.p('��� � �������� ����������� ���� ��������� ������� �� �������:')
        self.te.math(r'I_{\text{����}} = \frac{\sqrt{3} \cdot S_{\text{����}}}{U_{\text{��}}}, �')
        i = u2ssum * math.sqrt(3) / self.u2
        self.te.math(r'I_{\text{����}} = \frac{\sqrt{3} \cdot ' + f'{u2ssum}' + r'}{' + str(self.u2) +'} = ' +
                     f'{i:.4f}  A')
        self.te.ul(' ��� ' + self.te.m(r'S_{\text{����}}') + ' � �������� �������� ����������� ����, ��,')
        self.te.ul(' ' + self.te.m(r'U_{\text{��}}') + ' � ����������� ����������� ����������, �.')
        self.te.p('������������� ��������� ����� �� �������������� ���������� �� ��������� ����������� ����������:')
        self.te.math(r'R_{\text{���}} = \text{?} \cdot \frac{l}{S} ,')
        r = 0.0175 * self.lenght / self.s
        self.te.math(r'R_{\text{���}} = 0.0175 \cdot \frac{' + str(self.lenght) + '}{' + str(self.s) + '} = ' +
                     f'{r:.4f}' + r' \text{��}')
        self.te.ul('��� ? � �������� ������������� ���� ������ 0,0175 ' +
                   self.te.m(r'\text{��} \cdot \frac{\text{��}^2}{\text{�}};'))
        self.te.ul('l � ����� ������������ ������, �; ')
        self.te.ul('S � ������� ������������ ������, ��2')
        self.te.p('�������� ������� ���������� �� �������� ����������� ����������� � ������� �� �������:')
        self.te.math(r'?U = \sqrt{3} \cdot I_{\text{����}} \cdot R_{\text{���}} < ?U_{\text{���}}')
        u2perm = math.sqrt(3) * i * r / self.u2 * 100
        self.te.p('��������� �������:')
        self.te.math(r'?U = \sqrt{3} \cdot ' + f'{i:.3f}' + ' \cdot ' + f'{r:.3f} = {u2perm:.4f}' + r' \% < ' +
                     f'{self.u2permissible}' + ' \%')
        self.te.p('���������� � ������ �������� �� ��� ����� ����� � ����� � ����������� ������� ���������� ���������� '
                  '� ������������ � ��� 339-2022 (33240).')


    def table_load(self, load: list[tuple]):
        self.te.table_head('���������� ������������ � ��', '�������� ����������� (��� ������� ������ �� ���� ����), ��')
        ssum = 0
        for device, power in load:
            self.te.table_row(device, power)
            ssum += power
        self.te.table_row('�����', ssum)
        return ssum
