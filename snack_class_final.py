from snack_utils import *
import random


class Snack:

    def __init__(self, gameDisplay, color, head="right_up", length=200, width=4):

        if head == "right_up":
            self.head = (int(gameDisplay.get_width() * 0.8), int(gameDisplay.get_height() * 0.1))
        elif head == "right_down":
            self.head = (int(gameDisplay.get_width() * 0.8), int(gameDisplay.get_height() * 0.9))
        elif head == "left_up":
            self.head = (int(gameDisplay.get_width() * 0.2), int(gameDisplay.get_height() * 0.1))
        else:
            self.head = (int(gameDisplay.get_width() * 0.2), int(gameDisplay.get_height() * 0.9))
        self.corners_with_tracks = [[self.head, (0, 1)]]
        self.length = length

        self.width = width
        self.color = color
        self.living = True
        self.purple = (187, 189, 224)

        self.gameDisplay = gameDisplay

    def length(self):
        return self.length

    def draw(self):
        cur_length_left = self.length
        corners = list(self.corners_with_tracks[i][0] for i in range(len(self.corners_with_tracks)))

        for i in range(1, len(corners)):
            pygame.draw.line(self.gameDisplay, self.color, corners[i-1], corners[i], self.width)
            cur_length = compute_distance(corners[i-1], corners[i])
            cur_length_left -= cur_length

        if cur_length_left > 0 and self.corners_with_tracks[-1][1] == (0, 1):
            pygame.draw.line(self.gameDisplay, self.color, corners[-1],
                             (corners[-1][0], corners[-1][1] + cur_length_left), self.width)

        elif cur_length_left > 0 and self.corners_with_tracks[-1][1] == (0, -1):
            pygame.draw.line(self.gameDisplay, self.color, corners[-1],
                             (corners[-1][0], corners[-1][1] - cur_length_left), self.width)

        elif cur_length_left > 0 and self.corners_with_tracks[-1][1] == (1, 0):
            pygame.draw.line(self.gameDisplay, self.color, corners[-1],
                             (corners[-1][0] + cur_length_left, corners[-1][1]), self.width)

        elif cur_length_left > 0 and self.corners_with_tracks[-1][1] == (-1, 0):
            pygame.draw.line(self.gameDisplay, self.color, corners[-1],
                             (corners[-1][0] - cur_length_left, corners[-1][1]), self.width)

        # for i in range(100):
        #     x = self.head[0] + random.gauss(0, 2)
        #     y = self.head[1] + random.gauss(0, 4)
        pygame.draw.circle(self.gameDisplay, self.purple, (self.head[0], self.head[1]), 5)

    def update_length(self, new_length):
        if self.living:
            self.length = new_length

    def update_corners(self, new_head):
        if self.living and new_head != self.head:
            change = (int((- new_head[0] + self.head[0]) / compute_distance(new_head, self.head)),
                      int((- new_head[1] + self.head[1]) / compute_distance(new_head, self.head)))
            if change[0] * self.corners_with_tracks[0][1][1] + change[1] * self.corners_with_tracks[0][1][0] != 0:
                self.corners_with_tracks.insert(0, [new_head, change])
            else:
                self.corners_with_tracks[0] = [new_head, self.corners_with_tracks[0][1]]
            self.head = new_head

            acc = 0
            corners = list(self.corners_with_tracks[i][0] for i in range(len(self.corners_with_tracks)))
            for i in range(1, len(corners)):
                acc += compute_distance(corners[i-1], corners[i])
            if acc >= self.length:
                self.corners_with_tracks.pop()

    def died(self):
        self.living = False

    def generate_buffer(self):

        to_return = []
        cur_length_left = self.length
        corners = list(self.corners_with_tracks[i][0] for i in range(len(self.corners_with_tracks)))

        for i in range(1, len(corners)):
            for pos in generate_buff_pos(None, None, None, corners[i - 1], corners[i], line=True):
                to_return.append(pos)
                pygame.draw.circle(self.gameDisplay, self.color, pos, 3)
            cur_length = compute_distance(corners[i - 1], corners[i])
            cur_length_left -= cur_length

        if cur_length_left > 0 and self.corners_with_tracks[-1][1] == (0, 1):
            for pos in generate_buff_pos(None, None, None, corners[-1],
                                         (corners[-1][0], corners[-1][1] + cur_length_left), line=True):

                to_return.append(pos)
                pygame.draw.circle(self.gameDisplay, self.color, pos, 3)

        elif cur_length_left > 0 and self.corners_with_tracks[-1][1] == (0, -1):
            for pos in generate_buff_pos(None, None, None, corners[-1],
                                         (corners[-1][0], corners[-1][1] - cur_length_left), line=True):

                to_return.append(pos)
                pygame.draw.circle(self.gameDisplay, self.color, pos, 3)

        elif cur_length_left > 0 and self.corners_with_tracks[-1][1] == (1, 0):
            for pos in generate_buff_pos(None, None, None, corners[-1],
                                         (corners[-1][0] + cur_length_left, corners[-1][1]), line=True):

                to_return.append(pos)
                pygame.draw.circle(self.gameDisplay, self.color, pos, 3)

        elif cur_length_left > 0 and self.corners_with_tracks[-1][1] == (-1, 0):
            for pos in generate_buff_pos(None, None, None, corners[-1],
                                         (corners[-1][0] - cur_length_left, corners[-1][1]), line=True):
                to_return.append(pos)
                pygame.draw.circle(self.gameDisplay, self.color, pos, 3)

        return to_return

    def is_crashed(self, other):

        my_head = self.head
        cur_length_left = other.length
        corners = list(other.corners_with_tracks[i][0] for i in range(len(other.corners_with_tracks)))

        for i in range(1, len(corners)):
            if point_is_on_line(my_head, corners[i-1], corners[i]):
                return True
            cur_length = compute_distance(corners[i-1], corners[i])
            cur_length_left -= cur_length

        if cur_length_left > 0 and other.corners_with_tracks[-1][1] == (0, 1):
            if point_is_on_line(my_head, corners[-1], (corners[-1][0], corners[-1][1] + cur_length_left)):
                return True

        elif cur_length_left > 0 and other.corners_with_tracks[-1][1] == (0, -1):
            if point_is_on_line(my_head, corners[-1], (corners[-1][0], corners[-1][1] - cur_length_left)):
                return True

        elif cur_length_left > 0 and other.corners_with_tracks[-1][1] == (1, 0):
            if point_is_on_line(my_head, corners[-1], (corners[-1][0] + cur_length_left, corners[-1][1])):
                return True

        elif cur_length_left > 0 and other.corners_with_tracks[-1][1] == (-1, 0):
            if point_is_on_line(my_head, corners[-1], (corners[-1][0] - cur_length_left, corners[-1][1])):
                return True

        return False
