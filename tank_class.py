import pygame
from math import *


class Tank:

    def __init__(self, init_x, init_y, width, turret_width, wheel_width, display_surface, init_direction=45):

        self.x = int(init_x)
        self.y = int(init_y)
        self.direction = init_direction
        self.life_level = 100

        self.width = int(width)
        self.height = int(width * 3 / 4)
        self.turret_width = int(turret_width)
        self.wheel_width = int(wheel_width)
        self.surface = display_surface
        self.power_level = 0
        self.power_levels = [0.025, 0.024, 0.023, 0.022, 0.021] + \
                            [0.02 - 0.0005 * i for i in range(21)] + \
                            [0.009 - 0.00025 * i for i in range(20)]

    def update_position(self, change_x, change_y):
        self.x = int(self.x + change_x)
        self.y = int(self.y + change_y)

    def update_direction(self, change_angle):
        if 0 <= self.direction + change_angle <= 180:
            self.direction += change_angle

    def update_power_level(self, new_power_level):
        self.power_level = new_power_level

    def update_life(self, new_life_level):
        self.life_level = new_life_level

    def draw_tank(self, color):
        pygame.draw.circle(self.surface, color, (int(self.x), int(self.y)), int(1 * self.height / 3))
        pygame.draw.rect(self.surface, color,
                         (int(self.x - self.width / 2), int(self.y), self.width, int(1 * self.height / 2)))
        pygame.draw.line(self.surface, color,
                         (self.x, self.y - 5),
                         (int(self.x + (self.width / 2) * cos(radians(self.direction))),
                          int(self.y - 5 - (self.width / 2) * sin(radians(self.direction)))),
                         self.turret_width)
        for i in range(8):
            pygame.draw.circle(self.surface, color,
                               (int(self.x - (7 - 2 * i) * self.width / 16), int(self.y + 3 * self.height / 6)),
                               int(1 * self.height / 12))

    def turret_position(self):
        return [int(self.x + (self.width / 2) * cos(radians(self.direction))),
                int(self.y - 5 - (self.width / 2) * sin(radians(self.direction)))]

    def get_power(self):
        if self.power_level > len(self.power_levels) - 1:
            return self.power_levels[-1]
        return self.power_levels[self.power_level]

    def fire_trajectory(self):
        """Reture: a list of points indicating the trajectory."""
        cur = self.turret_position()
        trajectory = [cur]
        display_width = self.surface.get_width()
        display_height = self.surface.get_height()
        count = 0
        while 0 < cur[0] < display_width and 0 < cur[1] < display_height:
            x = int(cur[0] + cos(radians(self.direction)) * 8)
            y = int(cur[1] - (sin(radians(self.direction)) - count * self.get_power()) * 8)
            cur = [x, y]
            trajectory.append(cur)
            count += 1
        return trajectory
