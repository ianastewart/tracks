from tracks import *


def test_exit():

    board = parse("4:11300311:EW20s:SW22:NS02e")
    board.draw(moves=True)
    try:
        board.solve()
    except ValueError as e:
        message = e.__str__()
        assert(message == "Complete")
    pass