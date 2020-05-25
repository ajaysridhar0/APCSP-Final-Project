import sys
import pygame
import math
import random
import matplotlib.pyplot as plt
import numpy as np
import pygame_textinput


# color definitions
black = (0, 0, 0)
white = (255, 255, 255)
dark_red = (145, 0, 0)
dark_green = (0, 145, 0)
red = (200, 0, 0)
green = (0, 200, 0)
blue = (0, 30, 255)
bright_red = (255, 0, 0)
bright_green = (0, 255, 0)
teal = (0, 255, 255)
yellow = (255, 255, 0)
magenta = (255, 0, 255)

# intial pygame variables
display_width = 1000
display_height = 1000
simulation_display = pygame.display.set_mode((display_width, display_height),
                                             pygame.HWSURFACE |
                                             pygame.DOUBLEBUF)
clock = pygame.time.Clock()

# initial factor
s0 = 100
i0 = 1
r0 = 0
population = s0 + i0 + r0
spread_radius = 10
avg_duration = 600
duration_variation = 1.0
infection_rate = 1.0
avg_vel = 1.0
vel_variation = 0.0

# other global variables
ticks = 0
simulation_exit = False
susceptible_people = []
infected_people = []
recovered_people = []
textinputs = []

# graphing data
t_data = []
s_data = []
i_data = []
r_data = []

# setup
pygame.init()
pygame.display.set_caption("Epidemic Simulation")
coronaImg = pygame.image.load('../assets/corona.png')
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
    def __init__(self, avg_duration, duration_variation,
                 infection_rate, color=red):
        self.start_time = ticks
        self.duration_variation = duration_variation
        self.duration = random.gauss(avg_duration, self.duration_variation)
        self.infection_rate = infection_rate
        self.color = color
        type(self.duration)

    def get_time(self):
        return ticks - self.start_time

    def infect_color(self, susceptible_color, recovered_color):
        color = [susceptible_color[0],
                 susceptible_color[1],
                 susceptible_color[2]]
        for c in range(0, 3):
            if(self.get_time() < self.duration * 0.125):
                color[c] = susceptible_color[c] + \
                    (self.color[c] - susceptible_color[c]) * \
                    (self.get_time() / (self.duration * 0.125))
            elif(self.get_time() < self.duration * 0.875):
                color[c] = self.color[c]
            elif(self.get_time() < self.duration):
                color[c] = self.color[c] + \
                    (recovered_color[c] - self.color[c]) * \
                    ((self.get_time() - self.duration * 0.875) /
                     (self.duration * 0.125))
        return (color[0], color[1], color[2])


