from Actor import *
import g2d


class MoonPatrolGame:
    def __init__(self, A, B, num):
        self._terrenoval = B - 100
        self._W = A
        self._H = B
        self._bucacont = 0
        self._rocciacont = 0
        self._arena = Arena(A, B)

        self._cielo = Sfondo(self._arena, (0, 0, A, B), (0, 0, 512, 128), 0)
        self._montagne1 = Sfondo(self._arena, (0, (B - 75) // 3, A, B - (B - 75) // 3), (0, 258, 512, 128), 1)
        self._montagne2 = Sfondo(self._arena, (A, (B - 75) // 3, A, B - (B - 75) // 3), (0, 258, 512, 128), 1)
        self._città1 = Sfondo(self._arena, (0, self._terrenoval - 90, A, B - (self._terrenoval - 90)),
                              (0, 386, 512, 128), 2)
        self._città2 = Sfondo(self._arena, (A, self._terrenoval - 90, A, B - (self._terrenoval - 90)),
                              (0, 386, 512, 128), 2)
        self._terreno1 = Sfondo(self._arena, (0, self._terrenoval, A, 100), (0, 513, 512, 128), 3)
        self._terreno2 = Sfondo(self._arena, (A, self._terrenoval, A, 100), (0, 513, 512, 128), 3)
        self._rover = [Rover(self._arena, 100, B - 100)]
        self._alien = []
        for i in range(0, num):
            self._alien.append(Alien(self._arena))

    def win(self):
        actors = self._arena.actors()
        for i in self._alien:
            if i in actors:
                return False
        return True

    def defeat(self):
        actors = self._arena.actors()
        for i in self._rover:
            if i in actors:
                return False
        return True

    def getArena(self):
        return self._arena

    def getRover(self):
        return self._rover

    def createRover(self):
        self._rover.append(Rover(self._arena, 200, self._H - 100))

    def createBuca(self):
        if random.randint(0, 50) == 0 and \
                self._rocciacont >= 30 and \
                self._arena.stop() is False and self._bucacont >= 30:
            choice = bool(random.getrandbits(1))
            if choice:
                Roccia(self._arena, self._W, self._terrenoval - 16, choice)
            else:
                Roccia(self._arena, self._W, self._terrenoval - 36, choice)
            self._rocciacont = 0
        else:
            self._rocciacont += 1

    def createRoccia(self):
        if random.randint(0, 50) == 0 and \
                self._bucacont >= 30 and \
                self._arena.stop() is False and self._rocciacont >= 30:
            Buca(self._arena, self._W)
            self._bucacont = 0
        else:
            self._bucacont += 1

    def checkgame(self):
        if self.win():
            self._arena.stay_all()
            g2d.alert("Hai vinto!")
            g2d.close_canvas()
        elif self.defeat():
            self._arena.stay_all()
            g2d.alert("Hai perso!")
            g2d.close_canvas()

    def drawimages(self, image, sprites):
        for a in self._arena.actors():
            if a.symbol() != (0, 0, 0, 0):
                if isinstance(a,
                              Sfondo):  # il discriminante tra gli sfondi e tutto il resto è l'immagine da cui prendere le porzioni symbol
                    g2d.draw_image_clip(image, a.symbol(), a.position())
                else:
                    g2d.draw_image_clip(sprites, a.symbol(), a.position())
            else:
                g2d.fill_rect(a.position())


class MoonPatrolGui:
    def __init__(self, players, sprites, image, num=2):
        W = 600
        H = 500
        self._game = MoonPatrolGame(W, H, num)
        self._players = players
        if self._players:
            self._game.createRover()
        self._sprites = sprites
        self._image = image

    def tick(self):
        g2d.clear_canvas()
        self._game.getArena().move_all()
        self.tastiera()  # gestisco la tastiera
        self._game.createBuca()  # decido se creare una buca
        self._game.createRoccia()  # decido se creare una roccia
        self._game.drawimages(self._image, self._sprites)
        self._game.checkgame()

    def tastiera(self):
        if self._game.getArena().stop() is False:
            if g2d.key_pressed("ArrowUp"):
                self._game.getRover()[0].go_up()
            elif g2d.key_pressed("ArrowDown"):
                self._game.getRover()[0].go_down()
            elif g2d.key_pressed("Spacebar"):
                x, y, w, h = self._game.getRover()[0].position()
                Proiettile(self._game.getArena(), x + (w / 4), y, 0, -5)
                Proiettile(self._game.getArena(), x + w, y + (h / 2), 5, 0)
            elif g2d.key_pressed("ArrowRight"):
                self._game.getRover()[0].go_right()
            elif g2d.key_pressed("ArrowLeft"):
                self._game.getRover()[0].go_left()
            elif (
                    g2d.key_released("ArrowUp") or g2d.key_released("ArrowRight") or g2d.key_released("ArrowLeft")):
                self._game.getRover()[0].stay()
            if self._players:  # secondo giocatore
                if g2d.key_pressed("w"):
                    self._game.getRover()[1].go_up()
                elif g2d.key_pressed("s"):
                    self._game.getRover()[1].go_down()
                elif g2d.key_pressed("LeftButton"):
                    x, y, w, h = self._game.getRover()[1].position()
                    Proiettile(self._game.getArena(), x + (w / 4), y, 0, -5)
                    Proiettile(self._game.getArena(), x + w, y + (h / 2), 5, 0)
                elif g2d.key_pressed("d"):
                    self._game.getRover()[1].go_right()
                elif g2d.key_pressed("a"):
                    self._game.getRover()[1].go_left()
                elif (
                        g2d.key_released("w") or g2d.key_released("d") or g2d.key_released("a")):
                    self._game.getRover()[1].stay()
