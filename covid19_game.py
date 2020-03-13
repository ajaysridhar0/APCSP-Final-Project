import pygame
import time
import random
import math

# dimensions
display_width = 800
display_height = 800
person_width = 15
person_height = 20

# color definitions
black = (0, 0, 0)
white = (255, 255, 255)
red = (200, 0, 0)
green = (0, 200, 0)
bright_red = (255, 0, 0)
bright_green = (0, 255, 0)

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


class Patient:
    def __init__(self, pos, infected):
        self.pos = pos
        self.infected = infected

    def is_hit(self, axis, n):
        if axis == 'x':
            if self.pos.x <= n <= self.pos.x + person_width:
                return True
        elif axis == 'y':
            if self.pos.y <= n <= self.pos.y + person_height:
                return True
        return False

    def out_of_bounds(self):
        if self.is_hit('x', 0) or self.is_hit('x', display_width) or self.is_hit('y', 0) or self.is_hit('y', display_height):
            return True
        return False

    def is_infected(self):
        for infected_patient in infected_people:
            if (self.is_hit('x', infected_patient.pos.x) or
                    self.is_hit('x', infected_patient.pos.x + person_width)):
                if (self.is_hit('y', infected_patient.pos.y) or
                        self.is_hit('y', infected_patient.pos.y + person_height)):
                    self.infected = True
                    people.remove(self)
                    infected_people.append(self)
                    return True
        return False

    def draw(self, infected_color=bright_red, healthy_color=bright_green):
        if self.infected:
            color = infected_color
        else:
            color = healthy_color
        pygame.draw.rect(game_display, color,
                         [self.pos.x, self.pos.y, person_width, person_height])


# TODO: NPC and Player inherits from the player superclass
class Npc(Patient):
    def __init__(self, infected):
        pos = Vector(
            random.randrange(0, display_width - person_width),
            random.randrange(0, display_height - person_height)
        )
        Patient.__init__(self, pos, infected)
        self.vel = Vector(random.randrange(-200, 200),
                          random.randrange(-200, 200))
        self.vel.normalize()
        scal = random.randrange(5, 20) / 10
        self.vel.x *= scal
        self.vel.y *= scal

    def bounce(self):
        if self.is_hit('x', 0) or self.is_hit('x', 800):
            self.vel.x = -self.vel.x
        if self.is_hit('y', 0) or self.is_hit('y', 800):
            self.vel.y = -self.vel.y

    def move(self):
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y

    def animate(self):
        if not self.infected:
            self.is_infected()
        self.bounce()
        self.move()
        self.draw()


# functions
def quit_game():
    pygame.quit()
    quit()


def game_loop():
    for i in range(0, 200):
        people.append(Npc(False))
    # patient 0
    infected_people.append(Npc(True))

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
