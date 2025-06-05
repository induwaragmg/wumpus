# import pygame
# import time
# from wumpus_world import WumpusWorld
# from logic_agent import LogicAgent

# # Grid & window dimensions
# GRID_ROWS = 4
# GRID_COLS = 4
# CELL_SIZE = 120
# GRID_WIDTH = GRID_COLS * CELL_SIZE
# GRID_HEIGHT = GRID_ROWS * CELL_SIZE
# TITLE_BAR_HEIGHT = 40
# STATUS_BAR_HEIGHT = 60
# WINDOW_WIDTH = GRID_WIDTH
# WINDOW_HEIGHT = TITLE_BAR_HEIGHT + GRID_HEIGHT + STATUS_BAR_HEIGHT

# # Helper to convert hex
# def hex_to_rgb(hex_color):
#     hex_color = hex_color.lstrip("#")
#     return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# # Colors
# BROWN        = hex_to_rgb("#f8be98")
# BLACK        = hex_to_rgb("#000000")
# GRAY         = hex_to_rgb("#c8c8c8")
# RED          = hex_to_rgb("#ff0000")
# GOLD         = hex_to_rgb("#ffd700")
# BLUE         = hex_to_rgb("#0000ff")
# LIGHT_BROWN  = hex_to_rgb("#e9dfd7")
# DARK_BROWN   = hex_to_rgb("#3b1a00")
# GREEN        = hex_to_rgb("#a5e790")
# DARK_GREEN   = hex_to_rgb("#65bf4a")

# # Pygame setup
# pygame.init()
# screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
# pygame.display.set_caption("Wumpus World")
# font = pygame.font.SysFont(None, 30)
# clock = pygame.time.Clock()
# FPS = 5

# # Load images
# try:
#     wumpus_img = pygame.transform.scale(pygame.image.load("assets/wumpus.png"), (80, 80))
#     wumpus_dead_img = pygame.transform.scale(pygame.image.load("assets/dead_wumpus.png"), (80, 80))
#     pit_img = pygame.transform.scale(pygame.image.load("assets/pit.png"), (80, 80))
#     gold_img = pygame.transform.scale(pygame.image.load("assets/gold.png"), (50, 50))
#     agent_imgs = {
#         "up": pygame.transform.scale(pygame.image.load("assets/agent_up.png"), (80, 80)),
#         "down": pygame.transform.scale(pygame.image.load("assets/agent_down.png"), (80, 80)),
#         "left": pygame.transform.scale(pygame.image.load("assets/agent_left.png"), (80, 80)),
#         "right": pygame.transform.scale(pygame.image.load("assets/agent_right.png"), (80, 80)),
#     }
# except Exception as e:
#     print("Error loading images:", e)
#     wumpus_img = wumpus_dead_img = pit_img = gold_img = None
#     agent_imgs = {}

# def draw_world(world, agent_pos, percepts, safe_cells=None):
#     screen.fill(BROWN)
#     pygame.draw.rect(screen, DARK_BROWN, (0, 0, WINDOW_WIDTH, TITLE_BAR_HEIGHT))
#     title_surface = font.render("Logic Based Agent", True, LIGHT_BROWN)
#     screen.blit(title_surface, (WINDOW_WIDTH // 2 - title_surface.get_width() // 2, 10))

#     for i in range(GRID_ROWS):
#         for j in range(GRID_COLS):
#             x = j * CELL_SIZE
#             y = i * CELL_SIZE + TITLE_BAR_HEIGHT

#             if safe_cells and (i, j) in safe_cells:
#                 pygame.draw.rect(screen, GREEN, (x+2, y+2, CELL_SIZE-4, CELL_SIZE-4))

#             pygame.draw.rect(screen, DARK_BROWN, (x, y, CELL_SIZE, CELL_SIZE), 1)
#             cell = world.world[i][j]

#             # Pit
#             if cell["pit"] and pit_img:
#                 screen.blit(pit_img, (x + 20, y + 20))
#             # Wumpus
#             if cell["wumpus"]:
#                 if world.wumpus_alive and wumpus_img:
#                     screen.blit(wumpus_img, (x + 20, y + 20))
#                 elif not world.wumpus_alive and wumpus_dead_img:
#                     screen.blit(wumpus_dead_img, (x + 20, y + 20))
#             # Gold
#             if cell["gold"] and gold_img:
#                 screen.blit(gold_img, (x + 35, y + 35))

#     ax, ay = agent_pos
#     direction = world.agent_dir
#     if direction in agent_imgs:
#         screen.blit(agent_imgs[direction], (
#             ay * CELL_SIZE + (CELL_SIZE - agent_imgs[direction].get_width()) // 2,
#             ax * CELL_SIZE + TITLE_BAR_HEIGHT + (CELL_SIZE - agent_imgs[direction].get_height()) // 2
#         ))

