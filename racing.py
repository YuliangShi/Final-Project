import random
import select
import pygame
import time
import os
import json
import math
import sys
from snack_class_final import *
from snack_utils import *
from buff_class import *
from chat_utils import *
from camera import *
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *


class Racing:

    def __init__(self, s, display=(800, 600), max_distance=50):

        self.camera = Camera()
        self.display = display
        self.max_distance = max_distance
        self.object_speed = 2
        self.camera.speed = 0.2
        self.s = s

        pygame.init()

        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)  # | FULLSCREEN)

        gluPerspective(45, (self.display[0] / self.display[1]), 0, self.max_distance)

        glTranslatef(0, 0, self.camera.z)

        # Colors
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.red = (255, 0, 0)
        self.light_red = (255, 153, 153)
        self.yellow = (230, 230, 0)
        self.light_yellow = (255, 255, 153)
        self.green = (0, 255, 0)
        self.light_green = (153, 255, 153)
        self.royal_blue = (65, 105, 225)
        self.light_black = (105, 105, 105)

        # Fonts
        self.small_font = pygame.font.SysFont("comicsansms", 25)
        self.med_font = pygame.font.SysFont("comicsansms", 50)
        self.large_font = pygame.font.SysFont("comicsansms", 80)

        self.vertices = (
            (1, -1, -1),
            (1, 1, -1),
            (-1, 1, -1),
            (-1, -1, -1),
            (1, -1, 1),
            (1, 1, 1),
            (-1, -1, 1),
            (-1, 1, 1),
        )

        self.edges = (
            (0, 1),
            (0, 3),
            (0, 4),
            (2, 1),
            (2, 3),
            (2, 7),
            (6, 3),
            (6, 4),
            (6, 7),
            (5, 1),
            (5, 4),
            (5, 7),
        )

        self.surfaces = (
            (0, 1, 2, 3),
            (3, 2, 7, 6),
            (6, 7, 5, 4),
            (4, 5, 1, 0),
            (1, 5, 7, 2),
            (4, 0, 3, 6),
        )

        self.colors = (
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1),
            (0, 1, 0),
            (1, 1, 1),
            (0, 1, 1),
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1),
            (1, 0, 0),
            (1, 1, 1),
            (0, 1, 1),
        )

        self.ground_vertices = (
            (-10, -0.1, 20),
            (10, -0.1, 20),
            (-10, -0.1, -300),
            (-10, -0.1, -300),
        )

    # def ground(self):
    #     glBegin(GL_QUADS)
    #     for vertex in ground_vertices:
    #         glColor3fv((0, 0.5, 0.5))
    #         glVertex3fv(vertex)
    #
    #     glEnd()

    def message_to_whole_screen(self, msg, color, y_displacement=0, size='small'):
        text_surface, text_rec = self.text_object(msg, color, size)
        text_rec.center = self.display[0] / 2, self.display[1] / 2 + y_displacement
        self.gameDisplay.blit(text_surface, text_rec)

    def text_object(self, text, color, size):
        if size == "small":
            text_surface = self.small_font.render(text, True, color)
        elif size == "medium":
            text_surface = self.med_font.render(text, True, color)
        elif size == "large":
            text_surface = self.large_font.render(text, True, color)
        else:
            pass

        return text_surface, text_surface.get_rect()

    def cube(self, vertices):
        glBegin(GL_QUADS)

        for surface in self.surfaces:
            x = 0
            for vertex in surface:
                x += 1
                glColor3fv(self.colors[x])
                glVertex3fv(vertices[vertex])
        glEnd()

    def set_vertices(self, max_distance, min_distance=-20, camera_x=0, camera_y=0):

        camera_x = -1 * int(camera_x)
        camera_y = -1 * int(camera_y)

        x_change = random.randrange(camera_x - 10, camera_x + 10)
        y_change = random.randrange(camera_y - 10, camera_y + 10)  # -1
        z_change = random.randrange(-1 * max_distance, min_distance)

        new_vertices = []

        for vert in self.vertices:
            new_vert = list()

            new_vert.append(vert[0] + x_change)
            new_vert.append(vert[1] + y_change)
            new_vert.append(vert[2] + z_change)

            new_vertices.append(new_vert)
        return new_vertices

    def game_over(self):

        game_over = True

        while game_over:
            #     self.message_to_whole_screen("Game over",
            #                                  self.red,
            #                                  y_displacement=-90,
            #                                  size="large")
            #     self.message_to_whole_screen("Distance: " + str(self.camera.z),
            #                                  self.green,
            #                                  y_displacement=10,
            #                                  size="medium")
            #     self.message_to_whole_screen("Press C to play again or Q to quit.",
            #                                  self.black,
            #                                  y_displacement=90,
            #                                  size="small")
            # pygame.display.update()

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    game_over = False
                    to_send = {"action": "update", "continue": False}
                    mysend(self.s, json.dumps(to_send))

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        to_send = {"action": "update", "continue": True}
                        mysend(self.s, json.dumps(to_send))
                        self.__init__(self.s, self.me)
                        self.game_loop()

            replay = "waiting"

            read, write, error = select.select([self.s], [], [], 0)
            if self.s in read:
                raw_recv = myrecv(self.s)
                if raw_recv:
                    recv = json.loads(raw_recv)
                    replay = recv["continue"]

            if replay is False:
                game_over = False
            if replay is True:
                self.game_loop()

    def game_loop(self):
        main_loop = True
        x_move = 0
        y_move = 0

        self.camera.x = 0
        self.camera.y = 0

        cube_dict = {}

        for cube_idx in range(40):
            cube_dict[cube_idx] = self.set_vertices(self.max_distance)

        while main_loop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        x_move = self.camera.speed
                    if event.key == pygame.K_RIGHT:
                        x_move = - self.camera.speed
                    if event.key == pygame.K_UP:
                        y_move = - self.camera.speed
                    if event.key == pygame.K_DOWN:
                        y_move = self.camera.speed
                    if event.key == pygame.K_ESCAPE:
                        pygame.display.quit()
                        pygame.display.init()
                        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        x_move = 0
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        y_move = 0

                # if event.type == pygame.MOUSEBUTTONDOWN:
                #     if event.button == 4:
                #         glTranslatef(0, 0, 1.0)
                #     if event.button == 5:
                #         glTranslatef(0, 0, -1.0)

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.camera.x += x_move
            self.camera.y += y_move
            self.camera.z += self.object_speed
            glTranslatef(x_move, y_move, self.object_speed)

            x = glGetDoublev(GL_MODELVIEW_MATRIX)

            camera_x = x[3][0]
            camera_y = x[3][1]
            camera_z = x[3][2]

            # ground()

            for cube_idx in cube_dict:
                self.cube(cube_dict[cube_idx])

            for cube_idx in cube_dict:
                if camera_z <= cube_dict[cube_idx][0][2] and \
                        cube_dict[cube_idx][0][0] - 2 <= camera_x <= cube_dict[cube_idx][0][0] and \
                        cube_dict[cube_idx][0][1] <= camera_y <= cube_dict[cube_idx][0][1] + 2:
                    self.camera.life -= 10
                if camera_z <= cube_dict[cube_idx][0][2]:
                    new_max = int(self.max_distance * 2 - camera_z)
                    cube_dict[cube_idx] = self.set_vertices(new_max, int(camera_z - self.max_distance),
                                                            self.camera.x, self.camera.y)

            if self.camera.life <= 0:
                self.game_over()
                main_loop = False

            pygame.display.flip()

        pygame.quit()
