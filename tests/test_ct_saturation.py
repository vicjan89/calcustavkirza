import pytest


import matplotlib.pyplot as plt


from calcustavkirza.select.CT import CT


@pytest.fixture
def data():
    data = [[{ #данные из примера Б.8 ПНСТ 283-2018
        'name': 'ТТ из ПНСТ',
        'model': 'ТФЗМ-500',
        'i1': 2000,
        'i2': 1,
        'length': 900,
        's': 2.5,
        'kr': 0,
        'cos': 1,
        'accuracy': '10Р',
        'sn': 50,
        'kn': 18,
        'r2': 10,
        'loads': [0],
        'isc1': [
            {
                'name': '',
                'i': 20910,
                't': 217,
            },
            {
                'name': '',
                'i': 2366,
                't': 60,
            },
            {
                'name': '',
                'i': 3380,
                't': 32.4,
            },
        ],
        'isc3': [
            {
                'name': '',
                'i': 20910,
                't': 217,
            },
        ]
    }, {'r_cab': 6.3, 'a1ph': 3.55, 't_eq1ph': 180, 't_saturation1ph': 8.3, 'saturation': True}],
        [
    { #данные из примера Г-3
        'name': '15TA(17TA) Г-3',
        'model': 'ТШЛ-20',
        'i1': 12000,
        'i2': 5,
        'length': 60,
        's': 6,
        'kr': 0.86,
        'cos': 0.8,
        'r_cont': 0,
        'accuracy': '10Р',
        'sn': 30,
        'kn': 50,
        'r2': 4.985,
        'loads': [0],
        'isc1': [
            {
                'name': '',
                'i': 20910,
                't': 217,
            },
            {
                'name': '',
                'i': 2366,
                't': 60,
            },
            {
                'name': '',
                'i': 3380,
                't': 32.4,
            },
        ],
        'isc3': [
            {
                'name': '',
                'i': 58713,
                't': 67,
            },
        ]
    }, {'r_cab': 0.175, 'a3ph': 11.81, 't_eq3ph': 67, 't_saturation3ph': 48.31, 't_saturation3ph_kr': 2.11, 'saturation3ph': True}],
        [
            { #данные из ГОСТ Р 58669-2019 B.2
                'name': 'SAS 550',
                'model': 'SAS',
                'i1': 2000,
                'i2': 1,
                'length': 900,
                's': 2.5,
                'kr': 0,
                'cos': 0.8,
                'v': 0,
                'accuracy': '10Р',
                'sn': 40,
                'kn': 20,
                'r2': 7.51,
                'loads': [1],
                'isc3': [
                    {
                        'i': 2899,
                        't': 283,
                    },
                    {
                        'i': 2882,
                        't': 283,
                    },
                    {
                        'i': 2861,
                        't': 283,
                    },
                    {
                        'i': 1766,
                        't': 60,
                    },
                    {
                        'i': 3248,
                        't': 32.4,
                    },
                    {
                        'i': 3172,
                        't': 32.2,
                    },
                    {
                        'i': 1642,
                        't': 32.8,
                    },
                    {
                        'i': 1328,
                        't': 32.4,
                    },
                    {
                        'i': 1684,
                        't': 32.2,
                    },
                    {
                        'i': 1663,
                        't': 32.6,
                    },
                ],
                'isc1': [
                    {
                        'i': 7226,
                        't': 217,
                    },
                    {
                        'i': 6980,
                        't': 217,
                    },
                    {
                        'i': 6948,
                        't': 217,
                    },
                    {
                        'i': 2366,
                        't': 60,
                    },
                    {
                        'i': 832,
                        't': 32.4,
                    },
                    {
                        'i': 797,
                        't': 32.2,
                    },
                    {
                        'i': 401,
                        't': 32.8,
                    },
                    {
                        'i': 441,
                        't': 32.4,
                    },
                    {
                        'i': 458,
                        't': 32.2,
                    },
                    {
                        'i': 451,
                        't': 32.6,
                    },
                ]
            }, {'r_cab': 6.3, 'a1ph': 3.418, 'a3ph': 5.785, 't_eq1ph': 180, 't_eq3ph': 128,
                'saturation3ph': True}],
    ]

    return data

