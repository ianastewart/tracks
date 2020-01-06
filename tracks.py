from enum import Enum
from time import perf_counter
import turtle

FONT = ("sans-serif", 18, "normal")
DEBUG = False


class Track(Enum):
    NE = 1
    SE = 2
    SW = 3
    NW = 4
    NS = 5
    EW = 6
    TEMP = 7

    @classmethod
    def identify(cls, str):
        """ return matching enum from 2 char string, order undefined"""
        for tr in cls:
            if str[0] in tr.name and str[1] in tr.name:
                return tr


class Cell:
    def __init__(self, row, col, cell_size):
        self.cell_size = cell_size
        self.x = col * self.cell_size + self.cell_size / 2
        self.y = row * self.cell_size + self.cell_size / 2
        self.row = row
        self.col = col
        self.permanent = False
        self.track = None
        self.must_connect = ""
        self.is_start = False
        self.is_end = False

    def __str__(self):
        return f"R:{self.row} C:{self.col} {self.content} {self.track}"

    def is_empty(self):
        return self.track is None

    def has_dir(self, dir):
        if self.track:
            return dir in self.track.name

    def draw_border(self, t):
        t.pensize(1)
        t.setpos(self.x, self.y)
        t.pendown()
        t.color("gray")
        if DEBUG:
            t.write(f" {self.row},{self.col}", font=FONT)
        t.setheading(0)
        t.forward(self.cell_size)
        t.left(90)
        t.forward(self.cell_size)
        t.left(90)
        t.forward(self.cell_size)
        t.left(90)
        t.forward(self.cell_size)
        t.penup()

    def draw_track(self, t, erase=False):
        """ Draw the track piece in the cell """
        s = self.cell_size
        s2 = s / 2
        x1 = self.x + s2
        x2 = self.x + s
        y1 = self.y + s2
        y2 = self.y + s
        t.pensize(4)
        t.penup()
        if DEBUG and self.must_connect:
            t.goto(x1, y1)
            t.write(self.must_connect, font=FONT)
        if self.track:
            color = "white" if erase else "black"
            if self.permanent:
                color = "blue"
            t.color(color)
            if self.track == Track.NS:
                t.setheading(90)
                t.goto(x1, self.y)
                t.pendown()
                t.forward(s)
            elif self.track == Track.EW:
                t.setheading(0)
                t.goto(self.x, y1)
                t.pendown()
                t.forward(s)
            elif self.track == Track.NE:
                t.goto(x1, y2)
                t.pendown()
                t.goto(x1, y1)
                t.goto(x2, y1)
            elif self.track == Track.SE:
                t.goto(x1, self.y)
                t.pendown()
                t.goto(x1, y1)
                t.goto(x2, y1)
            elif self.track == Track.NW:
                t.goto(x1, y2)
                t.pendown()
                t.goto(x1, y1)
                t.goto(self.x, y1)
            elif self.track == Track.SW:
                t.goto(x1, self.y)
                t.pendown()
                t.goto(x1, y1)
                t.goto(self.x, y1)
            t.penup()
            turtle.update()


