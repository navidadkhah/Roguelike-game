import pygame
import random
from menu import main_menu
from colors import BROWN, BLACK, WHITE, DARK_BROWN, LIGHT_BROWN, YELLOW, GREEN, RED
from setting import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TILE_SIZE
from Enemy1 import Enemy
from sound import j_sound, stars_sound, back_ground_sound

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Load heart and star images
heart_image = pygame.image.load("images/Heart/Heart.png")
heart_image = pygame.transform.scale(heart_image, (30, 30))

star_image = pygame.image.load("images/Ninja_Star/Ninja_star.png")  # Replace with your star image
star_image = pygame.transform.scale(star_image, (20, 20))  # Adjust size as needed


enemy_image = pygame.image.load("images/Enemy1/Enemy1_1.png")
enemy_image = pygame.transform.scale(enemy_image, (TILE_SIZE, TILE_SIZE))


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
        x = min(0, x)
        x = max(-(self.width - SCREEN_WIDTH), x)
        y = min(0, y)
        y = max(-(self.height - SCREEN_HEIGHT), y)
        self.camera = pygame.Rect(x, y, self.width, self.height)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.original_image = pygame.image.load("images/Knight/knight1.png")  # Original image
        self.original_image = pygame.transform.scale(self.original_image, (TILE_SIZE, TILE_SIZE))
        self.alternate_image = pygame.image.load("images/Knight/knight2.png")  # Alternate image
        self.alternate_image = pygame.transform.scale(self.alternate_image, (TILE_SIZE, TILE_SIZE))
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.dx, self.dy = 0, 0
        self.facing_right = True  # Track the direction the player is facing
        self.last_image_change_time = None  # Timer for image change

    def update(self, tiles):
        self.rect.x += self.dx
        if pygame.sprite.spritecollideany(self, tiles):
            self.rect.x -= self.dx
        self.rect.y += self.dy
        if pygame.sprite.spritecollideany(self, tiles):
            self.rect.y -= self.dy

        # Revert to the correct `knight1` image (rotated or original) after 1 second
        if self.last_image_change_time:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_image_change_time > 50:  # 1 second
                if self.facing_right:
                    self.image = self.original_image
                else:
                    self.image = pygame.transform.flip(self.original_image, True, False)
                self.last_image_change_time = None

    def move(self, dx, dy):
        self.dx, self.dy = dx, dy

        # Flip the images when changing direction
        if dx < 0 and self.facing_right:  # Moving left
            self.image = pygame.transform.flip(self.original_image, True, False)
            self.alternate_image = pygame.transform.scale(self.alternate_image, (TILE_SIZE, TILE_SIZE))
            self.facing_right = False
        elif dx > 0 and not self.facing_right:  # Moving right
            self.image = self.original_image
            self.alternate_image = pygame.image.load("images/Knight/knight2.png")  # Reload original alternate image
            self.alternate_image = pygame.transform.scale(self.alternate_image, (TILE_SIZE, TILE_SIZE))
            self.facing_right = True

    def change_image_temporarily(self):
        # Switch to the alternate image but keep track of the direction
        if self.facing_right:
            self.image = self.alternate_image
        else:
            self.image = pygame.transform.flip(self.alternate_image, True, False)
        self.last_image_change_time = pygame.time.get_ticks()


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
    def __init__(self, x, y, direction, level_width):
        super().__init__()
        self.original_image = star_image  # Save the original image for rotation
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.angle = 0  # Initial angle for rotation
        self.level_width = level_width  # Level width in pixels

    def update(self, tiles, enemy_group):
        # Rotate the star
        self.angle += 10  # Adjust rotation speed as needed
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        # Move the star
        self.rect.x += self.direction * 10

        # Remove the star if it reaches the level boundaries
        if self.rect.right < 0 or self.rect.left > self.level_width:
            self.kill()

        # Check collision with walls (tiles)
        if pygame.sprite.spritecollideany(self, tiles):
            self.kill()

        # Check collision with enemies
        collided_enemies = pygame.sprite.spritecollide(self, enemy_group, False)  # Do not remove the enemy immediately
        if collided_enemies:
            for enemy in collided_enemies:
                enemy.take_damage()  # Reduce enemy's health
            self.kill()  # Remove the star after hitting the enemy





