from moonpatrolgame import *
import os


def main():
    g2d.init_canvas((600, 500))

    players = g2d.confirm("2 Giocatori?")

    sprites = g2d.load_image("moon-patrol.png")
    image = g2d.load_image("moon-patrol-bg.png")
    if os.path.isfile("cfg.txt"):
        with open("cfg.txt", "r") as myfile:
            for i in myfile:
                if i.startswith("alien"):
                    i = i.strip()
                    num = int(i[-1])
            gui = MoonPatrolGui(players, sprites, image, num)
    else:
        gui = MoonPatrolGui(players, sprites, image)
        with open("cfg.txt", "w") as myfile:
            myfile.write("alien: 2")
    g2d.main_loop(gui.tick)


if __name__ == '__main__':
    main()