#     pygame.draw.rect(screen, BROWN, (0, TITLE_BAR_HEIGHT + GRID_HEIGHT, WINDOW_WIDTH, STATUS_BAR_HEIGHT))
#     status_y = TITLE_BAR_HEIGHT + GRID_HEIGHT + 15
#     x_offset = 10

#     for label in ['breeze', 'stench', 'glitter']:
#         value = percepts[label]
#         if label == 'glitter':
#             color = DARK_GREEN if world.has_gold else BLACK
#         else:
#             color = DARK_GREEN if value else BLACK
#         text = f"{label.capitalize()}: {value}  "
#         text_surface = font.render(text, True, color)
#         screen.blit(text_surface, (x_offset, status_y))
#         x_offset += text_surface.get_width() + 5

#     pygame.display.flip()
#     clock.tick(FPS)

# def show_message(text, color):
#     msg_surface = font.render(text, True, color)
#     screen.blit(msg_surface, (
#         WINDOW_WIDTH // 2 - msg_surface.get_width() // 2,
#         TITLE_BAR_HEIGHT + GRID_HEIGHT + 20
#     ))
#     pygame.display.flip()
#     time.sleep(3)

# def run_visual_simulation():
#     world = WumpusWorld()
#     agent = LogicAgent(world, draw_callback=draw_world)

#     draw_world(world, agent.position, world.percepts, safe_cells=agent.safe_cells)
#     time.sleep(1)

#     while world.is_game_over() == "continue":
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 return

#         agent.update_knowledge()
#         agent.act()
#         draw_world(world, agent.position, world.percepts, safe_cells=agent.safe_cells)
#         time.sleep(0.8)

#         next_cell = agent.choose_next_move()
#         if next_cell:
#             agent.move_to(next_cell)
#             draw_world(world, agent.position, world.percepts, safe_cells=agent.safe_cells)
#         else:
#             print("No more safe moves.")
#             break

#     result = world.is_game_over()
#     if result == "win":
#         show_message("Agent WON! 🏆", GREEN)
#     elif result == "lose":
#         show_message("Agent DIED 💀", RED)
#     else:
#         show_message("Game ended.", BLACK)

#     pygame.quit()

# if __name__ == "__main__":
#     run_visual_simulation()



import pygame
import time
from wumpus_world import WumpusWorld
from logic_agent import LogicAgent

# Grid & window dimensions
GRID_ROWS = 4
GRID_COLS = 4
CELL_SIZE = 120
GRID_WIDTH = GRID_COLS * CELL_SIZE
GRID_HEIGHT = GRID_ROWS * CELL_SIZE
TITLE_BAR_HEIGHT = 40
STATUS_BAR_HEIGHT = 80
WINDOW_WIDTH = GRID_WIDTH
WINDOW_HEIGHT = TITLE_BAR_HEIGHT + GRID_HEIGHT + STATUS_BAR_HEIGHT

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Colors
WHITE = hex_to_rgb("#ffffff")
BROWN = hex_to_rgb("#f8be98")
BLACK = hex_to_rgb("#000000")
GRAY = hex_to_rgb("#c8c8c8")
RED = hex_to_rgb("#f82727")
GOLD = hex_to_rgb("#f6f166")
BLUE = hex_to_rgb("#0000ff")
LIGHT_BROWN = hex_to_rgb("#e9dfd7")
DARK_BROWN = hex_to_rgb("#3b1a00")
TEXT_LIGHT_BROWN = hex_to_rgb("#C95C08")
HEADER_LIGHT_BROWN = hex_to_rgb("#EBAD7E")
GREEN = hex_to_rgb("#a5e790")
DARK_GREEN = hex_to_rgb("#65bf4a")
BUTTON_GREEN = hex_to_rgb("#33b80a")

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Wumpus World")
font = pygame.font.SysFont(None, 32)
large_font = pygame.font.SysFont(None, 60)
clock = pygame.time.Clock()
FPS = 5

# Load images
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
    print("Error loading images:", e)
    wumpus_img = wumpus_dead_img = pit_img = gold_img = None
    agent_imgs = {}

