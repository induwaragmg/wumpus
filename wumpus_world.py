import random

class WumpusWorld:
    """
    This class represents the Wumpus World environment.
    It handles world generation, agent movement, percepts, and game state.
    """

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
        """
        Randomly generates a 4x4 grid with pits, one Wumpus, and one gold.
        Ensures safety in the starting cell and its adjacent cells.
        """
        world = [[{"pit": False, "wumpus": False, "gold": False} for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        restricted = {(0, 0), (0, 1), (1, 0), (1,1)}

        # Place pits randomly (20% probability), avoiding start and neighbors
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if (i, j) not in restricted and random.random() < 0.2:
                    world[i][j]["pit"] = True

        # Place Wumpus not adjacent to start
        while True:
            wx, wy = random.randint(0, 3), random.randint(0, 3)
            if (wx, wy) not in restricted:
                world[wx][wy]["wumpus"] = True
                break

        # Place gold in any free cell
        while True:
            gx, gy = random.randint(0, 3), random.randint(0, 3)
            if (gx, gy) != (0, 0) and not world[gx][gy]["pit"] and not world[gx][gy]["wumpus"]:
                world[gx][gy]["gold"] = True
                break

        return world

    def get_percepts(self):
        """Returns current percepts based on agent’s position."""
        return self.get_percepts_at(*self.agent_pos)

    def get_percepts_at(self, x, y):
        """
        Computes percepts (stench, breeze, glitter, bump, scream) at given position.
        """
        cell = self.world[x][y]
        percepts = {
            "stench": False,
            "breeze": False,
            "glitter": cell["gold"],
            "bump": False,
            "scream": False
        }

        # Check adjacent cells for Wumpus (stench) or pit (breeze)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                if self.world[nx][ny]["wumpus"] and self.wumpus_alive:
                    percepts["stench"] = True
                if self.world[nx][ny]["pit"]:
                    percepts["breeze"] = True
        return percepts

    def move_forward(self):
        """Moves the agent one step forward in the current direction if possible."""
        x, y = self.agent_pos
        new_x, new_y = x, y

        if self.agent_dir == "up": new_x -= 1
        elif self.agent_dir == "down": new_x += 1
        elif self.agent_dir == "left": new_y -= 1
        elif self.agent_dir == "right": new_y += 1

        if 0 <= new_x < self.grid_size and 0 <= new_y < self.grid_size:
            self.agent_pos = (new_x, new_y)
            self.percepts = self.get_percepts()
            return True
        else:
            self.percepts["bump"] = True
            return False

    def turn_left(self):
        """Rotates the agent's direction 90 degrees to the left."""
        directions = ["up", "left", "down", "right"]
        index = directions.index(self.agent_dir)
        self.agent_dir = directions[(index + 1) % 4]
        self.percepts = self.get_percepts()

    def turn_right(self):
        """Rotates the agent's direction 90 degrees to the right."""
        directions = ["up", "right", "down", "left"]
        index = directions.index(self.agent_dir)
        self.agent_dir = directions[(index + 1) % 4]
        self.percepts = self.get_percepts()

    def shoot_arrow(self):
        """
        Shoots an arrow in the current direction.
        If the Wumpus is hit, it dies and a scream percept is triggered.
        """
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

        self.percepts = self.get_percepts()
        return wumpus_killed

    def grab_gold(self):
        """Grabs the gold if present in the agent's current position."""
        x, y = self.agent_pos
        if self.world[x][y]["gold"]:
            self.has_gold = True
            self.world[x][y]["gold"] = False
            return True
        return False

    def is_game_over(self):
        """
        Checks current game status.
        Returns:
            'win' if gold is collected and agent is at start,
            'lose' if agent is in pit or alive Wumpus cell,
            'continue' otherwise.
        """
        x, y = self.agent_pos
        cell = self.world[x][y]

        if cell["pit"] or (cell["wumpus"] and self.wumpus_alive):
            return "lose"
        if self.has_gold and self.agent_pos == (0, 0):
            return "win"
        return "continue"
