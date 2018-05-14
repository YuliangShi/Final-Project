import pygame
import time
import os
import random
import json
import math
import select
import sys
from snack_class_final import *
from snack_utils import *
from buff_class import *
from chat_utils import *


class SnackGame:
    def __init__(self, s, me, display_height=600, display_width=800):
        print("snack_game_final", 16)
        result = pygame.init()
        print(result)
        print("snack_game_final", 19)

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
        self.purple = (187, 189, 224)

        # start positions with corresponding color
        self.start_pos = ["right_up", "left_down", "right_down", "left_up"]
        self.snacks_color = [self.red, self.green, self.white, self.yellow]

        # Fonts
        self.small_font = pygame.font.SysFont("comicsansms", 25)
        self.med_font = pygame.font.SysFont("comicsansms", 50)
        self.large_font = pygame.font.SysFont("comicsansms", 80)

        # Clock
        print("snack_game_final", 43)
        self.clock = pygame.time.Clock()  # clock object
        print("snack_game_final", 45)

        # frames per second
        self.FPS = 8

        # Screen size
        self.display_height = display_height
        self.display_width = display_width

        self.gameDisplay = None

        # Snacks/Players
        self.players = None

        # Me:
        self.me = me

        # buffers
        self.buffers = []

        # socket
        self.s = s
        self.to_send = self.to_send = {"action": "update", "head": None,
                                       "length": None, "from": self.me}
        print("snack_game_final", 69)

    def set_window(self, num_players, icon=None, ):
        # Init the display surface; Return pygame.surface object
        self.gameDisplay = pygame.display.set_mode((self.display_width, self.display_height))

        # Add caption for the game window
        pygame.display.set_caption('Snacks')

        # Set an icon for the window
        if icon:
            icon_surf = self.load_image(icon)
            pygame.display.set_icon(icon_surf)

        self.players = [Snack(self.gameDisplay, self.snacks_color[i], self.start_pos[i]) for i in range(num_players)]

    def load_image(self, image):
        """
        :param image: (file name full under the same folder)
        :return: surface object
        """
        return pygame.image.load(image)

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

    def text_to_button(self, msg, color, rect, size="small"):
        text_surface, text_rec = self.text_object(msg, color, size)
        text_rec.center = rect[0] + (rect[2] / 2), rect[1] + (rect[3] / 2)
        self.gameDisplay.blit(text_surface, text_rec)

    def message_to_whole_screen(self, msg, color, y_displacement=0, size='small'):
        text_surface, text_rec = self.text_object(msg, color, size)
        text_rec.center = self.display_width / 2, self.display_height / 2 + y_displacement
        self.gameDisplay.blit(text_surface, text_rec)

    def make_button(self, mouse_cur, click, color_react, color_regular, rect, text, text_color, action=None):
        if rect[0] < mouse_cur[0] < rect[0] + rect[2] and rect[1] < mouse_cur[1] < rect[1] + rect[3]:
            pygame.draw.rect(self.gameDisplay, color_react, rect)
            if click[0] == 1 and action is not None:
                if action == "play":
                    self.game_loop()
                elif action == "controls":
                    self.game_controls()
                elif action == "quit":
                    pygame.display.quit()
                    quit()
                elif action == "main_menu":
                    self.game_intro()
                elif action == "pause":
                    self.pause()
                elif action == "continue":
                    return True
        else:
            pygame.draw.rect(self.gameDisplay, color_regular, rect)
        self.text_to_button(text, text_color, rect)

    def in_game_instructions(self):
        cur = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        self.make_button(cur, click, self.light_green, self.green,
                         (self.display_width / 2 - 50, 0, 100, 40),
                         "pause", self.black,
                         action="pause")
        self.make_button(cur, click, self.light_red, self.red,
                         (self.display_width / 2 - 50, 40, 100, 40),
                         "quit", self.black,
                         action="quit")

    def pause(self):
        pause = True
        self.message_to_whole_screen("Paused",
                                     self.green,
                                     y_displacement=-40,
                                     size="large")
        pygame.draw.rect(self.gameDisplay, self.white, (self.display_width / 2 - 50, 0, 100, 40))
        while pause:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        pause = False

            cur = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
            to_continue = self.make_button(cur, click, self.light_green, self.green,
                                           (200, 350, 100, 50),
                                           "continue", self.black, action="continue")
            if to_continue:
                pause = False

            self.make_button(cur, click, self.light_red, self.red,
                             (500, 350, 100, 50),
                             "quit", self.black, action="quit")

            pygame.display.update()
            self.clock.tick(10)

    def game_intro(self):
        intro = True

        self.gameDisplay.fill(self.light_black)
        self.message_to_whole_screen("Welcome to Snacks",
                                     self.green,
                                     y_displacement=-100,
                                     size="large")
        self.message_to_whole_screen("The objective of the game is to destroy",
                                     self.black,
                                     y_displacement=-30)
        self.message_to_whole_screen("the enemy snack while trying to get longer.",
                                     self.black,
                                     y_displacement=5)
        self.message_to_whole_screen("The longer you get the harder the game will be.",
                                     self.black,
                                     y_displacement=40)
        self.message_to_whole_screen("Shortcut: Press P to pause or Q to quit",
                                     self.black,
                                     y_displacement=75)

        while intro:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    quit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        intro = False
                    elif event.key == pygame.K_p:
                        self.pause()

            cur = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
            self.make_button(cur, click, self.light_green, self.green,
                             (150, 450, 100, 50),
                             "play", self.black,
                             action="play")
            self.make_button(cur, click, self.light_yellow, self.yellow,
                             (350, 450, 100, 50),
                             "controls", self.black,
                             action="controls")
            self.make_button(cur, click, self.light_red, self.red,
                             (550, 450, 100, 50),
                             "quit", self.black,
                             action="quit")

            pygame.display.update()
            self.clock.tick(10)

    def game_controls(self):
        controls = True

        self.gameDisplay.fill(self.light_black)
        self.message_to_whole_screen("Controls",
                                     self.green,
                                     y_displacement=-100,
                                     size="large")
        self.message_to_whole_screen("Fire: Press space.",
                                     self.black,
                                     y_displacement=-30)
        self.message_to_whole_screen("Move Turret: Up and Down arrows",
                                     self.black,
                                     y_displacement=5)
        self.message_to_whole_screen("Move Tank: Left and Right arrows",
                                     self.black,
                                     y_displacement=40)
        self.message_to_whole_screen("Press P to pause or Q to quit at amy time of this game.",
                                     self.black,
                                     y_displacement=75)

        while controls:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    quit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        controls = False
                    elif event.key == pygame.K_p:
                        self.pause()

            cur = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
            self.make_button(cur, click, self.light_green, self.green,
                             (150, 450, 100, 50),
                             "play", self.black,
                             action="play")
            self.make_button(cur, click, self.light_yellow, self.yellow,
                             (350, 450, 100, 50),
                             "back", self.black,
                             action="main_menu")
            self.make_button(cur, click, self.light_red, self.red,
                             (550, 450, 100, 50),
                             "quit", self.black,
                             action="quit")

            pygame.display.update()
            self.clock.tick(10)

    def game_over(self):

        game_over = True

        while game_over:
            self.gameDisplay.fill(self.light_black)

            self.message_to_whole_screen("Game over",
                                         self.red,
                                         y_displacement=-90,
                                         size="large")
            # self.message_to_whole_screen("Score: " + "",
            #                              self.green,
            #                              y_displacement=10,
            #                              size="medium")
            self.message_to_whole_screen("Press C to play again or Q to quit.",
                                         self.black,
                                         y_displacement=90,
                                         size="small")
            pygame.display.update()

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    game_over = False
                    self.to_send = {"action": "update", "continue": False}
                    mysend(self.s, json.dumps(self.to_send))

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        self.to_send = {"action": "update", "continue": True}
                        mysend(self.s, json.dumps(self.to_send))
                        self.__init__(self.s, self.me)
                        # self.set_window(len(self.players))
                        # self.waiting()

            i = 0
            while i < 4:
                read, write, error = select.select([self.s], [], [], 0)
                if self.s in read:
                    raw_recv = myrecv(self.s)
                    # print(raw_recv)
                    if raw_recv:
                        recv = json.loads(raw_recv)
                        try:
                            game_over = recv["continue"]
                            break
                        except:
                            continue
                i += 1

        # pygame.quit()
        # sys.exit()

    def waiting(self):
        pass

    def game_watch(self):
        game_watching = True
        while game_watching:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    game_watching = False

            self.gameDisplay.fill(self.light_black)

            for_update = {}

            i = 0
            while i < 4:
                read, write, error = select.select([self.s], [], [], 0)
                if self.s in read:
                    raw_recv = myrecv(self.s)
                    print(raw_recv, type(raw_recv))
                    if raw_recv:
                        recv = json.loads(raw_recv)
                        head = recv["head"]
                        for_update[int(recv["from"])] = [int(recv["length"]), tuple(head)]
                i += 1

            for keys in for_update.keys():
                self.players[keys].update_length(for_update[keys][0])
                self.players[keys].update_corners(for_update[keys][1])

            result = judge(self.players, self.gameDisplay)
            if result:
                for k in result.keys():
                    self.players[k].died()
                    self.buffers.extend(self.players[k].generate_buffer())
                    if result[k][0] == "killed":
                        self.message_to_whole_screen(str(result[k][1]) + " killed " + str(k),
                                                     self.white,
                                                     y_displacement=-200)
                    else:
                        self.message_to_whole_screen(str(k) + "suicided",
                                                     self.white,
                                                     y_displacement=-200)

            for each in self.players:
                if each.living is True:
                    each.draw()
            # self.players[self.me].draw()

            for each in self.buffers:
                pygame.draw.circle(self.gameDisplay, self.royal_blue, each, 3)

            living = 0
            for each in self.players:
                if each.living is True:
                    living += 1

            if living <= 1:
                self.game_over()

            pygame.display.update()

            self.clock.tick(self.FPS)

    def game_loop(self):
        game_exit = False

        self.gameDisplay.fill(self.light_black)
        pygame.display.update()
        pygame.time.wait(2000)

        # temporary
        for each in generate_buff_pos((self.display_width / 2, self.display_height / 2),
                                      len(self.players) * 10, 100,
                                      None, None):
            self.buffers.append(each)

        change_head = [0, -3]

        self.gameDisplay.fill(self.light_black)
        pygame.display.update()

        while not game_exit:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    game_exit = True
                    self.to_send = {"action": "update", "continue": False}
                    mysend(self.s, json.dumps(self.to_send))

                if self.players[self.me].corners_with_tracks[0][1] == (1, 0):
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            change_head[0] = -3
                            change_head[1] = 0
                        elif event.key == pygame.K_UP:
                            change_head[1] = -3
                            change_head[0] = 0
                        elif event.key == pygame.K_DOWN:
                            change_head[1] = 3
                            change_head[0] = 0
                        # elif event.key == pygame.K_p:
                        #     self.pause()

                if self.players[self.me].corners_with_tracks[0][1] == (-1, 0):
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RIGHT:
                            change_head[0] = 3
                            change_head[1] = 0
                        elif event.key == pygame.K_UP:
                            change_head[1] = -3
                            change_head[0] = 0
                        elif event.key == pygame.K_DOWN:
                            change_head[1] = 3
                            change_head[0] = 0
                        # elif event.key == pygame.K_p:
                        #     self.pause()

                if self.players[self.me].corners_with_tracks[0][1] == (0, 1):
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            change_head[0] = -3
                            change_head[1] = 0
                        elif event.key == pygame.K_RIGHT:
                            change_head[0] = 3
                            change_head[1] = 0
                        elif event.key == pygame.K_UP:
                            change_head[1] = -3
                            change_head[0] = 0
                        # elif event.key == pygame.K_p:
                        #     self.pause()

                if self.players[self.me].corners_with_tracks[0][1] == (0, -1):
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            change_head[0] = -3
                            change_head[1] = 0
                        elif event.key == pygame.K_RIGHT:
                            change_head[0] = 3
                            change_head[1] = 0
                        elif event.key == pygame.K_DOWN:
                            change_head[1] = 3
                            change_head[0] = 0
                        # elif event.key == pygame.K_p:
                        #     self.pause()

            self.gameDisplay.fill(self.light_black)

            my_new_head = (self.players[self.me].head[0] + change_head[0],
                           self.players[self.me].head[1] + change_head[1])

            to_pop = None
            for i in range(len(self.buffers)):
                if self.buffers[i][0] - 3 < my_new_head[0] < self.buffers[i][0] + 3 and \
                        self.buffers[i][1] - 3 < my_new_head[1] < self.buffers[i][1] + 3:  # .pos
                    to_pop = i
                    self.players[self.me].update_length(self.players[self.me].length + 5)
            if to_pop:
                self.buffers.pop(to_pop)
            
            for_update = {self.me: [self.players[self.me].length, my_new_head]}

            if not game_exit:
                self.to_send = {"action": "update", "head": list(my_new_head),
                                "length": self.players[self.me].length, "from": self.me}
                mysend(self.s, json.dumps(self.to_send))
            # recv = json.loads(myrecv(self.s))
            # for_update[recv["from"]] = [recv["length"], tuple(recv["head"])]

            i = 0
            while i < 4:
                read, write, error = select.select([self.s], [], [], 0)
                if self.s in read:
                    raw_recv = myrecv(self.s)
                    print(raw_recv, type(raw_recv))
                    if raw_recv:
                        recv = json.loads(raw_recv)
                        try:
                            head = recv["head"]
                            for_update[int(recv["from"])] = [int(recv["length"]), tuple(head)]
                        except:
                            if "continue" in recv:
                                game_exit = recv["continue"]
                i += 1
            
            # ####################
            # head = recv["head"]
            # head = head[1:-1].split(",")
            # head = (int(head[0]), int(head[1]))
            # for_update[int(recv["from"])] = [int(recv["length"]), head]
            # ####################
            
            for keys in for_update.keys():
                self.players[keys].update_length(for_update[keys][0])
                self.players[keys].update_corners(for_update[keys][1])
            
            result = judge(self.players, self.gameDisplay)
            if result:
                for k in result.keys():
                    self.players[k].died()
                    self.buffers.extend(self.players[k].generate_buffer())
                    if result[k][0] == "killed":
                        self.message_to_whole_screen(str(result[k][1]) + " killed " + str(k),
                                                     self.white,
                                                     y_displacement=-200)
                    else:
                        self.message_to_whole_screen(str(k) + "suicided",
                                                     self.white,
                                                     y_displacement=-200)
            
            for each in self.players:
                if each.living is True:
                    each.draw()
            # self.players[self.me].draw()

            for each in self.buffers:
                pygame.draw.circle(self.gameDisplay, self.purple, each, 5)

            living = 0
            for each in self.players:
                if each.living is True:
                    living += 1

            # print(living)

            if living <= 1:
                print("game_over")
                self.game_over()
                game_exit = True

            elif self.players[self.me].living is False:
                print("watching(temp)")
                self.game_watch()

            if len(self.buffers) < len(self.players) + 5:
                for each in generate_buff_pos((self.display_width / 2, self.display_height / 2),
                                              len(self.players), 100,
                                              None, None):
                    self.buffers.append(each)

            pygame.display.update()

            self.clock.tick(self.FPS)

        print("snack_game_final", 564)
        pygame.display.quit()
        pygame.quit()

        # os._exit(0)
        # quit()
