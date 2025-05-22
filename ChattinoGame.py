import pygame
import random

# Step 1: Constants and Initialization
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jetpack Escape")
WHITE = (255, 255, 255)
FPS = 60
clock = pygame.time.Clock()

# Colors
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
# GRAY defined with an alpha value for transparency
GRAY = (128, 128, 128, 150)

# Game parameters
gravity = 0.5          # slower descent
jump_power = -8
velocity = 0
obstacle_width = 50
obstacle_speed = 5
obstacle_gap = 200
score = 0
is_lunging = False
lunge_timer = 0

gates_cleared = 0  # Track how many gates have been cleared

enemy_active = False  # Track if the enemy is active

lunge_type = 'straight'  # Track current lunge type
zigzag_direction = 1     # For zigzag lunge

# Game state (menu or playing)
state = "menu"  

# Step 2: Load Assets
background = pygame.image.load("background.png")
character_img = pygame.image.load("jetpack_character.png")
enemy_img = pygame.image.load("enemy.png")
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
character_img = pygame.transform.scale(character_img, (50, 50))
enemy_img = pygame.transform.scale(enemy_img, (40, 40))

# Step 3: Game Objects
character_rect = character_img.get_rect(topleft=(100, SCREEN_HEIGHT // 2))
enemy_rect = enemy_img.get_rect(topleft=(-50, SCREEN_HEIGHT // 2))  # enemy starts off-screen left
obstacles = []
font = pygame.font.Font(None, 36)

# Scrolling background setup
bg_x1 = 0
bg_x2 = SCREEN_WIDTH

# Define Tunnel Area (a rectangle at the bottom of the screen)
tunnel_rect = pygame.Rect(0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100)

# Menu Screen Function
def show_menu():
    screen.fill(WHITE)
    font_large = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 36)
    
    title_text = font_large.render("Jetpack Escape", True, BLACK)
    start_text = font_small.render("Start Game", True, BLACK)
    quit_text = font_small.render("Quit", True, BLACK)
    
    # Define button areas for Start and Quit
    start_button = pygame.Rect((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50), (200, 50))
    quit_button = pygame.Rect((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20), (200, 50))
    
    pygame.draw.rect(screen, GREEN, start_button)
    pygame.draw.rect(screen, GREEN, quit_button)
    
    screen.blit(title_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 3))
    screen.blit(start_text, (start_button.x + 40, start_button.y + 10))
    screen.blit(quit_text, (quit_button.x + 65, quit_button.y + 10))
    
    pygame.display.flip()
    return start_button, quit_button

# Game Over Screen Function
def game_over_screen():
    global is_lunging, lunge_timer, gates_cleared, enemy_active
    screen.fill(WHITE)
    font_large = pygame.font.Font(None, 72)
    text = font_large.render("Game Over!", True, BLACK)
    button_text = font.render("Try Again", True, BLACK)
    button_rect = pygame.Rect((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2), (200, 50))
    
    screen.blit(text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 3))
    pygame.draw.rect(screen, GREEN, button_rect)
    screen.blit(button_text, (button_rect.x + 25, button_rect.y + 10))
    pygame.display.flip()
    
    # Reset enemy state and gates_cleared on game over
    enemy_rect.topleft = (-50, SCREEN_HEIGHT // 2)
    is_lunging = False
    lunge_timer = 0
    gates_cleared = 0
    enemy_active = False
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
                waiting = False

# Main Game Loop
running = True
while running:
    if state == "menu":
        start_button, quit_button = show_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    state = "playing"
                if quit_button.collidepoint(event.pos):
                    running = False

    elif state == "playing":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Handle input: jump on SPACE press
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and velocity > -5:
            velocity = jump_power

        # Update character physics: add gravity and apply a cap + air resistance
        velocity += gravity
        if velocity > 5:
            velocity = 5
        if velocity > 0:
            velocity -= 0.1
        character_rect.y += velocity
        if character_rect.y > SCREEN_HEIGHT - character_rect.height:
            character_rect.y = SCREEN_HEIGHT - character_rect.height
        if character_rect.y < 0:
            character_rect.y = 0

        # Generate obstacles as needed
        if len(obstacles) == 0 or obstacles[-1].x < SCREEN_WIDTH - 300:
            obstacle_y = random.randint(100, SCREEN_HEIGHT - obstacle_gap - 100)
            top_obstacle = pygame.Rect(SCREEN_WIDTH, 0, obstacle_width, obstacle_y)
            bottom_obstacle = pygame.Rect(SCREEN_WIDTH, obstacle_y + obstacle_gap, obstacle_width, SCREEN_HEIGHT - obstacle_y - obstacle_gap)
            obstacles.append(top_obstacle)
            obstacles.append(bottom_obstacle)

        # Move obstacles leftwards
        for obstacle in obstacles:
            obstacle.x -= obstacle_speed
        obstacles = [obs for obs in obstacles if obs.x + obstacle_width > 0]

        # Tunnel penalty logic:
        # If the player's center is inside the tunnel area and the horizontal range of an obstacle overlaps with the character,
        # deduct 2 points and remove that obstacle so the penalty is applied only once.
        for obstacle in obstacles[:]:
            if tunnel_rect.collidepoint(character_rect.center) and obstacle.x < character_rect.x < obstacle.x + obstacle_width:
                score -= 2
                obstacles.remove(obstacle)

        # Only check for obstacle collisions if the character is NOT in the tunnel
        if not tunnel_rect.colliderect(character_rect):
            for obstacle in obstacles:
                if character_rect.colliderect(obstacle):
                    game_over_screen()
                    score = 0
                    obstacles = []
                    enemy_rect.topleft = (-50, SCREEN_HEIGHT // 2)

        # Only update/draw enemy if 3 or more gates have been cleared
        if gates_cleared >= 3:
            # Activate enemy if just reached 3 gates
            if not enemy_active:
                # Spawn enemy at vertical center of play area (not in tunnel)
                enemy_y = SCREEN_HEIGHT // 2 - enemy_rect.height // 2
                enemy_rect.topleft = (-50, enemy_y)
                enemy_active = True
                is_lunging = True
                lunge_timer = 30
                lunge_type = 'straight'
                zigzag_direction = 1
            if enemy_active:
                # Choose lunge type for each new lunge after 5 gates
                if is_lunging and enemy_rect.x == -50 and gates_cleared >= 8:
                    lunge_type = random.choice(['straight', 'up', 'down', 'zigzag'])
                    zigzag_direction = 1
                # Enemy lunges right until it reaches 1/3 of the screen, then returns left
                if is_lunging:
                    enemy_rect.x += 7
                    # Lunge movement types
                    if gates_cleared >= 8:
                        if lunge_type == 'up':
                            enemy_rect.y -= 4
                        elif lunge_type == 'down':
                            enemy_rect.y += 4
                        elif lunge_type == 'zigzag':
                            enemy_rect.y += 6 * zigzag_direction
                            if (enemy_rect.y <= 0) or (enemy_rect.y >= SCREEN_HEIGHT - enemy_rect.height - 100):
                                zigzag_direction *= -1
                    # Clamp y to stay in play area (not in tunnel or off top)
                    if enemy_rect.y < 0:
                        enemy_rect.y = 0
                    if enemy_rect.y > SCREEN_HEIGHT - enemy_rect.height - 100:
                        enemy_rect.y = SCREEN_HEIGHT - enemy_rect.height - 100
                    # Lunge target: 1/3 of the screen
                    if enemy_rect.x >= SCREEN_WIDTH // 3:
                        is_lunging = False
                else:
                    enemy_rect.x -= 7
                    if enemy_rect.x <= -50:
                        is_lunging = True
                        # Optionally, randomize y again for next lunge
                        enemy_y = SCREEN_HEIGHT // 2 - enemy_rect.height // 2
                        enemy_rect.y = enemy_y
                # Check for collision with character at all times when enemy is active
                if character_rect.colliderect(enemy_rect):
                    game_over_screen()
                    score = 0
                    gates_cleared = 0
                    obstacles = []
                    enemy_rect.topleft = (-50, SCREEN_HEIGHT // 2)
                    enemy_active = False
                print(f"Enemy x: {enemy_rect.x}, y: {enemy_rect.y}, is_lunging: {is_lunging}, enemy_active: {enemy_active}, lunge_type: {lunge_type}")

        # Scoring: if the player passes the obstacle's right side exactly, increase score
        for obstacle in obstacles:
            if obstacle.x + obstacle_width == character_rect.x:
                score += 1
                gates_cleared += 1

        # Render everything
        screen.fill(WHITE)
        bg_x1 -= obstacle_speed
        bg_x2 -= obstacle_speed
        if bg_x1 < -SCREEN_WIDTH:
            bg_x1 = SCREEN_WIDTH
        if bg_x2 < -SCREEN_WIDTH:
            bg_x2 = SCREEN_WIDTH

        screen.blit(background, (bg_x1, 0))
        screen.blit(background, (bg_x2, 0))
        screen.blit(character_img, character_rect.topleft)
        for obstacle in obstacles:
            pygame.draw.rect(screen, GREEN, obstacle)

        # Draw the transparent tunnel using a surface with an alpha channel
        tunnel_surface = pygame.Surface((SCREEN_WIDTH, 100), pygame.SRCALPHA)
        tunnel_surface.fill(GRAY)
        screen.blit(tunnel_surface, (0, SCREEN_HEIGHT - 100))

        # Draw enemy on top of everything
        if enemy_active and gates_cleared >= 3:
            screen.blit(enemy_img, enemy_rect.topleft)

        # Display score
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

pygame.quit() 