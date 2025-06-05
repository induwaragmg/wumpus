# import random

# class WumpusWorld:
#     def __init__(self):
#         self.grid_size = 4
#         self.agent_pos = (0, 0)
#         self.agent_dir = "right"
#         self.has_gold = False
#         self.has_arrow = True
#         self.wumpus_alive = True
#         self.wumpus_pos = None
#         self.world = self.generate_world()
#         self.percepts = self.get_percepts()

#     def generate_world(self):
#         world = [[{"pit": False, "wumpus": False, "gold": False} for _ in range(self.grid_size)] for _ in range(self.grid_size)]

#         adjacent_to_start = {(0, 1), (1, 0)}
#         for i in range(self.grid_size):
#             for j in range(self.grid_size):
#                 if (i, j) != (0, 0) and (i, j) not in adjacent_to_start and random.random() < 0.2:
#                     world[i][j]["pit"] = True

#         # Place Wumpus
#         self.wumpus_pos = (random.randint(0, 3), random.randint(0, 3))
#         while self.wumpus_pos == (0, 0) or self.wumpus_pos in adjacent_to_start:
#             self.wumpus_pos = (random.randint(0, 3), random.randint(0, 3))
#         x, y = self.wumpus_pos
#         world[x][y]["wumpus"] = True

#         # Place Gold
#         gold_pos = (random.randint(0, 3), random.randint(0, 3))
#         while world[gold_pos[0]][gold_pos[1]]["pit"] or world[gold_pos[0]][gold_pos[1]]["wumpus"] or gold_pos == (0, 0):
#             gold_pos = (random.randint(0, 3), random.randint(0, 3))
#         world[gold_pos[0]][gold_pos[1]]["gold"] = True

#         return world

#     def get_percepts(self):
#         x, y = self.agent_pos
#         return self.get_percepts_at(x, y)

#     def get_percepts_at(self, x, y):
#         cell = self.world[x][y]
#         percepts = {
#             "stench": False,
#             "breeze": False,
#             "glitter": cell["gold"],
#             "bump": False,
#             "scream": False
#         }

#         for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
#             nx, ny = x + dx, y + dy
#             if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
#                 if self.world[nx][ny]["wumpus"] and self.wumpus_alive:
#                     percepts["stench"] = True
#                 if self.world[nx][ny]["pit"]:
#                     percepts["breeze"] = True

#         return percepts

#     def move_forward(self):
#         x, y = self.agent_pos
#         new_x, new_y = x, y
#         if self.agent_dir == "up":
#             new_x -= 1
#         elif self.agent_dir == "down":
#             new_x += 1
#         elif self.agent_dir == "left":
#             new_y -= 1
#         elif self.agent_dir == "right":
#             new_y += 1

#         if 0 <= new_x < self.grid_size and 0 <= new_y < self.grid_size:
#             self.agent_pos = (new_x, new_y)
#             self.percepts = self.get_percepts()
#             return True
#         else:
#             self.percepts["bump"] = True
#             return False

#     def turn_left(self):
#         dirs = ["up", "left", "down", "right"]
#         idx = dirs.index(self.agent_dir)
#         self.agent_dir = dirs[(idx + 1) % 4]
#         self.percepts = self.get_percepts()

#     def turn_right(self):
#         dirs = ["up", "right", "down", "left"]
#         idx = dirs.index(self.agent_dir)
#         self.agent_dir = dirs[(idx + 1) % 4]
#         self.percepts = self.get_percepts()

#     def shoot_arrow(self):
#         if not self.has_arrow:
#             return False
#         self.has_arrow = False
#         x, y = self.agent_pos
#         scream = False

