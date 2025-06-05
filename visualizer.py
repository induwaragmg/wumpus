import pygame
import time
from wumpus_world import WumpusWorld
from logic_agent import LogicAgent

# Constants
GRID_SIZE = 4
CELL_SIZE = 120
TITLE_BAR_HEIGHT = 40
STATUS_BAR_HEIGHT = 80
GRID_WIDTH = CELL_SIZE * GRID_SIZE
GRID_HEIGHT = CELL_SIZE * GRID_SIZE
WINDOW_WIDTH = GRID_WIDTH
WINDOW_HEIGHT = TITLE_BAR_HEIGHT + GRID_HEIGHT + STATUS_BAR_HEIGHT

# Color definitions
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

WHITE = hex_to_rgb("#ffffff")
BLACK = hex_to_rgb("#000000")
GRAY = hex_to_rgb("#c8c8c8")
RED = hex_to_rgb("#f82727")
BLUE = hex_to_rgb("#0000ff")
GOLD = hex_to_rgb("#f6f166")
GREEN = hex_to_rgb("#a5e790")
DARK_GREEN = hex_to_rgb("#65bf4a")
BROWN = hex_to_rgb("#f8be98")
DARK_BROWN = hex_to_rgb("#3b1a00")
LIGHT_BROWN = hex_to_rgb("#e9dfd7")
HEADER_LIGHT_BROWN = hex_to_rgb("#EBAD7E")
TEXT_LIGHT_BROWN = hex_to_rgb("#C95C08")
BUTTON_GREEN = hex_to_rgb("#33b80a")

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Wumpus World - Logic-Based Agent")
font = pygame.font.SysFont(None, 32)
large_font = pygame.font.SysFont(None, 60)
clock = pygame.time.Clock()
FPS = 5

# Load assets
try:
    wumpus_img = pygame.transform.scale(pygame.image.load("assets/wumpus.png"), (80, 80))
    wumpus_dead_img = pygame.transform.scale(pygame.image.load("assets/dead_wumpus.png"), (80, 80))
    pit_img = pygame.transform.scale(pygame.image.load("assets/pit.png"), (80, 80))
    gold_img = pygame.transform.scale(pygame.image.load("assets/gold.png"), (50, 50))
    agent_imgs = {
        "up": pygame.transform.scale(pygame.image.load("assets/agent_up.png"), (80, 80)),
        "down": pygame.transform.scale(pygame.image.load("assets/agent_down.png"), (80, 80)),
        "left": pygame.transform.scale(pygame.image.load("assets/agent_left.png"), (80, 80)),
        "right": pygame.transform.scale(pygame.image.load("assets/agent_right.png"), (80, 80)),
    }
except Exception as e:
    print("Asset loading failed:", e)
    wumpus_img = wumpus_dead_img = pit_img = gold_img = None
    agent_imgs = {}

