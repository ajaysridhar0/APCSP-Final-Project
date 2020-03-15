import pygame
import time
import random
import math

# dimensions
display_width = 1200
display_height = 1200
population = 100

# color definitions
black = (0, 0, 0)
white = (255, 255, 255)
dark_red = (145, 0, 0)
dark_green = (0, 145, 0)
red = (200, 0, 0)
green = (0, 200, 0)
bright_red = (255, 0, 0)
bright_green = (0, 255, 0)
teal = (0, 255, 255)
yellow = (255, 255, 0)

# global variables
game_display = pygame.display.set_mode((display_width, display_height))
clock = pygame.time.Clock()
virus_level = 0
game_exit = False
people = []
infected_people = []
immune_people = []

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


class Virus:
    def __init__(self, level):
        self.level = level
        self.start_time = time.time()
        self.duration = random.randrange(5, 6 + level)
        self.radius = random.randrange(15, 16 + level)
        self.color = (random.randrange(0, 255), 0,
                      random.randrange(0, 255))
        # self.death_rate = death_rate

    def get_time(self):
        return time.time() - self.start_time

    def infect_radius(self, healthy_radius):
        radius = healthy_radius
        if(self.get_time() < self.duration * 0.2):
            radius = healthy_radius + (self.radius - healthy_radius) * \
                (self.get_time() / (self.duration * 0.2))
        elif(self.get_time() < self.duration * 0.9):
            radius = self.radius
        elif(self.get_time() < self.duration):
            radius = self.radius + (healthy_radius - self.radius) * \
                ((self.get_time() - self.duration * 0.9) /
                 (self.duration * 0.1))
        return int(radius)

    def infect_color(self, healthy_color):
        color = [healthy_color[0],
                 healthy_color[1],
                 healthy_color[2]]
        for c in range(0, 3):
            if(self.get_time() < self.duration * 0.2):
                color[c] = healthy_color[c] + \
                    (self.color[c] - healthy_color[c]) * \
                    (self.get_time() / (self.duration * 0.2))
            elif(self.get_time() < self.duration * 0.9):
                color[c] = self.color[c]
            elif(self.get_time() < self.duration):
                color[c] = self.color[c] + \
                    (healthy_color[c] - self.color[c]) * \
                    ((self.get_time() - self.duration * 0.9) /
                     (self.duration * 0.1))
        return (color[0], color[1], color[2])


class Patient:
    def __init__(self, pos, radius, healthy_color=green, virus=None):
        self.pos = pos
        self.healthy_radius = radius
        self.radius = self.healthy_radius
        self.healthy_color = healthy_color
        self.immune = False
        self.virus = virus
        if self.virus is not None:
            self.virus_carrier = True
        else:
            self.virus_carrier = False

    def is_hit(self, pos, radius):
        if (self.pos - pos).v < self.radius + radius:
            return True
        return False

    def is_healed(self):
        if self.virus is None:
            return True
        if self.virus.get_time() > self.virus.duration:
            self.immune = True
            self.virus = None
            infected_people.remove(self)
            immune_people.append(self)
            return True
        else:
            return False

    def test_for_infection(self):
        if self.immune:
            return False
        for infected_patient in infected_people:
            if self.is_hit(infected_patient.pos, infected_patient.radius):
                self.virus = infected_patient.virus
                people.remove(self)
                infected_people.append(self)
                return True
        return False

    def update_health(self):
        if self.virus is None:
            self.test_for_infection()
        else:
            self.is_healed()

    def move(self, dx, dy):
        self.pos.x += dx
        self.pos.y += dy

    def draw(self):
        self.update_health()
        if self.virus is None:
            color = self.healthy_color
            self.radius = self.healthy_radius
        else:
            color = self.virus.infect_color(self.healthy_color)
            self.radius = self.virus.infect_radius(self.healthy_radius)
        pygame.draw.circle(game_display, color,
                           (int(self.pos.x), int(self.pos.y)), self.radius)


# TODO: NPC and Player inherits from the player superclass
class Npc(Patient):
    def __init__(self, healthy_radius, healthy_color=green, virus=None):
        Patient.__init__(self, Vector(0, 0), healthy_radius, healthy_color, virus)
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
        self.bounce()
        self.move(self.vel.x, self.vel.y)
        self.draw()


class Player(Patient):
    def __init__(self, pos, healthy_radius, healthy_color, controls, virus=None):
        Patient.__init__(self, pos, healthy_radius, healthy_color, virus)
        self.controls = controls
        self.start_time = time.time()

    def animate(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[self.controls[0]] and self.pos.x > self.radius:
            self.move(-2, 0)
        if key_pressed[self.controls[1]] and self.pos.x < display_width - self.radius:
            self.move(2, 0)
        if key_pressed[self.controls[2]] and self.pos.y > self.radius:
            self.move(0, -2)
        if key_pressed[self.controls[3]] and self.pos.y < display_height - self.radius:
            self.move(0, 2)
        self.draw()

    def time_survived(self):
        if self.virus is None:
            self.age = time.time() - self.start_time
        formatted_time = f"{self.age:.1f}"
        score_time = float(formatted_time)
        font = pygame.font.SysFont(None, 50)
        text = font.render("Time uninfected: " + str(score_time), True, white)
        game_display.blit(text, (10, 10))
        return score_time


# functions
def quit_game():
    pygame.quit()
    quit()


'''# TODO: Create intro screen to pick gamemode
def game_intro():
    pass


# TODO: Create model with adjustable variables
def model_loop():
    pass
'''


def game_loop():
    global virus_level
    for i in range(0, population):
        people.append(Npc(15))
    player = Player(
        Vector(int(display_width/2), int(display_height/2)),
        15,
        white,
        [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]
    )
    people.append(player)
    infected_people.append(Npc(15, virus=Virus(virus_level)))

    game_exit = False
    while not game_exit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

        game_display.fill(black)

        if len(infected_people) == 0:
            virus_level += 5
            for patient in immune_people:
                patient.immune = False
                if patient.virus_carrier:
                    patient.virus = Virus(virus_level)
                    infected_people.append(patient)
                else:
                    people.append(patient)
            del immune_people[:]

        for patient in people:
            patient.animate()
        for patient in infected_people:
            patient.animate()
        for patient in immune_people:
            patient.animate()
        player.time_survived()
        pygame.display.flip()
        clock.tick(120)


game_loop()
quit_game()
