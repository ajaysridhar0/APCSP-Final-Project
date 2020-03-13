import pygame
import time
import random
import math

# dimensions
display_width = 1200
display_height = 1200
'''person_width = 15
person_height = 20'''
population = 200

# color definitions
black = (0, 0, 0)
white = (255, 255, 255)
red = (200, 0, 0)
green = (0, 200, 0)
bright_red = (255, 0, 0)
bright_green = (0, 255, 0)
teal = (0, 255, 255)
yellow = (255, 255, 0)

# global variables
game_display = pygame.display.set_mode((display_width, display_height))
clock = pygame.time.Clock()
game_exit = False
people = []
infected_people = []

# setup
pygame.init()
pygame.display.set_caption("Project COVID19")


# classes
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.v = math.sqrt(pow(x, 2) + pow(y, 2))

    def normalize(self):
        self.x /= self.v
        self.y /= self.v

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)


class Patient:
    def __init__(self, pos, radius, infected):
        self.pos = pos
        self.radius = radius
        self.infected = infected

    def is_hit(self, pos, radius):
        '''if axis == 'x':
            if self.pos.x <= n <= self.pos.x + person_width:
                return True
        elif axis == 'y':
            if self.pos.y <= n <= self.pos.y + person_height:
                return True'''
        if (self.pos - pos).v < self.radius + radius:
            return True
        return False

    def out_of_bounds(self):
        '''if self.is_hit('x', 0) or self.is_hit('x', display_width) or self.is_hit('y', 0) or self.is_hit('y', display_height):'''
        if self.pos.x < self.radius or self.pos.x > display_width - self.radius or self.pos.y < self.radius or self.pos.y > display_height - self.radius:
            return True
        return False

    def is_infected(self):
        for infected_patient in infected_people:
            if self.is_hit(infected_patient.pos, infected_patient.radius):
                self.infected = True
                people.remove(self)
                infected_people.append(self)
                return True
        return False

    def move(self, dx, dy):
        self.pos.x += dx
        self.pos.y += dy

    def draw(self, infected_color=red, healthy_color=green):
        if self.infected:
            color = infected_color
        else:
            color = healthy_color
        pygame.draw.circle(game_display, color,
                           (int(self.pos.x), int(self.pos.y)), self.radius)


# TODO: NPC and Player inherits from the player superclass
class Npc(Patient):
    def __init__(self, radius, infected):

        Patient.__init__(self, Vector(0, 0), radius, infected)
        self.pos = Vector(
            random.randrange(self.radius, display_width - self.radius),
            random.randrange(self.radius, display_height - self.radius)
        )
        self.vel = Vector(random.randrange(-200, 200),
                          random.randrange(-200, 200))
        self.vel.normalize()
        scal = random.randrange(5, 20) / 10
        self.vel.x *= scal
        self.vel.y *= scal

    def bounce(self):
        if self.pos.x < self.radius or self.pos.x > display_width - self.radius:
            self.vel.x = -self.vel.x
        if self.pos.y < self.radius or self.pos.y > display_height - self.radius:
            self.vel.y = -self.vel.y

    def animate(self):
        if not self.infected:
            self.is_infected()
        self.bounce()
        self.move(self.vel.x, self.vel.y)
        self.draw()


'''class Player(Patient):
    def __init__(self, pos, controls, infected):
        Patient.__init__(self, pos, infected)
        self.controls = controls

    def animate(self):
        key_pressed = pygame.key.get_pressed()
        if not self.infected:
            self.is_infected()
        if key_pressed[self.controls[0]] and self.pos.x > 0:
            self.move(-2, 0)
        if key_pressed[self.controls[1]] and self.pos.x < display_width - person_width:
            self.move(2, 0)
        if key_pressed[self.controls[2]] and self.pos.y > 0:
            self.move(0, -2)
        if key_pressed[self.controls[3]] and self.pos.y < display_height - person_height:
            self.move(0, 2)
        self.draw(infected_color=yellow, healthy_color=teal)
'''

# functions


def quit_game():
    pygame.quit()
    quit()


def game_loop():
    # time.sleep(3)
    for i in range(0, population):
        people.append(Npc(10, False))

    '''player = Player(Vector(display_width/2 - person_width/2, display_height/2 - person_height/2), [pygame.K_LEFT, pygame.K_RIGHT,
                                                                                                   pygame.K_UP, pygame.K_DOWN], False)
    people.append(player)'''
    infected_people.append(Npc(10, True))

    game_exit = False
    while not game_exit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

        game_display.fill(black)
        for npc in people:
            npc.animate()
        for npc in infected_people:
            npc.animate()

        pygame.display.flip()
        clock.tick(120)


game_loop()
