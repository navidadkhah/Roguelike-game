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
            self.coins = 0
            self.stars = 10

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

class Shop(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("images/shop/shop.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self))


# Level class
class Level:
    def __init__(self, width, height, level_index, knight_start=(100, 100), safe_zone=2):
        self.width = width * 2
        self.height = height * 2
        self.tiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.portal = None
        self.level_index = level_index
        self.knight_start = knight_start
        self.safe_zone = safe_zone
        self.shop = None
        self.generate_level()

    def generate_level(self):
        grid = [[0 for _ in range(self.width)] for _ in range(self.height)]

        # Define walls and obstacles
        for x in range(self.width):
            grid[0][x] = 1  # Top wall
            grid[self.height - 1][x] = 1  # Bottom wall
        for y in range(self.height):
            grid[y][0] = 1  # Left wall
            grid[y][self.width - 1] = 1  # Right wall

        knight_x_tile = self.knight_start[0] // TILE_SIZE
        knight_y_tile = self.knight_start[1] // TILE_SIZE

        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if (
                    random.random() < 0.15 and
                    not (knight_x_tile - self.safe_zone <= x <= knight_x_tile + self.safe_zone and
                         knight_y_tile - self.safe_zone <= y <= knight_y_tile + self.safe_zone)
                ):
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
        num_items = 5
        num_enemies = 5
        for _ in range(num_items):
            x, y = self.get_valid_position(grid)
            item = pygame.sprite.Sprite()
            item.image = coin
            item.rect = item.image.get_rect()
            item.rect.topleft = (x, y)
            self.items.add(item)

        for _ in range(num_enemies):
            x, y = self.get_valid_position(grid)
            enemy_choice = random.choice([Enemy, Enemy2, Enemy3]) if self.level_index < 4 else Enemy3
            enemy = enemy_choice(x, y)
            self.enemies.add(enemy)

        shop_x, shop_y = self.get_valid_position(grid)
        self.shop = Shop(shop_x, shop_y)
        print(shop_x, shop_y)
    def get_valid_position(self, grid):
        """Find a random position where there is no tile."""
        while True:
            x = random.randint(1, self.width - 2) * TILE_SIZE
            y = random.randint(1, self.height - 2) * TILE_SIZE
            tile_x, tile_y = x // TILE_SIZE, y // TILE_SIZE
            if grid[tile_y][tile_x] == 0:  # No tile present
                return x, y

    def draw(self, surface, camera):
        for tile in self.tiles:
            surface.blit(tile.image, camera.apply(tile))
        for item in self.items:
            surface.blit(item.image, camera.apply(item))
        for enemy in self.enemies:
            surface.blit(enemy.image, camera.apply(enemy))
            enemy.draw_health_bar(surface, camera)
        if self.portal:
            surface.blit(self.portal.image, camera.apply(self.portal))
        if self.shop:
            self.shop.draw(surface, camera)


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
        if self.shop:
            surface.blit(self.shop.image, camera.apply(self.shop))  # Draw the shop

def shop_menu(player, level):
    """Shop menu where player can buy health and stars."""
    shop_running = True
    font = pygame.font.Font(None, 40)
    notification = None
    notification_time = 0

    while shop_running:
        screen.fill(DARK_BROWN)  # Background color

        # Display shop options
        heading = font.render("You can only use shop once in each level!", True, WHITE)
        health_text = font.render("Press H to buy +1 Health (5 Coins)", True, WHITE)
        star_text = font.render("Press S to buy +5 Stars (5 Coins)", True, WHITE)
        exit_text = font.render("Press X to Exit", True, WHITE)
        coins_text = font.render(f"Coins: {player.coins}", True, WHITE)

        screen.blit(heading, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3))
        screen.blit(health_text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3 + 50))
        screen.blit(star_text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3 + 100))
        screen.blit(exit_text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3 + 150))
        screen.blit(coins_text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3 + 200))

        # Display notification if any
        if notification and pygame.time.get_ticks() - notification_time < 2000:  # Show notification for 2 seconds
            notification_render = font.render(notification, True, RED if "not enough" in notification else GREEN)
            screen.blit(notification_render, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3 + 200))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    if player.coins >= 5:
                        if player.health % 4 == 0:
                            player.health += 4  # Restore one full heart
                            player.coins -= 5
                            notification = "One heart restored!"
                        else:
                            notification = "No full heart lost!"
                    else:
                        notification = "Not enough coins!"
                    notification_time = pygame.time.get_ticks()
                if event.key == pygame.K_x:
                    level.shop = None
                    shop_running = False




# Main game function
def main():
    main_menu()
    back_ground_sound.play(-1)
    player = Player(KNIGHT_SIZE, KNIGHT_SIZE)
    level_index = 0
    level = Level(SCREEN_WIDTH // TILE_SIZE,
                  SCREEN_HEIGHT // TILE_SIZE, level_index)
    print(level.tiles)

    all_sprites = pygame.sprite.Group()
    stars = pygame.sprite.Group()
    all_sprites.add(player)
    all_sprites.add(level.enemies)
    all_sprites.add(level.items)

    camera = Camera(level.width * TILE_SIZE, level.height * TILE_SIZE)

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

        if keys[pygame.K_k] and current_time - last_throw_time > cooldown and player.stars > 0:
            stars_sound.play()
            direction = 1 if player.facing_right else -1
            star = Star(player.rect.centerx, player.rect.centery,
                        direction, level.width * TILE_SIZE)
            stars.add(star)
            all_sprites.add(star)
            last_throw_time = current_time
            player.stars -= 1

        if keys[pygame.K_j]:
            j_sound.play()
            player.activate_knight2(level.enemies)

        player.update(level.tiles)
        stars.update(level.tiles, level.enemies)
        if level.shop and pygame.sprite.collide_rect(player, level.shop):
            shop_menu(player, level)

        camera.update(player)
        screen.blit(level_backgrounds[level_index], (0, 0))
        level.draw(screen, camera)
        for enemy in level.enemies:
            enemy.update(player, level.tiles)  # Update enemy logic
            screen.blit(enemy.image, camera.apply(enemy.rect))  # Draw enemy at camera-adjusted position
            enemy.draw_health_bar(screen, camera)  # Draw health bar at camera-adjusted position

            # Update the camera to follow the player
        camera.update(player)

        collected_items = pygame.sprite.spritecollide(
            player, level.items, True)
        for _ in collected_items:
            player.coins += 1

        if not level.enemies and not level.portal:
            level.portal = Portal(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            all_sprites.add(level.portal)

        if level.portal and pygame.sprite.spritecollideany(player, [level.portal]):
            level_index += 1
            if level_index >= len(level_backgrounds):
                print("You won!")
                running = False
            else:
                player.rect.topleft = (100, 100)
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
            # Draw player and stars with camera offset
            screen.blit(sprite.image, camera.apply(sprite))

        player.draw_health(screen)

        screen.blit(star_image, (15, 53))
        font = pygame.font.Font(None, 36)
        stars_text = font.render(f"x {player.stars}", True, WHITE)
        screen.blit(stars_text, (45, 50))

        screen.blit(coin, (10, 80))
        font = pygame.font.Font(None, 36)
        stars_text = font.render(f"x {player.coins}", True, WHITE)
        screen.blit(stars_text, (45, 83))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
