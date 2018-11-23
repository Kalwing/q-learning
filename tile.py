import time
import random
from tkinter import CENTER


class Tile:
    TYPES = {
        'X': ('black', 0),
        '0': ('#FFFFFF', 0),
        '1': ('green', 1),
        '2': ('red', -1),
    }
    DIRECTION = {
        'TOP': 0,
        'RIGHT': 1,
        'BOTTOM': 2,
        'LEFT': 3
    }

    def __init__(self, type='X', tile_width=20):
        assert tile_width > 3
        self.tile_type = type
        self.tile_width = tile_width
        self.base_color = self.TYPES[type][0]
        self.colors = [self.TYPES[type][0] for i in range(4)]
        self.reward = self.TYPES[type][1]
        self.q_values = [0.0 for i in range(4)]
        self.v = 0.0

    def is_accessible(self):
        return self.tile_type != 'X'

    def is_path(self):
        return self.tile_type == '0'

    def is_end(self):
        return self.tile_type in ['1', '2']

    def get_base_color(self):
        return self.base_color

    def get_side_color(self, direction):
        assert direction in self.DIRECTION.keys()
        return self.colors[self.DIRECTION[direction]]

    def get_q_values(self, direction):
        assert direction in self.DIRECTION.keys()
        return self.q_values[self.DIRECTION[direction]]

    def set_q_values(self, direction, value):
        self.q_values[self.DIRECTION[direction]] = value
        red_v = int(self.base_color[1:-4], 16)
        gre_v = int(self.base_color[-4:-2], 16)
        blu_v = int(self.base_color[-2:], 16)
        if value >= 0:
            GOAL = [0x00, 0xFF, 0x00]
        else:
            GOAL = [0xFF, 0x00, 0x00]
            value = -value
        red_v = max(0x00, min(0xFF, int(((1-value)*red_v + value*GOAL[0]))))
        red_v = "{:#04x}".format(red_v)[-2:]
        gre_v = max(0x00, min(0xFF, int(((1-value)*gre_v + value*GOAL[1]))))
        gre_v = "{:#04x}".format(gre_v)[-2:]
        blu_v = max(0x00, min(0xFF, int(((1-value)*blu_v + value*GOAL[2]))))
        blu_v = "{:#04x}".format(blu_v)[-2:]
        color = "#{:2}{:2}{:2}".format(red_v, gre_v, blu_v)
        self.colors[self.DIRECTION[direction]] = color

