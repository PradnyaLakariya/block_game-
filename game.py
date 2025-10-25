import pygame
import random
import sys

# -----------------------------
# Settings
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60
LANES = 3
LANE_WIDTH = SCREEN_WIDTH // LANES

# Colors
BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (50,50,255)
RED = (255,50,50)
GREEN = (0,200,0)
YELLOW = (255,215,0)
CYAN = (0,255,255)
ORANGE = (255,140,0)
GRAY = (180,180,180)
DARK_GRAY = (100,100,100)

# Player
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
JUMP_HEIGHT = 120
GRAVITY = 8
DUCK_HEIGHT = 30

# Obstacle / Coin / Power-up
OBSTACLE_WIDTH = 40
OBSTACLE_HEIGHT = 60
COIN_WIDTH = 20
POWER_WIDTH = 25

# -----------------------------
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Doraemon Subway Surfer (Blocks Version)")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

# -----------------------------
# Player class
class Player:
    def __init__(self):
        self.lane = 1
        self.x = self.lane*LANE_WIDTH + (LANE_WIDTH-PLAYER_WIDTH)//2
        self.y = SCREEN_HEIGHT - PLAYER_HEIGHT - 10
        self.vel_y = 0
        self.is_jumping = False
        self.is_ducking = False
        self.rect = pygame.Rect(self.x, self.y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.color = ORANGE
        self.power = None
        self.power_timer = 0
        self.anim_frame = 0

    def update(self):
        if self.is_jumping:
            self.y += self.vel_y
            self.vel_y += GRAVITY
            if self.y >= SCREEN_HEIGHT - PLAYER_HEIGHT - 10:
                self.y = SCREEN_HEIGHT - PLAYER_HEIGHT - 10
                self.is_jumping = False
                self.vel_y = 0
        self.rect.topleft = (self.x, self.y)
        if self.power_timer > 0:
            self.power_timer -= 1
        else:
            self.power = None
        self.anim_frame = (self.anim_frame + 1) % 20

    def jump(self):
        if not self.is_jumping and not self.is_ducking:
            self.is_jumping = True
            self.vel_y = -JUMP_HEIGHT//10

    def duck(self):
        if not self.is_jumping:
            self.is_ducking = True
            self.rect.height = DUCK_HEIGHT
            self.rect.y = SCREEN_HEIGHT - DUCK_HEIGHT - 10

    def stand_up(self):
        self.is_ducking = False
        self.rect.height = PLAYER_HEIGHT
        self.rect.y = SCREEN_HEIGHT - PLAYER_HEIGHT - 10

    def move_lane(self, lane):
        self.lane = max(0, min(LANES-1, lane))
        self.x = self.lane*LANE_WIDTH + (LANE_WIDTH-PLAYER_WIDTH)//2

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

# -----------------------------
class Entity:
    def __init__(self, lane, kind='obstacle', size='normal', power_type=None):
        self.lane = lane
        self.kind = kind
        self.size = size
        self.power_type = power_type
        self.x = lane*LANE_WIDTH + (LANE_WIDTH-OBSTACLE_WIDTH)//2
        self.y = -OBSTACLE_HEIGHT
        self.speed = 5
        self.rect = pygame.Rect(self.x, self.y, OBSTACLE_WIDTH, OBSTACLE_HEIGHT)

    def update(self):
        self.y += self.speed
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        if self.kind=='coin':
            pygame.draw.circle(surface, YELLOW, self.rect.center, COIN_WIDTH//2)
        elif self.kind=='power':
            color = CYAN if self.power_type=='shield' else BLUE
            pygame.draw.rect(surface, color, self.rect)
        else:
            # Obstacle colors based on size
            if self.size=='low':
                pygame.draw.rect(surface, DARK_GRAY, (self.x, self.y, OBSTACLE_WIDTH, 30))
            elif self.size=='high':
                pygame.draw.rect(surface, BLUE, (self.x, self.y, OBSTACLE_WIDTH, 80))
            else:
                pygame.draw.rect(surface, RED, self.rect)

# -----------------------------
player = Player()
entities = []
score = 0
frame_count = 0
SPAWN_RATE = 50
game_over = False
distance = 0

def spawn_entity():
    kind_roll = random.randint(0,100)
    lane = random.randint(0, LANES-1)
    if kind_roll<60:
        size = random.choice(['low','normal','high'])
        entities.append(Entity(lane, 'obstacle', size))
    elif kind_roll<90:
        entities.append(Entity(lane, 'coin'))
    else:
        power_type = random.choice(['shield','boost'])
        entities.append(Entity(lane, 'power', 'normal', power_type))

def reset_game():
    global entities, score, frame_count, game_over, distance
    entities = []
    score = 0
    frame_count = 0
    distance = 0
    player.x = player.lane*LANE_WIDTH + (LANE_WIDTH-PLAYER_WIDTH)//2
    player.y = SCREEN_HEIGHT - PLAYER_HEIGHT - 10
    player.is_jumping = False
    player.vel_y = 0
    player.stand_up()
    player.power = None
    player.power_timer = 0
    game_over = False

def draw_background():
    screen.fill(WHITE)
    for i in range(1, LANES):
        pygame.draw.line(screen, GRAY, (i*LANE_WIDTH,0),(i*LANE_WIDTH,SCREEN_HEIGHT),2)

# -----------------------------
# Main loop
while True:
    clock.tick(FPS)
    frame_count += 1
    if not game_over:
        distance += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Touchpad / mouse control
    mouse_x, mouse_y = pygame.mouse.get_pos()
    player.move_lane(mouse_x // LANE_WIDTH)
    if pygame.mouse.get_pressed()[0]:
        if mouse_y < player.y:
            player.jump()
        elif mouse_y > player.y + PLAYER_HEIGHT//2:
            player.duck()
    else:
        player.stand_up()

    # Spawn entities
    if frame_count % SPAWN_RATE == 0:
        spawn_entity()

    # Update
    if not game_over:
        player.update()
    for ent in entities:
        if not game_over:
            ent.update()

    # Collision
    for ent in entities:
        if player.rect.colliderect(ent.rect):
            if ent.kind=='obstacle':
                if player.power!='shield':
                    game_over = True
            elif ent.kind=='coin':
                score += 10
                entities.remove(ent)
            elif ent.kind=='power':
                player.power = ent.power_type
                player.power_timer = 300
                entities.remove(ent)

    # Remove off-screen
    entities = [ent for ent in entities if ent.y < SCREEN_HEIGHT]

    # Draw everything
    draw_background()
    for ent in entities:
        ent.draw(screen)
    player.draw(screen)

    # HUD
    score_text = font.render(f"Score: {score}  Distance: {distance}  Power: {player.power or 'None'}", True, BLACK)
    screen.blit(score_text, (10,10))

    if game_over:
        over_text = font.render("GAME OVER! Click to restart", True, BLUE)
        screen.blit(over_text, (50, SCREEN_HEIGHT//2))

    pygame.display.update()
