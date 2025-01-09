from setting import TILE_SIZE
from collections import deque
import pygame

enemy_image = pygame.image.load("images/Enemy1/Enemy1_1.png")
enemy_image = pygame.transform.scale(enemy_image, (TILE_SIZE, TILE_SIZE))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image1 = pygame.image.load("images/Enemy1/Enemy1_1.png").convert_alpha()
        self.image1 = pygame.transform.scale(self.image1, (TILE_SIZE, TILE_SIZE))
        self.image2 = pygame.image.load("images/Enemy1/Enemy1_2.png").convert_alpha()
        self.image2 = pygame.transform.scale(self.image2, (TILE_SIZE, TILE_SIZE))
        self.image = self.image1  # Start with the default image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = 2  # Movement speed
        self.health = 2  # Enemy requires two hits to die
        self.cooldown = 100  # Cooldown period of 2 seconds for image toggling
        self.time_of_last_change = pygame.time.get_ticks()  # Set initial time to current tick
        self.path = []  # Pathfinding


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
        current_time = pygame.time.get_ticks()

        # Ensuring that time_of_last_change is not None
        if self.time_of_last_change is None:
            self.time_of_last_change = pygame.time.get_ticks()

        # Check if enemy collides with player and if the cooldown has passed
        if self.rect.colliderect(player.rect):
            if (current_time - self.time_of_last_change > self.cooldown):
                # Toggle the image based on the current image state
                self.image = self.image2 if self.image == self.image1 else self.image1
                # Apply damage to the player on collision

                player.take_damage()
                self.time_of_last_change = current_time  # Reset the cooldown timer

            # If already in collision and cooldown not passed, ensure no change
            if self.image == self.image2:
                if (current_time - self.time_of_last_change > self.cooldown):
                    self.image = self.image1

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

        # # Apply damage to the player on collision
        # if self.rect.colliderect(player.rect):
        #     player.take_damage()

        # Image reversion outside of cooldown control for more dynamic interaction
        if self.time_of_last_change is not None and current_time - self.time_of_last_change > 100:
            self.image = self.image1
            self.time_of_last_change = None  # Reset timer for reverting image