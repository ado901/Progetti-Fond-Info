import random


class Actor():
    '''Interfaccia che deve essere implementata dai vari tipi 
       di personaggi del gioco 
    '''

    def move(self):
        '''Chiamato da Arena, ad ogni turno del personaggio
        '''
        raise NotImplementedError('Abstract method')

    def collide(self, other: 'Actor'):
        '''Chiamato da Arena, quando il personaggio (self)
           entra in collisione con un altro personaggio (other)
        '''
        raise NotImplementedError('Abstract method')

    def position(self) -> (int, int, int, int):
        '''Restituisce il rettangolo che contiene il personaggio
           tupla di 4 valori interi (left, top, width, height)
        '''
        raise NotImplementedError('Abstract method')

    def symbol(self) -> (int, int, int, int):
        '''Restituisce la posizione (x, y, w, h) dello sprite corrente, 
           se l'immagine è contenuta in una immagine di grandi dimensioni
           altrimenti restituisce la tupla (0, 0, 0, 0)
        '''
        raise NotImplementedError('Abstract method')


class Arena():
    '''Generica 2D game, cui vengono assegnate le dimensioni di gioco
       e che contiene la lista dei personaggi del gioco
    '''

    def __init__(self, width: int, height: int):
        '''Crea una arena con specifica altezza e larghezza
           e lista di personaggi inizialmente vuota
        '''
        self._w, self._h = width, height
        self._actors = []
        self._stop = 0

    def add(self, a: Actor):
        '''Aggiunge un personaggio al gioco
           I pesonaggi sono gestiti seguendo il loro ordine di inserimento
        '''
        if a not in self._actors:
            self._actors.append(a)

    def remove(self, a: Actor):
        '''Elimina un personaggio dal gioco
        '''
        if a in self._actors:
            self._actors.remove(a)

    def move_all(self):
        '''chiama il metodo move di ogni personaggio
           dopo aver effettuato il movimento verica
           se è avvenuta un collisione tra il personaggio
           e un altro personaggio e in tal caso chiama
           il metodo collide di entrambi
        '''
        actors = list(reversed(self._actors))
        for a in actors:
            previous_pos = a.position()
            a.move()
            if a.position() != previous_pos:  # inutile per personaggi statici
                for other in actors:
                    # reversed order, so actors drawn on top of others
                    # (towards the end of the cycle) are checked first
                    if other is not a and self.check_collision(a, other):
                        a.collide(other)
                        other.collide(a)

    def stay_all(self):
        self._stop = 1
        for a in list(reversed(self._actors)):
            a.stay()

    def stop(self):
        return bool(self._stop)

    def check_collision(self, a1: Actor, a2: Actor) -> bool:
        '''Verifica se i due personaggi (parametri) sono in collisione 
           (bounding-box collision detection)
        '''
        x1, y1, w1, h1 = a1.position()
        x2, y2, w2, h2 = a2.position()
        return (y2 < y1 + h1 and y1 < y2 + h2
                and x2 < x1 + w1 and x1 < x2 + w2
                and a1 in self._actors and a2 in self._actors)

    def actors(self) -> list:
        '''Restituisce una copia della lista dei personaggi
        '''
        return list(self._actors)

    def size(self) -> (int, int):
        '''Restituisce le dimensioni dell'arena di gioco (width, height)
        '''
        return self._w, self._h


class Explosion(Actor):
    def __init__(self, arena, x, y):
        self._x, self._y = x, y - 5
        self._w1, self._h1 = 20, 20
        self._arena = arena
        self._dx = -3
        self._arena.add(self)
        self._time = 0

    def move(self):
        self._x += self._dx
        if self._time >= 21:
            self._arena.remove(self)

    def stay(self):
        self._dx = 0

    def collide(self, other):
        pass

    def position(self):
        return self._x, self._y, self._w1, self._h1

    def symbol(self):
        if 0 <= self._time <= 7:
            self._time += 1
            return 224, 141, 6, 8

        if 7 < self._time <= 14:
            self._time += 1
            return 238, 139, 9, 11

        if 14 < self._time <= 21:
            self._time += 1
            return 252, 137, 265 - 152, 152 - 137