class GameMap:
    MOVES = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    DIRECTION = ['TOP', 'RIGHT', 'BOTTOM', 'LEFT']

    def __init__(self, char_array, tile_width=20, player_pos=(0, 0),
                 player_width=30):
        assert player_pos[0] % 1 == 0 and player_pos[1] % 1 == 0
        self.tile_width = tile_width
        self.tile_map = []
        for line_nb, line in enumerate(char_array):
            self.tile_map.append([])
            for tile_nb, char in enumerate(line):
                tile = Tile(type=char, tile_width=tile_width)
                self.tile_map[line_nb].append(tile)
        self.width = max([len(line) for line in self.tile_map])
        self.height = len(self.tile_map)
        self.player_pos = player_pos
        self.player_width = player_width
        self.use_q = True
        self.gamma = 0.9
        self.learning_rate = 0.1
        self.exploration_rate = 0.5

    def get_tiles(self):
        return self.tile_map

    def print_to_canvas(self, canvas, iteration=None):
        half = self.tile_width / 2
        for y, lines in enumerate(self.tile_map):
            for x, tile in enumerate(lines):
                x0 = x * self.tile_width
                x1 = x0 + self.tile_width
                y0 = y * self.tile_width
                y1 = y0 + self.tile_width
                canvas.create_rectangle(
                    x0, y0, x1, y1,
                    fill=tile.get_base_color(),
                )
                if (tile.is_path() and self.use_q):
                    # TOP triangle
                    canvas.create_polygon(
                        x0, y0,
                        x1, y0,
                        x0 + half, y0 + half,
                        fill=tile.get_side_color('TOP'),
                        outline='black'
                    )
                    canvas.create_text(
                        x0 + half,
                        y0 + half/3,
                        justify=CENTER,
                        text="{:4.2f}".format(tile.get_q_values('TOP'))
                    )
                    # RIGHT triangle
                    canvas.create_polygon(
                        x1, y0,
                        x1, y1,
                        x0 + half, y0 + half,
                        fill=tile.get_side_color('RIGHT'),
                        outline='black'
                    )
                    canvas.create_text(
                        x0 + 5*half/3,
                        y0 + half,
                        justify=CENTER,
                        text="{:4.2f}".format(tile.get_q_values('RIGHT'))
                    )
                    # BOTTOM triangle
                    canvas.create_polygon(
                        x0, y1,
                        x1, y1,
                        x0 + half, y0 + half,
                        fill=tile.get_side_color('BOTTOM'),
                        outline='black'
                    )
                    canvas.create_text(
                        x0 + half,
                        y0 + 5*half/3,
                        justify=CENTER,
                        text="{:4.2f}".format(tile.get_q_values('BOTTOM'))
                    )
                    # LEFT triangle
                    canvas.create_polygon(
                        x0, y0,
                        x0, y1,
                        x0 + half, y0 + half,
                        fill=tile.get_side_color('LEFT'),
                        outline='black'
                    )
                    canvas.create_text(
                        x0 + half/3,
                        y0 + half,
                        justify=CENTER,
                        text="{:4.2f}".format(tile.get_q_values('LEFT'))
                    )
                if (not self.use_q):
                    canvas.create_text(
                        x0 + half,
                        y0 + half,
                        justify=CENTER,
                        text="{:4.2f}".format(tile.v)
                    )
        # Player
        canvas.create_oval(
            (self.player_pos[0] + 0.5)*self.tile_width - self.player_width/2,
            (self.player_pos[1] + 0.5)*self.tile_width - self.player_width/2,
            (self.player_pos[0] + 0.5)*self.tile_width + self.player_width/2,
            (self.player_pos[1] + 0.5)*self.tile_width + self.player_width/2,
            fill='blue'
        )
        if iteration:
            canvas.create_text(1, 1, text="{}".format(iteration), anchor='nw')
        canvas.update()

    def get_pixel_width(self):
        """
        Return the width of the map in pixel
        """
        len_list = [len(line) for line in self.get_tiles()]
        return max(len_list) * self.tile_width

    def get_pixel_height(self):
        """
        Return the height of the map in pixel.
        """
        return len(self.get_tiles()) * self.tile_width

    def set_player_at(self, x, y):
        """
        Move player on the tile at position (x,y). Those number must be
        integers, and must correspond to a tile in get_tiles(). The tile must
        be accessible.
        """
        assert x % 1 == 0 and y % 1 == 0, "Coordinates are not Integer"
        # We make sure that the tile exist and is accessible before placing
        # the player
        assert x >= 0 and y >= 0, "Coordinates are not positives"
        tile = self.get_tiles()[y][x]
        assert tile.is_accessible(), "Player can't go there."
        self.player_pos = (x, y)

    def move_player(self, x_offset, y_offset):
        """
        Move player by x_offset tiles and y_offset tiles. Those number must be
        integers, and must correspond to a tile in get_tiles().
        """
        x, y = self.player_pos
        x += x_offset
        y += y_offset
        try:
            self.set_player_at(x, y)
        except Exception:
            pass

    def explore_action(self, epsilon):
        if random.uniform(0, 1) < epsilon:
            action = random.choice(range(4))
        else:
            tile = self.get_tiles()[self.player_pos[1]][self.player_pos[0]]
            action = tile.q_values.index(max(tile.q_values))
        return action

    def run_on_canvas(self, canvas, speed=1, iteration_nb=1,
                      exploration_rate=0.3):
        """
        Run a game on canvas, with a delay between frame of 1/speed seconds.
        """
        assert speed > 0.1
        assert iteration_nb > 0
        for i in range(1, iteration_nb + 1):
            self.set_player_at(0, 2)
            self.print_to_canvas(canvas, i)
            time.sleep(1/speed)
            tile = self.get_current_tile()
            while not tile.is_end():
                a = self.explore_action(exploration_rate)  # Best action
                self.move_player(*self.MOVES[a])
                old_tile = tile
                tile = self.get_current_tile()
                a1 = self.explore_action(0)  # Best action for the next state
                q = old_tile.q_values[a]
                temporal_diff = (tile.reward +
                                 self.gamma*tile.q_values[a1] - q)
                dir = self.DIRECTION[a]
                old_tile.set_q_values(dir, q+self.learning_rate*temporal_diff)
                self.print_to_canvas(canvas, i)
                time.sleep(1/speed)

    def get_current_tile(self):
        return self.get_tiles()[self.player_pos[1]][self.player_pos[0]]
