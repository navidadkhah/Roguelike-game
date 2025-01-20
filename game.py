import pygame
import random
from menu import main_menu
from colors import BROWN, BLACK, WHITE, DARK_BROWN, LIGHT_BROWN, YELLOW, GREEN, RED
from setting import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TILE_SIZE, ENEMY_SIZE, ITEMS_SIZE, KNIGHT_SIZE, PORTAL_SIZE
from Enemy1 import Enemy, Enemy2, Enemy3, BossEnemy
from sound import j_sound, stars_sound, back_ground_sound

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Load heart
full_heart_image = pygame.image.load("images/Heart/Heart.png").convert_alpha()
full_heart_image = pygame.transform.scale(full_heart_image, (30, 30))
half_heart_image = pygame.image.load(
    "images/Heart/Half_heart.png").convert_alpha()
half_heart_image = pygame.transform.scale(half_heart_image, (30, 30))
empty_heart_image = pygame.image.load(
    "images/Heart/Heart_empty.png").convert_alpha()
empty_heart_image = pygame.transform.scale(empty_heart_image, (30, 30))

coin = pygame.image.load("images/Coin/Coin.png").convert_alpha()
coin = pygame.transform.scale(coin, (30, 30))

# Load star images
star_image = pygame.image.load("images/Ninja_Star/Ninja_star.png")
star_image = pygame.transform.scale(
    star_image, (20, 20))  # Adjust size as needed

# Backgrounds for each level
level_backgrounds = [
    pygame.image.load(f"images/backgrounds/level{i+1}.png").convert() for i in range(5)
]
for i in range(len(level_backgrounds)):
    level_backgrounds[i] = pygame.transform.scale(
        level_backgrounds[i], (SCREEN_WIDTH, SCREEN_HEIGHT))

# Portal class
class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(
            "images/portal/portal.png").convert_alpha()
        self.image = pygame.transform.scale(
            self.image, (PORTAL_SIZE, PORTAL_SIZE))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