class Proiettile(Actor):
    def __init__(self, arena, x: int, y, dx, dy):
        self._w, self._h = 4, 4
        self._x, self._y = x, y
        self._dy = dy
        self._dx = dx
        self._arenaw, self._arenah = arena.size()
        self._arena = arena
        arena.add(self)

    def move(self):
        arenaw, arenah = self._arena.size()
        self._y += self._dy
        self._x += self._dx
        if self._y < 0:
            self._arena.remove(self)
        if self._x > arenaw:
            self._arena.remove(self)

    def position(self):
        return self._x, self._y, self._w, self._h

    def symbol(self):
        return 0, 0, 0, 0

    def collide(self, other):
        if self._y > self._arenah - 100:
            x, y, w, h = other.position()
            if random.randint(0, 5) == 0:
                Buca(self._arena, x)
            self._arena.remove(self)
        if isinstance(other, Rover):
            self._arena.remove(self)
            Explosion(self._arena, self._x, self._y)

    def stay(self):
        self._dx = 0
        self._dy = 0


class Roccia(Actor):
    def __init__(self, arena, x, y, choice):
        self._x, self._y = x, y
        self._w1, self._h1 = 20, 20
        self._w2, self._h2 = 30, 40
        self._speed = 3
        self._bool = choice
        self._dx, self._dy = -self._speed, 0
        self._arena = arena
        self._arena.add(self)
        self._g = 0.4
        self._life = 1

    def move(self):

        self._x += self._dx
        if self._bool is True:
            if self._x < 0 - self._w1:
                self._arena.remove(self)
        else:
            if self._x < 0 - self._w2:
                self._arena.remove(self)

    def stay(self):
        self._dx = 0

    def collide(self, other):
        if isinstance(other, Rover):
            other.explode()
        if isinstance(other, Proiettile):
            x, y, w, h = other.position()
            Explosion(self._arena, x, y)
            self._arena.remove(other)
            if self._bool:
                self._arena.remove(self)
                return
            else:
                if self._life == 0:
                    self._arena.remove(self)
                    return
                self._life -= 1

    def position(self):
        if self._bool is True:
            return self._x, self._y, self._w1, self._h1
        else:
            return self._x, self._y, self._w2, self._h2

    def symbol(self):
        if self._bool is True:
            return 63, 207, 72 - 63, 215 - 207
        else:
            return 79, 202, 94 - 79, 215 - 202


class Rover(Actor):
    ''' Tartaruga: movimento guidato dai tasti freccia
        non supera i bordi dell'arena
    '''

    def __init__(self, arena, x, y):
        self._x, self._y = x, y
        self._w, self._h = 31, 23
        self._speed = 10
        self._dx, self._dy = 0, 0
        self._arena = arena
        self._arena.add(self)
        self._arena_w, self._arena_h = self._arena.size()
        self._g = 0.4
        self._explode = False
        self._explodecount = 0
        self._exploding = 0

    def move(self):

        self._dy += self._g
        self._y += self._dy
        self._x += self._dx
        if self._y < 0:
            self._y = 0
            self._dy = self._speed
        elif self._y > (self._arena_h - self._h) - 95:
            self._y = (self._arena_h - self._h) - 95
            self._dy = 0

        if self._x < 0:
            self._x = 0
        elif self._x > self._arena_w - self._w:
            self._x = self._arena_w - self._w
        if self._explodecount >= 45:
            self._arena.remove(self)

    def go_left(self):
        if self._x > 50:
            self._dx, self._dy = -5, 0
        pass

    def go_right(self):
        if self._x < 300:
            self._dx, self._dy = 5, 0
        pass

    def go_up(self):
        if self._dy == 0:
            self._dx, self._dy = 0, -self._speed

    def go_down(self):
        self._dx, self._dy = 0, +self._speed

    def stay(self):
        if self._dy <= 0:
            self._dy = 0
        self._dx = 0

    def collide(self, other):
        if isinstance(other, Buca):
            x, y, w, h = other.position()
            self._arena.remove(self)
            self._arena.add(self)

            self._x = x + (w / 2) - 15
            self._y = y + (h / 2) - 5
        if isinstance(other, Roccia):
            self._arena.remove(self)
            self._arena.add(self)
        if isinstance(other, Proiettile):
            self.explode()

    def position(self):
        return self._x, self._y, self._w, self._h

    def symbol(self):
        ''' sprite coordinate 0,0 20,20 '''
        if self._explode is False:
            if self._dy > 0:
                return 79, 103, self._w, self._h
            if self._dy < 0:
                return 46, 102, self._w, self._h
            elif self._y == self._arena_h - self._h - 95 or self._dy == 0:
                return 212, 158, self._w, self._h
        else:
            if 0 <= self._explodecount <= 15:
                self._explodecount += 1
                return 113, 100, 157 - 113, 131 - 100
            elif 15 < self._explodecount <= 30:
                self._explodecount += 1
                return 166, 100, 207 - 166, 131 - 100
            elif 30 < self._explodecount <= 45:
                self._explodecount += 1
                return 213, 102, 255 - 213, 131 - 102

    def explode(self):
        self._dx=-3
        self._explode = True


