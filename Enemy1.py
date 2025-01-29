from setting import TILE_SIZE
from colors import RED, GREEN, WHITE
from collections import deque
import pygame

enemy_image = pygame.image.load("images/Enemy1/Enemy1_1.png")
enemy_image = pygame.transform.scale(enemy_image, (TILE_SIZE, TILE_SIZE))


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image1 = pygame.image.load(
            "images/Enemy1/Enemy1_1.png").convert_alpha()
        self.image1 = pygame.transform.scale(
            self.image1, (TILE_SIZE, TILE_SIZE))
        self.image2 = pygame.image.load(
            "images/Enemy1/Enemy1_2.png").convert_alpha()
        self.image2 = pygame.transform.scale(
            self.image2, (TILE_SIZE, TILE_SIZE))
        self.image = self.image1  # Start with the default image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = 2  # Movement speed
        self.health = 1  # Enemy requires two hits to die
        self.max_health = 2  # Store max health for health bar scaling
        self.cooldown = 500  # Cooldown period of 2 seconds for image toggling
        # Set initial time to current tick
        self.time_of_last_change = pygame.time.get_ticks()
        self.path = []  # Pathfinding


    def take_damage(self, player):
        """Reduce health and check if the enemy is dead."""
        self.health -= 1
        if self.health <= 0:
            self.kill()
            player.coins += 1

    def draw_health_bar(self, surface, camera):
        pass
    #     bar_length = 50  # Length of the health bar
    #     bar_height = 5  # Height of the health bar
    #     fill = (self.health / self.max_health) * bar_length
    #
    #     # Position health bar right above the enemy's head without any arbitrary offsets
    #     health_bar_x = -self.rect.centerx + bar_length // 2
    #     health_bar_y = -self.rect.top + bar_height - 10  # Positioned 10 pixels above the enemy
    #
    #     # Create the rectangles for the health bar
    #     fill_rect = pygame.Rect(health_bar_x, health_bar_y, fill, bar_height)
    #     outline_rect = pygame.Rect(health_bar_x, health_bar_y, bar_length, bar_height)
    #
    #     # Apply camera transformation to adjust health bar position based on camera's view
    #     fill_rect = camera.apply(fill_rect)
    #     outline_rect = camera.apply(outline_rect)
    #
    #     # Draw the health bar on the surface
    #     pygame.draw.rect(surface, RED, fill_rect)
    #     pygame.draw.rect(surface, WHITE, outline_rect, 1)

    def update(self, player, tiles):
        """Update enemy movement and handle interaction with the player."""
        current_time = pygame.time.get_ticks()
        # Ensuring that time_of_last_change is not None
        if self.time_of_last_change is None:
            self.time_of_last_change = pygame.time.get_ticks()

        # Check if enemy collides with player and if the cooldown has passed
        if self.rect.colliderect(player.rect):
            if current_time - self.time_of_last_change > self.cooldown:
                self.image = self.image2 if self.image == self.image1 else self.image1
                player.take_damage()
                self.time_of_last_change = current_time  # Reset the cooldown timer

        # Pathfinding and movement
        enemy_pos = self.get_tile_pos(self.rect.x, self.rect.y)
        player_pos = self.get_tile_pos(player.rect.x, player.rect.y)
        walls = {self.get_tile_pos(tile.rect.x, tile.rect.y) for tile in tiles}

        if not self.path or self.path[-1] != player_pos:
            self.path = self.bfs(enemy_pos, player_pos, walls)

        if self.path:
            next_tile = self.path[0]
            next_x, next_y = self.get_pixel_pos(next_tile[0], next_tile[1])

            if self.rect.x < next_x:
                self.rect.x = min(self.rect.x + self.speed, next_x)
            elif self.rect.x > next_x:
                self.rect.x = max(self.rect.x - self.speed, next_x)

            if self.rect.y < next_y:
                self.rect.y = min(self.rect.y + self.speed, next_y)
            elif self.rect.y > next_y:
                self.rect.y = max(self.rect.y - self.speed, next_y)

            if self.rect.topleft == (next_x, next_y):
                self.path.pop(0)  # Move to the next step in the path

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


class Enemy2(Enemy):

    def __init__(self, x, y):
        super().__init__(x, y)
        # Load different images for Enemy2
        self.image1 = pygame.image.load(
            "images/Enemy2/Enemy2_1.png").convert_alpha()
        self.image1 = pygame.transform.scale(
            self.image1, (TILE_SIZE, TILE_SIZE))
        self.image2 = pygame.image.load(
            "images/Enemy2/Enemy2_2.png").convert_alpha()
        self.image2 = pygame.transform.scale(
            self.image2, (TILE_SIZE, TILE_SIZE))
        self.image = self.image1
        self.speed = 2  # Faster than Enemy1
        self.health = 2  # Takes 2 hits to die
        self.max_health = 4
        self.cooldown = 400  # Cooldown period for image toggling remains the same

    def take_damage(self, player):
        """Reduce health and check if the enemy is dead."""
        self.health -= 1
        if self.health <= 0:
            self.kill()
            player.coins += 3


class Enemy3(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        # Load different images for Enemy3
        self.image1 = pygame.image.load(
            "images/Enemy3/Enemy3_1.png").convert_alpha()
        self.image1 = pygame.transform.scale(
            self.image1, (TILE_SIZE, TILE_SIZE))
        self.image2 = pygame.image.load(
            "images/Enemy3/Enemy3_2.png").convert_alpha()
        self.image2 = pygame.transform.scale(
            self.image2, (TILE_SIZE, TILE_SIZE))
        self.image = self.image1
        self.speed = 3  # Faster than Enemy2
        self.health = 4  # Takes 4 hits to die
        self.max_health = 6
        self.cooldown = 300  # Reduced cooldown for faster interaction
        
    def take_damage(self, player):
        """Reduce health and check if the enemy is dead."""
        self.health -= 1
        if self.health <= 0:
            self.kill()
            player.coins += 5


class BossEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        # Load unique images for the boss enemy
        self.image1 = pygame.image.load(
            "images/Boss/Boss.png").convert_alpha()
        self.image1 = pygame.transform.scale(
            self.image1, (TILE_SIZE * 1.5, TILE_SIZE * 1.5))  # Boss is larger
        self.image2 = pygame.image.load(
            "images/Boss/Boss.png").convert_alpha()
        self.image2 = pygame.transform.scale(
            self.image2, (TILE_SIZE * 2, TILE_SIZE * 2))
        self.image = self.image1
        self.speed = 1  # Slower movement due to size
        self.health = 15  # Takes 20 hits to die
        self.max_health = 20
        self.cooldown = 500  # Faster interaction
