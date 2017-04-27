# coding:utf-8

import time
import Tkinter
import cStringIO
import random
import config as cfg


class Cell:
    def __init__(self):
        self.wall = False

    def color(self):
        if self.wall:
            return cfg.wall_color
        else:
            return 'white'

    def load(self, data):
        if data == 'X':
            self.wall = True
        else:
            self.wall = False

    def __getattr__(self, key):
        if key == 'neighbors':
            opts = [self.world.get_next_grid(self.x, self.y, dir) for dir in xrange(self.world.directions)]
            next_states = tuple(self.world.grid[y][x] for (x, y) in opts)
            return next_states
        raise AttributeError(key)


class Agent:
    def __setattr__(self, key, value):
        if key == 'cell':
            old = self.__dict__.get(key, None)
            if old is not None:
                old.agents.remove(self)
            if value is not None:
                value.agents.append(self)
        self.__dict__[key] = value

    def go_direction(self, dir):
        target = self.cell.neighbors[dir]
        if getattr(target, 'wall', False):
            print "hit a wall"
            return False
        self.cell = target
        return True


class World:
    def __init__(self, cell=None, directions=cfg.directions, filename=None):
        if cell is None:
            cell = Cell
        self.Cell = cell
        self.display = make_display(self)
        self.directions = directions
        self.filename = filename

        self.grid = None
        self.dictBackup = None
        self.agents = []
        self.age = 0

        self.height = None
        self.width = None
        self.get_file_size(filename)

        self.image = None
        self.mouseWin = None
        self.catWin = None
        self.reset()
        self.load(filename)

    def get_file_size(self, filename):
        if filename is None:
            raise Exception("world file not exist!")
        data = file(filename).readlines()
        if self.height is None:
            self.height = len(data)
        if self.width is None:
            self.width = max([len(x.rstrip()) for x in data])

    def reset(self):
        self.grid = [[self.make_cell(i, j) for i in xrange(self.width)] for j in xrange(self.height)]
        self.dictBackup = [[{} for _i in xrange(self.width)] for _j in xrange(self.height)]
        self.agents = []
        self.age = 0

    def make_cell(self, x, y):
        c = self.Cell()
        c.x = x
        c.y = y
        c.world = self
        c.agents = []
        return c

    def get_cell(self, x, y):
        return self.grid[y][x]

    def get_relative_cell(self, x, y):
        return self.grid[y % self.height][x % self.width]

    def load(self, f):
        if not hasattr(self.Cell, 'load'):
            return
        if isinstance(f, type('')):
            f = file(f)
        lines = f.readlines()
        lines = [x.rstrip() for x in lines]
        fh = len(lines)
        fw = max([len(x) for x in lines])

        if fh > self.height:
            fh = self.height
            start_y = 0
        else:
            start_y = (self.height - fh) / 2
        if fw > self.width:
            fw = self.width
            start_x = 0
        else:
            start_x = (self.width - fw) / 2

        self.reset()
        for j in xrange(fh):
            line = lines[j]
            for i in xrange(min(fw, len(line))):
                self.grid[start_y + j][start_x + i].load(line[i])

    def update(self, mouse_win=None, cat_win=None):
        if hasattr(self.Cell, 'update'):
            for a in self.agents:
                a.update()
            self.display.redraw()
        else:
            for a in self.agents:
                old_cell = a.cell
                a.update()
                if old_cell != a.cell:  # old cell won't disappear when new cell
                    self.display.redraw_cell(old_cell.x, old_cell.y)

                self.display.redraw_cell(a.cell.x, a.cell.y)

        if mouse_win:
            self.mouseWin = mouse_win
        if cat_win:
            self.catWin = cat_win
        self.display.update()
        self.age += 1

    def get_next_grid(self, x, y, dir):
        dx = 0
        dy = 0
        if self.directions == 8:
            dx, dy = [(0, -1), (1, -1), (
                1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)][dir]
        elif self.directions == 4:
            dx, dy = [(0, -1), (1, 0), (0, 1), (-1, 0)][dir]
        elif self.directions == 6:
            if y % 2 == 0:
                dx, dy = [(1, 0), (0, 1), (-1, 1), (-1, 0),
                          (-1, -1), (0, -1)][dir]
            else:
                dx, dy = [(1, 0), (1, 1), (0, 1), (-1, 0),
                          (0, -1), (1, -1)][dir]

        x2 = x + dx
        y2 = y + dy

        if x2 < 0:
            x2 += self.width
        if y2 < 0:
            y2 += self.height
        if x2 >= self.width:
            x2 -= self.width
        if y2 >= self.height:
            y2 -= self.height

        return x2, y2

    def add_agent(self, agent, x=None, y=None, cell=None, dir=None):
        self.agents.append(agent)
        if cell is not None:
            x = cell.x
            y = cell.y
        if x is None:
            x = random.randrange(self.width)
        if y is None:
            y = random.randrange(self.height)
        if dir is None:
            dir = random.randrange(self.directions)

        agent.cell = self.grid[y][x]
        agent.dir = dir
        agent.world = self


