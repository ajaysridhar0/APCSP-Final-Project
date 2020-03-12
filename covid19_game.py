import pygame
import time
import random
import math

# dimensions
display_width = 800
display_height = 800

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
        self.w = 10
        self.h = 20

    def is_hit(self, axis, n):
        if axis == 'x':
            if self.pos.x <= n <= self.pos.x + self.w:
                return True
        elif axis == 'y':
            if self.pos.y <= n <= self.pos.y + self.h:
                return True
        return False

    def out_of_bounds(self):
        if self.is_hit('x', 0) or self.is_hit('x', 800) or self.is_hit('y', 0) or self.is_hit('x', 800):
            return True
        return False

    def draw(self, infected_color=bright_red, healthy_color=bright_green):
        if self.infected:
            color = infected_color
        else:
            color = healthy_color
        pygame.draw.rect(game_display, color,
                         [self.pos.x, self.pos.y, self.w, self.h])


# TODO: NPC and Player inherits from the player superclass
class Npc(Patient):
    def __init__(self, pos, infected):
        Patient.__init__(self, pos, infected)
        self.gen_vel()

    def gen_vel(self):
        self.vel = Vector(random.randrange(0, 200),
                          random.randrange(0, 200))
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
        self.bounce()
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y


# functions
def quit_game():
    pygame.quit()
    quit()


def game_loop():
    test_npc = Npc(Vector(display_width/2, display_height/2), False)
    game_exit = False
    while not game_exit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
        game_display.fill(black)
        test_npc.move()
        test_npc.draw()
        pygame.display.flip()
        clock.tick(120)


game_loop()
