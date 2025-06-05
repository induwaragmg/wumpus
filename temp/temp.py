import random
import pygame
import sys
from collections import deque
import os

# Initialize Pygame
pygame.init()

# Constants
GRID_SIZE = 4
CELL_SIZE = 120
WINDOW_SIZE = GRID_SIZE * CELL_SIZE
INFO_HEIGHT = 200
WINDOW_HEIGHT = WINDOW_SIZE + INFO_HEIGHT
SCREEN_WIDTH = WINDOW_SIZE
SCREEN_HEIGHT = WINDOW_HEIGHT

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
BROWN = (139, 69, 19)
DARK_RED = (150, 0, 0)
DARK_GREEN = (0, 100, 0)


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
        self.game_over = False

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
        if self.game_over:
            return False

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
        if self.game_over:
            return

        dirs = ["up", "left", "down", "right"]
        idx = dirs.index(self.agent_dir)
        self.agent_dir = dirs[(idx + 1) % 4]
        self.percepts = self.get_percepts()

    def turn_right(self):
        if self.game_over:
            return

        dirs = ["up", "right", "down", "left"]
        idx = dirs.index(self.agent_dir)
        self.agent_dir = dirs[(idx + 1) % 4]
        self.percepts = self.get_percepts()

    def shoot_arrow(self):
        if self.game_over or not self.has_arrow:
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
        if self.game_over:
            return False

        x, y = self.agent_pos
        if self.world[x][y]["gold"]:
            self.has_gold = True
            self.world[x][y]["gold"] = False
            self.percepts["glitter"] = False
            self.score += 1000  # Grabbing gold gives 1000 points
            return True
        return False

    def is_game_over(self):
        if self.game_over:
            return self.game_state

        x, y = self.agent_pos
        cell = self.world[x][y]

        if cell["pit"] or (cell["wumpus"] and self.wumpus_alive):
            self.score -= 1000  # Death costs 1000 points
            self.game_over = True
            self.game_state = "lose"
            return "lose"
        if self.has_gold and self.agent_pos == (0, 0):
            self.game_over = True
            self.game_state = "win"
            return "win"
        return "continue"

    def reset(self):
        self.__init__()