def draw_world(world, agent_pos, percepts, score, safe_cells=None):
    screen.fill(BROWN)
    pygame.draw.rect(screen, DARK_BROWN, (0, 0, WINDOW_WIDTH, TITLE_BAR_HEIGHT))
    title_surface = font.render("Logic Based Agent", True, LIGHT_BROWN)
    screen.blit(title_surface, (WINDOW_WIDTH // 2 - title_surface.get_width() // 2, 10))

    for i in range(GRID_ROWS):
        for j in range(GRID_COLS):
            x = j * CELL_SIZE
            y = i * CELL_SIZE + TITLE_BAR_HEIGHT
            if safe_cells and (i, j) in safe_cells:
                pygame.draw.rect(screen, GREEN, (x+2, y+2, CELL_SIZE-4, CELL_SIZE-4))
            pygame.draw.rect(screen, DARK_BROWN, (x, y, CELL_SIZE, CELL_SIZE), 1)
            cell = world.world[i][j]
            if cell["pit"] and pit_img:
                screen.blit(pit_img, (x + 20, y + 20))
            if cell["wumpus"]:
                img = wumpus_img if world.wumpus_alive else wumpus_dead_img
                if img:
                    screen.blit(img, (x + 20, y + 20))
            if cell["gold"] and gold_img:
                screen.blit(gold_img, (x + 35, y + 35))

    ax, ay = agent_pos
    direction = world.agent_dir
    if direction in agent_imgs:
        screen.blit(agent_imgs[direction], (
            ay * CELL_SIZE + (CELL_SIZE - agent_imgs[direction].get_width()) // 2,
            ax * CELL_SIZE + TITLE_BAR_HEIGHT + (CELL_SIZE - agent_imgs[direction].get_height()) // 2
        ))

    pygame.draw.rect(screen, BROWN, (0, TITLE_BAR_HEIGHT + GRID_HEIGHT, WINDOW_WIDTH, STATUS_BAR_HEIGHT))
    status_y = TITLE_BAR_HEIGHT + GRID_HEIGHT + 15
    x_offset = 10
    for label in ['breeze', 'stench', 'glitter']:
        value = percepts[label]
        color = DARK_GREEN  if value else BLACK
        text = f"{label.capitalize()}: {value}  "
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (x_offset, status_y))
        x_offset += text_surface.get_width() + 5

    score_surface = font.render(f"Score: {score}", True, BLUE)
    screen.blit(score_surface, (10, status_y + 30))

    pygame.display.flip()
    clock.tick(FPS)

def show_end_screen(message, score):
     # Simulate background blur by scaling
    background = screen.copy()
    scaled_down = pygame.transform.smoothscale(background, (WINDOW_WIDTH//10, WINDOW_HEIGHT//10))
    blurred = pygame.transform.smoothscale(scaled_down, (WINDOW_WIDTH, WINDOW_HEIGHT))
    screen.blit(blurred, (0, 0))

    # Dark overlay
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(160)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    # Victory/Defeat
    result_text = large_font.render(message, True, HEADER_LIGHT_BROWN if message == "VICTORY!" else HEADER_LIGHT_BROWN)
    screen.blit(result_text, (WINDOW_WIDTH//2 - result_text.get_width()//2, GRID_HEIGHT//2 - 60))

    score_text = font.render(f"Final Score: {score}", True, GOLD)
    screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, GRID_HEIGHT//2 ))

    # Buttons
    button_font = pygame.font.SysFont(None, 28)
    play_again_text = button_font.render("Play Again", True, WHITE)
    quit_text = button_font.render("Quit", True, WHITE)

    play_btn = pygame.Rect(WINDOW_WIDTH//2 - 135, GRID_HEIGHT//2 + 80, 125, 35)
    quit_btn = pygame.Rect(WINDOW_WIDTH//2 + 30, GRID_HEIGHT//2 + 80, 100, 35)


    pygame.draw.rect(screen, TEXT_LIGHT_BROWN, play_btn, border_radius=32)
    pygame.draw.rect(screen, TEXT_LIGHT_BROWN, quit_btn, border_radius=32)
    screen.blit(play_again_text, (play_btn.x + 10, play_btn.y + 8))
    screen.blit(quit_text, (quit_btn.x + 25, quit_btn.y + 8))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    return False
                elif event.key == pygame.K_r:
                    return True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.collidepoint(event.pos):
                    return True
                elif quit_btn.collidepoint(event.pos):
                    pygame.quit()
                    return False

def run_visual_simulation():
    while True:
        world = WumpusWorld()
        agent = LogicAgent(world, draw_callback=draw_world)

        draw_world(world, agent.position, world.percepts, score=agent.score, safe_cells=agent.safe_cells)
        time.sleep(1)

        while world.is_game_over() == "continue":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            agent.update_knowledge()
            agent.act()
            draw_world(world, agent.position, world.percepts, score=agent.score, safe_cells=agent.safe_cells)
            time.sleep(0.8)

            next_cell = agent.choose_next_move()
            if next_cell:
                agent.move_to(next_cell)
                draw_world(world, agent.position, world.percepts, score=agent.score, safe_cells=agent.safe_cells)
            else:
                print("No more safe moves.")
                break

        result = world.is_game_over()
        message = "VICTORY!" if result == "win" else "DEFEAT!" if result == "lose" else "Game Over"
        if not show_end_screen(message, agent.score):
            break

if __name__ == "__main__":
    run_visual_simulation()
