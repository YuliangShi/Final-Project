import pygame
import time
import random
import json
import math
import select
from snack_class_final import *
from snack_utils import *
from buff_class import *
from chat_utils import *


class GameMenu:
    def __init__(self, s, display_height=600, display_width=800, icon=None):
        pygame.init()

        # Colors
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.red = (255, 50, 50)
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

        # Clock
        self.clock = pygame.time.Clock()  # clock object

        # frames per second
        self.FPS = 10

        # Screen size
        self.display_height = display_height
        self.display_width = display_width

        # Set display
        self.gameDisplay = pygame.display.set_mode((self.display_width, self.display_height))
        pygame.display.set_caption('Snacks')

        # Set Icon
        if icon:
            icon_surf = self.load_image(icon)
            pygame.display.set_icon(icon_surf)

        # socket
        self.s = s

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
                if action == "Power Line":
                    mysend(self.s, json.dumps({"action": "vote", "game": "power line"}))
                    return True
                elif action == "Racing":
                    mysend(self.s, json.dumps({"action": "vote", "game": "racing"}))
                    return True
                elif action == "Tanks":
                    mysend(self.s, json.dumps({"action": "vote", "game": "tanks"}))
                    return True
        else:
            pygame.draw.rect(self.gameDisplay, color_regular, rect)
        self.text_to_button(text, text_color, rect)
        return False

    def main_loop(self):
        main_loop = True
        success = False
        peer_msg = ""
        # print("GM", "start main loop")

        self.gameDisplay.fill(self.light_black)
        self.message_to_whole_screen("Welcome!",
                                     self.green,
                                     y_displacement=-110,
                                     size="large")
        self.message_to_whole_screen("Please choose the game you would like to play.",
                                     self.black,
                                     y_displacement=-30,
                                     size="small")

        while main_loop:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    main_loop = False
                    success = False
                    to_send = {"action": "update", "continue": False}
                    mysend(self.s, json.dumps(to_send))

            read, write, error = select.select([self.s], [], [], 0)
            if self.s in read:
                raw_recv = myrecv(self.s)
                if raw_recv:
                    recv = json.loads(raw_recv)
                    # print(raw_recv, "GM", 129)
                    if recv["action"] == "update":
                        if "continue" in recv:
                            main_loop = recv["continue"]
                    if recv["action"] == "voted":
                        pass

            cur = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
            choice_1 = self.make_button(cur, click, self.light_green, self.green,
                                        (200, 300, 400, 50),
                                        "Power Line", self.black,
                                        action="Power Line")
            choice_2 = self.make_button(cur, click, self.light_yellow, self.yellow,
                                        (200, 380, 400, 50),
                                        "Racing", self.black,
                                        action="Racing")
            choice_3 = self.make_button(cur, click, self.light_red, self.red,
                                        (200, 460, 400, 50),
                                        "Tanks", self.black,
                                        action="Tanks")

            if choice_1 or choice_2 or choice_3:
                # print("to wait", "GM", 147)
                success, peer_msg = self.waiting()
                main_loop = False
                # print(success, peer_msg, "GM", 149)

            pygame.display.update()
            self.clock.tick(self.FPS)

        pygame.time.wait(2000)
        pygame.display.quit()
        pygame.quit()
        # print("GM", 156)

        # print(success, peer_msg, "GM", 158)

        return success, peer_msg

    def waiting(self):
        waiting = True
        success = False
        peer_msg = ""

        self.gameDisplay.fill(self.light_black)
        self.message_to_whole_screen("Waiting...",
                                     self.green,
                                     y_displacement=-100,
                                     size="large")

        while waiting:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    waiting = False
                    success = False
                    to_send = {"action": "update", "continue": False}
                    mysend(self.s, json.dumps(to_send))

            read, write, error = select.select([self.s], [], [], 0)
            if self.s in read:
                raw_recv = myrecv(self.s)
                if raw_recv:
                    recv = json.loads(raw_recv)
                    print(recv, "GM", 200)
                    if recv["action"] == "decision":
                        peer_msg = raw_recv
                        success = True
                        waiting = False
                    elif recv["action"] == "update":
                        # print(recv, "GM", 199)
                        if "continue" in recv:
                            waiting = recv["continue"]
                            if recv["continue"] is False:
                                success = False
                                waiting = False
                    elif recv["action"] == "voted":
                        pass

            pygame.display.update()
            self.clock.tick(self.FPS)

        # print(success, peer_msg, "GM", 198)
        return success, peer_msg
