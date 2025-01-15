from setting import TILE_SIZE
from colors import RED, GREEN
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
        self.health = 2  # Enemy requires two hits to die
        self.max_health = 2  # Store max health for health bar scaling
        self.cooldown = 100  # Cooldown period of 2 seconds for image toggling
        # Set initial time to current tick
        self.time_of_last_change = pygame.time.get_ticks()
        self.path = []  # Pathfinding

    def take_damage(self):
        """Reduce health and check if the enemy is dead."""
        self.health -= 1
        if self.health <= 0:
            self.kill()

    def draw_health_bar(self, surface):
        """Draw the enemy's health bar closer to the enemy."""
        bar_width = 100  # Fixed width for health bar
        bar_height = 5
        health_ratio = self.health / self.max_health  # Scale based on max health
        # Adjust width based on current health
        current_bar_width = int(bar_width * health_ratio)

        # Position the health bar closer to the enemy
        bar_x = self.rect.x
        bar_y = self.rect.y - bar_height + 10  # Adjust the -2 to control the distance

        # Draw the background and foreground of the health bar
        pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y,
                         bar_width, bar_height))  # Red background
        pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y,
                         current_bar_width, bar_height))  # Green foreground

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
        self.health = 4  # Takes 4 hits to die
        self.max_health = 4
        self.cooldown = 100  # Cooldown period for image toggling remains the same


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
        self.health = 6  # Takes 6 hits to die
        self.max_health = 6
        self.cooldown = 100  # Reduced cooldown for faster interaction


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
        self.health = 20  # Takes 20 hits to die
        self.max_health = 20
        self.cooldown = 100  # Faster interaction
