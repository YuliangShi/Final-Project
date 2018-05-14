import pygame
import buff_class
import random
import math


def compute_distance(pos1, pos2):
    return int(math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2))


def generate_buff_pos(pos, num, var, start, end, line=False):
    if line is False:
        for i in range(2 * num):
            x = pos[0] + random.gauss(0, var)
            y = pos[1] + random.gauss(0, var)
            yield (int(x), int(y))

    else:
        num_sources = (abs(start[0] - end[0]) + abs(start[1] - end[1])) // 10
        for i in range(1, int(num_sources + 1)):
            to_generate = (i / num_sources * abs(start[0] - end[0]) + min(start[0], end[0]),
                           i / num_sources * abs(start[1] - end[1]) + min(start[1], end[1]))
            yield from generate_buff_pos(to_generate, 1, 5, None, None)


def judge(players, gameDisplay):
    display_size = gameDisplay.get_size()
    to_return = {}
    for i in range(len(players)):
        if (0 <= players[i].head[0] <= display_size[0] and
            0 <= players[i].head[1] <= display_size[1]) or \
                players[i].living is False:
            continue
        else:
            to_return[i] = ("suicided", None)

    for j in range(len(players)):
        for i in range(len(players)):
            if players[j].is_crashed(players[i]) and players[i].living is True and players[j].living is True:
                to_return[j] = ("killed", i)

    return to_return


def point_is_on_line(point, line_start, line_end, var=1):
    if line_end[0] - line_start[0] != 0:
        line_small, line_large = min(line_end[0], line_start[0]), max(line_end[0], line_start[0])
        if line_small < point[0] < line_large and line_start[1] - var < point[1] < line_start[1] + var:
            return True

    if line_end[1] - line_start[1] != 0:
        line_small, line_large = min(line_end[1], line_start[1]), max(line_end[1], line_start[1])
        if line_small < point[1] < line_large and line_start[0] - var < point[0] < line_start[0] + var:
            return True

    return False


if __name__ == "__main__":
    print(compute_distance((1, 0), (2, 0)))
