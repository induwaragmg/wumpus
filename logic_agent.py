import time
from collections import deque

class LogicAgent:
    """
    A logic-based agent for the Wumpus World.
    Uses simple rule-based inference to deduce safe cells and make decisions.
    """

    def __init__(self, world, draw_callback=None):
        self.world = world
        self.draw_callback = draw_callback
        self.position = (0, 0)
        self.grid_size = world.grid_size

        # Agent state
        self.has_gold = False
        self.returning_home = False
        self.score = -1  # Initial movement penalty

        # Knowledge base
        self.visited = set()
        self.safe_cells = {(0, 0)}
        self.possible_pits = set()
        self.possible_wumpus = set()
        self.confirmed_wumpus = None

    def update_knowledge(self):
        """
        Updates knowledge about the environment using current percepts and past observations.
        Adds cells to safe/pit/wumpus lists based on percepts.
        """
        x, y = self.position
        self.visited.add((x, y))
        percepts = self.world.percepts

        # No breeze or stench → all neighbors are safe
        if not percepts["breeze"] and not percepts["stench"]:
            self.safe_cells.update(self.get_neighbors(x, y))

        # Re-check past visited cells to expand safe area
        updated = True
        while updated:
            updated = False
            for cx, cy in list(self.visited):
                past_percepts = self.world.get_percepts_at(cx, cy)
                if not past_percepts["breeze"] and not past_percepts["stench"]:
                    for nx, ny in self.get_neighbors(cx, cy):
                        if (nx, ny) not in self.safe_cells:
                            self.safe_cells.add((nx, ny))
                            updated = True

        # Mark possible hazards
        for nx, ny in self.get_neighbors(x, y):
            if (nx, ny) not in self.safe_cells and (nx, ny) not in self.visited:
                if percepts["stench"]:
                    self.possible_wumpus.add((nx, ny))
                if percepts["breeze"]:
                    self.possible_pits.add((nx, ny))

        # Try to confirm Wumpus location if only one candidate fits logic
        candidates = [cell for cell in self.possible_wumpus if self.is_consistent_wumpus(cell)]
        if len(candidates) == 1:
            self.confirmed_wumpus = candidates[0]

    def is_consistent_wumpus(self, cell):
        """
        Verifies if a suspected Wumpus cell is consistent with all known stench observations.
        """
        cx, cy = cell
        for vx, vy in self.visited:
            percept = self.world.get_percepts_at(vx, vy)
            manhattan = abs(cx - vx) + abs(cy - vy)
            if percept["stench"] and manhattan != 1:
                return False
            if not percept["stench"] and manhattan == 1:
                return False
        return True

    def get_neighbors(self, x, y):
        """Returns valid grid neighbors for a given (x, y) position."""
        neighbors = []
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                neighbors.append((nx, ny))
        return neighbors

    def bfs(self, start, goal):
        """
        Performs Breadth-First Search (BFS) from start to goal through safe cells.
        Returns the path if found, else None.
        """
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
        """
        Chooses the next best safe unvisited move.
        Prioritizes shortest safe path via BFS.
        """
        if self.returning_home:
            path = self.bfs(self.position, (0, 0))
            return path[1] if path and len(path) > 1 else None

        unvisited_safe = [cell for cell in self.safe_cells if cell not in self.visited]
        min_path = None
        min_length = float('inf')
        for cell in unvisited_safe:
            path = self.bfs(self.position, cell)
            if path and 1 < len(path) < min_length:
                min_path = path
                min_length = len(path)
        return min_path[1] if min_path else None

    def move_to(self, destination):
        """
        Moves agent toward a chosen destination cell, updating orientation.
        """
        dx = destination[0] - self.position[0]
        dy = destination[1] - self.position[1]

        if dx == 1: self.world.agent_dir = "down"
        elif dx == -1: self.world.agent_dir = "up"
        elif dy == 1: self.world.agent_dir = "right"
        elif dy == -1: self.world.agent_dir = "left"

        # Redraw before moving
        if self.draw_callback:
            self.draw_callback(self.world, self.position, self.world.percepts, score=self.score, safe_cells=self.safe_cells)
        time.sleep(0.2)

        moved = self.world.move_forward()
        self.score -= 1  # Cost of move or bump
        if moved:
            self.position = self.world.agent_pos

    def act(self):
        """
        Executes an action based on current percepts and knowledge:
        - Grab gold
        - Shoot Wumpus
        - Return home
        """
        percepts = self.world.percepts

        # Grab gold if present
        if percepts["glitter"] and not self.has_gold:
            self.world.grab_gold()
            self.has_gold = True
            self.returning_home = True
            self.score += 1000
            return

        # Shoot Wumpus if confirmed and in line of sight
        if self.confirmed_wumpus and self.world.has_arrow:
            wx, wy = self.confirmed_wumpus
            ax, ay = self.position

            if ax == wx or ay == wy:
                # Rotate toward Wumpus before shooting
                if ax == wx:
                    self.world.agent_dir = "left" if wy < ay else "right"
                else:
                    self.world.agent_dir = "up" if wx < ax else "down"

                if self.draw_callback:
                    self.draw_callback(self.world, self.position, percepts, score=self.score, safe_cells=self.safe_cells)
                time.sleep(0.3)

                self.world.shoot_arrow()
                self.score -= 10

                # Mark Wumpus cell as safe if it is no longer dangerous if there isnot a pit
                if not self.world.wumpus_alive:
                    if self.confirmed_wumpus not in self.possible_pits:
                        self.safe_cells.add(self.confirmed_wumpus)
                    self.confirmed_wumpus = None
