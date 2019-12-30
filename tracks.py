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
    def __init__(self):
        self.left = False
        self.right = False
        self.top = False
        self.bottom = False
        self.content = Content.EMPTY
        self.track = None

class Layout:
    def __init__(self, size=8):
        self.size = size
        self.scr = turtle.Screen()
        self.scr.title("Train tracks")
        self.turtle = turtle.Turtle()
        turtle.mode('standard')

        turtle.screensize(1000,1000)
        self.screen_size = 1000
        self.cell_size = self.screen_size/(size + 1)
        turtle.setworldcoordinates(0, 0, self.screen_size, self.screen_size)
        self.turtle.hideturtle()
        self.turtle.speed('fast')
        turtle.delay(0)
        turtle.tracer(0,0)
        self.turtle.penup()

        self.layout = []
        for y in range(size):
            col = []
            for x in range(size):
                col.append(Cell())
            self.layout.append(col)
        # Add borders
        for i in range(size):
            self.layout[0][i].bottom = True
            self.layout[size-1][i].top = True
            self.layout[i][0].left = True
            self.layout[i][size-1].right = True

    def draw(self):
        for row in range(self.size):
            for col in range(self.size):
                self.draw_cell(row, col)
        turtle.update()
        row = self.size
        font = font=('sans-serif', 18, 'normal')
        self.turtle.color('black')
        # Numbers across the top
        for col in range(self.size):
            x, y = self.coords(row, col)
            self.turtle.setpos(x+self.cell_size/3, y)
            self.turtle.write(self.col_constraints[col], font=font)
        col = self.size
        # Numbers down right side
        for row in range(self.size-1, -1, -1):
            x, y = self.coords(row, col)
            self.turtle.setpos(x + self.cell_size / 6, y + self.cell_size / 3 )
            self.turtle.write(self.row_constraints[row], font=font)
        # start and end
        x, y = self.coords(*self.start)
        self.turtle.setpos(x-self.cell_size / 3, y+self.cell_size / 3)
        self.turtle.write("A", font=font)
        x, y = self.coords(*self.end)
        self.turtle.setpos(x+self.cell_size / 3, y - self.cell_size / 2)
        self.turtle.write("B", font=font)
        turtle.update()
        # self.turtle.setpos()

    def coords(self, row, col):
        x = col * self.cell_size + self.cell_size / 2
        y = row * self.cell_size + self.cell_size / 2
        return x, y

    def draw_cell(self, row, col):
        cell = self.layout[row][col]
        x, y = self.coords(row, col)
        self.turtle.pensize(1)
        self.turtle.setpos(x, y)
        self.turtle.pendown()
        self.turtle.setheading(0)
        color = "red" if cell.bottom else "gray"
        self.turtle.color(color)
        self.turtle.forward(self.cell_size-4 )
        self.turtle.left(90)
        color = "red" if cell.right else "gray"
        self.turtle.color(color)
        self.turtle.forward(self.cell_size - 4)
        self.turtle.left(90)
        color = "red" if cell.top else "gray"
        self.turtle.color(color)
        self.turtle.forward(self.cell_size - 4)
        self.turtle.left(90)
        color = "red" if cell.left else "gray"
        self.turtle.color(color)
        self.turtle.forward(self.cell_size - 4)
        self.turtle.penup()
        self.draw_track(cell, x, y)
        self.turtle.penup()
        turtle.update()

    def draw_track(self, cell, x, y):
        """ draw th etrack piece in the cell """
        if cell.track:
            t = self.turtle
            s = self.cell_size
            s2 = s / 2
            x1 = x + s2
            x2 = x + s
            y1 = y + s2
            y2 = y + s
            r = self.cell_size * 3 / 4
            t.pensize(4)
            t.penup()
            color='gray'
            if cell.content == Content.TEMP_TRACK:
                color = ("blue")
            elif cell.content == Content.PERMANENT:
                color = ("orange")
            self.turtle.color(color)
            if cell.track == Track.NS:
                t.setheading(90)
                t.goto(x1, y)
                t.pendown()
                t.forward(s)
            elif cell.track == Track.EW:
                t.setheading(0)
                t.goto(x, y1)
                t.pendown()
                t.forward(s)
            elif cell.track == Track.NE:
                t.goto(x1, y2)
                t.pendown()
                t.goto(x, y1)
                # t.circle(-r, -90)
            elif cell.track == Track.SE:
                t.goto(x1, y)
                t.pendown()
                t.goto(x, y1)
                # t.circle(r, -90)
            elif cell.track == Track.NW:
                t.goto(x1, y2)
                t.pendown()
                t.goto(x2, y1)
                # t.circle(r, -90)
            elif cell.track == Track.SW:
                t.goto(x1, y)
                t.pendown()
                t.goto(x2, y1)
                # t.circle(-r, 90)
    def set_constraints(self, values):
        """ Takes string of 16 numbers representing top and right side """
        v = list(values)
        self.col_constraints = [int(i) for i in v[:8]]
        right = v[8:]
        right.reverse()
        self.row_constraints = [int(i) for i in right]


    def add_track(self, track=Track.EW, hcol=1, hrow=1, permanent=False):
        """ Add track uses human row column coordinates 1 to 8 """
        cell = self.layout[hrow-1][hcol-1]
        cell.content = Content.PERMANENT if permanent else Content.TEMP_TRACK
        cell.track = track
        name = track.name
        cell.top = False if "N" in name else True
        cell.bottom = False if "S" in name and hrow > 1 else True
        cell.left = False if "W" in name and hcol > 1 else True
        cell.right = False if "E" in name else True


    def set_start(self, hrow):
        self.start = (hrow - 1, 0,)

    def set_end(self, hcol):
        self.end = (0, hcol - 1,)

    def check_constraints(self, exact=False):
        for row in range(self.size):
            count = 0
            for col in range(self.size):
                if self.layout[row][col].content != Content.EMPTY:
                    count += 1
            if exact:
                if count != self.row_constraints[row]:
                    return False
            else:
                if count > self.row_constraints[row]:
                    return False
        for col in range(self.size):
            count = 0
            for row in range(self.size):
                if self.layout[row][col].content != Content.EMPTY:
                    count += 1
            if exact:
                if count != self.col_constraints[col]:
                    return False
            else:
                if count > self.col_constraints[col]:
                    return False
        return True

    def move_to(self, row, col, first_move=False):
        cell = self.layout[row][col]
        if cell.content == Content.PERMANENT:
            if (row, col) == self.start and not first_move:
                return False
            elif (row, col) == self.end:
                if self.check_constraints(exact = True):
                    print("FINISHED")
                    return True
        elif cell.content == Content.TEMP_TRACK:
            return False
        if cell.content == Content.EMPTY:
            cell.content = Content.TEMP_TRACK
        self.draw_cell(row, col)
        if self.check_constraints():
            if not cell.right:
                col += 1
                if not self.move_to(row, col):
                    self.undo(cell)
            if not cell.bottom:
                row -= 1
                if not self.move_to(row, col):
                    self.undo(cell)
            if not cell.left:
                col -= 1
                if not self.move_to(row, col):
                    self.undo(cell)
            if not cell.top:
                row += 1
                if not self.move_to(row, col):
                    self.undo(cell)

    def undo(self, cell):
        if cell.content == Content.TEMP_TRACK:
            cell.content = Content.EMPTY


board = Layout()
board.add_track(Track.NW, 1,2)
board.add_track(Track.NE, 1,3)
board.add_track(Track.SW, 1,4)
board.add_track(Track.SE, 1,5)
#
#
#
# board.add_track(Track.NW, 1, 7, True)
# board.add_track(Track.SE, 3, 8, True)
# board.add_track(Track.EW, 5, 3, True)
# board.add_track(Track.NS, 5, 1, True)
board.set_start(7)
board.set_end(5)
board.set_constraints("2464575286563421")
board.draw()
board.move_to(*board.start, first_move=True)
screen = turtle.Screen()
ans = screen.textinput("Done", "Hit key")