def draw_world(world, agent_pos, percepts, score, safe_cells=None):
    """Draws the game world, agent, and percept indicators."""
    screen.fill(BROWN)

    # Draw title bar
    pygame.draw.rect(screen, DARK_BROWN, (0, 0, WINDOW_WIDTH, TITLE_BAR_HEIGHT))
    title_surface = font.render("WUMPUS WORLD", True, LIGHT_BROWN)
    screen.blit(title_surface, (WINDOW_WIDTH // 2 - title_surface.get_width() // 2, 10))

    # Draw grid and contents
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            x, y = j * CELL_SIZE, i * CELL_SIZE + TITLE_BAR_HEIGHT
            cell = world.world[i][j]

            if safe_cells and (i, j) in safe_cells:
                pygame.draw.rect(screen, GREEN, (x+2, y+2, CELL_SIZE-4, CELL_SIZE-4))

            pygame.draw.rect(screen, DARK_BROWN, (x, y, CELL_SIZE, CELL_SIZE), 1)

            if cell["pit"] and pit_img:
                screen.blit(pit_img, (x + 20, y + 20))
            if cell["wumpus"]:
                image = wumpus_img if world.wumpus_alive else wumpus_dead_img
                if image:
                    screen.blit(image, (x + 20, y + 20))
            if cell["gold"] and gold_img:
                screen.blit(gold_img, (x + 35, y + 35))

    # Draw agent
    ax, ay = agent_pos
    if world.agent_dir in agent_imgs:
        screen.blit(agent_imgs[world.agent_dir], (
            ay * CELL_SIZE + (CELL_SIZE - agent_imgs[world.agent_dir].get_width()) // 2,
            ax * CELL_SIZE + TITLE_BAR_HEIGHT + (CELL_SIZE - agent_imgs[world.agent_dir].get_height()) // 2
        ))

    # Draw percepts and score
    pygame.draw.rect(screen, BROWN, (0, TITLE_BAR_HEIGHT + GRID_HEIGHT, WINDOW_WIDTH, STATUS_BAR_HEIGHT))
    status_y = TITLE_BAR_HEIGHT + GRID_HEIGHT + 15
    x_offset = 10

    for label in ['breeze', 'stench', 'glitter']:
        value = percepts[label]
        color = DARK_GREEN if value else BLACK
        text_surface = font.render(f"{label.capitalize()}: {value}", True, color)
        screen.blit(text_surface, (x_offset, status_y))
        x_offset += text_surface.get_width() + 15

    score_surface = font.render(f"Score: {score}", True, BLUE)
    screen.blit(score_surface, (10, status_y + 30))

    pygame.display.flip()
    clock.tick(FPS)

def show_end_screen(message, score):
    """Displays end screen with result, score, and option to play again or quit."""
    # Simulate blur background
    background = screen.copy()
    scaled = pygame.transform.smoothscale(background, (WINDOW_WIDTH // 10, WINDOW_HEIGHT // 10))
    blurred = pygame.transform.smoothscale(scaled, (WINDOW_WIDTH, WINDOW_HEIGHT))
    screen.blit(blurred, (0, 0))

    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(160)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    # Victory or Defeat message
    result_text = large_font.render(message, True, HEADER_LIGHT_BROWN)
    screen.blit(result_text, (WINDOW_WIDTH//2 - result_text.get_width()//2, GRID_HEIGHT//2 - 60))

    score_text = font.render(f"Final Score: {score}", True, GOLD)
    screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, GRID_HEIGHT//2))

    # Buttons
    button_font = pygame.font.SysFont(None, 28)
    play_text = button_font.render("Play Again", True, WHITE)
    quit_text = button_font.render("Quit", True, WHITE)

    play_btn = pygame.Rect(WINDOW_WIDTH//2 - 135, GRID_HEIGHT//2 + 80, 125, 35)
    quit_btn = pygame.Rect(WINDOW_WIDTH//2 + 30, GRID_HEIGHT//2 + 80, 100, 35)

    pygame.draw.rect(screen, TEXT_LIGHT_BROWN, play_btn, border_radius=32)
    pygame.draw.rect(screen, TEXT_LIGHT_BROWN, quit_btn, border_radius=32)
    screen.blit(play_text, (play_btn.x + 10, play_btn.y + 8))
    screen.blit(quit_text, (quit_btn.x + 25, quit_btn.y + 8))

    pygame.display.flip()

    # Event handling loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q: pygame.quit(); return False
                if event.key == pygame.K_r: return True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.collidepoint(event.pos): return True
                if quit_btn.collidepoint(event.pos): pygame.quit(); return False

def run_visual_simulation():
    """Main simulation loop: creates world, runs agent, and visualizes steps."""
    while True:
        world = WumpusWorld()
        agent = LogicAgent(world, draw_callback=draw_world)

        draw_world(world, agent.position, world.percepts, agent.score, safe_cells=agent.safe_cells)
        time.sleep(1)

        while world.is_game_over() == "continue":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); return

            agent.update_knowledge()
            agent.act()
            draw_world(world, agent.position, world.percepts, agent.score, safe_cells=agent.safe_cells)
            time.sleep(0.8)

            next_cell = agent.choose_next_move()
            if next_cell:
                agent.move_to(next_cell)
                draw_world(world, agent.position, world.percepts, agent.score, safe_cells=agent.safe_cells)
            else:
                print("No more safe moves.")
                break

        result = world.is_game_over()
        outcome = "VICTORY!" if result == "win" else "DEFEAT!" if result == "lose" else "Game Over"
        if not show_end_screen(outcome, agent.score):
            break

if __name__ == "__main__":
    run_visual_simulation()
