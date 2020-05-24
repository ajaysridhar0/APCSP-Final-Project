import sys
import pygame
import time
import random
import math
import matplotlib.pyplot as plt
# import numpy as np

# dimensions
display_width = 1000
display_height = 1000

# color definitions
black = (0, 0, 0)
white = (255, 255, 255)
dark_red = (145, 0, 0)
dark_green = (0, 145, 0)
red = (200, 0, 0)
green = (0, 200, 0)
blue = (0, 0, 255)
bright_red = (255, 0, 0)
bright_green = (0, 255, 0)
teal = (0, 255, 255)
yellow = (255, 255, 0)

# global variables
simulation_display = pygame.display.set_mode((display_width, display_height),
                                             pygame.HWSURFACE | pygame.DOUBLEBUF |
                                             pygame.RESIZABLE)
clock = pygame.time.Clock()
ticks = 0
population = 75
virus_level = -2
healthy_radius = 12
simulation_exit = False
susceptible_people = []
infected_people = []
recovered_people = []

# setup
pygame.init()
pygame.display.set_caption("SIR Model")
coronaImg = pygame.image.load('corona.png')
pygame.display.set_icon(coronaImg)


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
    def __init__(self, duration, radius, color=red):
        self.level = virus_level
        self.start_time = ticks
        self.duration = duration
        self.radius = radius
        self.color = color
        # self.death_rate = death_rate

    @classmethod
    def mutate(cls):
        return cls(
            random.randrange(500 + int(virus_level * 20), 600 + virus_level),
            random.randrange(healthy_radius + int(virus_level * 0.6), 16 + virus_level)
        )

    def get_time(self):
        return ticks - self.start_time

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

    # TODO: Add susceptible_color and recovered_color

    def infect_color(self, susceptible_color, recovered_color):
        color = [susceptible_color[0],
                 susceptible_color[1],
                 susceptible_color[2]]
        for c in range(0, 3):
            if(self.get_time() < self.duration * 0.2):
                color[c] = susceptible_color[c] + \
                    (self.color[c] - susceptible_color[c]) * \
                    (self.get_time() / (self.duration * 0.2))
            elif(self.get_time() < self.duration * 0.9):
                color[c] = self.color[c]
            elif(self.get_time() < self.duration):
                color[c] = self.color[c] + \
                    (recovered_color[c] - self.color[c]) * \
                    ((self.get_time() - self.duration * 0.9) /
                     (self.duration * 0.1))
        return (color[0], color[1], color[2])


class Person:
    def __init__(self, pos=Vector(0, 0), susceptible_color=blue, recovered_color=green, virus=None):
        self.healthy_radius = healthy_radius
        self.radius = self.healthy_radius
        self.susceptible_color = susceptible_color
        self.recovered_color = recovered_color
        self.recovered = False
        self.virus = virus
        self.pos = Vector(
            random.randrange(self.radius, display_width - self.radius),
            random.randrange(self.radius, display_height - self.radius)
        )
        self.vel = Vector(random.randrange(-200, 200),
                          random.randrange(-200, 200))
        self.vel.normalize()
        scal = random.randrange(5, 10) / 10
        self.vel.x *= scal
        self.vel.y *= scal

    def is_hit(self, pos, radius):
        if (self.pos - pos).v < self.radius + radius:
            return True
        return False

    def is_recovered(self):
        if self.virus is None:
            return True
        if self.virus.get_time() > self.virus.duration:
            self.recovered = True
            self.virus = None
            infected_people.remove(self)
            recovered_people.append(self)
            return True
        else:
            return False

    def test_for_infection(self):
        if self.recovered:
            return False
        for infected_patient in infected_people:
            if self.is_hit(infected_patient.pos, infected_patient.radius):
                self.virus = Virus(
                    infected_patient.virus.duration,
                    infected_patient.virus.radius,
                    infected_patient.virus.color
                )
                susceptible_people.remove(self)
                infected_people.append(self)
                return True
        return False

    def update_health(self):
        if self.virus is None:
            self.test_for_infection()
        else:
            self.is_recovered()

    def move(self, dx, dy):
        self.pos.x += dx
        self.pos.y += dy

    def draw(self):
        self.update_health()
        if self.virus is None:
            if self.recovered:
                color = self.recovered_color
            else:
                color = self.susceptible_color
            self.radius = self.healthy_radius
        else:
            color = self.virus.infect_color(self.susceptible_color,
                                            self.recovered_color)
            self.radius = self.virus.infect_radius(self.healthy_radius)
        pygame.draw.circle(simulation_display, color,
                           (int(self.pos.x), int(self.pos.y)), self.radius)

    def bounce(self):
        if self.pos.x < self.radius or self.pos.x > display_width - self.radius:
            self.vel.x = -self.vel.x
        if self.pos.y < self.radius or self.pos.y > display_height - self.radius:
            self.vel.y = -self.vel.y

    def animate(self):
        self.bounce()
        self.move(self.vel.x, self.vel.y)
        self.draw()

