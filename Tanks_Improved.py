import pygame
import time
import random
import select
import json
from tank_class import *
from chat_utils import *


class Tanks:
    def __init__(self, s, display_height=600, display_width=800, icon=None):
        pygame.init()

        # Colors
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.light_black = (55, 55, 55)
        self.red = (255, 0, 0)
        self.light_red = (255, 153, 153)
        self.yellow = (230, 230, 0)
        self.light_yellow = (255, 255, 153)
        self.green = (0, 255, 0)
        self.light_green = (153, 255, 153)

        # Fonts
        self.small_font = pygame.font.SysFont("comicsansms", 25)
        self.med_font = pygame.font.SysFont("comicsansms", 50)
        self.large_font = pygame.font.SysFont("comicsansms", 80)

        # Clock
        self.clock = pygame.time.Clock()  # clock object

        # frames per second
        self.FPS = 8

        # Screen size
        self.display_height = display_height
        self.display_width = display_width

        self.gameDisplay = pygame.display.set_mode((self.display_width, self.display_height))
        pygame.display.set_caption('Tanks')

        # socket
        self.s = s

        if icon:
            icon_surf = self.load_image(icon)
            pygame.display.set_icon(icon_surf)

    def set_window(self, icon=None):
        # Init the display surface; Return pygame.surface object
        self.gameDisplay = pygame.display.set_mode((self.display_width, self.display_height))

        # Add caption for the game window
        pygame.display.set_caption('Tanks')

        # Set an icon for the window
        # if not icon:
        #     icon_surf = self.load_i   mage(icon)
        #     pygame.display.set_icon(icon_surf)

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
                    pygame.quit()
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

    def get_new_barrier(self):
        barrier_width = 50
        xlocation = self.display_width / 2 - barrier_width / 2
        ylocation = 3 * self.display_height / 5

        return xlocation, ylocation, barrier_width, self.display_height - ylocation

    def display_power_level(self, tank):
        text = self.small_font.render("Power: " + "{:.2%}".format(min(tank.power_level / len(tank.power_levels), 1)),
                                      True, self.black)
        self.gameDisplay.blit(text, [2 * self.display_width / 3, 0])

    def explosion(self, x_y):
        explore = True
        x = x_y[0]
        y = x_y[1]
        while explore:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            magnitude = 1
            colors = [self.red, self.light_red, self.yellow, self.light_yellow]

            while magnitude < 50:
                exploding_bit_x = x + random.randrange(-1 * magnitude, magnitude)
                exploding_bit_y = y + random.randrange(-1 * magnitude, magnitude)

                pygame.draw.circle(self.gameDisplay, colors[random.randrange(0, 4)], (exploding_bit_x, exploding_bit_y),
                                   random.randrange(1, 5))
                magnitude += 1

                pygame.display.update()
                self.clock.tick(100)

            explore = False

    def fire(self, trajectory, new_barrier, enemy):
        pygame.draw.rect(self.gameDisplay, self.white, (self.display_width / 2 - 50, 0, 100, 40))
        for x_y in trajectory:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                if event.type == pygame.KEYDOWN:
                    # if event.key == pygame.K_p:
                    #     pause()
                    if event.key == pygame.K_q:
                        pygame.quit()
                        quit()

            cur = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
            self.make_button(cur, click, self.light_red, self.red,
                             (self.display_width / 2 - 50, 40, 100, 40),
                             "quit", self.black, action="quit")

            if enemy.x - enemy.width / 2 < x_y[0] < enemy.x + enemy.width / 2 and \
                    enemy.y - enemy.height / 3 < x_y[1] < enemy.y + 2 * enemy.width / 3:
                self.explosion(x_y)
                return True

            if new_barrier[0] < x_y[0] < new_barrier[0] + new_barrier[2] and \
                    new_barrier[1] < x_y[1] < new_barrier[1] + new_barrier[3]:
                self.explosion(x_y)
                break

            if x_y[1] >= enemy.y + 7 * enemy.height / 11:
                self.explosion(x_y)
                break
            else:
                pygame.draw.circle(self.gameDisplay, self.red, x_y, 5)
                pygame.display.update()
                pygame.time.wait(15)

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
                    pygame.quit()
                    quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        pause = False
                    if event.key == pygame.K_q:
                        pygame.quit()
                        quit()

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

        self.gameDisplay.fill(self.white)
        self.message_to_whole_screen("Welcome to Tanks",
                                     self.green,
                                     y_displacement=-100,
                                     size="large")
        self.message_to_whole_screen("The objective of the game is to destroy",
                                     self.black,
                                     y_displacement=-30)
        self.message_to_whole_screen("the enemy tank before they destroy you.",
                                     self.black,
                                     y_displacement=5)
        self.message_to_whole_screen("The more enemy you destroy the harder you ones will get.",
                                     self.black,
                                     y_displacement=40)
        self.message_to_whole_screen("Shortcut: Press P to pause or Q to quit",
                                     self.black,
                                     y_displacement=75)

        while intro:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        intro = False
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        quit()
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

        self.gameDisplay.fill(self.white)
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
                    pygame.quit()
                    quit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        controls = False
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        quit()
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

    def game_loop(self):

        game_exit = False
        game_over = False

        tank1 = Tank(self.display_width * 0.9, self.display_height * 0.9, 60, 5, 10, self.gameDisplay, 135)
        tank2 = Tank(self.display_width * 0.1, self.display_height * 0.9, 60, 5, 10, self.gameDisplay)

        new_barrier = self.get_new_barrier()

        damage = False
        fired = False

        change_x_1 = 0
        change_x_2 = 0

        change_angle_1 = 0
        change_angle_2 = 0

        barrier_refresh = 0

        change_power_level = 0

        while not game_exit:

            while game_over is True:
                gameDisplay.fill(white)

                self.message_to_whole_screen("Game over",
                                             self.red,
                                             y_displacement=-90,
                                             size="large")
                self.message_to_whole_screen("Score: " + "",
                                             self.green,
                                             y_displacement=10,
                                             size="medium")
                self.message_to_whole_screen("Press C to play again or Q to quit.",
                                             self.black,
                                             y_displacement=90,
                                             size="small")
                pygame.display.update()

                for event in pygame.event.get():

                    if event.type == pygame.QUIT:
                        game_exit = True
                        game_over = False

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            game_exit = True
                            game_over = False
                        elif event.key == pygame.K_c:
                            self.game_loop()

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    game_exit = True

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        change_x_1 = -5
                    elif event.key == pygame.K_RIGHT:
                        change_x_1 = 5
                    elif event.key == pygame.K_UP:
                        change_angle_1 = -5
                    elif event.key == pygame.K_DOWN:
                        change_angle_1 = 5
                    elif event.key == pygame.K_SPACE:
                        change_power_level = 1
                    elif event.key == pygame.K_p:
                        self.pause()
                    elif event.key == pygame.K_q:
                        pygame.quit()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        change_x_1 = 0
                    elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        change_angle_1 = 0
                    elif event.key == pygame.K_SPACE:
                        # fired = True
                        to_send = {"action": "update", "position": 0, "direction": 0, "fired": True,
                                   "power_level": tank1.power_level, "life_level": tank1.life_level, "damage": damage}
                        print(tank1.power_level, tank1.direction, tank1.life_level, 438)
                        mysend(self.s, json.dumps(to_send))
                        damage = self.fire(tank1.fire_trajectory(), new_barrier, tank2)
                        change_power_level = 0
                        tank1.power_level = 0

            self.gameDisplay.fill(self.white)
            pygame.draw.rect(self.gameDisplay, self.green,
                             (0, tank1.y + 7 * tank1.height / 11, self.display_width,
                              self.display_height - tank1.y - 7 * tank1.height / 11))

            # if barrier_refresh % 10 == 0:
            #     new_barrier = self.get_new_barrier()
            pygame.draw.rect(self.gameDisplay, self.light_yellow, new_barrier)
            # barrier_refresh += 1
            pygame.draw.rect(self.gameDisplay, self.red, (20, 10, tank1.life_level, 30))

            if self.display_width / 2 + 50 + tank1.width < tank1.x < self.display_width - (tank1.width / 2) or \
                    (change_x_1 > 0 and tank1.x <= self.display_width / 2 + 50 + tank1.width) or \
                    (change_x_1 < 0 and tank1.x >= self.display_width - (tank1.width / 2)):
                tank1.update_position(change_x_1, 0)
            tank1.update_direction(change_angle_1)
            tank1.power_level += change_power_level
            if damage:
                tank1.life_level -= 10
            damage = False
            self.display_power_level(tank1)

            tank1.draw_tank(self.light_green)
            tank2.draw_tank(self.light_red)

            # print(myrecv(self.s))
            read, write, error = select.select([self.s], [], [], 0)
            if self.s in read:
                raw_recieve = myrecv(self.s)
                if raw_recieve:
                    received = json.loads(raw_recieve)
                    tank2.update_position(received["position"], 0)
                    tank2.update_direction(received["direction"])
                    tank2.update_power_level(received["power_level"])
                    tank2.update_life(received["life_level"])
                    if received["fired"] is True:
                        print(tank2.power_level, tank2.direction, tank2.life_level, 476)
                        self.fire(tank2.fire_trajectory(), new_barrier, tank1)
                    # damage = received["damage"]

            # if fired:
            #     to_send = {"action": "update", "position": 0, "direction": 0, "fired": True,
            #                "power_level": tank1.power_level, "life_level": tank1.power_level}  # , "damage": damage}
            #     mysend(self.s, json.dumps(to_send))
            #     damage = self.fire(tank1.fire_trajectory(), new_barrier, tank2)
            #     change_power_level = 0
            #     tank1.power_level = 0
            #     fired = False
            # else:
            to_send = {"action": "update", "position": - change_x_1, "direction": - change_angle_1, "fired": False,
                       "power_level": tank1.power_level, "life_level": tank1.life_level}  # , "damage": damage}
            mysend(self.s, json.dumps(to_send))

            # print(tank1.life_level, tank2.life_level)

            self.in_game_instructions()

            pygame.display.update()

            self.clock.tick(self.FPS)

        pygame.quit()
