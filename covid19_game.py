import pygame
import time
import random
import math

# dimensions
display_width = 800
display_height = 600

# color definintions
black = (0, 0, 0)
white = (255, 255, 255)
red = (200, 0, 0)
green = (0, 200, 0)
bright_red = (255, 0, 0)
bright_green = (0, 255, 0)

# global variables
game_display = pygame.display.set_mode((display_width, display_width))
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
        self.theta = math.atan(x / y)

    def normalize(self):
        self.x /= self.v
        self.y /= self.v


class Patient:
    def __init__(self, pos, infected):
        self.pos = pos
        self.infected = infected


# TODO: NPC and Player inherits from the player superclass
class Npc(Patient):
    def __init__(self, pos, infected):
        Patient.__init__(self, pos, infected)
        self.vel = Vector(random.randrange(0, 20),
                          random.randrange(0, 20))
        self.vel.normalize()

    def gen_vel(self):
        self.vel = Vector(random.randrange(0, 20),
                          random.randrange(0, 20))
        self.vel.normalize()

    def move(self):
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y

    def draw(self):
        if self.infected:
            color = bright_red
        else:
            color = bright_green
        pygame.draw.rect(game_display, color,
                         [self.pos.x, self.pos.y, 10, 20])


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
