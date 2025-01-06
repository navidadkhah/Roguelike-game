from setting import TILE_SIZE
from collections import deque
import pygame

enemy_image = pygame.image.load("images/Enemy1/Enemy1_1.png")
enemy_image = pygame.transform.scale(enemy_image, (TILE_SIZE, TILE_SIZE))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image1 = enemy_image  # Enemy1 default image
        self.image2 = pygame.image.load("images/Enemy1/Enemy1_2.png")  # Enemy2 image
        self.image2 = pygame.transform.scale(self.image2, (TILE_SIZE, TILE_SIZE))
        self.image = self.image1  # Start with the default image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = 2  # Movement speed
        self.health = 2  # Enemy requires two hits to die
        self.path = []  # Store the path from BFS
        self.time_of_last_change = None  # To store the time when the image last changedsuper().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.health = 3  # Enemy's health

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
        current_time = pygame.time.get_ticks()  # Get the current time in milliseconds

        # Check if enemy collides with player
        if self.rect.colliderect(player.rect):
            if self.image != self.image2:  # Change to image2 only if not already in image2
                self.image = self.image2
                self.time_of_last_change = current_time  # Record the time when the image changed

        # Revert to image1 after 1 second
        if self.time_of_last_change is not None and current_time - self.time_of_last_change > 100:
            self.image = self.image1
            self.time_of_last_change = None  # Reset the timer after reverting the image

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