class LogicBasedAgent:
    def __init__(self, world):
        self.world = world
        self.knowledge_base = {}  # (x, y): {'safe': True/False, 'visited': True/False, 'pit': True/False/None, 'wumpus': True/False/None}
        self.visited = set()
        self.safe_cells = set()
        self.danger_cells = set()
        self.path_to_gold = []
        self.returning_home = False
        self.percept_history = {}  # Store actual percepts experienced at each position

        # Initialize knowledge base
        for i in range(4):
            for j in range(4):
                self.knowledge_base[(i, j)] = {
                    'safe': None,
                    'visited': False,
                    'pit': None,
                    'wumpus': None,
                    'breeze_around': False,
                    'stench_around': False
                }

        # Starting position is safe
        self.knowledge_base[(0, 0)]['safe'] = True
        self.safe_cells.add((0, 0))

    def get_adjacent_cells(self, pos):
        x, y = pos
        adjacent = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 4 and 0 <= ny < 4:
                adjacent.append((nx, ny))
        return adjacent

    def update_knowledge(self):
        current_pos = self.world.agent_pos
        percepts = self.world.percepts

        # Store the actual percepts we experienced at this position
        self.percept_history[current_pos] = percepts.copy()

        # Mark current position as visited and safe (no pit or wumpus here since we're alive)
        self.knowledge_base[current_pos]['visited'] = True
        self.knowledge_base[current_pos]['safe'] = True
        self.knowledge_base[current_pos]['pit'] = False
        self.knowledge_base[current_pos]['wumpus'] = False
        self.visited.add(current_pos)
        self.safe_cells.add(current_pos)

        adjacent_cells = self.get_adjacent_cells(current_pos)

        # If no breeze, adjacent cells have no pits
        if not percepts['breeze']:
            for adj_pos in adjacent_cells:
                self.knowledge_base[adj_pos]['pit'] = False
                # Check if cell is now completely safe
                if (self.knowledge_base[adj_pos]['pit'] == False and
                        (self.knowledge_base[adj_pos]['wumpus'] == False or not self.world.wumpus_alive)):
                    self.knowledge_base[adj_pos]['safe'] = True
                    self.safe_cells.add(adj_pos)

        # If no stench, adjacent cells have no wumpus
        if not percepts['stench']:
            for adj_pos in adjacent_cells:
                self.knowledge_base[adj_pos]['wumpus'] = False
                # Check if cell is now completely safe
                if (self.knowledge_base[adj_pos]['wumpus'] == False and
                        self.knowledge_base[adj_pos]['pit'] == False):
                    self.knowledge_base[adj_pos]['safe'] = True
                    self.safe_cells.add(adj_pos)

        # If wumpus is dead, all cells are safe from wumpus
        if not self.world.wumpus_alive:
            for pos in self.knowledge_base:
                if self.knowledge_base[pos]['wumpus'] != False:
                    self.knowledge_base[pos]['wumpus'] = False
                    # Check if cell is now completely safe
                    if self.knowledge_base[pos]['pit'] == False:
                        self.knowledge_base[pos]['safe'] = True
                        self.safe_cells.add(pos)

        # Advanced inference: If we have breeze/stench, try to deduce specific locations
        self.perform_advanced_inference()

    def perform_advanced_inference(self):
        """Perform more sophisticated logical inference about pit and wumpus locations"""

        # For each visited cell with percepts, try to infer danger locations
        for visited_pos in self.visited:
            percepts_at_pos = self.get_percepts_at_position(visited_pos)
            adjacent_cells = self.get_adjacent_cells(visited_pos)

            # Count how many adjacent cells could contain pits/wumpus
            if percepts_at_pos['breeze']:
                unknown_adjacent = [pos for pos in adjacent_cells if self.knowledge_base[pos]['pit'] is None]
                safe_adjacent = [pos for pos in adjacent_cells if self.knowledge_base[pos]['pit'] == False]

                # If only one unknown adjacent cell and we have breeze, it must contain pit
                if len(unknown_adjacent) == 1:
                    pit_pos = unknown_adjacent[0]
                    self.knowledge_base[pit_pos]['pit'] = True
                    self.knowledge_base[pit_pos]['safe'] = False
                    if pit_pos in self.safe_cells:
                        self.safe_cells.remove(pit_pos)
                    self.danger_cells.add(pit_pos)

            if percepts_at_pos['stench'] and self.world.wumpus_alive:
                unknown_adjacent = [pos for pos in adjacent_cells if self.knowledge_base[pos]['wumpus'] is None]
                safe_adjacent = [pos for pos in adjacent_cells if self.knowledge_base[pos]['wumpus'] == False]

                # If only one unknown adjacent cell and we have stench, it must contain wumpus
                if len(unknown_adjacent) == 1:
                    wumpus_pos = unknown_adjacent[0]
                    self.knowledge_base[wumpus_pos]['wumpus'] = True
                    self.knowledge_base[wumpus_pos]['safe'] = False
                    if wumpus_pos in self.safe_cells:
                        self.safe_cells.remove(wumpus_pos)
                    self.danger_cells.add(wumpus_pos)

    def get_percepts_at_position(self, pos):
        """Get what the percepts were at a given position"""
        if pos in self.percept_history:
            return self.percept_history[pos]
        return {'breeze': False, 'stench': False}

    def find_safe_unvisited_cells(self):
        safe_unvisited = []
        for pos in self.safe_cells:
            if not self.knowledge_base[pos]['visited']:
                safe_unvisited.append(pos)
        return safe_unvisited

    def find_path_to_target(self, target):
        """BFS to find shortest path to target"""
        if self.world.agent_pos == target:
            return []

        queue = deque([(self.world.agent_pos, [])])
        visited = {self.world.agent_pos}

        while queue:
            current, path = queue.popleft()

            for adj_pos in self.get_adjacent_cells(current):
                if adj_pos == target:
                    return path + [adj_pos]

                if adj_pos not in visited and adj_pos in self.safe_cells:
                    visited.add(adj_pos)
                    queue.append((adj_pos, path + [adj_pos]))

        return None

    def get_direction(self, from_pos, to_pos):
        """Get direction to move from one position to an adjacent position"""
        fx, fy = from_pos
        tx, ty = to_pos

        if tx < fx:
            return "up"
        elif tx > fx:
            return "down"
        elif ty < fy:
            return "left"
        elif ty > fy:
            return "right"
        return self.world.agent_dir  # fallback if positions are the same

    def get_turn_action(self, target_direction):
        current_dir = self.world.agent_dir
        dirs = ["up", "right", "down", "left"]

        current_idx = dirs.index(current_dir)
        target_idx = dirs.index(target_direction)

        # Calculate the shortest turn
        diff = (target_idx - current_idx) % 4
        if diff == 1 or diff == -3:
            return "turn_right"
        elif diff == 3 or diff == -1:
            return "turn_left"
        else:
            return "turn_right"  # Default

    def get_move_action(self, from_pos, to_pos):
        target_direction = self.get_direction(from_pos, to_pos)

        if self.world.agent_dir == target_direction:
            return "move"
        else:
            return self.get_turn_action(target_direction)

    def choose_action(self):
        self.update_knowledge()
        current_pos = self.world.agent_pos
        percepts = self.world.percepts

        # If we have gold and we're returning home
        if self.world.has_gold:
            if current_pos == (0, 0):
                return "climb"  # Win condition
            else:
                # Find path home
                path_home = self.find_path_to_target((0, 0))
                if path_home:
                    next_pos = path_home[0]
                    return self.get_move_action(current_pos, next_pos)

        # If we see glitter, grab the gold
        if percepts['glitter']:
            return "grab"

        # Try to shoot wumpus if we have arrow and can identify wumpus location
        if (self.world.has_arrow and self.world.wumpus_alive and
                any(self.knowledge_base[pos]['wumpus'] == True for pos in self.knowledge_base)):

            # Find wumpus position
            wumpus_positions = [pos for pos, info in self.knowledge_base.items() if info['wumpus'] == True]
            if wumpus_positions:
                wumpus_pos = wumpus_positions[0]
                # Check if we can shoot wumpus from current position
                if self.can_shoot_target(current_pos, wumpus_pos):
                    target_direction = self.get_shooting_direction(current_pos, wumpus_pos)
                    if self.world.agent_dir == target_direction:
                        return "shoot"
                    else:
                        return self.get_turn_action(target_direction)

        # Find safe unvisited cells to explore
        safe_unvisited = self.find_safe_unvisited_cells()

        if safe_unvisited:
            # Choose the closest safe unvisited cell
            closest_cell = min(safe_unvisited,
                               key=lambda pos: abs(pos[0] - current_pos[0]) + abs(pos[1] - current_pos[1]))

            path = self.find_path_to_target(closest_cell)
            if path:
                next_pos = path[0]
                return self.get_move_action(current_pos, next_pos)

        # If no definitively safe moves, avoid known dangers and pick best option
        adjacent_cells = self.get_adjacent_cells(current_pos)
        safe_adjacent = []
        risky_adjacent = []

        for adj_pos in adjacent_cells:
            if adj_pos in self.visited:
                continue

            # Definitely dangerous
            if (self.knowledge_base[adj_pos]['pit'] == True or
                    self.knowledge_base[adj_pos]['wumpus'] == True):
                continue

            # Definitely safe
            if (self.knowledge_base[adj_pos]['pit'] == False and
                    (self.knowledge_base[adj_pos]['wumpus'] == False or not self.world.wumpus_alive)):
                safe_adjacent.append(adj_pos)
            # Unknown but not definitely dangerous
            elif (self.knowledge_base[adj_pos]['pit'] is None or
                  self.knowledge_base[adj_pos]['wumpus'] is None):
                risky_adjacent.append(adj_pos)

        # Prefer safe moves
        if safe_adjacent:
            next_pos = safe_adjacent[0]
            return self.get_move_action(current_pos, next_pos)

        # If must take risk, prefer cells with less risk indicators
        if risky_adjacent:
            # Sort by risk level (cells with fewer breeze/stench indicators around them)
            def risk_score(pos):
                risk = 0
                for visited_pos in self.visited:
                    if pos in self.get_adjacent_cells(visited_pos):
                        # Check if this visited position had dangerous percepts
                        if self.had_breeze_at(visited_pos):
                            risk += 1
                        if self.had_stench_at(visited_pos):
                            risk += 1
                return risk

            safest_risky = min(risky_adjacent, key=risk_score)
            return self.get_move_action(current_pos, safest_risky)

        # Last resort - go back to a safe visited cell
        visited_adjacent = [pos for pos in adjacent_cells if pos in self.visited]
        if visited_adjacent:
            return self.get_move_action(current_pos, visited_adjacent[0])

        return "turn_right"  # Absolute fallback

    def had_breeze_at(self, pos):
        """Check if we experienced breeze at this position"""
        if pos in self.percept_history:
            return self.percept_history[pos].get('breeze', False)
        return False

    def had_stench_at(self, pos):
        """Check if we experienced stench at this position"""
        if pos in self.percept_history:
            return self.percept_history[pos].get('stench', False)
        return False

    def can_shoot_target(self, from_pos, target_pos):
        """Check if we can shoot target from current position"""
        fx, fy = from_pos
        tx, ty = target_pos

        # Must be in same row or column
        if fx != tx and fy != ty:
            return False

        # Check if path is clear (no walls, within bounds)
        if fx == tx:  # Same row, shooting horizontally
            start_y, end_y = min(fy, ty), max(fy, ty)
            for y in range(start_y + 1, end_y):
                if (fx, y) == target_pos:
                    continue
                # Arrow path is clear in this simple world
            return True
        else:  # Same column, shooting vertically
            start_x, end_x = min(fx, tx), max(fx, tx)
            for x in range(start_x + 1, end_x):
                if (x, fy) == target_pos:
                    continue
                # Arrow path is clear in this simple world
            return True

    def get_shooting_direction(self, from_pos, target_pos):
        """Get direction to shoot at target"""
        fx, fy = from_pos
        tx, ty = target_pos

        if tx < fx:
            return "up"
        elif tx > fx:
            return "down"
        elif ty < fy:
            return "left"
        elif ty > fy:
            return "right"
        return self.world.agent_dir