# Level generator
class Level:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.items = pygame.sprite.Group()  # For hearts or other collectibles
        self.generate_level()

    def generate_level(self):
        # Generate tiles
        for x in range(0, self.width * TILE_SIZE, TILE_SIZE):
            for y in range(0, self.height * TILE_SIZE, TILE_SIZE):
                # Outer boundary or random obstacles
                if random.random() < 0.2 or x == 0 or y == 0 or x == (self.width - 1) * TILE_SIZE or y == (
                        self.height - 1) * TILE_SIZE:
                    tile = Tile(x, y)
                    self.tiles.add(tile)

                # Randomly place collectible items
                elif random.random() < 0.05:
                    item = pygame.sprite.Sprite()
                    item.image = heart_image  # Example: Heart image as collectible
                    item.rect = item.image.get_rect()
                    item.rect.topleft = (x, y)
                    self.items.add(item)

        # Fixed number of enemies
        num_enemies = 10  # Set the exact number of enemies you want
        placed_enemies = 0
        while placed_enemies < num_enemies:
            x = random.randint(1, self.width - 2) * TILE_SIZE  # Avoid edge
            y = random.randint(1, self.height - 2) * TILE_SIZE  # Avoid edge
            enemy = Enemy(x, y)
            self.enemies.add(enemy)
            placed_enemies += 1

    def draw(self, surface, camera):
        # Draw tiles
        for tile in self.tiles:
            surface.blit(tile.image, camera.apply(tile))

        # Draw items
        for item in self.items:
            surface.blit(item.image, camera.apply(item))

        # Draw enemies
        for enemy in self.enemies:
            surface.blit(enemy.image, camera.apply(enemy))

# Main game function
def main():
    main_menu()
    back_ground_sound.play(-1)  # Loop the background sound
    player = Player(TILE_SIZE, TILE_SIZE)
    level = Level(SCREEN_WIDTH // TILE_SIZE * 3, SCREEN_HEIGHT // TILE_SIZE * 3)

    all_sprites = pygame.sprite.Group()
    stars = pygame.sprite.Group()
    all_sprites.add(player)
    all_sprites.add(level.enemies)  # Add generated enemies to all_sprites
    all_sprites.add(level.items)  # Add items to all_sprites

    camera = Camera(level.width * TILE_SIZE, level.height * TILE_SIZE)

    remaining_stars = 10
    last_throw_time = 0
    cooldown = 200

    running = True
    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 5
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 5
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 5
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 5
        player.move(dx, dy)

        if keys[pygame.K_k] and current_time - last_throw_time > cooldown and remaining_stars > 0:
            stars_sound.play()
            direction = 1 if player.facing_right else -1
            star = Star(player.rect.centerx, player.rect.centery, direction, level.width * TILE_SIZE)
            stars.add(star)
            all_sprites.add(star)
            last_throw_time = current_time
            remaining_stars -= 1

        if keys[pygame.K_j]:
            j_sound.play()
            player.change_image_temporarily()

        # Update all entities
        player.update(level.tiles)
        stars.update(level.tiles, level.enemies)

        # Update each enemy in the level
        for enemy in level.enemies:
            enemy.update(player, level.tiles)

        camera.update(player)

        # Check for item collection
        collected_items = pygame.sprite.spritecollide(player, level.items, True)
        for item in collected_items:
            remaining_stars += 1  # Example: Increment star count on item collection

        # Draw the screen
        screen.fill(GREEN)
        level.draw(screen, camera)
        for sprite in all_sprites:
            screen.blit(sprite.image, camera.apply(sprite))

        for i in range(3):  # Draw 3 hearts
            screen.blit(heart_image, (10 + i * 40, 10))

        screen.blit(star_image, (15, 53))  # Draw star icon
        font = pygame.font.Font(None, 36)
        stars_text = font.render(f"x {remaining_stars}", True, (255, 255, 255))
        screen.blit(stars_text, (45, 50))  # Draw remaining stars

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
