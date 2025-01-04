import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
TILE_SIZE = 40
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
DARK_BROWN = (101, 67, 33)
LIGHT_BROWN = (210, 180, 140)
YELLOW = (255, 255, 0)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Roguelike Game")
clock = pygame.time.Clock()

# Draw text helper function
def draw_text(surface, text, font, color, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)

# Menu function
def main_menu():
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)

    menu_running = True
    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Start game on Enter
                    menu_running = False

        # Background
        screen.fill(LIGHT_BROWN)
        pygame.draw.rect(screen, DARK_BROWN, (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100))
        pygame.draw.rect(screen, BROWN, (60, 60, SCREEN_WIDTH - 120, SCREEN_HEIGHT - 120))

        # Title
        draw_text(screen, "Roguelike Game", font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)

        # Instructions
        draw_text(screen, "Press ENTER to Start", small_font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
        draw_text(screen, "Press ESC to Quit", small_font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)

        pygame.display.flip()
        clock.tick(FPS)

# Camera class
class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + SCREEN_WIDTH // 2
        y = -target.rect.centery + SCREEN_HEIGHT // 2

        # Limit scrolling to level boundaries
        x = min(0, x)  # Left
        x = max(-(self.width - SCREEN_WIDTH), x)  # Right
        y = min(0, y)  # Top
        y = max(-(self.height - SCREEN_HEIGHT), y)  # Bottom

        self.camera = pygame.Rect(x, y, self.width, self.height)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("images/Knight/knight1.png")
        self.image = pygame.transform.scale(self.image, (TILE_SIZE , TILE_SIZE ))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.dx, self.dy = 0, 0

    def update(self, tiles):
        self.rect.x += self.dx
        if pygame.sprite.spritecollideany(self, tiles):
            self.rect.x -= self.dx

        self.rect.y += self.dy
        if pygame.sprite.spritecollideany(self, tiles):
            self.rect.y -= self.dy

    def move(self, dx, dy):
        self.dx, self.dy = dx, dy

# Tile class
class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

# Star class
class Star(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.rect.x += self.direction * 10
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

# Level generator
class Level:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = pygame.sprite.Group()
        self.generate_level()

    def generate_level(self):
        for x in range(0, self.width * TILE_SIZE, TILE_SIZE):
            for y in range(0, self.height * TILE_SIZE, TILE_SIZE):
                if random.random() < 0.3 or x == 0 or y == 0 or x == (self.width - 1) * TILE_SIZE or y == (self.height - 1) * TILE_SIZE:
                    tile = Tile(x, y)
                    self.tiles.add(tile)

    def draw(self, surface, camera):
        for tile in self.tiles:
            surface.blit(tile.image, camera.apply(tile))

# Main game function
def main():
    main_menu()
    player = Player(TILE_SIZE, TILE_SIZE)
    level = Level(SCREEN_WIDTH // TILE_SIZE * 3, SCREEN_HEIGHT // TILE_SIZE * 3)  # Larger level

    all_sprites = pygame.sprite.Group()
    stars = pygame.sprite.Group()
    all_sprites.add(player)

    camera = Camera(level.width * TILE_SIZE, level.height * TILE_SIZE)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Player movement
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx -= 5
        if keys[pygame.K_RIGHT]:
            dx += 5
        if keys[pygame.K_UP]:
            dy -= 5
        if keys[pygame.K_DOWN]:
            dy += 5

        player.move(dx, dy)

        if keys[pygame.K_k]:
            star = Star(player.rect.centerx, player.rect.centery, 1 if player.dx >= 0 else -1)
            stars.add(star)
            all_sprites.add(star)

        # Update
        player.update(level.tiles)
        stars.update()
        camera.update(player)

        # Draw
        screen.fill(BLACK)
        level.draw(screen, camera)
        for sprite in all_sprites:
            screen.blit(sprite.image, camera.apply(sprite))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
