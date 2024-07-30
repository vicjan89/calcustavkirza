from textengines.interfaces import TextEngine


from calcustavkirza.classes import Element


class EF4PTOC(Element):
    name: str = 'Направленная токовая защита нулевой последоветальности'
    name_short: str = 'НТЗНП'
    step: list[dict]
    Kn: float = 1.3 #коэффициент надёжности
    Ks: float = 1.1 #коэффициент согласования
    Kch: float = 1.3 #коэффициент чувствительности
    Kzap: float = 0.4 #коэффициент запаса
    dir: bool = True #необходимость расчёта органа направления мощности
    # [[pris]]
    # name = "ВЛ-110кВ на Полоцк-Районная"
    # [[pris.ef4]]
    # [[pris.ef4.step]]
    # step = 1
    # i_sz = 3300
    # t = 0
    # [[pris.ef4.step.condition]]
    # condition = 1
    # bus = 204
    # mode = 'Вкл. АТ-1,2 и СВВ-110 на Пол.330, откл.Г-7,8, откл. ВЛ-110 кВ Пол.- 330-ГПП-1,Пол.-330- НТЭЦ,Пол-330-Нафт.'
    # i = 2406
    # [[pris.ef4.step]]
    # step = 2
    # i_sz = 1975
    # t = 0.6
    # [[pris.ef4.step.condition]]
    # condition = 2
    # next_prot = 'с первой ступенью защиты ВЛ-110 кВ Районная-Полоцк-330 №2'
    # mode = 'Вкл. все АТ на Пол.330, откл.Г-5,6,7,8, откл. и заз. ВЛ-110 кВ Район-ная- ГПП-1, откл. ВЛ-110 кВ Районная-Мяс.'
    # i = 1796
    # [[pris.ef4.step]]
    # step = 3
    # i_sz = 420
    # t = 2.2
    # [[pris.ef4.step.condition]]
    # condition = 3
    # bus = 204
    # mode = 'Откл. АТ-1,2 Пол.330, в раб. один ген. НТЭЦ, вкл СВВ-110 на Пол.330 нет ген. Нафтана'
    # i = 1796

    def calc_ust(self, te: TextEngine, res_sc_min: list, res_sc_max: list):
        te.table_name(self.name)
        te.table_head('Наименование величины', 'Режим', 'Расчётная формула, обозначение', 'Результат',
                      widths=(2, 3, 1, 1))
        for s in self.step:
            for c in s['condition']:
                match c['condition']:
                    case 1:
                        te.table_row(f'Ток срабатывания {s['step']} ступени по условию отстройки от 3I0 при КЗ на '
                                     f'{res_sc_min[c['bus']][0]}, A',
                                     c['mode'], f'Iс.з. ≥ Кн·3I0max = {self.Kn}*{c["i"]}', f'{self.Kn * c["i"]:.1f}')
                    case 2:
                        te.table_row(f'Ток срабатывания {s['step']} ступени по условию согласования с последующей защитой '
                                     f'{c['next_prot']},  А', c['mode'], f'Iс.з. ≥ Ксогл· 3I0расч.мax = {self.Ks}*{c["i"]}',
                                     f'{self.Ks * c["i"]:.1f}')
                    case 3:
                        te.table_row(f'Ток срабатывания {s['step']} ступени по условию чувствительности при КЗ на '
                                     f'{res_sc_min[c['bus']][0]}, A',
                                     c['mode'], f'Iс.з.≤ 3I0min/Кч = {c["i"]} / {self.Kch}', f'{c["i"] / self.Kch:.1f}')

            note = ''
            if s.get('note'):
                note = s.get('note')
            te.table_row(f'Принимаем ток срабатывания {s['step']} ступени {note}, А', '', 'Iсз', f'{s['i_sz']}')
            if s.get('i'):
                te.table_row('Коэффициент чувствительности', s['mode'], f'Кч=Iкз/Iсз = {s["i"]}/{s["i_sz"]}',
                             f'{s["i"]/s["i_sz"]:.1f}')
            te.table_row(f'Время срабатывания  {s['step']} ступени по условию селективности, с '
                         f'{s.get('t_note', '')}', '', 'tср', s['t'])
        i_sz_min = min([s['i_sz'] for s in self.step])
        te.table_row('Минимальный ток нулевой последоваельности для органа направления мощности',
                     '', '3Iомин. = Кзап * 3I0рас.', f'{self.Kzap * i_sz_min:.1f}')
        te.table_row('Минимальный расчетный ток протекающий через защиту принимается равным току срабатывания самой '
                     'чувствительной ступени направленной ступени', '', '3I0рас.', f'{i_sz_min:.1f}')