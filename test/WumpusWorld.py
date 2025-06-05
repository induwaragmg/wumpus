import random
import pygame
import sys
from collections import deque
import os

# Initialize Pygame
pygame.init()




class WumpusWorld:
    def __init__(self):
        self.grid_size = 4
        self.agent_pos = (0, 0)
        self.agent_dir = "right"
        self.has_gold = False
        self.has_arrow = True
        self.wumpus_alive = True
        self.world = self.generate_world()
        self.percepts = self.get_percepts()
        self.score = 0

    def generate_world(self):
        world = [[{"pit": False, "wumpus": False, "gold": False} for _ in range(self.grid_size)] for _ in
                 range(self.grid_size)]

        # Place pits (20% chance per cell, except start)
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if (i, j) != (0, 0) and random.random() < 0.2:
                    world[i][j]["pit"] = True

        # Place Wumpus (random, not at start)
        wumpus_pos = (random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1))
        while wumpus_pos == (0, 0):
            wumpus_pos = (random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1))
        world[wumpus_pos[0]][wumpus_pos[1]]["wumpus"] = True

        # Place gold (random, not at start, not in pit)
        gold_pos = (random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1))
        while gold_pos == (0, 0) or world[gold_pos[0]][gold_pos[1]]["pit"]:
            gold_pos = (random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1))
        world[gold_pos[0]][gold_pos[1]]["gold"] = True

        return world

    def get_percepts(self):
        x, y = self.agent_pos
        cell = self.world[x][y]
        percepts = {
            "stench": False,
            "breeze": False,
            "glitter": False,
            "bump": False,
            "scream": False
        }

        # Check adjacent cells for Wumpus (stench) and pits (breeze)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                if self.world[nx][ny]["wumpus"] and self.wumpus_alive:
                    percepts["stench"] = True
                if self.world[nx][ny]["pit"]:
                    percepts["breeze"] = True

        # Current cell percepts
        if cell["gold"]:
            percepts["glitter"] = True

        return percepts

    def move_forward(self):
        x, y = self.agent_pos
        new_x, new_y = x, y

        if self.agent_dir == "up":
            new_x -= 1
        elif self.agent_dir == "down":
            new_x += 1
        elif self.agent_dir == "left":
            new_y -= 1
        elif self.agent_dir == "right":
            new_y += 1

        # Check if move is valid
        if 0 <= new_x < self.grid_size and 0 <= new_y < self.grid_size:
            self.agent_pos = (new_x, new_y)
            self.score -= 1  # Each move costs 1 point
            self.percepts = self.get_percepts()
            return True
        else:
            self.percepts["bump"] = True
            return False

    def turn_left(self):
        dirs = ["up", "left", "down", "right"]
        idx = dirs.index(self.agent_dir)
        self.agent_dir = dirs[(idx + 1) % 4]
        self.percepts = self.get_percepts()

    def turn_right(self):
        dirs = ["up", "right", "down", "left"]
        idx = dirs.index(self.agent_dir)
        self.agent_dir = dirs[(idx + 1) % 4]
        self.percepts = self.get_percepts()

    def shoot_arrow(self):
        if not self.has_arrow:
            return False

        self.has_arrow = False
        self.score -= 10  # Arrow shot costs 10 points
        x, y = self.agent_pos
        wumpus_killed = False

        # Arrow travels in a straight line in the current direction
        if self.agent_dir == "up":
            for i in range(x - 1, -1, -1):
                if self.world[i][y]["wumpus"]:
                    wumpus_killed = True
                    break
        elif self.agent_dir == "down":
            for i in range(x + 1, self.grid_size):
                if self.world[i][y]["wumpus"]:
                    wumpus_killed = True
                    break
        elif self.agent_dir == "left":
            for j in range(y - 1, -1, -1):
                if self.world[x][j]["wumpus"]:
                    wumpus_killed = True
                    break
        elif self.agent_dir == "right":
            for j in range(y + 1, self.grid_size):
                if self.world[x][j]["wumpus"]:
                    wumpus_killed = True
                    break

        if wumpus_killed:
            self.wumpus_alive = False
            self.percepts["scream"] = True
            return True
        return False

    def grab_gold(self):
        x, y = self.agent_pos
        if self.world[x][y]["gold"]:
            self.has_gold = True
            self.world[x][y]["gold"] = False
            self.percepts["glitter"] = False
            self.score += 1000  # Grabbing gold gives 1000 points
            return True
        return False

    # In the WumpusWorld class
    def is_game_over(self):
        x, y = self.agent_pos
        cell = self.world[x][y]
        if cell["pit"] or (cell["wumpus"] and self.wumpus_alive):
            return "lose"
        if self.has_gold and self.agent_pos == (0, 0):
            return "win"
        return "continue"

