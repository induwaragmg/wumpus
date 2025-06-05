import time
from collections import deque

class LogicAgent:
    def __init__(self, world, draw_callback=None):
        self.world = world
        self.draw_callback = draw_callback
        self.position = (0, 0)
        self.has_gold = False
        self.returning_home = False
        self.visited = set()
        self.safe_cells = set([(0, 0)])
        self.possible_pits = set()
        self.possible_wumpus = set()
        self.confirmed_wumpus = None
        self.grid_size = world.grid_size

        # Scoring
        self.score = 0
        self.score -= 1  # Initial step cost

    def update_knowledge(self):
        x, y = self.position
        self.visited.add((x, y))
        percepts = self.world.percepts

        if not percepts["breeze"] and not percepts["stench"]:
            for nx, ny in self.get_neighbors(x, y):
                self.safe_cells.add((nx, ny))

        updated = True
        while updated:
            updated = False
            for cx, cy in list(self.visited):
                p = self.world.get_percepts_at(cx, cy)
                if not p["breeze"] and not p["stench"]:
                    for nx, ny in self.get_neighbors(cx, cy):
                        if (nx, ny) not in self.safe_cells:
                            self.safe_cells.add((nx, ny))
                            updated = True

        for nx, ny in self.get_neighbors(x, y):
            if (nx, ny) not in self.safe_cells and (nx, ny) not in self.visited:
                if percepts["stench"]:
                    self.possible_wumpus.add((nx, ny))
                if percepts["breeze"]:
                    self.possible_pits.add((nx, ny))

        confirmed = [cell for cell in self.possible_wumpus if self.is_consistent_wumpus(cell)]
        if len(confirmed) == 1:
            self.confirmed_wumpus = confirmed[0]

    def is_consistent_wumpus(self, cell):
        cx, cy = cell
        for x, y in self.visited:
            p = self.world.get_percepts_at(x, y)
            if p["stench"] and abs(cx - x) + abs(cy - y) != 1:
                return False
            if not p["stench"] and abs(cx - x) + abs(cy - y) == 1:
                return False
        return True

    def get_neighbors(self, x, y):
        neighbors = []
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                neighbors.append((nx, ny))
        return neighbors

    def bfs(self, start, goal):
        queue = deque([[start]])
        visited = set([start])
        while queue:
            path = queue.popleft()
            curr = path[-1]
            if curr == goal:
                return path
            for neighbor in self.get_neighbors(*curr):
                if neighbor in self.safe_cells and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])
        return None

    def choose_next_move(self):
        if self.returning_home:
            path = self.bfs(self.position, (0, 0))
            if path and len(path) > 1:
                return path[1]
            return None

        unvisited_safe = [cell for cell in self.safe_cells if cell not in self.visited]
        min_path = None
        min_length = float('inf')
        for cell in unvisited_safe:
            path = self.bfs(self.position, cell)
            if path and len(path) < min_length and len(path) > 1:
                min_path = path
                min_length = len(path)
        if min_path:
            return min_path[1]
        return None

    def move_to(self, destination):
        dx, dy = destination[0] - self.position[0], destination[1] - self.position[1]
        if dx == 1:
            self.world.agent_dir = "down"
        elif dx == -1:
            self.world.agent_dir = "up"
        elif dy == 1:
            self.world.agent_dir = "right"
        elif dy == -1:
            self.world.agent_dir = "left"

        if self.draw_callback:
            self.draw_callback(self.world, self.position, self.world.percepts, score=self.score, safe_cells=self.safe_cells)
        time.sleep(0.2)

        moved = self.world.move_forward()
        if moved:
            self.position = self.world.agent_pos
            self.score -= 1  # movement cost
        else:
            self.score -= 1  # bump also costs a move

    def act(self):
        percepts = self.world.percepts

        if percepts["glitter"] and not self.has_gold:
            self.world.grab_gold()
            self.has_gold = True
            self.returning_home = True
            self.score += 1000
            return

        if self.confirmed_wumpus and self.world.has_arrow:
            wx, wy = self.confirmed_wumpus
            ax, ay = self.position

            if ax == wx or ay == wy:
                if ax == wx:
                    self.world.agent_dir = "left" if wy < ay else "right"
                elif ay == wy:
                    self.world.agent_dir = "up" if wx < ax else "down"

                if self.draw_callback:
                    self.draw_callback(self.world, self.position, self.world.percepts, score=self.score, safe_cells=self.safe_cells)
                time.sleep(0.3)

                self.world.shoot_arrow()
                self.score -= 10
                if not self.world.wumpus_alive:
                    if self.confirmed_wumpus not in self.possible_pits:
                        self.safe_cells.add(self.confirmed_wumpus)
                    self.confirmed_wumpus = None
