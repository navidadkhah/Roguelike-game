import pygame
import random
from menu import main_menu
from colors import BROWN, BLACK, WHITE, DARK_BROWN, LIGHT_BROWN, YELLOW, GREEN, RED
from setting import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TILE_SIZE
from collections import deque

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Load heart and star images
heart_image = pygame.image.load("images/Heart/Heart.png")
heart_image = pygame.transform.scale(heart_image, (30, 30))

star_image = pygame.image.load("images/Ninja_Star/Ninja_star.png")  # Replace with your star image
star_image = pygame.transform.scale(star_image, (20, 20))  # Adjust size as needed

j_sound = pygame.mixer.Sound("Sounds/Sword/sword-sound.mp3")  # Replace with the path to your sound file
j_sound.set_volume(0.4)  # Adjust volume if needed

back_ground_sound = pygame.mixer.Sound("Sounds/SoundTracks/SoundTrack1/s1.mp3")  # Replace with the path to your sound file
back_ground_sound.set_volume(0.6)  # Adjust volume if needed

stars_sound = pygame.mixer.Sound("Sounds/Star/stars.mp3")  # Replace with the path to your sound file
stars_sound.set_volume(0.4)  # Adjust volume if needed

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

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image1 = enemy_image  # Enemy1 image
        self.image2 = pygame.image.load("images/Enemy1/Enemy1_2.png")  # Enemy2 image
        self.image2 = pygame.transform.scale(self.image2, (TILE_SIZE, TILE_SIZE))
        self.image = self.image1
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = 2  # Movement speed
        self.health = 2  # Enemy requires two hits to die
        self.last_image_change_time = 0  # Timer for alternating images
        self.image_toggle_interval = 100  # Time in milliseconds to alternate images
        self.path = []  # Store the path from BFS

    def take_damage(self):
        """Reduce health and check if the enemy is dead."""
        self.health -= 1
        if self.health <= 0:
            self.kill()

    def get_tile_pos(self, x, y):
        """Convert pixel coordinates to grid coordinates."""
        return x // TILE_SIZE, y // TILE_SIZE

    def get_pixel_pos(self, tile_x, tile_y):
        """Convert grid coordinates back to pixel coordinates."""
        return tile_x * TILE_SIZE, tile_y * TILE_SIZE

    def bfs(self, start, goal, walls):
        """Perform BFS to find the shortest path from start to goal."""
        queue = deque([start])
        visited = {start}
        came_from = {}

        while queue:
            current = queue.popleft()
            if current == goal:
                # Reconstruct the path
                path = []
                while current != start:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            # Explore neighbors
            neighbors = [
                (current[0] + 1, current[1]),  # Right
                (current[0] - 1, current[1]),  # Left
                (current[0], current[1] + 1),  # Down
                (current[0], current[1] - 1),  # Up
            ]

            for neighbor in neighbors:
                if (
                    neighbor not in visited
                    and neighbor not in walls
                    and neighbor[0] >= 0
                    and neighbor[1] >= 0
                ):
                    visited.add(neighbor)
                    queue.append(neighbor)
                    came_from[neighbor] = current
        return None  # No path found

    def update(self, player, tiles):
        """Update enemy movement and handle interaction with the player."""
        # Get the current positions of the enemy and player in grid coordinates
        enemy_pos = self.get_tile_pos(self.rect.x, self.rect.y)
        player_pos = self.get_tile_pos(player.rect.x, player.rect.y)

        # Build a set of wall positions in grid coordinates
        walls = {self.get_tile_pos(tile.rect.x, tile.rect.y) for tile in tiles}

        # Recalculate path if player moved to a new tile or the path is empty
        if not self.path or self.path[-1] != player_pos:
            self.path = self.bfs(enemy_pos, player_pos, walls)

        # Follow the path if available
        if self.path:
            next_tile = self.path[0]
            next_x, next_y = self.get_pixel_pos(next_tile[0], next_tile[1])

            # Smooth movement toward the next tile
            if self.rect.x < next_x:
                self.rect.x = min(self.rect.x + self.speed, next_x)
            elif self.rect.x > next_x:
                self.rect.x = max(self.rect.x - self.speed, next_x)

            if self.rect.y < next_y:
                self.rect.y = min(self.rect.y + self.speed, next_y)
            elif self.rect.y > next_y:
                self.rect.y = max(self.rect.y - self.speed, next_y)

            # Check if the enemy has reached the next tile
            if self.rect.topleft == (next_x, next_y):
                self.path.pop(0)  # Remove the reached tile from the path

        # If enemy reaches the player's exact tile, toggle images
        if enemy_pos == player_pos:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_image_change_time > self.image_toggle_interval:
                self.image = self.image2 if self.image == self.image1 else self.image1
                self.last_image_change_time = current_time


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
    back_ground_sound.play(-1)  # Loop the background sound
    player = Player(TILE_SIZE, TILE_SIZE)
    enemy = Enemy(TILE_SIZE * 5, TILE_SIZE * 5)  # Enemy starts at a specific position
    level = Level(SCREEN_WIDTH // TILE_SIZE * 3, SCREEN_HEIGHT // TILE_SIZE * 3)

    all_sprites = pygame.sprite.Group()
    stars = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()  # Group to manage enemies
    all_sprites.add(player)
    all_sprites.add(enemy)
    enemy_group.add(enemy)  # Add the enemy to the group

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
        enemy.update(player, level.tiles)  # Enemy uses BFS to track player
        stars.update(level.tiles, enemy_group)  # Pass tiles and enemies for collision check # Pass tiles and enemies for collision check
        camera.update(player)

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