class Layout:
    def __init__(self, size=8):
        self.size = size
        self.scr = turtle.Screen()
        self.scr.title("Train tracks")
        self.turtle = turtle.Turtle()
        turtle.mode("standard")

        turtle.screensize(1000, 1000)
        self.screen_size = 1000
        self.cell_size = self.screen_size / (size + 1)
        turtle.setworldcoordinates(0, 0, self.screen_size, self.screen_size)
        self.turtle.hideturtle()
        self.turtle.speed("fast")
        turtle.delay(0)
        turtle.tracer(0, 0)
        self.turtle.penup()

        self.layout = []
        for row in range(size):
            col_list = []
            for col in range(size):
                col_list.append(Cell(row, col, self.cell_size))
            self.layout.append(col_list)

        self.start = 0
        self.end = 0
        self.move_count = 0
        self.move_max = 1000000
        self.col_count = []
        self.row_count = []
        self.col_perm = []
        self.row_perm = []

    def draw(self, moves=False):
        """ Draw the whole layout """
        for row in range(self.size):
            for col in range(self.size):
                cell = self.layout[row][col]
                cell.draw_border(self.turtle)
                if moves:
                    s = self.cell_size / 6
                    self.turtle.goto(cell.x + s, cell.y + s)
                    self.turtle.write(self.moves(cell))
                cell.draw_track(self.turtle)
        turtle.update()
        row = self.size
        self.turtle.color("black")
        # Numbers across the top
        for col in range(self.size):
            x, y = self.coords(row, col)
            self.turtle.setpos(x + self.cell_size / 3, y)
            self.turtle.write(self.col_constraints[col], font=FONT)
        col = self.size
        # Numbers down right side
        for row in range(self.size - 1, -1, -1):
            x, y = self.coords(row, col)
            self.turtle.setpos(x + self.cell_size / 6, y + self.cell_size / 3)
            self.turtle.write(self.row_constraints[row], font=FONT)
        # start and end
        x, y = self.coords(self.start, 0)
        self.turtle.setpos(x - self.cell_size / 3, y + self.cell_size / 3)
        self.turtle.write("A", font=FONT)
        x, y = self.coords(0, self.end)
        self.turtle.setpos(x + self.cell_size / 3, y - self.cell_size / 2)
        self.turtle.write("B", font=FONT)
        turtle.update()

    def coords(self, row, col):
        """ Convert row, column to screen coordinates """
        x = col * self.cell_size + self.cell_size / 2
        y = row * self.cell_size + self.cell_size / 2
        return x, y

    def draw_moves(self, cell):
        """ debug routine to list all possible moves from a cell """
        self.turtle.goto(cell.x, cell.y)
        self.turtle.write(self.moves(cell))

    def set_constraints(self, values):
        """ Takes string of numbers representing top and right side """
        v = list(values)
        self.col_constraints = [int(i) for i in v[: self.size]]
        right = v[self.size :]
        right.reverse()
        self.row_constraints = [int(i) for i in right]

    def add_track(self, track, row, col, start=False, end=False):
        """
        Add a permanent piece of track to the layout
        Start and end are special cases
        """
        cell = self.layout[row][col]
        cell.permanent = True
        cell.track = Track[track]
        if start:
            if col != 0:
                raise ValueError("Invalid start position")
            self.start = row
            cell.is_start = True
        if end:
            if row != 0:
                raise ValueError("Invalid end position")
            self.end = col
            cell.is_end = True

        # determine adjacent cells that must connect
        if "N" in track:
            self.layout[row + 1][col].must_connect += "S"
        if "S" in track and row > 0:
            self.layout[row - 1][col].must_connect += "N"
        if "W" in track and col > 0:
            self.layout[row][col - 1].must_connect += "E"
        if "E" in track:
            self.layout[row][col + 1].must_connect += "W"

    def moves(self, cell):
        """ return a list of possible moves from a cell """

        result = []
        r1 = cell.row - 1
        r2 = cell.row + 1
        c1 = cell.col - 1
        c2 = cell.col + 1

        if r2 < self.size and (not cell.track or cell.has_dir("N")):
            new_cell = self.layout[r2][cell.col]
            if not new_cell.track or new_cell.has_dir("S"):
                result.append("N")
        if r1 >= 0 and (not cell.track or cell.has_dir("S")):
            new_cell = self.layout[r1][cell.col]
            if not new_cell.track or new_cell.has_dir("N"):
                result.append("S")
        if c1 >= 0 and (not cell.track or cell.has_dir("W")):
            new_cell = self.layout[cell.row][c1]
            if not new_cell.track or new_cell.has_dir("E"):
                result.append("W")
        if c2 < self.size and (not cell.track or cell.has_dir("E")):
            new_cell = self.layout[cell.row][c2]
            if not new_cell.track or new_cell.has_dir("W"):
                result.append("E")
        if cell.is_start and "W" in result:
            result.remove("W")
        if cell.is_end and "S" in result:
            result.remove("S")
        return result

    def check_constraints(self, exact=False):
        """ Returns true if all cell counts within limits """
        self.row_count = (
            []
        )  # difference between actual count of occupied cells and expected count
        self.row_perm = []  # number of permanent cells in this row
        self.col_count = []
        self.col_perm = []
        for row in range(self.size):
            count = 0
            perm = 0
            for col in range(self.size):
                cell = self.layout[row][col]
                if cell.track:
                    count += 1
                if cell.permanent:
                    perm += 1
                if exact:
                    if cell.must_connect and not cell.track:
                        if DEBUG:
                            print("Must connect failure")
                        return False
            self.row_count.append(self.row_constraints[row] - count)
            self.row_perm.append(perm)
            if exact:
                if count != self.row_constraints[row]:
                    if DEBUG:
                        print(
                            f"Exact Row {row} failure {count} != {self.row_constraints[row]}"
                        )
                    return False
            elif count > self.row_constraints[row]:
                if DEBUG:
                    print(f"Row {row} failure {count} > {self.row_constraints[row]}")
                return False
        for col in range(self.size):
            count = 0
            perm = 0
            for row in range(self.size):
                cell = self.layout[row][col]
                if cell.track:
                    count += 1
                if cell.permanent:
                    perm += 1
            self.col_count.append(self.col_constraints[col] - count)
            self.col_perm.append(perm)
            if exact:
                if count != self.col_constraints[col]:
                    if DEBUG:
                        print(
                            f"Exact column {col} failure {count} != {self.col_constraints[col]}"
                        )
                    return False
            elif count > self.col_constraints[col]:
                if DEBUG:
                    print(f"Column {col} failure {count} > {self.col_constraints[col]}")
                return False
        return True

    def not_trapped(self, cell):
        """ Return false if trapped one side of a full row or col and need to get to the other side """

        for c in range(1, self.size - 1):
            if self.col_count[c] == 0:
                # ignore cols with a permanent track - if not connected, it may be a path back to other side
                if self.col_perm[c] == 0:
                    if cell.col < c:
                        for i in range(c + 1, self.size):
                            if self.col_count[i] > 0:
                                return False
                    elif cell.col > c:
                        for i in range(0, c):
                            if self.col_count[i] > 0:
                                return False
        for r in range(1, self.size - 1):
            if self.row_count[r] == 0:
                # ignore rows with a permanent track - if not connected, it may be a path back to other side
                if self.row_perm[r] == 0:
                    if cell.row < r:
                        for i in range(r + 1, self.size):
                            if self.row_count[i] > 0:
                                return False
                    if cell.row > r:
                        for i in range(0, 2):
                            if self.row_count[i] > 0:
                                return False
        return True

    def done(self, cell):
        if cell.row == 0 and cell.col == self.end:
            if self.check_constraints(exact=True):
                return True
        return False

    def move_from(self, cell, dir):
        """ move from cell in direction dir  """
        self.move_count += 1
        if self.move_count == self.move_max:
            raise ValueError("Max move count reached")
        # if self.move_count == 8400:
        #     self.draw()
        #     breakpoint()
        if DEBUG:
            cell.draw_track(self.turtle)
        if dir == "N":
            from_dir = "S"
            new_cell = self.layout[cell.row + 1][cell.col]
        elif dir == "S":
            from_dir = "N"
            new_cell = self.layout[cell.row - 1][cell.col]
        elif dir == "E":
            from_dir = "W"
            new_cell = self.layout[cell.row][cell.col + 1]
        elif dir == "W":
            from_dir = "E"
            new_cell = self.layout[cell.row][cell.col - 1]
        undo = False
        # temporarily add a track if empty so can calculate constraints
        if not new_cell.track:
            new_cell.track = Track.TEMP
        if self.done(new_cell):
            raise ValueError("Solved")
        if self.check_constraints():
            if self.not_trapped(new_cell):
                if new_cell.track == Track.TEMP:
                    new_cell.track = None
                moves = self.moves(new_cell)
                if from_dir in moves:
                    moves.remove(from_dir)
                bad_move = False
                # must connect cells are special case not handled in move generation
                if new_cell.must_connect:
                    if from_dir in new_cell.must_connect:
                        to_dir = new_cell.must_connect.replace(from_dir, "")
                        if to_dir:
                            moves = to_dir
                    else:
                        if len(new_cell.must_connect) == 1:
                            moves = new_cell.must_connect
                        else:
                            # must connect cell is already fully connected
                            bad_move = True

                if not bad_move:
                    # Recursively explore each possible move, depth first
                    for to_dir in moves:
                        if not new_cell.track:
                            new_cell.track = Track.identify(from_dir + to_dir)
                        self.move_from(new_cell, to_dir)
            else:
                if DEBUG:
                    print("Would be trapped")
        # Get here if all moves fail and we need to backtrack
        if not new_cell.permanent:
            new_cell.track = None
        if not cell.permanent:
            if DEBUG:
                cell.draw_track(self.turtle, erase=True)
            cell.track = None

    def solve(self):
        """ Initiate the recursive solver """
        new_cell = self.layout[self.start][0]
        moves = self.moves(new_cell)
        for to_dir in moves:
            self.move_from(new_cell, to_dir)
        raise ValueError("Failed to find solution")

    def result(self, message, elapsed):
        self.draw()
        self.turtle.goto(0, 0)
        self.turtle.color("black")
        self.turtle.write(
            f"{message} in {self.move_count} moves. Time:{elapsed:.2f}s", font=FONT
        )
        self.scr.textinput("Done", "Hit key")