# GUI display
class TkinterDisplay:
    def __init__(self, size=cfg.grid_width):
        self.activated = False
        self.paused = False
        self.title = ''
        self.updateEvery = 1
        self.root = None
        self.speed = cfg.speed
        self.bg = None
        self.size = size
        self.imageLabel = None
        self.frameWidth = 0
        self.frameHeight = 0
        self.world = None
        self.bg = None
        self.image = None

    def activate(self):
        if self.root is None:
            self.root = Tkinter.Tk()
        for c in self.root.winfo_children():
            c.destroy()
        self.bg = None
        self.activated = True
        self.imageLabel = Tkinter.Label(self.root)
        self.imageLabel.pack(side=Tkinter.LEFT, fill=Tkinter.BOTH, expand=1)
        self.frameWidth, self.frameHeight = self.world.width * self.size, self.world.height * self.size
        self.root.geometry('%dx%d' % (self.world.width * self.size, self.world.height * self.size))
        self.root.update()
        self.redraw()
        self.root.bind('<Escape>', self.quit)

    def quit(self):
        self.root.destroy()

    def update(self):
        if not self.activated:
            return
        if self.world.age % self.updateEvery != 0 and not self.paused:
            return
        self.set_title(self.title)
        self.imageLabel.update()
        if self.speed > 0:
            time.sleep(float(1)/self.speed)

    def make_title(self, world):
        text = 'age: %d' % world.age
        extra = []
        if world.mouseWin:
            extra.append('mouseWin=%d' % world.mouseWin)
        if world.catWin:
            extra.append('catWin=%d' % world.catWin)
        if world.display.paused:
            extra.append('paused')
        if world.display.updateEvery != 1:
            extra.append('skip=%d' % world.display.updateEvery)
        if world.display.speed > 0:
            extra.append('speed=%dm/s' % world.display.speed)

        if len(extra) > 0:
            text += ' [%s]' % ', '.join(extra)
        return text

    def set_title(self, title):
        if not self.activated:
            return
        self.title = title
        title += ' %s' % self.make_title(self.world)
        if self.root.title() != title:
            self.root.title(title)

    def pause(self, event=None):
        self.paused = not self.paused
        while self.paused:
            self.update()

    def getBackground(self):
        if self.bg is None:
            r, g, b = self.imageLabel.winfo_rgb(self.root['background'])
            self.bg = '%c%c%c' % (r >> 8, g >> 8, b >> 8)
        return self.bg

    def redraw(self):
        if not self.activated:
            return

        iw = self.world.width * self.size
        ih = self.world.height * self.size

        hexgrid = self.world.directions == 6
        if hexgrid:
            iw += self.size / 2

        f = file('temp.ppm', 'wb')
        f.write('P6\n%d %d\n255\n' % (iw, ih))

        odd = False
        for row in self.world.grid:
            line = cStringIO.StringIO()
            if hexgrid and odd:
                line.write(self.getBackground() * (self.size / 2))
            for cell in row:
                if len(cell.agents) > 0:
                    c = self.get_data_color(cell.agents[-1])
                else:
                    c = self.get_data_color(cell)

                line.write(c * self.size)
            if hexgrid and not odd:
                line.write(self.getBackground() * (self.size / 2))
            odd = not odd

            f.write(line.getvalue() * self.size)
        f.close()

        self.image = Tkinter.PhotoImage(file='temp.ppm')
        self.imageLabel.config(image=self.image)

    imageCache = {}

    def redraw_cell(self, x, y):
        if not self.activated:
            return
        sx = x * self.size
        sy = y * self.size
        if y % 2 == 1 and self.world.directions == 6:
            sx += self.size / 2

        cell = self.world.grid[y][x]
        if len(cell.agents) > 0:
            c = self.get_text_color(cell.agents[-1])
        else:
            c = self.get_text_color(cell)

        sub = self.imageCache.get(c, None)
        if sub is None:
            sub = Tkinter.PhotoImage(width=1, height=1)
            sub.put(c, to=(0, 0))
            sub = sub.zoom(self.size)
            self.imageCache[c] = sub
        self.image.tk.call(self.image, 'copy', sub, '-from', 0, 0, self.size, self.size, '-to', sx, sy)

    def get_text_color(self, obj):
        c = getattr(obj, 'color', None)
        if c is None:
            c = getattr(obj, 'color', 'white')
        if callable(c):
            c = c()
        if isinstance(c, type(())):
            if isinstance(c[0], type(0.0)):
                c = (int(c[0] * 255), int(c[1] * 255), int(c[2] * 255))
            return '#%02x%02x%02x' % c
        return c

    dataCache = {}

    def get_data_color(self, obj):
        c = getattr(obj, 'color', None)
        if c is None:
            c = getattr(obj, 'color', 'white')
        if callable(c):
            c = c()
        if isinstance(c, type(())):
            if isinstance(c[0], type(0.0)):
                c = (int(c[0] * 255), int(c[1] * 255), int(c[2] * 255))
            return '%c%c%c' % c
        else:
            val = self.dataCache.get(c, None)
            if val is None:
                r, g, b = self.imageLabel.winfo_rgb(c)
                val = '%c%c%c' % (r >> 8, g >> 8, b >> 8)
                self.dataCache[c] = val
            return val


def make_display(world):
    d = TkinterDisplay()
    d.world = world
    return d