# Camera class
class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height


    def apply(self, target):
        """Applies the camera offset to the entity's position."""
        if isinstance(target, pygame.Rect):
            return target.move(-self.camera.x, -self.camera.y)
        elif isinstance(target, pygame.sprite.Sprite):
            # Create a new rect for the sprite based on the camera offset
            return target.rect.move(self.camera.x, self.camera.y)
        else:
            raise TypeError("Unsupported target type for camera application")
        # return rect.move(-self.camera.x, -self.camera.y)

    def apply_to_health_bar(self, x, y):
        """Adjusts x, y coordinates for health bars based on the camera's position."""
        return (x - self.camera.x, y - self.camera.y)

    def update(self, target):
        """Updates the camera to center on the target (player)."""
        x = -target.rect.centerx + SCREEN_WIDTH // 2
        y = -target.rect.centery + SCREEN_HEIGHT // 2
        self.camera = pygame.Rect(x, y, self.width, self.height)


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
        collided_enemies = pygame.sprite.spritecollide(
            self, enemy_group, False)  # Do not remove the enemy immediately
        if collided_enemies:
            for enemy in collided_enemies:
                enemy.take_damage()  # Reduce enemy's health
            self.kill()  # Remove the star after hitting the enemy

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
            super().__init__()
            self.original_image = pygame.image.load("images/Knight/knight1.png")  # Original image
            self.original_image = pygame.transform.scale(self.original_image, (KNIGHT_SIZE, KNIGHT_SIZE))
            self.alternate_image = pygame.image.load("images/Knight/knight2.png")  # Alternate image
            self.alternate_image = pygame.transform.scale(self.alternate_image, (KNIGHT_SIZE, KNIGHT_SIZE))
            self.image = self.original_image
            self.rect = self.image.get_rect()
            self.rect.topleft = (x, y)
            self.dx, self.dy = 0, 0
            self.facing_right = True  # Track the direction the player is facing
            self.last_image_change_time = None  # Timer for image change
            self.knight2_duration = 50  # Duration in milliseconds for "knight2" mode
            self.damage_applied = False
            self.health = 50  # Total health points (3 full hearts, 4 hits per heart)

    def update(self, tiles):
            self.rect.x += self.dx
            if pygame.sprite.spritecollideany(self, tiles):
                self.rect.x -= self.dx
            self.rect.y += self.dy
            if pygame.sprite.spritecollideany(self, tiles):
                self.rect.y -= self.dy

            # Revert to the correct `knight1` image after the knight2 duration
            current_time = pygame.time.get_ticks()
            if self.last_image_change_time and current_time - self.last_image_change_time > self.knight2_duration:
                if self.facing_right:
                    self.image = self.original_image
                else:
                    self.image = pygame.transform.flip(self.original_image, True, False)
                self.last_image_change_time = None
                self.damage_applied = False

    def move(self, dx, dy):
            self.dx, self.dy = dx, dy

            # Flip the images when changing direction
            if dx < 0 and self.facing_right:  # Moving left
                self.image = pygame.transform.flip(self.original_image, True, False)
                self.facing_right = False
            elif dx > 0 and not self.facing_right:  # Moving right
                self.image = self.original_image
                self.facing_right = True

    def activate_knight2(self, enemies):
            """Switch to the alternate image and damage nearby enemies."""
            if self.facing_right:
                self.image = self.alternate_image
            else:
                self.image = pygame.transform.flip(self.alternate_image, True, False)  # Flip image if facing left

            self.last_image_change_time = pygame.time.get_ticks()

            # Damage nearby enemies
            if not self.damage_applied:
                for enemy in enemies:
                    if self.is_nearby(enemy):
                        enemy.take_damage()  # Damage enemy
                self.damage_applied = True

    def is_nearby(self, enemy):
        """Check if an enemy is within a certain range of the player."""
        player_center = self.rect.center
        enemy_center = enemy.rect.center
        distance = pygame.math.Vector2(player_center).distance_to(enemy_center)
        return distance < 75  # Adjust the range as needed

    def take_damage(self):
        """Reduce health and manage heart images."""
        self.health -= 1
        print(self.health)
        if self.health <= 0:
            # Handle game over or player death scenario
            print("Player has died")

    def draw_health(self, screen):
        """Draw health bar on the screen."""
        for i in range(3):  # Player has 3 hearts
            heart_x = 10 + i * 40
            if self.health > (i + 1) * 4:
                screen.blit(full_heart_image, (heart_x, 10))
            elif self.health > i * 4 + 2:
                screen.blit(half_heart_image, (heart_x, 10))
            else:
                screen.blit(empty_heart_image, (heart_x, 10))

# Level class
class Level:
    def __init__(self, width, height, level_index):
        # Increase the level dimensions by a factor (e.g., 2x the original size)
        self.width = width * 2
        self.height = height * 2
        self.tiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.portal = None
        self.level_index = level_index
        self.generate_level()

    def generate_level(self):
        # Adjusted grid for the larger level
        grid = [[0 for _ in range(self.width)] for _ in range(self.height)]

        # Define walls and obstacles
        for x in range(self.width):
            grid[0][x] = 1  # Top wall
            grid[self.height - 1][x] = 1  # Bottom wall
        for y in range(self.height):
            grid[y][0] = 1  # Left wall
            grid[y][self.width - 1] = 1  # Right wall

        # More complex or larger patterns of walls and open spaces
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if random.random() < 0.15:  # Adjust randomness for wall placement
                    grid[y][x] = 1

        # Convert the grid to tiles
        for y in range(self.height):
            for x in range(self.width):
                if grid[y][x] == 1:
                    tile = pygame.sprite.Sprite()
                    tile.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
                    tile.image.fill(BROWN)
                    tile.rect = tile.image.get_rect()
                    tile.rect.topleft = (x * TILE_SIZE, y * TILE_SIZE)
                    self.tiles.add(tile)

        # Place items and enemies considering the increased map size
        num_items = 5  # Increase the number of collectible items
        num_enemies = 5  # Adjust number of enemies based on level size and complexity
        for _ in range(num_items):
            x = random.randint(1, self.width - 2) * TILE_SIZE
            y = random.randint(1, self.height - 2) * TILE_SIZE
            item = pygame.sprite.Sprite()
            item.image = coin
            item.rect = item.image.get_rect()
            item.rect.topleft = (x, y)
            self.items.add(item)

        for _ in range(num_enemies):
            x = random.randint(1, self.width - 2) * TILE_SIZE
            y = random.randint(1, self.height - 2) * TILE_SIZE
            enemy_choice = random.choice([Enemy, Enemy2, Enemy3]) if self.level_index < 4 else Enemy3
            enemy = enemy_choice(x, y)
            self.enemies.add(enemy)

    def draw(self, surface, camera):
        for tile in self.tiles:
            surface.blit(tile.image, camera.apply(tile))
        for item in self.items:
            surface.blit(item.image, camera.apply(item))
        for enemy in self.enemies:
            surface.blit(enemy.image, camera.apply(enemy))
            enemy.draw_health_bar(surface, camera)  # Draw the health bar
        if self.portal:
            surface.blit(self.portal.image, camera.apply(self.portal))

