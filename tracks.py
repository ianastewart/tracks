from enum import Enum
import turtle


class Track(Enum):
    NE = 1
    SE = 2
    SW = 3
    NW = 4
    NS = 5
    EW = 6


class Content(Enum):
    EMPTY = 0
    TEMP_TRACK = 1
    PERMANENT = 2


class Cell:
    def __init__(self, row, col, cell_size):
        self.cell_size = cell_size
        self.x = col * self.cell_size + self.cell_size / 2
        self.y = row * self.cell_size + self.cell_size / 2
        self.row = row
        self.col = col
        self.content = Content.EMPTY
        self.track = None
        self.must_connect = False
        self.is_start = False
        self.is_end = False

    def __str__(self):
        return f"R:{self.row} C:{self.col} {self.content} {self.track}"

    def is_empty(self):
        return self.content == Content.EMPTY

    def has_dir(self, dir):
        if self.content != Content.EMPTY:
            if self.track:
                if dir in self.track.name:
                    return True

    def draw_border(self, t):
        t.pensize(1)
        t.setpos(self.x, self.y)
        t.pendown()
        font = ("sans-serif", 18, "normal")
        t.color("gray")
        t.write(f" {self.row},{self.col}", font=font)
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
        """ draw the track piece in the cell """
        s = self.cell_size
        s2 = s / 2
        x1 = self.x + s2
        x2 = self.x + s
        y1 = self.y + s2
        y2 = self.y + s
        t.pensize(4)
        t.penup()
        if self.must_connect:
            t.goto(x1, y1)
            t.dot(10, "red")
        if self.track:
            color = "red"
            if self.content == Content.TEMP_TRACK:
                color = "yellow" if erase else "orange"
            elif self.content == Content.PERMANENT:
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
                # t.circle(-r, -90)
            elif self.track == Track.SE:
                t.goto(x1, self.y)
                t.pendown()
                t.goto(x1, y1)
                t.goto(x2, y1)
                # t.circle(r, -90)
            elif self.track == Track.NW:
                t.goto(x1, y2)
                t.pendown()
                t.goto(x1, y1)
                t.goto(self.x, y1)
                # t.circle(r, -90)
            elif self.track == Track.SW:
                t.goto(x1, self.y)
                t.pendown()
                t.goto(x1, y1)
                t.goto(self.x, y1)
                # t.circle(-r, 90)
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
        self.must_connect = []
        for row in range(size):
            col_list = []
            for col in range(size):
                col_list.append(Cell(row, col, self.cell_size))
            self.layout.append(col_list)

        self.start = 0
        self.end = 0
        self.move_count = 0
        self.move_max = 100000

    def draw(self):
        for row in range(self.size):
            for col in range(self.size):
                cell = self.layout[row][col]
                cell.draw_border(self.turtle)
                cell.draw_track(self.turtle)
        turtle.update()
        row = self.size
        font = ("sans-serif", 18, "normal")
        self.turtle.color("black")
        # Numbers across the top
        for col in range(self.size):
            x, y = self.coords(row, col)
            self.turtle.setpos(x + self.cell_size / 3, y)
            self.turtle.write(self.col_constraints[col], font=font)
        col = self.size
        # Numbers down right side
        for row in range(self.size - 1, -1, -1):
            x, y = self.coords(row, col)
            self.turtle.setpos(x + self.cell_size / 6, y + self.cell_size / 3)
            self.turtle.write(self.row_constraints[row], font=font)
        # start and end
        x, y = self.coords(self.start, 0)
        self.turtle.setpos(x - self.cell_size / 3, y + self.cell_size / 3)
        self.turtle.write("A", font=font)
        x, y = self.coords(0, self.end)
        self.turtle.setpos(x + self.cell_size / 3, y - self.cell_size / 2)
        self.turtle.write("B", font=font)
        turtle.update()

    def coords(self, row, col):
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
        cell.content = Content.PERMANENT
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

        cell.top = False if "N" in track else True
        cell.bottom = False if "S" in track and row > 0 else True
        cell.left = False if "W" in track and col > 0 else True
        cell.right = False if "E" in track else True
        # determine adjacent cells that must connect
        if not cell.top:
            self.layout[row + 1][col].must_connect = "S"
            self.must_connect.append(self.layout[row + 1][col])
        if not cell.bottom:
            self.layout[row - 1][col].must_connect = "N"
            self.must_connect.append(self.layout[row - 1][col])
        if not cell.left:
            self.layout[row][col - 1].must_connect = "E"
            self.must_connect.append(self.layout[row][col - 1])
        if not cell.right:
            self.layout[row][col + 1].must_connect = "W"
            self.must_connect.append(self.layout[row][col + 1])

    def moves(self, cell):
        """ return a list of possible moves for a cell """

        result = []
        r1 = cell.row - 1
        r2 = cell.row + 1
        c1 = cell.col - 1
        c2 = cell.col + 1

        if r2 < self.size and (cell.is_empty() or cell.has_dir("N")):
            if self.layout[r2][cell.col].content == Content.EMPTY:
                result.append("N")
            elif self.layout[r2][cell.col].has_dir("S"):
                result.append("N")
        if r1 >= 0 and (cell.is_empty() or cell.has_dir("S")):
            if self.layout[r1][cell.col].content == Content.EMPTY:
                result.append("S")
            elif self.layout[r1][cell.col].has_dir("N"):
                result.append("S")
        if c1 >= 0 and (cell.is_empty() or cell.has_dir("W")):
            if self.layout[cell.row][c1].content == Content.EMPTY:
                result.append("W")
            elif self.layout[cell.row][c1].has_dir("E"):
                result.append("W")
        if c2 < self.size and (cell.is_empty() or cell.has_dir("E")):
            if self.layout[cell.row][c2].content == Content.EMPTY:
                result.append("E")
            elif self.layout[cell.row][c2].has_dir("W"):
                result.append("E")
        if cell.is_start and "W" in result:
            result.remove("W")
        if cell.is_end and "S" in result:
            result.remove("S")
        return result

    def check_constraints(self, exact=False):
        """ Returns true if all cell counts within limits """
        self.row_count = []
        self.col_count = []
        for row in range(self.size):
            count = 0
            for col in range(self.size):
                cell = self.layout[row][col]
                if not cell.is_empty():
                    count += 1
                if exact:
                    if cell.must_connect and cell.is_empty():
                        print("Must connect failure")
                        return False
            self.row_count.append(self.row_constraints[row] - count)
            if exact:
                if count != self.row_constraints[row]:
                    print(
                        f"Exact Row {row} failure {count} != {self.row_constraints[row]}"
                    )
                    return False
            else:
                if count > self.row_constraints[row]:
                    print(f"Row {row} failure {count} > {self.row_constraints[row]}")
                    return False
        for col in range(self.size):
            count = 0
            for row in range(self.size):
                cell = self.layout[row][col]
                if not cell.is_empty():
                    count += 1
            self.col_count.append(self.col_constraints[col] - count)
            if exact:
                if count != self.col_constraints[col]:
                    print(
                        f"Exact column {col} failure {count} != {self.col_constraints[col]}"
                    )
                    return False
            else:
                if count > self.col_constraints[col]:
                    print(f"Column {col} failure {count} > {self.col_constraints[col]}")
                    return False
        if exact:
            for cell in self.must_connect:
                if cell.content != Content.EMPTY:
                    return True
        return True

    def not_trapped(self, cell):
        """ Return false if trapped one side of a full row or col and need to get to the other side """
        for c in range(1, self.size - 1):
            if self.col_count[c] == 0:
                if cell.col < c:
                    for i in range(c + 1, self.size):
                        if self.col_count[i] > 0:
                            return False
                elif cell.col > c:
                    for i in range(c - 1, 0, -1):
                        if self.col_count[i] > 0:
                            return False
        for r in range(1, self.size - 1):
            if self.row_count[r] == 0:
                if cell.row < r:
                    for i in range(r + 1, self.size):
                        if self.row_count[i] > 0:
                            return False
                elif cell.row > r:
                    for i in range(r - 1, 0, -1):
                        if self.row_count[i] > 0:
                            return False
        return True

    def not_one_short(self, cell):

        return True

        if cell.col > 0:
            if self.col_count[cell.col - 1] == 1:
                if cell.col == 1:
                    return False
                if self.col_count[cell.col - 2] == 0:
                    return False
        if cell.col < self.size - 1:
            if self.col_count[cell.col + 1] == 1:
                if cell.col == self.size - 2:
                    return False
                if self.col_count[cell.col + 2] == 0:
                    return False
        if cell.row > 0:
            if self.row_count[cell.row - 1] == 1:
                if cell.row == 1:
                    return False
                if self.row_count[cell.row - 2] == 0:
                    return False
        if cell.row < self.size - 1:
            if self.row_count[cell.row + 1] == 1:
                if cell.row == self.size - 2:
                    return False
                if self.row_count[cell.row + 2] == 0:
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
        if new_cell.content == Content.EMPTY:
            new_cell.content = Content.TEMP_TRACK
            undo = True
        if self.done(new_cell):
            raise ValueError("Complete")
        if self.check_constraints():
            if self.not_one_short(new_cell):
                if self.not_trapped(new_cell):
                    if undo:
                        new_cell.content = Content.EMPTY
                    moves = self.moves(new_cell)
                    if from_dir in moves:
                        moves.remove(from_dir)
                    # favour continuing in same direction
                    if dir in moves:
                        moves.remove(dir)
                        moves.insert(0, dir)
                    for to_dir in moves:
                        if new_cell.content == Content.EMPTY:
                            for tr in Track:
                                if from_dir in tr.name and to_dir in tr.name:
                                    new_cell.track = tr
                                    new_cell.content = Content.TEMP_TRACK
                                    break
                        self.move_from(new_cell, to_dir)
                else:
                    print("Would be trapped")
            else:
                print("One short")
        # get here if path we took is wrong somewhere
        if new_cell.content == Content.TEMP_TRACK:
            new_cell.content = Content.EMPTY
        if cell.content == Content.TEMP_TRACK:
            cell.draw_track(self.turtle, erase=True)
            cell.content = Content.EMPTY

    def begin(self):
        new_cell = self.layout[self.start][0]
        moves = self.moves(new_cell)
        for to_dir in moves:
            self.move_from(new_cell, to_dir)


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
                raise("Params wrong - 2")
        l.add_track(c[:2], int(c[2]), int(c[3]), start=start, end=end)
    return l


def main():
    board = parse("8:2464575286563421:NW60s:SE72:EW24:NS04e")

    # board = Layout(size=8)
    # board.add_track("NW", 6, 0, start=True)
    # board.add_track("SE", 7, 2)
    # board.add_track("EW", 2, 4)
    # board.add_track("NS", 0, 4, end=True)
    # board.set_constraints("2464575286563421")

    # board = Layout(size=4)
    # board.add_track(Track.SW, 2, 3)
    # board.add_track(Track.NW, 3, 1)
    # board.add_track(Track.EW, 0, 2, start=True)
    # board.add_track(Track.NS, 1, 0, end=True)
    # board.set_constraints("14322431")

    board.draw()

    try:
        board.begin()
    except ValueError as e:
        print(e)
    screen = turtle.Screen()
    ans = screen.textinput("Done", "Hit key")


if __name__ == "__main__":
    main()