class Sfondo(Actor):
    def __init__(self, arena, pos: (int, int, int, int), img: (int, int, int, int), speed):
        self._x, self._y, self._w, self._h = pos
        self._xinit = self._x
        self._speed = speed
        self._imagex, self._imagey, self._imagew, self._imageh = img
        self._dx = -speed
        self._arena = arena
        self._arena.add(self)

    def move(self):
        self._x += self._dx
        if self._xinit - self._x >= self._w:
            self._x = self._xinit

    def stay(self):
        self._dx = 0

    def collide(self, other):
        pass

    def position(self):
        return self._x, self._y, self._w, self._h

    def symbol(self):
        ''' sprite coordinate 0,0 20,20 '''
        return self._imagex, self._imagey, self._imagew, self._imageh


class Buca(Actor):
    def __init__(self, arena, x):

        self._w1, self._h1 = 20, 20
        self._w2, self._h2 = 30, 40
        self._speed = 3
        self._bool = bool(random.getrandbits(1))
        self._dx, self._dy = -self._speed, 0
        self._arena = arena
        self._arena.add(self)
        self._arena_w, self._arena_h = arena.size()
        self._x, self._y = x, self._arena_h - 100
        self._g = 0.4

    def move(self):

        self._x += self._dx
        if self._bool is True:
            if self._x < 0 - self._w1:
                self._arena.remove(self)
        else:
            if self._x < 0 - self._w2:
                self._arena.remove(self)

    def stay(self):
        self._dx = 0

    def collide(self, other):
        if isinstance(other, Rover):
            other.explode()

    def position(self):
        if self._bool is True:
            return self._x, self._y, self._w1, self._h1
        else:
            return self._x, self._y, self._w2, self._h2

    def symbol(self):
        if self._bool is True:
            return 136, 139, 15, 13
        else:
            return 158, 166, 183 - 158, 195 - 166


class Alien(Actor):
    def __init__(self, arena):
        self._arena = arena
        arena.add(self)
        self._x = random.choice([40, 200, 400])
        self._y = 60
        self._speed = 5
        self._dx = self._speed
        self._w = 20
        self._h = 20
        self._arenaw, self._arenah = arena.size()

    def move(self):
        self._x += self._dx
        if random.randint(0, 10) == 0:
            self._dx = random.choice([-self._speed, 0, self._speed])

        if random.randint(0, 100) == 0 and not self._arena.stop():
            Proiettile(self._arena, self._x + 1 / 2 * self._w, self._y + self._h, 0, 5)
        if self._x > self._arenaw - self._w:
            self._x = self._arenaw - self._w
        if self._x < 0 + self._w:
            self._x = 0 + self._w

    def stay(self):
        self._speed = 0

    def collide(self, other: 'Actor'):
        if isinstance(other, Proiettile):
            x, y, w, h = other.position()
            Explosion(self._arena, x, y)
            self._arena.remove(self)

    def position(self) -> (int, int, int, int):
        return self._x, self._y, self._w, self._h

    def symbol(self) -> (int, int, int, int):
        return 121, 228, 139 - 121, 238 - 228