class Person:
    def __init__(self, pos, vel, radius, susceptible_color,
                 recovered_color, virus, recovered):
        self.pos = pos
        self.vel = vel
        self.radius = radius
        self.susceptible_color = susceptible_color
        self.recovered_color = recovered_color
        self.virus = virus
        self.recovered = recovered

    @classmethod
    def randomize(cls, avg_vel, vel_variation,
                  radius, susceptible_color=blue,
                  recovered_color=green, virus=None, recovered=False):

        pos = Vector(
            random.randrange(spread_radius, display_width - radius),
            random.randrange(radius, display_height - radius)
        )
        vel = Vector(np.random.rand() * 2. - 1.,
                     np.random.rand() * 2. - 1.)
        vel.normalize()
        scal = random.gauss(avg_vel, vel_variation)
        vel.x *= scal
        vel.y *= scal
        return cls(pos, vel, radius, susceptible_color,
                   recovered_color, virus, recovered)

    def is_hit(self, other_person):
        if (self.pos - other_person.pos).v < self.radius + other_person.radius:
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
            if self.is_hit(infected_patient) and np.random.rand() <= infected_patient.virus.infection_rate:
                self.virus = Virus(
                    infected_patient.virus.duration,
                    infected_patient.virus.duration_variation,
                    infected_patient.virus.infection_rate,
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
        else:
            color = self.virus.infect_color(self.susceptible_color,
                                            self.recovered_color)
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


def activate_text_input(x, y, w, h, text_input, events, was_clicked, index):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x + w > mouse[0] > x and y + h > mouse[1] > y or was_clicked[index]:
        if click[0] == 1 or was_clicked[index]:
            text_input.update(events)
            for j in range(len(was_clicked)):
                was_clicked[j] = False
            was_clicked[index] = True
    return was_clicked


def display_stats():
    font = pygame.font.SysFont('calibri bold', 40)
    ticks_text = font.render("Ticks: " +
                             str(ticks), True, white)
    simulation_display.blit(ticks_text, (10, 10))
    s_text = font.render("Susceptible: " +
                         str(len(susceptible_people)), True, white)
    i_text = font.render("Infected: " +
                         str(len(infected_people)), True, white)
    r_text = font.render("Recovered: " +
                         str(len(recovered_people)), True, white)
    simulation_display.blit(s_text, (10, 50))
    simulation_display.blit(i_text, (10, 90))
    simulation_display.blit(r_text, (10, 130))


def quit_simulation():
    pygame.quit()
    sys.exit()


"""
def screen_resize(width, height):
    global simulation_display, display_width, display_height
    display_width = width
    display_height = height
    simulation_display = pygame.display.set_mode(
        (display_width, display_height),
        pygame.HWSURFACE |
        pygame.DOUBLEBUF |
        pygame.RESIZABLE
    )
"""

# TODO: Create intro screen to pick gamemode


def simluation_menu():
    global textinputs
    # Subtitle
    subtitles = [
        "Initial susceptible population: ",
        "Initial infected population: ",
        "Initial recovered population: ",
        "Spread radius: ",
        "Average duration of virus: ",
        "Variance in duration of virus: ",
        "Infection rate: ",
        "Average velocity: ",
        "Velocity variation: "
    ]

    # Initial conditions
    initial_conditions = [
        str(s0),
        str(i0),
        str(r0),
        str(spread_radius),
        str(avg_duration),
        str(duration_variation),
        str(infection_rate),
        str(avg_vel),
        str(vel_variation)
    ]

    # Text colors
    text_colors = [
        blue,
        red,
        green,
        teal,
        yellow,
        yellow,
        dark_green,
        magenta,
        magenta
    ]

    # Track clicking
    was_clicked = [
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False
    ]

    initially_clicked = [
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False
    ]

    for i in range(9):
        textinputs.append(pygame_textinput.TextInput(
            initial_string=initial_conditions[i],
            font_family="calibri",
            font_size=30,
            text_color=text_colors[i],
            cursor_color=text_colors[i],
            repeat_keys_initial_ms=500,
            repeat_keys_interval_ms=500,
        ))

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                quit_simulation()
            simulation_display.fill(black)

            # Title
            large_text = pygame.font.SysFont('calibri', 100)
            text_surf, text_rect = text_objects("Epidemic Simulation", large_text)
            text_rect.center = (display_width/2, 170)
            simulation_display.blit(text_surf, text_rect)

            for i in range(9):
                large_text = pygame.font.SysFont('calibri', 30)
                text_surf, text_rect = text_objects(subtitles[i], large_text)
                text_rect.center = (display_width/2, 250 + 60 * i)
                simulation_display.blit(text_surf, text_rect)

                # Placing text inputs
                large_text = pygame.font.SysFont('calibri', 30)
                text_surf, text_rect = text_objects(textinputs[i].get_text(), large_text)
                text_rect.center = (display_width/2, 280 + 60 * i)
                was_clicked = activate_text_input(0, 265 + 60 * i, display_width, 30,
                                                  textinputs[i], events, was_clicked, i)
                if not initially_clicked[i]:
                    textinputs[i].update(events)
                    initially_clicked[i] = True

                # textinputs[i].update(events)
                simulation_display.blit(textinputs[i].get_surface(), text_rect)

            button("Run", 175, 800, 200, 100, bright_green, green, simulation_loop)
            button("Quit", 625, 800, 200, 100, bright_red, red, quit_simulation)

            pygame.display.update()
            clock.tick(15)


def simulation_loop():
    global s0, i0, r0, population, spread_radius, avg_duration
    global duration_variation, infection_rate, avg_vel, vel_variation
    global display_width, display_height, recovered_people, ticks
    global t_data, s_data, i_data, r_data, simulation_display

    # Reset variables for simulation
    del susceptible_people[:], infected_people[:], recovered_people[:]
    del t_data[:], s_data[:], i_data[:], r_data[:]
    ticks = 0

    # Update global variables with user text input
    s0 = int(textinputs[0].get_text())
    i0 = int(textinputs[1].get_text())
    r0 = int(textinputs[2].get_text())
    population = s0 + i0 + r0
    spread_radius = int(textinputs[3].get_text())
    avg_duration = int(textinputs[4].get_text())
    duration_variation = float(textinputs[5].get_text())
    infection_rate = float(textinputs[6].get_text())
    avg_vel = float(textinputs[7].get_text())
    vel_variation = float(textinputs[8].get_text())

    for i in range(0, s0):
        susceptible_people.append(
            Person.randomize(
                avg_vel,
                vel_variation,
                spread_radius
            )
        )

    for i in range(0, i0):
        infected_people.append(
            Person.randomize(
                avg_vel,
                vel_variation,
                spread_radius,
                virus=Virus(
                    avg_duration,
                    duration_variation,
                    infection_rate
                )
            )
        )

    for i in range(0, r0):
        susceptible_people.append(
            Person.randomize(
                avg_vel,
                vel_variation,
                spread_radius,
                recovered=True
            )
        )

    simulation_exit = False
    while not simulation_exit:
        display_width, display_height = pygame.display.get_surface().get_size()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_simulation()
        # black background
        simulation_display.fill(black)

        # update graphing data
        t_data.append(ticks)
        ticks += 1
        s_data.append(len(susceptible_people) / population)
        i_data.append(len(infected_people) / population)
        r_data.append(len(recovered_people) / population)

        if len(infected_people) == 0:
            graph_data()
            simulation_exit = True
        else:
            for patient in susceptible_people:
                patient.animate()
            for patient in infected_people:
                patient.animate()
            for patient in recovered_people:
                patient.animate()
        display_stats()
        pygame.display.flip()
        clock.tick(120)


def graph_data():
    global t_data, s_data, i_data, r_data
    plt.plot(t_data, s_data, 'b', label='Susceptible')
    plt.plot(t_data, i_data, 'r', label='Infected')
    plt.plot(t_data, r_data, 'g', label='Recovered')
    plt.ylabel('Fraction of Population')
    plt.xlabel('Ticks in Simulation')
    legend = plt.legend()
    plt.title("SIR Model")
    plt.show()


if __name__ == "__main__":
    simluation_menu()