#         if self.agent_dir == "up":
#             for i in range(x - 1, -1, -1):
#                 if self.world[i][y]["wumpus"]:
#                     self.wumpus_alive = False
#                     # self.world[i][y]["wumpus"] = False
#                     self.percepts["scream"] = True
#                     self.percepts = self.get_percepts()
#                     scream = True
#                     break
#         elif self.agent_dir == "down":
#             for i in range(x + 1, self.grid_size):
#                 if self.world[i][y]["wumpus"]:
#                     self.wumpus_alive = False
#                     # self.world[i][y]["wumpus"] = False
#                     self.percepts["scream"] = True
#                     self.percepts = self.get_percepts()
#                     scream = True
#                     break
#         elif self.agent_dir == "left":
#             for j in range(y - 1, -1, -1):
#                 if self.world[x][j]["wumpus"]:
#                     self.wumpus_alive = False
#                     # self.world[x][j]["wumpus"] = False
#                     self.percepts["scream"] = True
#                     self.percepts = self.get_percepts()
#                     scream = True
#                     break
#         elif self.agent_dir == "right":
#             for j in range(y + 1, self.grid_size):
#                 if self.world[x][j]["wumpus"]:
#                     self.wumpus_alive = False
#                     # self.world[x][j]["wumpus"] = False
#                     self.percepts["scream"] = True
#                     self.percepts = self.get_percepts()
#                     scream = True
#                     break

#         return scream

#     def grab_gold(self):
#         x, y = self.agent_pos
#         if self.world[x][y]["gold"]:
#             self.has_gold = True
#             self.world[x][y]["gold"] = False
#             self.percepts = self.get_percepts()
#             return True
#         return False

#     def update_percepts(self):
#         self.percepts = self.get_percepts_at(*self.agent_pos)

#     def is_game_over(self):
#         x, y = self.agent_pos
#         cell = self.world[x][y]
#         if (cell["pit"] or (cell["wumpus"] and self.wumpus_alive)):
#             return "lose"
#         if self.has_gold and self.agent_pos == (0, 0):
#             return "win"
#         return "continue"

import random

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

    def generate_world(self):
        world = [[{"pit": False, "wumpus": False, "gold": False} for _ in range(self.grid_size)] for _ in range(self.grid_size)]

        # Avoid placing pits at (0,0), (0,1), (1,0)
        adjacent_to_start = {(0, 1), (1, 0)}
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if (i, j) != (0, 0) and (i, j) not in adjacent_to_start and random.random() < 0.2:
                    world[i][j]["pit"] = True

        # Wumpus not near start
        while True:
            wx, wy = random.randint(0, 3), random.randint(0, 3)
            if (wx, wy) != (0, 0) and (wx, wy) not in adjacent_to_start:
                world[wx][wy]["wumpus"] = True
                break

        # Gold anywhere not occupied
        while True:
            gx, gy = random.randint(0, 3), random.randint(0, 3)
            if not world[gx][gy]["pit"] and not world[gx][gy]["wumpus"]:
                world[gx][gy]["gold"] = True
                break

        return world

    def get_percepts(self):
        x, y = self.agent_pos
        return self.get_percepts_at(x, y)

    def get_percepts_at(self, x, y):
        cell = self.world[x][y]
        percepts = {
            "stench": False,
            "breeze": False,
            "glitter": cell["gold"],
            "bump": False,
            "scream": False
        }

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                if self.world[nx][ny]["wumpus"] and self.wumpus_alive:
                    percepts["stench"] = True
                if self.world[nx][ny]["pit"]:
                    percepts["breeze"] = True
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

        if 0 <= new_x < self.grid_size and 0 <= new_y < self.grid_size:
            self.agent_pos = (new_x, new_y)
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

        x, y = self.agent_pos
        wumpus_killed = False

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
            self.percepts = self.get_percepts()  # Refresh percepts after scream
            return True

        self.percepts = self.get_percepts()
        return False

    def grab_gold(self):
        x, y = self.agent_pos
        if self.world[x][y]["gold"]:
            self.has_gold = True
            self.world[x][y]["gold"] = False
            return True
        return False

    def is_game_over(self):
        x, y = self.agent_pos
        cell = self.world[x][y]
        if cell["pit"] or (cell["wumpus"] and self.wumpus_alive):
            return "lose"
        if self.has_gold and self.agent_pos == (0, 0):
            return "win"
        return "continue"
