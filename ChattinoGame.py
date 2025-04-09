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

# Game parameters
gravity = 1
jump_power = -15
velocity = 0
obstacle_width = 50
obstacle_speed = 5
obstacle_gap = 200
score = 0

# Step 2: Load Assets
background = pygame.image.load("background.png")
character_img = pygame.image.load("jetpack_character.png")
enemy_img = pygame.image.load("enemy.png")
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
character_img = pygame.transform.scale(character_img, (50, 50))
enemy_img = pygame.transform.scale(enemy_img, (40, 40))

# Step 3: Game Objects
character_rect = character_img.get_rect(topleft=(100, SCREEN_HEIGHT // 2))
enemy_rect = enemy_img.get_rect(topleft=(SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2))
obstacles = []
font = pygame.font.Font(None, 36)  # Default font for score

# Scrolling background setup
bg_x1 = 0
bg_x2 = SCREEN_WIDTH

# Step 4: Game Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] and velocity > -5:  # Flappy Bird-style jump
        velocity = jump_power

    # Update character position
    velocity += gravity
    character_rect.y += velocity
    if character_rect.y > SCREEN_HEIGHT - character_rect.height:
        character_rect.y = SCREEN_HEIGHT - character_rect.height
    if character_rect.y < 0:
        character_rect.y = 0

    # Move enemy towards character
    if enemy_rect.x < character_rect.x:
        enemy_rect.x += 2
    else:
        enemy_rect.x -= 2

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

    # Check for collision
    for obstacle in obstacles:
        if character_rect.colliderect(obstacle):
            print("Game Over!")
            running = False

    if character_rect.colliderect(enemy_rect):
        print("Game Over!")
        running = False

    # Check if character passed an obstacle for scoring
    for obstacle in obstacles:
        if obstacle.x + obstacle_width == character_rect.x:
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

    # Display score
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()  