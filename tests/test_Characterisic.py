from calcustavkirza.Characteristic import Characteristic

def test_log10():
    ch = Characteristic('TM')
    print(ch.log10(142.8579, 1, 547.4278, 1000))
    print(ch.log10(41.964, 0.001, 465.2026, 1000))
