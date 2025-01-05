import pygame
from colors import BROWN, BLACK, WHITE, DARK_BROWN, LIGHT_BROWN, YELLOW, GREEN, RED
from setting import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Draw text helper function
def draw_text(surface, text, font, color, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)

# Menu function
def main_menu():
    title_font = pygame.font.Font(None, 42)  # Font size for the title
    small_font = pygame.font.Font(None, 36)

    # Load button image
    start_button = pygame.image.load("images/Start_button/Start_button.png")
    start_button = pygame.transform.scale(start_button, (200, 80))  # Scale to desired size
    button_rect = start_button.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

    menu_running = True
    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    if button_rect.collidepoint(event.pos):  # Check if clicked on button
                        menu_running = False

        # Background
        screen.fill(LIGHT_BROWN)
        pygame.draw.rect(screen, DARK_BROWN, (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100))
        pygame.draw.rect(screen, BROWN, (60, 60, SCREEN_WIDTH - 120, SCREEN_HEIGHT - 120))

        # Title
        draw_text(screen, "Knight's Quest: Path to the Throne", title_font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150)

        # Draw button
        screen.blit(start_button, button_rect.topleft)

        pygame.display.flip()
        clock.tick(FPS)