def test_r_cab(data):
    for d in data:
        r_cab = d[1].get('r_cab')
        if r_cab:
            ct = CT(**d[0])
            assert abs(ct.r_cab - r_cab) < r_cab * 0.01

def test_a1ph(data):
    for d in data:
        a1ph = d[1].get('a1ph')
        if a1ph:
            ct = CT(**d[0])
            a1ph_calc = ct.a1ph
            res = abs(a1ph_calc - a1ph)
            print(f'\n{a1ph_calc=} {a1ph=} res={res/a1ph*100:.2f}%')
            assert res < a1ph * 0.02

def test_a3ph(data):
    for d in data:
        a3ph = d[1].get('a3ph')
        if a3ph:
            ct = CT(**d[0])
            a3ph_calc = ct.a3ph
            res = abs(a3ph_calc - a3ph)
            print(f'\n{a3ph_calc=} {a3ph=} res={res/a3ph*100:.2f}%')
            assert abs(a3ph_calc - a3ph) < a3ph * 0.03

def test_t_eq1ph(data):
    for d in data:
        if d[1].get('t_eq1ph'):
            ct = CT(**d[0])
            assert abs(ct.t_eq1ph - d[1]['t_eq1ph']) < d[1]['t_eq1ph'] * 0.01

def test_t_eq3ph(data):
    for d in data:
        if d[1].get('t_eq3ph'):
            ct = CT(**d[0])
            assert abs(ct.t_eq3ph - d[1]['t_eq3ph']) < d[1]['t_eq3ph'] * 0.01

def test_t_saturation1ph(data):
    for d in data:
        t = d[1].get('t_saturation1ph')
        if t:
            ct = CT(**d[0])
            assert abs(ct.t_saturation1ph - t) < 0.02

def test_t_saturation3ph(data):
    for d in data:
        t = d[1].get('t_saturation3ph')
        if t:
            ct = CT(**d[0])
            ct.kr = 0
            t_saturation3ph_calc = ct.t_saturation3ph
            res = abs(t_saturation3ph_calc - t)
            print(f'\n{ct.kr=} {t_saturation3ph_calc=} {t=} res={res/t*100:.2f}%')
            assert res < t * 0.07
        t = d[1].get('t_saturation3ph_kr')
        if t:
            ct = CT(**d[0])
            ct.kr = 0.86
            t_saturation3ph_calc = ct.t_saturation3ph
            res = abs(t_saturation3ph_calc - t)
            print(f'\n{ct.kr=} {t_saturation3ph_calc=} {t=} res={res/t*100:.2f}%')
            assert res < t * 0.01

def test_saturation3ph(data):
    for d in data:
        saturation = d[1].get('saturation3ph')
        if saturation is not None:
            ct = CT(**d[0])
            assert ct.saturation3ph == saturation

def test_saturation1ph(data):
    for d in data:
        saturation = d[1].get('saturation1ph')
        if saturation is not None:
            ct = CT(**d[0])
            assert ct.saturation1ph == saturation

def test_k_p_r(data):
    d = data[2]
    ct = CT(**d[0])
    axis_t = []
    axis_k1 = []
    axis_k3 = []
    for t in range(0, 1000):
        axis_t.append(t)
        t /= 1000
        axis_k1.append(ct.k_p_r(t=t, kz3ph=False))
        axis_k3.append(ct.k_p_r(t=t, kz3ph=True))
    fig, ax = plt.subplots()
    ax.plot(axis_t, axis_k3, label='Для режима трёхфазного КЗ')
    ax.plot(axis_t, axis_k1, label='Для режима однофазного КЗ')
    ax.set(xlabel='t,мc', ylabel='Кп.р.',
           title='Временные диаграммы коэффициента Кп.р.')
    ax.grid()
    plt.legend()
    plt.show()
