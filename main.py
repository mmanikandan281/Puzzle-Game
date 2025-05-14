import pygame
import random
import sys
import time
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 100

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Grid sizes for levels
levels = [3, 4, 5, 6, 7]
current_level = 0

# Load images safely
def safe_load_image(path):
    if os.path.exists(path):
        return pygame.image.load(path)
    else:
        print(f"[ERROR] Missing image: {path}")
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surface.fill(RED)
        font = pygame.font.Font(None, 24)
        text = font.render("Missing", True, WHITE)
        surface.blit(text, (10, TILE_SIZE // 3))
        return surface

# Build level image paths and load them
image_folder = 'images'
level_images = [
    [os.path.join(image_folder, f'level{lvl}_image{i}.jpg') for i in range(1, 6)]
    for lvl in range(1, 6)
]
loaded_images = [[safe_load_image(img) for img in level] for level in level_images]

# Set up the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sliding Puzzle Game")

# Font
font = pygame.font.Font(None, 36)

# Menu
def draw_menu(images):
    screen.fill(WHITE)
    text = font.render("Choose an image to start the level:", True, BLACK)
    screen.blit(text, (20, 20))
    for i, img in enumerate(images):
        scaled_img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        rect = pygame.Rect(20 + i * (TILE_SIZE + 10), 70, TILE_SIZE, TILE_SIZE)
        screen.blit(scaled_img, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)
    pygame.display.flip()

def handle_menu_events(images):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                for i in range(len(images)):
                    rect = pygame.Rect(20 + i * (TILE_SIZE + 10), 70, TILE_SIZE, TILE_SIZE)
                    if rect.collidepoint(x, y):
                        return images[i]

# Puzzle Logic
def create_tiles(grid_size):
    # Create tiles with their target positions
    tiles = []
    for y in range(grid_size):
        for x in range(grid_size):
            if x == grid_size - 1 and y == grid_size - 1:
                # Skip the last position for the empty tile
                continue
            tiles.append((x, y))
    
    # Shuffle the tiles (except the empty tile)
    shuffled = tiles.copy()
    random.shuffle(shuffled)
    
    # The empty position is always the last one initially
    empty_pos = (grid_size - 1, grid_size - 1)
    
    return shuffled, empty_pos

def create_grid(tiles, grid_size, empty_pos):
    """Create a 2D grid from the list of tiles and empty position."""
    grid = [[None for _ in range(grid_size)] for _ in range(grid_size)]
    
    # Fill in all non-empty positions
    for i, tile in enumerate(tiles):
        x = i % grid_size
        y = i // grid_size
        if (x, y) != empty_pos:
            grid[y][x] = tile
    
    # Mark the empty position as None
    grid[empty_pos[1]][empty_pos[0]] = None
    
    return grid

def get_empty_pos(grid):
    for y, row in enumerate(grid):
        for x, tile in enumerate(row):
            if tile is None:
                return (x, y)

def draw_grid(image, grid, grid_size, empty_pos):
    tile_width = image.get_width() // grid_size
    tile_height = image.get_height() // grid_size
    
    # Draw background grid
    for y in range(grid_size):
        for x in range(grid_size):
            rect = pygame.Rect(x * tile_width, y * tile_height, tile_width, tile_height)
            pygame.draw.rect(screen, (200, 200, 200), rect)
            pygame.draw.rect(screen, BLACK, rect, 1)
    
    # Draw tiles
    for y in range(grid_size):
        for x in range(grid_size):
            # Skip drawing the empty tile
            if (x, y) == empty_pos:
                continue
                
            tile = grid[y][x]
            if tile is None:
                continue
                
            try:
                # Get the original position of this tile in the source image
                src_x, src_y = tile
                
                # Source rectangle (where to get the image from)
                source_rect = pygame.Rect(src_x * tile_width, src_y * tile_height, tile_width, tile_height)
                
                # Destination rectangle (where to draw on screen)
                dest_rect = pygame.Rect(x * tile_width, y * tile_height, tile_width, tile_height)
                
                # Draw the tile
                tile_surface = image.subsurface(source_rect)
                screen.blit(tile_surface, dest_rect)
                pygame.draw.rect(screen, BLACK, dest_rect, 1)  # Draw border
                
                # Debug - draw the tile coordinates
                debug_font = pygame.font.Font(None, 20)
                debug_text = debug_font.render(f"{src_x},{src_y}", True, RED)
                screen.blit(debug_text, (x * tile_width + 5, y * tile_height + 5))
                
            except Exception as e:
                print(f"[ERROR] Failed to draw tile at ({x}, {y}):", e)
                # Draw error indicator
                error_rect = pygame.Rect(x * tile_width, y * tile_height, tile_width, tile_height)
                pygame.draw.rect(screen, RED, error_rect)
                pygame.draw.line(screen, BLACK, (x * tile_width, y * tile_height), 
                                (x * tile_width + tile_width, y * tile_height + tile_height), 2)
                pygame.draw.line(screen, BLACK, (x * tile_width + tile_width, y * tile_height), 
                                (x * tile_width, y * tile_height + tile_height), 2)

def draw_reference_image(image, grid_size):
    ref_size = int(TILE_SIZE * 3)
    scaled_reference = pygame.transform.scale(image, (ref_size, ref_size))
    screen.blit(scaled_reference, (WIDTH - ref_size - 20, 20))
    pygame.draw.rect(screen, BLACK, (WIDTH - ref_size - 20, 20, ref_size, ref_size), 2)

def move_tile(x, y, grid, empty_pos):
    empty_x, empty_y = empty_pos
    if (x == empty_x and abs(y - empty_y) == 1) or (y == empty_y and abs(x - empty_x) == 1):
        grid[empty_y][empty_x], grid[y][x] = grid[y][x], grid[empty_y][empty_x]
        return (x, y)
    return empty_pos

def is_solved(grid, grid_size):
    """Check if the puzzle is solved by comparing each tile's position."""
    for y in range(grid_size):
        for x in range(grid_size):
            # The bottom-right corner should be empty
            if x == grid_size - 1 and y == grid_size - 1:
                if grid[y][x] is not None:
                    return False
                continue
                
            # Otherwise check if each tile is in its correct position
            tile = grid[y][x]
            if tile != (x, y):
                return False
    
    return True

def display_confetti():
    colors = [RED, GREEN, BLUE, YELLOW]
    for _ in range(100):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        pygame.draw.circle(screen, random.choice(colors), (x, y), 5)
    pygame.display.flip()
    time.sleep(2)

# Game loop
def game_loop(image, grid_size):
    tiles, empty_pos = create_tiles(grid_size)
    grid = create_grid(tiles, grid_size, empty_pos)
    dragging = False
    drag_tile = None
    tile_size = image.get_width() // grid_size
    
    # For debugging
    print(f"Grid size: {grid_size}")
    print(f"Tile size: {tile_size}")
    print(f"Empty position: {empty_pos}")
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = event.pos
                    grid_x = x // tile_size
                    grid_y = y // tile_size
                    if 0 <= grid_x < grid_size and 0 <= grid_y < grid_size:
                        # Check if a tile can be moved
                        if (abs(grid_x - empty_pos[0]) == 1 and grid_y == empty_pos[1]) or \
                           (abs(grid_y - empty_pos[1]) == 1 and grid_x == empty_pos[0]):
                            # Move the tile
                            grid[empty_pos[1]][empty_pos[0]] = grid[grid_y][grid_x]
                            grid[grid_y][grid_x] = None
                            empty_pos = (grid_x, grid_y)
                            print(f"Moved tile to {empty_pos}")

        screen.fill(WHITE)
        
        # Draw the grid
        draw_grid(image, grid, grid_size, empty_pos)
        
        # Draw the reference image
        draw_reference_image(image, grid_size)
        
        # Show instructions
        instructions = font.render("Click adjacent tiles to move them", True, BLACK)
        screen.blit(instructions, (20, HEIGHT - 50))

        pygame.display.flip()

        if is_solved(grid, grid_size):
            display_confetti()
            return

# Show all level thumbnails
def show_level_images(level_images):
    screen.fill(WHITE)
    text = font.render("Level Images", True, BLACK)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 20))

    for level_index, images in enumerate(level_images):
        for img_index, img in enumerate(images):
            scaled_img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
            rect = pygame.Rect(20 + img_index * (TILE_SIZE + 10), 70 + level_index * (TILE_SIZE + 10), TILE_SIZE, TILE_SIZE)
            screen.blit(scaled_img, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)

    pygame.display.flip()
    time.sleep(2)

# Main
if __name__ == "__main__":
    while current_level < len(levels):
        show_level_images(loaded_images)

        # Let player choose image
        chosen_image = None
        while not chosen_image:
            draw_menu(loaded_images[current_level])
            chosen_image = handle_menu_events(loaded_images[current_level])

        print(f"Level {current_level + 1} selected image.")

        # Start the puzzle
        grid_size = levels[current_level]
        scaled_image = pygame.transform.scale(chosen_image, (grid_size * TILE_SIZE, grid_size * TILE_SIZE))
        game_loop(scaled_image, grid_size)

        # Show level complete message
        current_level += 1
        if current_level < len(levels):
            text = font.render(f"Level {current_level} Completed!", True, BLACK)
        else:
            text = font.render("Congratulations! All levels completed!", True, BLACK)
        screen.fill(WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
        pygame.display.flip()
        time.sleep(2)

    pygame.quit()
    sys.exit()