# functions


def text_objects(text, font, color=white):
    text_surface = font.render(text, True, color)
    return text_surface, text_surface.get_rect()


def button(msg, x, y, w, h, inactive_color, active_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(simulation_display, active_color, (x, y, w, h))
        if click[0] == 1 and action is not None:
            action()
    else:
        pygame.draw.rect(simulation_display, inactive_color, (x, y, w, h))

    small_text = pygame.font.SysFont('calibri', 50)
    text_surf, text_rect = text_objects(msg, small_text, color=black)
    text_rect.center = ((x + (w / 2)), (y + (h / 2)))
    simulation_display.blit(text_surf, text_rect)


def quit_simulation():
    pygame.quit()
    sys.exit()


# TODO: Create intro screen to pick gamemode
def simluation_menu():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_simulation()
            simulation_display.fill(black)
            large_text = pygame.font.SysFont('calibri', 100)
            text_surf, text_rect = text_objects("Project COVID19 (Beta)", large_text)
            text_rect.center = (display_width/2, display_height/2)
            simulation_display.blit(text_surf, text_rect)

            button("Run", 175, 650, 200, 100, bright_green, green, simulation_loop)
            button("Quit", 625, 650, 200, 100, bright_red, red, quit_simulation)

            pygame.display.update()
            clock.tick(15)


def simulation_loop():
    global display_width
    global display_height
    global virus_level
    global recovered_people
    global ticks

    del susceptible_people[:]
    del infected_people[:]
    del recovered_people[:]
    virus_level = 0

    for i in range(0, population):
        susceptible_people.append(Person())

    infected_people.append(Person(virus=Virus.mutate()))

    # graphing stuff
    t_data = []
    s_data = []
    i_data = []
    r_data = []

    simulation_exit = False
    while not simulation_exit:
        display_width, display_height = pygame.display.get_surface().get_size()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_simulation()
            elif event.type == pygame.VIDEORESIZE:
                print('resize')
                screen = pygame.display.set_mode(
                    event.dict['size'], pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
                print(event.dict['size'])
                screen.blit(pygame.transform.scale(simulation_display, event.dict['size']), (0, 0))
        # black background
        simulation_display.fill(black)

        # update graphing data
        t_data.append(ticks)
        ticks += 1
        s_data.append(len(susceptible_people) / population)
        i_data.append(len(infected_people) / population)
        r_data.append(len(recovered_people) / population)

        if len(infected_people) == 0:
            """
            virus_level += 5
            for patient in recovered_people:
                patient.recovered = False
                if patient.virus_carrier:
                    patient.virus = Virus.mutate()
                    infected_people.append(patient)
                else:
                    susceptible_people.append(patient)
            recovered_people = []
            """
            # graphing population susceptible_people
            # TODO: graphing

            plt.plot(t_data, s_data, 'b', label='Susceptible')
            plt.plot(t_data, i_data, 'r', label='Infected')
            plt.plot(t_data, r_data, 'g', label='Recovered')
            plt.ylabel('Fraction of Population')
            plt.xlabel('Ticks in Simulation')
            leg = plt.legend()
            plt.show()
        else:
            for patient in susceptible_people:
                patient.animate()
            for patient in infected_people:
                patient.animate()
            for patient in recovered_people:
                patient.animate()

        # simulation_display.blit(pygame.transform.scale(simulation_display, (700, 700)), (0, 0))
        pygame.display.flip()
        clock.tick(120)


simluation_menu()
