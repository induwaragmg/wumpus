
from collections import deque


class LogicBasedAgent:
    def _init_(self, world):
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

    def find_safe_unvisited_cells(self):
        safe_unvisited = []
        for pos in self.safe_cells:
            if not self.knowledge_base[pos]['visited']:
                safe_unvisited.append(pos)
        return safe_unvisited

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

    def get_percepts_at_position(self, pos):
        """Get what the percepts were at a given position"""
        if pos in self.percept_history:
            return self.percept_history[pos]
        return {'breeze': False, 'stench': False}

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
        return self.world.agent_dir

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