# Main game function
def main():
    main_menu()
    back_ground_sound.play(-1)
    player = Player(KNIGHT_SIZE, KNIGHT_SIZE)
    level_index = 0
    level = Level(SCREEN_WIDTH // TILE_SIZE,
                  SCREEN_HEIGHT // TILE_SIZE, level_index)

    all_sprites = pygame.sprite.Group()
    stars = pygame.sprite.Group()
    all_sprites.add(player)
    all_sprites.add(level.enemies)
    all_sprites.add(level.items)

    camera = Camera(level.width * TILE_SIZE, level.height * TILE_SIZE)

    remaining_stars = 10
    remaining_coins = 0
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
            star = Star(player.rect.centerx, player.rect.centery,
                        direction, level.width * TILE_SIZE)
            stars.add(star)
            all_sprites.add(star)
            last_throw_time = current_time
            remaining_stars -= 1

        if keys[pygame.K_j]:
            j_sound.play()
            player.activate_knight2(level.enemies)

        player.update(level.tiles)
        stars.update(level.tiles, level.enemies)

        for enemy in level.enemies:
            enemy.update(player, level.tiles)  # Update enemy logic
            screen.blit(enemy.image, camera.apply(enemy.rect))  # Draw enemy at camera-adjusted position
            enemy.draw_health_bar(screen, camera)  # Draw health bar at camera-adjusted position

            # Update the camera to follow the player
        camera.update(player)

        # Debug: Print player and camera positions
        print(f"Player Position: {player.rect.topleft}")
        print(f"Camera Position: {camera.camera.topleft}")

        collected_items = pygame.sprite.spritecollide(
            player, level.items, True)
        for item in collected_items:
            remaining_coins += 1

        if not level.enemies and not level.portal:
            level.portal = Portal(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            all_sprites.add(level.portal)

        if level.portal and pygame.sprite.spritecollideany(player, [level.portal]):
            level_index += 1
            if level_index >= len(level_backgrounds):
                print("You won!")
                running = False
            else:
                level = Level(SCREEN_WIDTH // TILE_SIZE,
                              SCREEN_HEIGHT // TILE_SIZE, level_index)
                all_sprites.empty()
                all_sprites.add(player, level.enemies, level.items)

        # Draw everything relative to the camera
        # Draw background without camera offset
        screen.blit(level_backgrounds[level_index], (0, 0))
        # Draw tiles, items, enemies, and portal with camera offset
        level.draw(screen, camera)

        for sprite in all_sprites:
            # Debug: Print sprite positions after applying camera offset
            print(f"Sprite Position: {camera.apply(sprite).topleft}")
            # Draw player and stars with camera offset
            screen.blit(sprite.image, camera.apply(sprite))

        player.draw_health(screen)

        screen.blit(star_image, (15, 53))
        font = pygame.font.Font(None, 36)
        stars_text = font.render(f"x {remaining_stars}", True, WHITE)
        screen.blit(stars_text, (45, 50))

        screen.blit(coin, (10, 80))
        font = pygame.font.Font(None, 36)
        stars_text = font.render(f"x {remaining_coins}", True, WHITE)
        screen.blit(stars_text, (45, 83))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
