from tracks import *


def test_exit():
    l = Layout(size=4)
    l.add_track(Track.EW, 2, 0)
    l.add_track(Track.SW, 2, 2)
    l.add_track(Track.NS, 0, 2)
    l.set_constraints("11300311")
    l.set_start(3)
    l.set_end(3)
    l.draw()
    try:
        l.begin()
    except ValueError as e:
        print(e)
        assert(e = "Complete")
