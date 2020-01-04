from tracks import *


def test_exit():
    l = Layout(size=4)
    l.add_track("EW", 2, 0, start=True)
    l.add_track("SW", 2, 2)
    l.add_track("NS", 0, 2, end=True)
    l.set_constraints("11300311")
    l.draw()
    try:
        l.begin()
    except ValueError as e:
        print(e)
        assert(e == "Complete")