def parse(params):
    """
    Structure: Size:Constraints:track-tuple:track-tuple
    """
    bits = params.split(":")
    size = int(bits[0])
    if len(bits[1]) != 2 * size:
        raise ValueError("Params wrong - 1")
    l = Layout(size)
    l.set_constraints(bits[1])
    for i in range(2, len(bits)):
        c = bits[i]
        start = False
        end = False
        if len(c) == 5:
            if c[4] == "s":
                start = True
            elif c[4] == "e":
                end = True
            else:
                raise ("Params wrong - 2")
        l.add_track(c[:2], int(c[2]), int(c[3]), start=start, end=end)
    return l


def main():
    board = parse("8:2464575286563421:NW60s:SE72:EW24:NS04e") #904
    # board = parse("8:3456623347853221:NW30s:SW32:SW62:NS04e") #907
    # board = parse("8:8443143523676422:NW00s:NE41:NS45:NS07e") #908
    # board = parse("8:1216564534576221:EW40s:NS03e:NS45") #909
    # board = parse("8:1225446636611544:EW60s:NS03e:EW75:SE26") #910

    # board = parse("8:4533433525853421:SW40s:NE52:NS03e")
    board.draw()
    try:
        start = perf_counter()
        board.solve()
    except ValueError as e:
        end = perf_counter()
        elapsed = end - start
        board.result(str(e), elapsed)


if __name__ == "__main__":
    main()
