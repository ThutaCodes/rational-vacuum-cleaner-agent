import pygame
import random
import time
import math
from collections import deque

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 700
GRID_SIZE = 4
CELL_SIZE = 100
GRID_OFFSET_X = (WIDTH - GRID_SIZE * CELL_SIZE) // 2
GRID_OFFSET_Y = 150
AGENT_SIZE = 60
DIRT_SIZE = 30
ENERGY_BAR_WIDTH = 200
ENERGY_BAR_HEIGHT = 20

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (0, 200, 0)
RED = (220, 0, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 200, 0)
BROWN = (139, 69, 19)
LIGHT_BLUE = (220, 240, 255)
DARK_BLUE = (0, 80, 160)
LIGHT_GREEN = (220, 255, 220)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rational Vacuum Cleaner Agent")
font = pygame.font.SysFont('Arial', 16)
title_font = pygame.font.SysFont('Arial', 28, bold=True)
subtitle_font = pygame.font.SysFont('Arial', 20, bold=True)

class VacuumAgent:
    def __init__(self):
        # PEAS Description (for reference only)
        # Performance Measure: Clean all dirt and return to home with minimum energy
        # Environment: 4x4 grid world with dirt in some locations
        # Actuators: Movement (N, S, E, W), Suck dirt, Empty bag
        # Sensors: Detect dirt, Detect current location, Detect bag capacity
        
        # Initialize environment (4x4 grid with locations A-P)
        self.locations = [['A', 'B', 'C', 'D'],
                         ['E', 'F', 'G', 'H'],
                         ['I', 'J', 'K', 'L'],
                         ['M', 'N', 'O', 'P']]
        
        # Initialize dirt - ensure dirt is distributed across the grid
        self.dirt = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        # Add dirt to random cells (40-60% of cells)
        num_dirty_cells = random.randint(6, 10)  # 6-10 dirty cells out of 16
        dirty_positions = random.sample([(i, j) for i in range(GRID_SIZE) for j in range(GRID_SIZE)], num_dirty_cells)
        
        for x, y in dirty_positions:
            self.dirt[y][x] = True
        
        # Ensure home location is clean
        self.dirt[0][0] = False
        
        # Agent state
        self.x, self.y = 0, 0  # Start at location A (home)
        self.energy = 100
        self.bag_capacity = 10
        self.bag_current = 0
        self.actions_taken = 0
        self.total_dirt_cleaned = 0
        self.path = []
        self.going_home = False
        self.completed = False
        
        # Action costs
        self.MOVE_COST = 1
        self.SUCK_COST = 1
        self.EMPTY_COST = 1
        
        # History of actions
        self.history = []
        
    def get_current_location(self):
        return self.locations[self.y][self.x]
    
    def is_dirty(self, x=None, y=None):
        if x is None or y is None:
            x, y = self.x, self.y
        return self.dirt[y][x]
    
    def suck_dirt(self):
        if self.is_dirty() and self.bag_current < self.bag_capacity:
            self.dirt[self.y][self.x] = False
            self.bag_current += 1
            self.total_dirt_cleaned += 1
            self.energy -= self.SUCK_COST
            self.actions_taken += 1
            self.history.append(f"Sucked dirt at {self.get_current_location()}")
            return True
        return False
    
    def move(self, direction):
        new_x, new_y = self.x, self.y
        
        if direction == 'N' and self.y > 0:
            new_y -= 1
        elif direction == 'S' and self.y < GRID_SIZE - 1:
            new_y += 1
        elif direction == 'E' and self.x < GRID_SIZE - 1:
            new_x += 1
        elif direction == 'W' and self.x > 0:
            new_x -= 1
        else:
            return False  # Invalid move
        
        self.x, self.y = new_x, new_y
        self.energy -= self.MOVE_COST
        self.actions_taken += 1
        self.history.append(f"Moved {direction} to {self.get_current_location()}")
        return True
    
    def empty_bag(self):
        if self.get_current_location() == 'A':  # Can only empty at home
            self.bag_current = 0
            self.energy -= self.EMPTY_COST
            self.actions_taken += 1
            self.history.append("Emptied bag at home")
            self.going_home = False
            return True
        return False
    
    def should_empty_bag(self):
        return self.bag_current >= self.bag_capacity
    
    def find_path_home(self):
        # Use BFS to find the shortest path home
        start = (self.x, self.y)
        goal = (0, 0)  # Home is at (0,0) - location A
        
        queue = deque([(start, [])])
        visited = set([start])
        
        while queue:
            (x, y), path = queue.popleft()
            
            if (x, y) == goal:
                return path
            
            # Check all four directions
            for dx, dy, direction in [(0, -1, 'N'), (0, 1, 'S'), (1, 0, 'E'), (-1, 0, 'W')]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and (nx, ny) not in visited:
                    queue.append(((nx, ny), path + [direction]))
                    visited.add((nx, ny))
        
        return []  # No path found (shouldn't happen in a connected grid)
    
    def decide_action(self):
        # If all dirt is cleaned and not at home, go home
        if all(not any(row) for row in self.dirt) and self.get_current_location() != 'A':
            if not self.going_home:
                self.path = self.find_path_home()
                self.going_home = True
            if self.path:
                return self.path.pop(0)
            else:
                return 'N'  # Default

        # If bag is full, go home to empty it
        if self.should_empty_bag():
            if self.get_current_location() == 'A':
                return 'EMPTY'
            else:
                if not self.going_home:
                    self.path = self.find_path_home()
                    self.going_home = True
                if self.path:
                    return self.path.pop(0)
                else:
                    return 'EMPTY'

        # If current location is dirty, suck it
        if self.is_dirty():
            return 'SUCK'

        # Otherwise, explore in a systematic pattern
        # Use a modified BFS to find the nearest dirty cell
        start = (self.x, self.y)
        queue = deque([(start, [])])
        visited = set([start])

        while queue:
            (x, y), path = queue.popleft()

            if self.is_dirty(x, y) and (x, y) != (self.x, self.y):
                return path[0] if path else 'SUCK'

            # Check all four directions
            for dx, dy, direction in [(0, -1, 'N'), (0, 1, 'S'), (1, 0, 'E'), (-1, 0, 'W')]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and (nx, ny) not in visited:
                    queue.append(((nx, ny), path + [direction]))
                    visited.add((nx, ny))

        # If no dirt found (shouldn't happen if goal not achieved)
        return 'N'  # Default move
    
    def is_goal_achieved(self):
        # Goal is achieved when all dirt is cleaned and agent is at home
        if self.get_current_location() != 'A':
            return False
        
        for row in self.dirt:
            if any(row):
                return False
                
        return True
    
    def step(self):
        if self.energy <= 0:
            return False
        
        if self.is_goal_achieved():
            self.completed = True
            return False
        
        action = self.decide_action()
        
        if action == 'SUCK':
            self.suck_dirt()
        elif action == 'EMPTY':
            self.empty_bag()
        else:
            self.move(action)
        
        return True
    
    def get_percept_sequence(self):
        return f"[{self.get_current_location()}, {'Dirty' if self.is_dirty() else 'Clean'}]"
    
    def draw(self, screen):
        # Draw grid
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rect = pygame.Rect(
                    GRID_OFFSET_X + x * CELL_SIZE,
                    GRID_OFFSET_Y + y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                
                # Use different color for home location
                if x == 0 and y == 0:
                    pygame.draw.rect(screen, LIGHT_GREEN, rect)
                else:
                    pygame.draw.rect(screen, LIGHT_BLUE, rect)
                    
                pygame.draw.rect(screen, DARK_BLUE, rect, 2)
                
                # Draw location label
                loc_text = subtitle_font.render(self.locations[y][x], True, DARK_BLUE)
                screen.blit(loc_text, (rect.x + CELL_SIZE//2 - loc_text.get_width()//2, 
                                      rect.y + CELL_SIZE//2 - loc_text.get_height()//2))
                
                # Draw dirt if present
                if self.dirt[y][x]:
                    dirt_rect = pygame.Rect(
                        rect.centerx - DIRT_SIZE // 2,
                        rect.centery - DIRT_SIZE // 2 - 10,
                        DIRT_SIZE,
                        DIRT_SIZE
                    )
                    pygame.draw.ellipse(screen, BROWN, dirt_rect)
        
        # Draw agent
        agent_rect = pygame.Rect(
            GRID_OFFSET_X + self.x * CELL_SIZE + (CELL_SIZE - AGENT_SIZE) // 2,
            GRID_OFFSET_Y + self.y * CELL_SIZE + (CELL_SIZE - AGENT_SIZE) // 2,
            AGENT_SIZE,
            AGENT_SIZE
        )
        pygame.draw.rect(screen, RED, agent_rect, 0, 10)
        # Draw vacuum icon on agent
        pygame.draw.circle(screen, BLUE, 
                          (agent_rect.centerx, agent_rect.centery), 
                          AGENT_SIZE // 3)
        
        # Draw info panel
        info_rect = pygame.Rect(20, 20, WIDTH - 40, 110)
        pygame.draw.rect(screen, (240, 240, 240), info_rect, 0, 10)
        pygame.draw.rect(screen, DARK_BLUE, info_rect, 2, 10)
        
        # Draw energy bar
        energy_text = font.render("ENERGY", True, DARK_BLUE)
        screen.blit(energy_text, (40, 35))
        
        energy_bg = pygame.Rect(120, 35, ENERGY_BAR_WIDTH, ENERGY_BAR_HEIGHT)
        pygame.draw.rect(screen, GRAY, energy_bg, 0, 5)
        
        energy_level = max(0, min(self.energy, 100))
        energy_fill = pygame.Rect(120, 35, ENERGY_BAR_WIDTH * energy_level / 100, ENERGY_BAR_HEIGHT)
        color = GREEN if energy_level > 30 else YELLOW if energy_level > 10 else RED
        pygame.draw.rect(screen, color, energy_fill, 0, 5)
        
        pygame.draw.rect(screen, BLACK, energy_bg, 1, 5)
        
        energy_value = font.render(f"{self.energy}/100", True, DARK_BLUE)
        screen.blit(energy_value, (120 + ENERGY_BAR_WIDTH + 10, 35))
        
        # Draw bag capacity
        bag_text = font.render(f"BAG: {self.bag_current}/{self.bag_capacity}", True, DARK_BLUE)
        screen.blit(bag_text, (40, 65))
        
        # Draw actions taken
        actions_text = font.render(f"ACTIONS: {self.actions_taken}", True, DARK_BLUE)
        screen.blit(actions_text, (200, 65))
        
        # Draw dirt cleaned
        dirt_text = font.render(f"DIRT CLEANED: {self.total_dirt_cleaned}", True, DARK_BLUE)
        screen.blit(dirt_text, (40, 95))
        
        # Draw current location and status
        status = "MISSION COMPLETE!" if self.completed else "WORKING..."
        status_color = GREEN if self.completed else DARK_BLUE
        status_text = font.render(f"LOCATION: {self.get_current_location()} | STATUS: {status}", True, status_color)
        screen.blit(status_text, (200, 95))
        
        # Draw history panel
        history_rect = pygame.Rect(20, HEIGHT - 150, WIDTH - 40, 120)
        pygame.draw.rect(screen, (240, 240, 240), history_rect, 0, 10)
        pygame.draw.rect(screen, DARK_BLUE, history_rect, 2, 10)
        
        history_title = font.render("RECENT ACTIONS:", True, DARK_BLUE)
        screen.blit(history_title, (40, HEIGHT - 140))
        
        for i, action in enumerate(self.history[-6:]):
            action_text = font.render(action, True, BLACK)
            screen.blit(action_text, (40, HEIGHT - 120 + i * 18))

def draw_instructions(screen):
    instructions = [
        "SPACE: Step manually",
        "A: Toggle auto mode",
        "UP/DOWN: Change speed",
        "R: Reset simulation"
    ]
    
    for i, text in enumerate(instructions):
        instr_text = font.render(text, True, DARK_BLUE)
        screen.blit(instr_text, (WIDTH - 180, 150 + i * 25))

def main():
    agent = VacuumAgent()
    clock = pygame.time.Clock()
    running = True
    auto_mode = False
    speed = 1  # Steps per second
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    agent.step()
                elif event.key == pygame.K_a:
                    auto_mode = not auto_mode
                elif event.key == pygame.K_UP:
                    speed = min(10, speed + 1)
                elif event.key == pygame.K_DOWN:
                    speed = max(1, speed - 1)
                elif event.key == pygame.K_r:
                    agent = VacuumAgent()  # Reset
        
        screen.fill(WHITE)
        
        # Draw title
        title = title_font.render("Rational Vacuum Cleaner Agent", True, DARK_BLUE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
        
        # Draw speed indicator
        speed_text = font.render(f"Speed: {speed} step{'s' if speed != 1 else ''}/sec | Mode: {'Auto' if auto_mode else 'Manual'}", True, DARK_BLUE)
        screen.blit(speed_text, (WIDTH // 2 - speed_text.get_width() // 2, 85))
        
        # Draw instructions
        draw_instructions(screen)
        
        # Update agent if in auto mode
        if auto_mode and not agent.completed and agent.energy > 0:
            for _ in range(speed):
                if not agent.step():
                    break
        
        agent.draw(screen)
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()

if __name__ == "__main__":
    main()