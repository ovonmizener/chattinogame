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
GRAY = (128, 128, 128)

# Game parameters
gravity = 0.5  # Reduced gravity for slower descent
jump_power = -15
velocity = 0
obstacle_width = 50
obstacle_speed = 5
obstacle_gap = 200
score = 0
is_lunging = False
lunge_timer = 0

# Game state
state = "menu"  # Start with the menu

# Step 2: Load Assets
background = pygame.image.load("background.png")
character_img = pygame.image.load("jetpack_character.png")
enemy_img = pygame.image.load("enemy.png")
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
character_img = pygame.transform.scale(character_img, (50, 50))
enemy_img = pygame.transform.scale(enemy_img, (40, 40))

# Step 3: Game Objects
character_rect = character_img.get_rect(topleft=(100, SCREEN_HEIGHT // 2))
enemy_rect = enemy_img.get_rect(topleft=(50, SCREEN_HEIGHT // 2))  # Start enemy behind the character
obstacles = []
font = pygame.font.Font(None, 36)  # Default font for score

# Scrolling background setup
bg_x1 = 0
bg_x2 = SCREEN_WIDTH

# Define Tunnel Area
tunnel_rect = pygame.Rect(0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100)  # Tunnel at the bottom of the screen

# Menu Screen Function
def show_menu():
    screen.fill(WHITE)
    font_large = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 36)
    
    title_text = font_large.render("Jetpack Escape", True, BLACK)
    start_text = font_small.render("Start Game", True, BLACK)
    quit_text = font_small.render("Quit", True, BLACK)
    
    # Button areas
    start_button = pygame.Rect((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50), (200, 50))
    quit_button = pygame.Rect((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20), (200, 50))
    
    # Draw buttons
    pygame.draw.rect(screen, GREEN, start_button)
    pygame.draw.rect(screen, GREEN, quit_button)
    
    # Render text
    screen.blit(title_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 3))
    screen.blit(start_text, (start_button.x + 40, start_button.y + 10))
    screen.blit(quit_text, (quit_button.x + 65, quit_button.y + 10))
    
    pygame.display.flip()
    
    return start_button, quit_button

# Game Over Screen Function
def game_over_screen():
    screen.fill(WHITE)
    font_large = pygame.font.Font(None, 72)
    text = font_large.render("Game Over!", True, BLACK)
    button_text = font.render("Try Again", True, BLACK)
    button_rect = pygame.Rect((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2), (200, 50))

    screen.blit(text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 3))
    pygame.draw.rect(screen, GREEN, button_rect)
    screen.blit(button_text, (button_rect.x + 25, button_rect.y + 10))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
                waiting = False

# Step 4: Main Game Loop
running = True
while running:
    if state == "menu":
        start_button, quit_button = show_menu()  # Display menu screen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):  # Start Game button
                    state = "playing"
                if quit_button.collidepoint(event.pos):  # Quit button
                    running = False

    elif state == "playing":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Handle input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and velocity > -5:  # Flappy Bird-style jump
            velocity = jump_power

        # Update character position with slower descent
        velocity += gravity
        if velocity > 5:  # Cap downward speed
            velocity = 5
        if velocity > 0:  # Apply air resistance when falling
            velocity -= 0.1

        character_rect.y += velocity
        if character_rect.y > SCREEN_HEIGHT - character_rect.height:
            character_rect.y = SCREEN_HEIGHT - character_rect.height
        if character_rect.y < 0:
            character_rect.y = 0

        # Move enemy towards character with lunging
        if not is_lunging and random.randint(1, 200) == 1:  # Random chance to lunge
            is_lunging = True
            lunge_timer = 30  # Lunge lasts for 30 frames
        if is_lunging:
            enemy_rect.x += 7  # Boost speed for lunge
            lunge_timer -= 1
            if lunge_timer <= 0:
                is_lunging = False
        else:
            if enemy_rect.x < character_rect.x - 150:  # Maintain distance
                enemy_rect.x += 2
            else:
                enemy_rect.x -= 1
        if enemy_rect.x < 0:  # Prevent moving offscreen
            enemy_rect.x = 0

        # Generate obstacles
        if len(obstacles) == 0 or obstacles[-1].x < SCREEN_WIDTH - 300:
            obstacle_y = random.randint(100, SCREEN_HEIGHT - obstacle_gap - 100)
            top_obstacle = pygame.Rect(SCREEN_WIDTH, 0, obstacle_width, obstacle_y)
            bottom_obstacle = pygame.Rect(SCREEN_WIDTH, obstacle_y + obstacle_gap, obstacle_width, SCREEN_HEIGHT - obstacle_y - obstacle_gap)
            obstacles.append(top_obstacle)
            obstacles.append(bottom_obstacle)

        # Move obstacles
        for obstacle in obstacles:
            obstacle.x -= obstacle_speed
        obstacles = [obs for obs in obstacles if obs.x + obstacle_width > 0]  # Remove offscreen obstacles

        # Tunnel logic: Check if player enters tunnel and passes gate
        if tunnel_rect.colliderect(character_rect):
            score -= 2  # Penalize score for entering tunnel

        # Check for collision
        for obstacle in obstacles:
            if character_rect.colliderect(obstacle):
                game_over_screen()
                score = 0  # Reset score
                obstacles = []  # Reset obstacles
                enemy_rect.topleft = (-50, SCREEN_HEIGHT // 2)  # Reset enemy

        if character_rect.colliderect(enemy_rect):  # Collision with enemy
            game_over_screen()
            score = 0  # Reset score
            obstacles = []  # Reset obstacles
            enemy_rect.topleft = (-50, SCREEN_HEIGHT // 2)  # Reset enemy

        # Check if character passed an obstacle for scoring
        for obstacle in obstacles:
            if obstacle.x + obstacle_width == character_rect.x:  # Passes obstacle
                score += 1

        # Render graphics
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
        screen.blit(enemy_img, enemy_rect.topleft)

        for obstacle in obstacles:
            pygame.draw.rect(screen, GREEN, obstacle)

        # Draw the tunnel
        pygame.draw.rect(screen, GRAY, tunnel_rect)  # Gray tunnel area

        # Display score
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

pygame.quit()