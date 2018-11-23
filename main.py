import os
import time
from tkinter import Tk, LabelFrame, Spinbox, Button, Canvas, Label, filedialog
from tile import GameMap

main = Tk()

MAP_PATH = '.'
MAP_NAME = 'map'

map_file = os.path.abspath(os.path.join(MAP_PATH, MAP_NAME))
main.filename = filedialog.askopenfilename(
    initialdir=".",
    title="Select file",
    filetypes=(("map files", "*.map"), ("all files", "*.*"))
)
map_file = main.filename
with open(map_file, "r") as fin:
    file = fin.readlines()

game = GameMap(
    [[tile for tile in line.strip()]
        for line in file],
    tile_width=100,
    player_pos=(0, 2))


WINDOW_H = 125 + game.get_pixel_height()
WINDOW_W = game.get_pixel_width()
main.geometry("{}x{}".format(WINDOW_W, WINDOW_H))


menu = LabelFrame(main, text="Menu")
menu.pack()

iter_label = Label(menu, text="Number of iteration:")
iter_label.grid(row=0, column=0)
iter_spinbox = Spinbox(menu, from_=1, to=1000)
iter_spinbox.grid(row=0, column=1)
speed_label = Label(menu, text="Speed :")
speed_label.grid(row=1, column=0)
speed_spinbox = Spinbox(menu, from_=0.1, to=1000)
speed_spinbox.grid(row=1, column=1)
speed_spinbox.delete(0)
speed_spinbox.insert(0, '10')
exploration_label = Label(menu, text="Exploration Rate :")
exploration_label.grid(row=2, column=0)
exploration_spinbox = Spinbox(menu, from_=0.0, to=1.0, increment=0.1)
exploration_spinbox.grid(row=2, column=1)
button = Button(
    menu,
    text='Start',
    command=lambda: game.run_on_canvas(
        canvas,
        speed=float(speed_spinbox.get()),
        iteration_nb=int(iter_spinbox.get()),
        exploration_rate=float(exploration_spinbox.get()),
    ))
button.grid(row=3, columnspan=2)


canvas = Canvas(
    main,
    width=game.get_pixel_width(),
    height=game.get_pixel_height()
)
canvas.pack()
game.print_to_canvas(canvas)

main.mainloop()