class WumpusGameVisualization:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Wumpus World - Logic-Based Agent")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.title_font = pygame.font.Font(None, 48)
        self.button_font = pygame.font.Font(None, 32)

        self.world = WumpusWorld()
        self.agent = LogicBasedAgent(self.world)
        self.auto_play = True
        self.move_delay = 500  # milliseconds
        self.last_move_time = 0
        self.game_state = "playing"  # "playing", "win", "lose", "menu"

    def draw_grid(self):
        for i in range(GRID_SIZE + 1):
            # Vertical lines
            pygame.draw.line(self.screen, BLACK,
                             (i * CELL_SIZE, 0),
                             (i * CELL_SIZE, WINDOW_SIZE), 2)
            # Horizontal lines
            pygame.draw.line(self.screen, BLACK,
                             (0, i * CELL_SIZE),
                             (WINDOW_SIZE, i * CELL_SIZE), 2)

    def draw_cell_contents(self, row, col):
        x = col * CELL_SIZE
        y = row * CELL_SIZE
        cell = self.world.world[row][col]

        # Draw cell background based on safety knowledge
        if (row, col) in self.agent.visited:
            pygame.draw.rect(self.screen, LIGHT_GRAY, (x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4))
        elif (row, col) in self.agent.safe_cells:
            pygame.draw.rect(self.screen, (200, 255, 200), (x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4))

        # Draw pit
        if cell["pit"]:
            pygame.draw.circle(self.screen, BLACK, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), 30)
            pygame.draw.circle(self.screen, WHITE, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), 25)
            text = self.font.render("PIT", True, BLACK)
            text_rect = text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
            self.screen.blit(text, text_rect)

        # Draw wumpus
        if cell["wumpus"]:
            color = RED if self.world.wumpus_alive else GRAY
            # Body
            pygame.draw.circle(self.screen, color, (x + CELL_SIZE // 2, y + CELL_SIZE // 2 + 10), 25)
            # Head
            pygame.draw.circle(self.screen, color, (x + CELL_SIZE // 2, y + CELL_SIZE // 2 - 15), 15)
            # Eyes
            pygame.draw.circle(self.screen, BLACK, (x + CELL_SIZE // 2 - 8, y + CELL_SIZE // 2 - 18), 3)
            pygame.draw.circle(self.screen, BLACK, (x + CELL_SIZE // 2 + 8, y + CELL_SIZE // 2 - 18), 3)

            if not self.world.wumpus_alive:
                # Draw X over dead wumpus
                pygame.draw.line(self.screen, BLACK, (x + 20, y + 20), (x + CELL_SIZE - 20, y + CELL_SIZE - 20), 3)
                pygame.draw.line(self.screen, BLACK, (x + CELL_SIZE - 20, y + 20), (x + 20, y + CELL_SIZE - 20), 3)

        # Draw gold
        if cell["gold"]:
            pygame.draw.circle(self.screen, YELLOW, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), 20)
            pygame.draw.circle(self.screen, ORANGE, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), 15)
            text = self.font.render("GOLD", True, BLACK)
            text_rect = text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
            self.screen.blit(text, text_rect)

    def draw_agent(self):
        row, col = self.world.agent_pos
        x = col * CELL_SIZE + CELL_SIZE // 2
        y = row * CELL_SIZE + CELL_SIZE // 2

        # Agent body - layered circles for depth
        # Shadow/base
        pygame.draw.circle(self.screen, (50, 50, 100), (x + 2, y + 2), 20)
        # Main body
        pygame.draw.circle(self.screen, (70, 130, 180), (x, y), 18)
        # Inner highlight
        pygame.draw.circle(self.screen, (100, 160, 220), (x - 3, y - 3), 12)
        # Core
        pygame.draw.circle(self.screen, (120, 180, 240), (x - 5, y - 5), 8)

        # Agent face/eyes
        pygame.draw.circle(self.screen, WHITE, (x - 6, y - 4), 3)
        pygame.draw.circle(self.screen, WHITE, (x + 4, y - 4), 3)
        pygame.draw.circle(self.screen, BLACK, (x - 6, y - 4), 2)
        pygame.draw.circle(self.screen, BLACK, (x + 4, y - 4), 2)

        # Direction indicator - enhanced arrow
        arrow_length = 25
        arrow_width = 8
        arrow_color = (255, 255, 100)  # Bright yellow
        arrow_outline = (200, 200, 0)  # Darker yellow for outline

        # Calculate arrow points based on direction
        if self.world.agent_dir == "up":
            # Main arrow body
            arrow_points = [
                (x, y - arrow_length),  # tip
                (x - arrow_width, y - 10),  # left wing
                (x - 4, y - 10),  # left body
                (x - 4, y + 5),  # left body bottom
                (x + 4, y + 5),  # right body bottom
                (x + 4, y - 10),  # right body
                (x + arrow_width, y - 10)  # right wing
            ]
            glow_center = (x, y - 15)
        elif self.world.agent_dir == "down":
            arrow_points = [
                (x, y + arrow_length),
                (x - arrow_width, y + 10),
                (x - 4, y + 10),
                (x - 4, y - 5),
                (x + 4, y - 5),
                (x + 4, y + 10),
                (x + arrow_width, y + 10)
            ]
            glow_center = (x, y + 15)
        elif self.world.agent_dir == "left":
            arrow_points = [
                (x - arrow_length, y),
                (x - 10, y - arrow_width),
                (x - 10, y - 4),
                (x + 5, y - 4),
                (x + 5, y + 4),
                (x - 10, y + 4),
                (x - 10, y + arrow_width)
            ]
            glow_center = (x - 15, y)
        elif self.world.agent_dir == "right":
            arrow_points = [
                (x + arrow_length, y),
                (x + 10, y - arrow_width),
                (x + 10, y - 4),
                (x - 5, y - 4),
                (x - 5, y + 4),
                (x + 10, y + 4),
                (x + 10, y + arrow_width)
            ]
            glow_center = (x + 15, y)

        # Draw arrow glow effect
        for i in range(3, 0, -1):
            glow_color = (255, 255, 100, 60 // i)
            glow_surface = pygame.Surface((i * 6, i * 6), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, glow_color, (i * 3, i * 3), i * 3)
            self.screen.blit(glow_surface, (glow_center[0] - i * 3, glow_center[1] - i * 3))

        # Draw arrow outline
        pygame.draw.polygon(self.screen, arrow_outline, arrow_points)
        # Draw arrow fill
        inner_points = [(px + (1 if px < x else -1 if px > x else 0),
                         py + (1 if py < y else -1 if py > y else 0)) for px, py in arrow_points]
        pygame.draw.polygon(self.screen, arrow_color, inner_points)

        # Gold indicator - enhanced
        if self.world.has_gold:
            # Gold aura
            for i in range(3):
                gold_surface = pygame.Surface((20 + i * 4, 20 + i * 4), pygame.SRCALPHA)
                gold_color = (255, 215, 0, 100 - i * 30)
                pygame.draw.circle(gold_surface, gold_color, (10 + i * 2, 10 + i * 2), 10 + i * 2)
                self.screen.blit(gold_surface, (x - 10 - i * 2, y - 35 - i * 2))

            # Main gold coin
            pygame.draw.circle(self.screen, (255, 215, 0), (x, y - 30), 12)
            pygame.draw.circle(self.screen, (255, 235, 59), (x, y - 30), 10)
            pygame.draw.circle(self.screen, (255, 215, 0), (x, y - 30), 8)

            # Gold shine effect
            pygame.draw.circle(self.screen, (255, 255, 200), (x - 3, y - 33), 3)

            # Dollar sign
            font_small = pygame.font.Font(None, 16)
            dollar_text = font_small.render("$", True, (180, 140, 0))
            dollar_rect = dollar_text.get_rect(center=(x, y - 30))
            self.screen.blit(dollar_text, dollar_rect)

        # Draw dead agent overlay if game over and lost
        if self.world.game_over and self.world.game_state == "lose":
            # Red X with glow effect
            for width in range(5, 2, -1):
                color_intensity = 255 - (5 - width) * 50
                pygame.draw.line(self.screen, (color_intensity, 0, 0),
                                 (x - 20, y - 20), (x + 20, y + 20), width)
                pygame.draw.line(self.screen, (color_intensity, 0, 0),
                                 (x + 20, y - 20), (x - 20, y + 20), width)

            # Skull emoji effect (simple representation)
            pygame.draw.circle(self.screen, (200, 200, 200), (x, y - 8), 6)
            pygame.draw.circle(self.screen, BLACK, (x - 3, y - 10), 2)
            pygame.draw.circle(self.screen, BLACK, (x + 3, y - 10), 2)
            pygame.draw.circle(self.screen, BLACK, (x, y - 6), 1)

        # Agent name tag (optional - can be removed if too cluttered)
        name_font = pygame.font.Font(None, 14)
        name_text = name_font.render("AGENT", True, (40, 40, 40))
        name_rect = name_text.get_rect(center=(x, y + 35))
        # Name background
        pygame.draw.rect(self.screen, (255, 255, 255, 180),
                         (name_rect.x - 2, name_rect.y - 1, name_rect.width + 4, name_rect.height + 2))
        pygame.draw.rect(self.screen, (100, 100, 100),
                         (name_rect.x - 2, name_rect.y - 1, name_rect.width + 4, name_rect.height + 2), 1)
        self.screen.blit(name_text, name_rect)

    def draw_percepts(self):
        row, col = self.world.agent_pos
        x = col * CELL_SIZE
        y = row * CELL_SIZE
        percepts = self.world.percepts

        percept_y = y + 5
        if percepts["stench"]:
            text = self.small_font.render("STENCH", True, RED)
            self.screen.blit(text, (x + 5, percept_y))
            percept_y += 15

        if percepts["breeze"]:
            text = self.small_font.render("BREEZE", True, BLUE)
            self.screen.blit(text, (x + 5, percept_y))
            percept_y += 15

        if percepts["glitter"]:
            text = self.small_font.render("GLITTER", True, YELLOW)
            self.screen.blit(text, (x + 5, percept_y))
            percept_y += 15

        if percepts["bump"]:
            text = self.small_font.render("BUMP", True, PURPLE)
            self.screen.blit(text, (x + 5, percept_y))

        if percepts["scream"]:
            text = self.font.render("SCREAM!", True, RED)
            self.screen.blit(text, (WINDOW_SIZE // 2 - 40, 10))

    def draw_info_panel(self):
        info_y = WINDOW_SIZE + 5
        panel_height = INFO_HEIGHT - 10

        # Draw background panel with border
        pygame.draw.rect(self.screen, (245, 245, 245), (5, info_y, WINDOW_SIZE - 10, panel_height))
        pygame.draw.rect(self.screen, (100, 100, 100), (5, info_y, WINDOW_SIZE - 10, panel_height), 2)

        # Title bar
        pygame.draw.rect(self.screen, (70, 130, 180), (10, info_y + 5, WINDOW_SIZE - 20, 30))
        title_text = self.font.render("WUMPUS WORLD - LOGIC AGENT STATUS", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_SIZE // 2, info_y + 20))
        self.screen.blit(title_text, title_rect)

        # Game Status Section
        status_y = info_y + 45
        pygame.draw.rect(self.screen, (220, 240, 255), (15, status_y, WINDOW_SIZE - 30, 25))
        pygame.draw.rect(self.screen, (150, 150, 150), (15, status_y, WINDOW_SIZE - 30, 25), 1)

        status_text = f"Score: {self.world.score:4d} | Position: {self.world.agent_pos} | Direction: {self.world.agent_dir.upper()}"
        status_surface = self.font.render(status_text, True, (20, 20, 20))
        self.screen.blit(status_surface, (20, status_y + 5))

        # Agent Status Section
        agent_y = status_y + 30
        pygame.draw.rect(self.screen, (255, 248, 220), (15, agent_y, WINDOW_SIZE - 30, 25))
        pygame.draw.rect(self.screen, (150, 150, 150), (15, agent_y, WINDOW_SIZE - 30, 25), 1)

        # Gold Status
        gold_status = "YES" if self.world.has_gold else "NO"
        gold_color = (34, 139, 34) if self.world.has_gold else (220, 20, 60)
        gold_bg_color = (240, 255, 240) if self.world.has_gold else (255, 240, 240)

        # Draw gold status box
        pygame.draw.rect(self.screen, gold_bg_color, (20, agent_y + 3, 70, 19))
        pygame.draw.rect(self.screen, gold_color, (20, agent_y + 3, 70, 19), 1)
        gold_text = self.small_font.render(f"GOLD: {gold_status}", True, gold_color)
        self.screen.blit(gold_text, (23, agent_y + 6))

        # Arrow Status
        arrow_status = "YES" if self.world.has_arrow else "NO"
        arrow_color = (34, 139, 34) if self.world.has_arrow else (220, 20, 60)
        arrow_bg_color = (240, 255, 240) if self.world.has_arrow else (255, 240, 240)

        # Draw arrow status box
        pygame.draw.rect(self.screen, arrow_bg_color, (100, agent_y + 3, 110, 19))
        pygame.draw.rect(self.screen, arrow_color, (100, agent_y + 3, 110, 19), 1)
        arrow_text = self.small_font.render(f"ARROW: {arrow_status}", True, arrow_color)
        self.screen.blit(arrow_text, (103, agent_y + 6))

        # Wumpus Status
        wumpus_status = "ALIVE" if self.world.wumpus_alive else "DEAD"
        wumpus_color = (220, 20, 60) if self.world.wumpus_alive else (34, 139, 34)
        wumpus_bg_color = (255, 240, 240) if self.world.wumpus_alive else (240, 255, 240)

        # Draw wumpus status box (with 30px gap from arrow box)
        pygame.draw.rect(self.screen, wumpus_bg_color, (240, agent_y + 3, 120, 19))
        pygame.draw.rect(self.screen, wumpus_color, (240, agent_y + 3, 120, 19), 1)
        wumpus_text = self.small_font.render(f"WUMPUS: {wumpus_status}", True, wumpus_color)
        self.screen.blit(wumpus_text, (243, agent_y + 6))

        # Percepts Section
        percept_y = agent_y + 30
        pygame.draw.rect(self.screen, (240, 255, 240), (15, percept_y, WINDOW_SIZE - 30, 25))
        pygame.draw.rect(self.screen, (150, 150, 150), (15, percept_y, WINDOW_SIZE - 30, 25), 1)

        active_percepts = [k.upper() for k, v in self.world.percepts.items() if v]
        percept_text = f"Percepts: {', '.join(active_percepts) if active_percepts else 'NONE'}"
        percept_surface = self.font.render(percept_text, True, (20, 20, 20))
        self.screen.blit(percept_surface, (20, percept_y + 5))

        # Enhanced Controls Section
        control_y = percept_y + 30

        # Create a nice container for the controls
        controls_bg_rect = pygame.Rect(15, control_y, WINDOW_SIZE - 30, 25)
        pygame.draw.rect(self.screen, (230, 240, 250), controls_bg_rect, border_radius=4)
        pygame.draw.rect(self.screen, (100, 100, 100), controls_bg_rect, 1, border_radius=4)

        # Create a key style for the control labels
        def draw_key(key, text, x_offset):
            key_rect = pygame.Rect(x_offset, control_y + 5, 25, 18)
            pygame.draw.rect(self.screen, (200, 200, 200), key_rect, border_radius=3)
            pygame.draw.rect(self.screen, (100, 100, 100), key_rect, 1, border_radius=3)
            key_surface = self.small_font.render(key, True, (40, 40, 40))
            self.screen.blit(key_surface, (x_offset + 8, control_y + 7))

            action_surface = self.small_font.render(text, True, (60, 60, 60))
            self.screen.blit(action_surface, (x_offset + 30, control_y + 7))

        # Draw the control keys with nice styling
        draw_key("R", "Reset", 25)
        draw_key("Q", "Quit", 125)  # Positioned with 100px gap between controls

        # Game Over Status (if applicable)
        if self.world.game_over:
            game_over_y = control_y + 25
            status_color = (34, 139, 34) if self.world.game_state == "win" else (220, 20, 60)
            bg_color = (240, 255, 240) if self.world.game_state == "win" else (255, 240, 240)

            pygame.draw.rect(self.screen, bg_color, (15, game_over_y, WINDOW_SIZE - 30, 25))
            pygame.draw.rect(self.screen, status_color, (15, game_over_y, WINDOW_SIZE - 30, 25), 2)

            # Use text symbols instead of emojis for better compatibility
            game_text = f"{'VICTORY! ★' if self.world.game_state == 'win' else 'DEFEATED! ☠'} Final Score: {self.world.score}"
            game_surface = self.font.render(game_text, True, status_color)
            game_rect = game_surface.get_rect(center=(WINDOW_SIZE // 2, game_over_y + 12))
            self.screen.blit(game_surface, game_rect)

    def draw_game_over_screen(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Game result text
        if self.world.game_state == "win":
            title = self.title_font.render("VICTORY!", True, GREEN)
            subtitle = self.font.render(f"Final Score: {self.world.score}", True, YELLOW)
        else:
            title = self.title_font.render("GAME OVER", True, RED)
            subtitle = self.font.render(f"Final Score: {self.world.score}", True, YELLOW)

        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)

        # Draw buttons
        pygame.draw.rect(self.screen, DARK_GREEN, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50, 140, 50))
        pygame.draw.rect(self.screen, DARK_RED, (SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT // 2 + 50, 140, 50))

        play_again = self.button_font.render("Play Again", True, WHITE)
        quit_game = self.button_font.render("Quit", True, WHITE)

        self.screen.blit(play_again, (SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(quit_game, (SCREEN_WIDTH // 2 + 50, SCREEN_HEIGHT // 2 + 60))

        # Instructions
        instructions = self.font.render("Press 'R' to restart or 'Q' to quit", True, WHITE)
        self.screen.blit(instructions, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT - 50))

    def execute_action(self, action):
        if action == "move":
            self.world.move_forward()
        elif action == "turn_left":
            self.world.turn_left()
        elif action == "turn_right":
            self.world.turn_right()
        elif action == "shoot":
            self.world.shoot_arrow()
        elif action == "grab":
            self.world.grab_gold()
        elif action == "climb":
            if self.world.agent_pos == (0, 0) and self.world.has_gold:
                self.world.is_game_over()  # This will set game over state
                return

        # Check for death
        self.world.is_game_over()

    def reset_game(self):
        self.world.reset()
        self.agent = LogicBasedAgent(self.world)
        self.auto_play = True
        self.game_state = "playing"

    def run(self):
        running = True

        while running:
            current_time = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_r:
                        # Reset game
                        self.reset_game()
                    elif event.key == pygame.K_SPACE:
                        # Toggle auto play
                        if not self.world.game_over:
                            self.auto_play = not self.auto_play
                    elif event.key == pygame.K_RETURN:
                        # Single step
                        if not self.world.game_over:
                            action = self.agent.choose_action()
                            self.execute_action(action)
                elif event.type == pygame.MOUSEBUTTONDOWN and self.world.game_over:
                    # Check if play again button clicked
                    mouse_pos = pygame.mouse.get_pos()
                    if SCREEN_WIDTH // 2 - 150 <= mouse_pos[0] <= SCREEN_WIDTH // 2 - 10 and SCREEN_HEIGHT // 2 + 50 <= \
                            mouse_pos[1] <= SCREEN_HEIGHT // 2 + 100:
                        self.reset_game()
                    elif SCREEN_WIDTH // 2 + 10 <= mouse_pos[
                        0] <= SCREEN_WIDTH // 2 + 150 and SCREEN_HEIGHT // 2 + 50 <= mouse_pos[
                        1] <= SCREEN_HEIGHT // 2 + 100:
                        running = False

            # Auto play logic
            if self.auto_play and not self.world.game_over and current_time - self.last_move_time > self.move_delay:
                action = self.agent.choose_action()
                self.execute_action(action)
                self.last_move_time = current_time

            # Drawing
            self.screen.fill(WHITE)

            # Draw game elements if playing
            if not self.world.game_over or self.game_state != "menu":
                # Draw grid and contents
                for row in range(GRID_SIZE):
                    for col in range(GRID_SIZE):
                        self.draw_cell_contents(row, col)

                self.draw_grid()
                self.draw_agent()
                self.draw_percepts()
                self.draw_info_panel()

            # Draw game over screen if game ended
            if self.world.game_over:
                self.draw_game_over_screen()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = WumpusGameVisualization()
    game.run()