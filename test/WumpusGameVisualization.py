import sys
import pygame

from test import LogicBasedAgent
from wumpus_world import WumpusWorld

# Constants
GRID_SIZE = 4
CELL_SIZE = 120
WINDOW_SIZE = GRID_SIZE * CELL_SIZE
INFO_HEIGHT = 200
WINDOW_HEIGHT = WINDOW_SIZE + INFO_HEIGHT

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

class WumpusGameVisualization:
    def _init_(self):
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_HEIGHT))
        pygame.display.set_caption("Wumpus World - Logic-Based Agent")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        self.world = WumpusWorld()
        self.agent = LogicBasedAgent(self.world)
        self.game_over = False
        self.auto_play = False
        self.move_delay = 500  # milliseconds
        self.last_move_time = 0

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

        # Agent body
        pygame.draw.circle(self.screen, BLUE, (x, y), 15)

        # Direction indicator
        if self.world.agent_dir == "up":
            pygame.draw.polygon(self.screen, WHITE, [(x, y - 10), (x - 5, y), (x + 5, y)])
        elif self.world.agent_dir == "down":
            pygame.draw.polygon(self.screen, WHITE, [(x, y + 10), (x - 5, y), (x + 5, y)])
        elif self.world.agent_dir == "left":
            pygame.draw.polygon(self.screen, WHITE, [(x - 10, y), (x, y - 5), (x, y + 5)])
        elif self.world.agent_dir == "right":
            pygame.draw.polygon(self.screen, WHITE, [(x + 10, y), (x, y - 5), (x, y + 5)])

        # Show if agent has gold
        if self.world.has_gold:
            pygame.draw.circle(self.screen, YELLOW, (x, y - 25), 8)

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
        info_y = WINDOW_SIZE + 10

        # Game status
        status_text = f"Score: {self.world.score} | Position: {self.world.agent_pos} | Direction: {self.world.agent_dir}"
        status_surface = self.font.render(status_text, True, BLACK)
        self.screen.blit(status_surface, (10, info_y))

        # Agent status
        agent_status = f"Has Gold: {self.world.has_gold} | Has Arrow: {self.world.has_arrow} | Wumpus Alive: {self.world.wumpus_alive}"
        agent_surface = self.font.render(agent_status, True, BLACK)
        self.screen.blit(agent_surface, (10, info_y + 25))

        # Controls
        controls1 = "Controls: SPACE=Auto/Manual, ENTER=Single Step, R=Reset, Q=Quit"
        controls_surface = self.small_font.render(controls1, True, BLACK)
        self.screen.blit(controls_surface, (10, info_y + 55))

        # Current percepts
        percept_text = f"Percepts: {', '.join([k for k, v in self.world.percepts.items() if v])}"
        percept_surface = self.font.render(percept_text, True, BLACK)
        self.screen.blit(percept_surface, (10, info_y + 80))

        # Game mode
        mode_text = f"Mode: {'AUTO' if self.auto_play else 'MANUAL'}"
        mode_surface = self.font.render(mode_text, True, GREEN if self.auto_play else RED)
        self.screen.blit(mode_surface, (10, info_y + 105))

        # Game over status
        game_status = self.world.is_game_over()
        if game_status != "continue":
            status_color = GREEN if game_status == "win" else RED
            game_text = f"Game Over: {'YOU WIN!' if game_status == 'win' else 'YOU LOSE!'}"
            game_surface = self.font.render(game_text, True, status_color)
            self.screen.blit(game_surface, (10, info_y + 130))

    # In the WumpusGameVisualization class
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
                return "win"

        # Check for death and apply penalty only once
        result = self.world.is_game_over()
        if result == "lose":
            self.world.score -= 1000  # Apply death penalty here
            return result

        return result

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
                        self.world = WumpusWorld()
                        self.agent = LogicBasedAgent(self.world)
                        self.game_over = False
                    elif event.key == pygame.K_SPACE:
                        # Toggle auto play
                        self.auto_play = not self.auto_play
                    elif event.key == pygame.K_RETURN:
                        # Single step
                        if not self.game_over:
                            action = self.agent.choose_action()
                            result = self.execute_action(action)
                            if result != "continue":
                                self.game_over = True

            # Auto play logic
            if self.auto_play and not self.game_over and current_time - self.last_move_time > self.move_delay:
                action = self.agent.choose_action()
                result = self.execute_action(action)
                if result != "continue":
                    self.game_over = True
                self.last_move_time = current_time

            # Drawing
            self.screen.fill(WHITE)

            # Draw grid and contents
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    self.draw_cell_contents(row, col)

            self.draw_grid()
            self.draw_agent()
            self.draw_percepts()
            self.draw_info_panel()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = WumpusGameVisualization()
    game.run()