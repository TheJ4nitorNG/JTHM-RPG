import pygame
import sys
from pygame.locals import *

# Initialize pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
TILE_SIZE = 32
PLAYER_SPEED = 5

# Colors
BLACK = (0, 0, 0)
DARK_GRAY = (20, 20, 20)
BLOOD_RED = (139, 0, 0)
WOOD_BROWN = (139, 69, 19)
PAPER_WHITE = (250, 250, 250)

# Room elements
WALL_THICKNESS = 20
LEFT_WALL = pygame.Rect(WINDOW_WIDTH // 3, 0, WALL_THICKNESS, WINDOW_HEIGHT)
DOOR_GAP = pygame.Rect(WINDOW_WIDTH // 3, WINDOW_HEIGHT // 2 - 50, WALL_THICKNESS, 100)
DESK_RECT = pygame.Rect(WINDOW_WIDTH // 2 - 100, 50, 200, 80)

# Room types
class Room:
    def __init__(self, wall_rects=None, furniture_rects=None, door_rects=None):
        self.wall_rects = wall_rects or []
        self.furniture_rects = furniture_rects or []
        self.door_rects = door_rects or []

    def draw(self, screen):
        # Draw walls
        for wall in self.wall_rects:
            pygame.draw.rect(screen, DARK_GRAY, wall)
        # Draw doors
        for door in self.door_rects:
            pygame.draw.rect(screen, BLACK, door)
        # Draw furniture
        for furniture in self.furniture_rects:
            pygame.draw.rect(screen, WOOD_BROWN, furniture)

# Define rooms
STUDIO_ROOM = Room(
    wall_rects=[LEFT_WALL],
    furniture_rects=[DESK_RECT],
    door_rects=[DOOR_GAP]
)

HALLWAY_ROOM = Room(
    wall_rects=[pygame.Rect(2 * WINDOW_WIDTH // 3, 0, WALL_THICKNESS, WINDOW_HEIGHT), LEFT_WALL],
    door_rects=[pygame.Rect(2 * WINDOW_WIDTH // 3, WINDOW_HEIGHT // 2 - 50, WALL_THICKNESS, 100), 
                pygame.Rect(WINDOW_WIDTH // 3, WINDOW_HEIGHT // 2 - 50, WALL_THICKNESS, 100)]
)

# Current room tracking
current_room = STUDIO_ROOM

# Studio elements
COMICS = [
    pygame.Rect(WINDOW_WIDTH // 2 - 80 + i * 30, 60 + (i % 2) * 20, 20, 25)
    for i in range(8)
]
NAIL_BUNNY = pygame.Rect(WINDOW_WIDTH - 100, 200, 40, 60)
LAMP_ON = True
LAMP_BASE = pygame.Rect(WINDOW_WIDTH // 2 + 80, 40, 20, 10)
LAMP_ARM = [(WINDOW_WIDTH // 2 + 90, 40), (WINDOW_WIDTH // 2 + 120, 60)]
LAMP_HEAD = pygame.Rect(WINDOW_WIDTH // 2 + 110, 55, 30, 15)


def is_near(player_pos, target_rect, distance=50):
    return abs(player_pos[0] - target_rect.centerx) < distance and abs(
        player_pos[1] - target_rect.centery) < distance


# Set up display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('JTHM RPG')
clock = pygame.time.Clock()


# Player class
class Player:

    def __init__(self):
        self.x = WINDOW_WIDTH - 100
        self.y = WINDOW_HEIGHT - 100
        self.width = TILE_SIZE
        self.height = TILE_SIZE * 2
        self.speed = PLAYER_SPEED
        self.color = DARK_GRAY

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def check_collision(self, rect):
        return self.get_rect().colliderect(rect)

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy

        # Create temporary rect for collision testing
        test_rect = pygame.Rect(new_x, new_y, self.width, self.height)

        global current_room

        # Check collisions with current room
        can_move = True

        # Check furniture collisions
        for furniture in current_room.furniture_rects:
            if test_rect.colliderect(furniture):
                can_move = False
                break

        # Check wall collisions and door passages separately
        door_passage = False
        wall_collision = False

        # First check if we're going through a door
        for door in current_room.door_rects:
            if test_rect.colliderect(door):
                door_passage = True
                if current_room == STUDIO_ROOM:
                    current_room = HALLWAY_ROOM
                    self.x = WINDOW_WIDTH // 3 + WALL_THICKNESS + 10
                else:
                    current_room = STUDIO_ROOM
                    self.x = WINDOW_WIDTH // 3 - self.width - 10
                return  # Exit the move function after room transition

        # If not going through a door, check wall collisions
        for wall in current_room.wall_rects:
            if test_rect.colliderect(wall) and not door_passage:
                can_move = False
                break

        if can_move:
            # Apply boundary limits
            self.x = max(0, min(WINDOW_WIDTH - self.width, new_x))
            self.y = max(0, min(WINDOW_HEIGHT - self.height, new_y))

    def draw(self, surface):
        # Draw body
        pygame.draw.rect(surface, self.color,
                         (self.x, self.y, self.width, self.height))
        # Draw head
        pygame.draw.rect(
            surface, self.color,
            (self.x - 4, self.y - 10, self.width + 8, self.height // 2))
        # Draw spiky hair
        for i in range(5):
            pygame.draw.line(surface, self.color,
                             (self.x + (i * 8), self.y - 10),
                             (self.x + 4 + (i * 8), self.y - 20), 2)


# Game state
player = Player()
running = True
interaction_message = ""
interaction_timer = 0

# Game loop
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN and event.key == K_SPACE:
            player_pos = (player.x, player.y)
            if is_near(player_pos, DESK_RECT):
                interaction_message = "WORSHIP MY PORES! HOW DARE YOU LOOK AT MY LEG YOU CLOWN?!"
                interaction_timer = 60
            elif current_room == STUDIO_ROOM and is_near(player_pos, NAIL_BUNNY):
                interaction_message = "You bought me at the pet store, fed me once and nailed me to this wall, 3 YEARS AGO."
                interaction_timer = 60

    # Input handling
    keys = pygame.key.get_pressed()
    dx = (keys[K_RIGHT] - keys[K_LEFT]) * player.speed
    dy = (keys[K_DOWN] - keys[K_UP]) * player.speed
    player.move(dx, dy)

    # Drawing
    screen.fill(BLACK)

    # Draw cluttered room details
    for i in range(0, WINDOW_WIDTH, TILE_SIZE * 2):
        for j in range(0, WINDOW_HEIGHT, TILE_SIZE * 2):
            pygame.draw.rect(screen, BLOOD_RED, (i, j, 2, 2))

    # Draw current room
    current_room.draw(screen)

    # Draw scattered comics only in studio room
    if current_room == STUDIO_ROOM:
        for comic in COMICS:
            pygame.draw.rect(screen, PAPER_WHITE, comic)
            pygame.draw.line(screen, BLACK, (comic.x + 2, comic.y + 5),
                             (comic.x + 18, comic.y + 5), 1)
            pygame.draw.line(screen, BLACK, (comic.x + 2, comic.y + 10),
                             (comic.x + 18, comic.y + 10), 1)
        
        # Draw Nail Bunny
        pygame.draw.rect(screen, DARK_GRAY, NAIL_BUNNY)
        # Draw nail through chest
        pygame.draw.line(screen, PAPER_WHITE, 
                        (NAIL_BUNNY.centerx, NAIL_BUNNY.y + 20),
                        (NAIL_BUNNY.centerx, NAIL_BUNNY.y + 35), 3)

    # Draw lamp
    pygame.draw.rect(screen, DARK_GRAY, LAMP_BASE)
    pygame.draw.line(screen, DARK_GRAY, LAMP_ARM[0], LAMP_ARM[1], 3)
    pygame.draw.rect(screen, DARK_GRAY, LAMP_HEAD)

    # Draw lamp light effect in both rooms
    if LAMP_ON:
        light_surface = pygame.Surface((200, 200), pygame.SRCALPHA)
        pygame.draw.polygon(light_surface, (255, 255, 100, 30), [(0, 0),
                                                                 (200, 0),
                                                                 (100, 200)])
        screen.blit(light_surface, (LAMP_HEAD.x - 85, LAMP_HEAD.y))

    player.draw(screen)

    # Draw interaction message in text box
    if interaction_timer > 0:
        # Draw text box background and border
        text_box_rect = pygame.Rect(50, WINDOW_HEIGHT - 120, WINDOW_WIDTH - 100, 80)
        pygame.draw.rect(screen, DARK_GRAY, text_box_rect)
        pygame.draw.rect(screen, PAPER_WHITE, text_box_rect, 2)
        
        # Render text with word wrap
        font = pygame.font.Font(None, 36)
        words = interaction_message.split()
        lines = []
        current_line = []
        current_width = 0
        
        for word in words:
            word_surface = font.render(word + " ", True, PAPER_WHITE)
            word_width = word_surface.get_width()
            
            if current_width + word_width < text_box_rect.width - 20:
                current_line.append(word)
                current_width += word_width
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_width = word_width
        
        if current_line:
            lines.append(" ".join(current_line))
            
        # Draw text lines
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, PAPER_WHITE)
            screen.blit(text_surface, (text_box_rect.x + 10, text_box_rect.y + 10 + i * 30))
        
        interaction_timer -= 1

    pygame.display.flip()
    clock.tick(60)
