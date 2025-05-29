import pygame
import random
import math

# Step 1: Constants and Initialization
pygame.init()
pygame.mixer.init()
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
enemy_direction = [0, 0]  # [x, y] direction vector for enemy movement
enemy_speed = 3  # Base speed for enemy movement

lives = 3  # Player starts with 3 lives
last_scored_obstacle = None  # Track the last obstacle that was scored

lunge_type = 'straight'  # Track current lunge type
zigzag_direction = 1     # For zigzag lunge

# Game state (menu, mode_select, traditional, or continuous)
state = "menu"
game_mode = "traditional"  # or "continuous"

# Continuous mode parameters
continuous_ground_height = 50
continuous_obstacle_speed = 5
continuous_obstacle_width = 30
continuous_obstacle_height = 50
continuous_obstacles = []
continuous_score = 0
continuous_start_time = 0
continuous_jump_power = -15
continuous_gravity = 0.8
continuous_ground_y = SCREEN_HEIGHT - continuous_ground_height
continuous_obstacle_spawn_chance = 0.02  # 2% chance per frame to spawn obstacle
continuous_floating_obstacle_chance = 0.3  # 30% chance for floating obstacle
continuous_speed_boost = 10  # Speed boost when landing on floating obstacle
continuous_speed_boost_duration = 60  # Frames the speed boost lasts
continuous_can_double_jump = False
continuous_has_double_jumped = False
continuous_speed_boost_timer = 0
continuous_current_speed = continuous_obstacle_speed
continuous_game_started = False  # New flag to track if game has started

# Step 2: Load Assets
background = pygame.image.load("background.png")
character_img = pygame.image.load("jetpack_character.png")
enemy_img = pygame.image.load("enemy.png")
jump_sound = pygame.mixer.Sound("jump.wav")
jump_sound.set_volume(0.3)
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
character_img = pygame.transform.scale(character_img, (50, 50))
enemy_img = pygame.transform.scale(enemy_img, (90, 90))

# Step 3: Game Objects
character_rect = character_img.get_rect(topleft=(100, SCREEN_HEIGHT // 2))
enemy_rect = enemy_img.get_rect(topleft=(SCREEN_WIDTH - 150, SCREEN_HEIGHT // 2 - 45))  # Spawn enemy on the right side
obstacles = []
font = pygame.font.Font(None, 36)

# Scrolling background setup
bg_x1 = 0
bg_x2 = SCREEN_WIDTH

# Define Tunnel Area (a rectangle at the bottom of the screen)
tunnel_rect = pygame.Rect(0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100)

game_volume = 0.3
jump_sound.set_volume(game_volume)

# Menu Screen Function
def show_menu():
    screen.fill(WHITE)
    font_large = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 36)
    
    title_text = font_large.render("Jetpack Escape", True, BLACK)
    start_text = font_small.render("Start Game", True, BLACK)
    quit_text = font_small.render("Quit", True, BLACK)
    credits_text = font_small.render("Credits", True, BLACK)
    
    # Define button areas for Start, Credits, and Quit
    start_button = pygame.Rect((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50), (200, 50))
    credits_button = pygame.Rect((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20), (200, 50))
    quit_button = pygame.Rect((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 90), (200, 50))
    
    pygame.draw.rect(screen, GREEN, start_button)
    pygame.draw.rect(screen, GREEN, credits_button)
    pygame.draw.rect(screen, GREEN, quit_button)
    
    screen.blit(title_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 3))
    screen.blit(start_text, (start_button.x + 40, start_button.y + 10))
    screen.blit(credits_text, (credits_button.x + 55, credits_button.y + 10))
    screen.blit(quit_text, (quit_button.x + 65, quit_button.y + 10))
    
    pygame.display.flip()
    return start_button, credits_button, quit_button

# Mode Selection Screen
def show_mode_select():
    screen.fill(WHITE)
    font_large = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 36)
    
    title_text = font_large.render("Select Mode", True, BLACK)
    traditional_text = font_small.render("Traditional", True, BLACK)
    continuous_text = font_small.render("Continuous", True, BLACK)
    back_text = font_small.render("Back", True, BLACK)
    
    # Define button areas
    traditional_button = pygame.Rect((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50), (200, 50))
    continuous_button = pygame.Rect((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20), (200, 50))
    back_button = pygame.Rect((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 90), (200, 50))
    
    pygame.draw.rect(screen, GREEN, traditional_button)
    pygame.draw.rect(screen, GREEN, continuous_button)
    pygame.draw.rect(screen, GREEN, back_button)
    
    screen.blit(title_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 3))
    screen.blit(traditional_text, (traditional_button.x + 40, traditional_button.y + 10))
    screen.blit(continuous_text, (continuous_button.x + 40, continuous_button.y + 10))
    screen.blit(back_text, (back_button.x + 65, back_button.y + 10))
    
    pygame.display.flip()
    return traditional_button, continuous_button, back_button

# Initialize continuous mode
def init_continuous_mode():
    global continuous_obstacles, continuous_score, continuous_start_time, velocity
    global continuous_can_double_jump, continuous_has_double_jumped, continuous_speed_boost_timer
    global continuous_current_speed, continuous_game_started
    continuous_obstacles = []
    continuous_score = 0
    continuous_start_time = pygame.time.get_ticks()
    velocity = 0
    character_rect.bottom = continuous_ground_y
    continuous_can_double_jump = False
    continuous_has_double_jumped = False
    continuous_speed_boost_timer = 0
    continuous_current_speed = continuous_obstacle_speed
    continuous_game_started = False  # Reset game started flag

# Update continuous mode
def update_continuous_mode():
    global continuous_obstacles, continuous_score, lives, velocity
    global continuous_can_double_jump, continuous_has_double_jumped, continuous_speed_boost_timer
    global continuous_current_speed
    
    # Update score based on time survived
    current_time = pygame.time.get_ticks()
    continuous_score = (current_time - continuous_start_time) // 1000  # Score is seconds survived
    
    # Handle speed boost
    if continuous_speed_boost_timer > 0:
        continuous_speed_boost_timer -= 1
        continuous_current_speed = continuous_obstacle_speed + continuous_speed_boost
    else:
        continuous_current_speed = continuous_obstacle_speed
    
    # Handle jumping physics
    velocity += continuous_gravity
    character_rect.y += velocity
    
    # Ground collision
    if character_rect.bottom > continuous_ground_y:
        character_rect.bottom = continuous_ground_y
        velocity = 0
        continuous_can_double_jump = True
        continuous_has_double_jumped = False
    
    # Spawn new obstacles
    if random.random() < continuous_obstacle_spawn_chance:
        is_floating = random.random() < continuous_floating_obstacle_chance
        if is_floating:
            # Spawn floating obstacle at jump height
            rect = pygame.Rect(
                SCREEN_WIDTH,
                continuous_ground_y - continuous_obstacle_height - 100,  # Higher up
                continuous_obstacle_width,
                continuous_obstacle_height
            )
        else:
            # Spawn ground obstacle
            rect = pygame.Rect(
                SCREEN_WIDTH,
                continuous_ground_y - continuous_obstacle_height,
                continuous_obstacle_width,
                continuous_obstacle_height
            )
        # Create obstacle dictionary with rect and properties
        obstacle = {
            'rect': rect,
            'is_floating': is_floating
        }
        continuous_obstacles.append(obstacle)
    
    # Update obstacles
    for obstacle in continuous_obstacles[:]:
        obstacle['rect'].x -= continuous_current_speed
        if obstacle['rect'].right < 0:
            continuous_obstacles.remove(obstacle)
    
    # Check for collisions and bounces
    for obstacle in continuous_obstacles:
        if character_rect.colliderect(obstacle['rect']):
            # Check if landing on top of a floating obstacle
            if (obstacle['is_floating'] and 
                character_rect.bottom <= obstacle['rect'].top + 10 and velocity > 0):
                # Bounce off the floating obstacle
                velocity = continuous_jump_power * 0.7  # Slightly weaker bounce
                continuous_speed_boost_timer = continuous_speed_boost_duration
                continuous_can_double_jump = True  # Reset double jump after bounce
                continuous_has_double_jumped = False
            else:
                # Normal collision
                lives -= 1
                if lives <= 0:
                    return "game_over"
                # Reset character position
                character_rect.bottom = continuous_ground_y
                velocity = 0
                continuous_can_double_jump = False
                continuous_has_double_jumped = False
                continuous_speed_boost_timer = 0
                # Clear obstacles
                continuous_obstacles.clear()
    return "continuous"

# Credits Screen Function
def show_credits():
    running_credits = True
    while running_credits:
        screen.fill(WHITE)
        font_large = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 32)
        credits_title = font_large.render("Credits", True, BLACK)
        credits_body = font_small.render("This game was developed by Oliver von Mizener.", True, BLACK)
        credits_note1 = font_small.render("Assets are temporary as of 5/22/25", True, BLACK)
        credits_note2 = font_small.render("and will be substituted at a later date.", True, BLACK)
        back_text = font_small.render("Back", True, BLACK)
        back_button = pygame.Rect((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 80), (200, 50))
        
        screen.blit(credits_title, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 3 - 40))
        screen.blit(credits_body, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 30))
        screen.blit(credits_note1, (SCREEN_WIDTH // 2 - credits_note1.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
        screen.blit(credits_note2, (SCREEN_WIDTH // 2 - credits_note2.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
        pygame.draw.rect(screen, GREEN, back_button)
        screen.blit(back_text, (back_button.x + 65, back_button.y + 10))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN and back_button.collidepoint(event.pos):
                running_credits = False

# Game Over Screen Function
def game_over_screen():
    global is_lunging, lunge_timer, gates_cleared, enemy_active, lives, state
    screen.fill(WHITE)
    font_large = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 36)
    
    text = font_large.render("Game Over!", True, BLACK)
    try_again_text = font_small.render("Try Again", True, BLACK)
    menu_text = font_small.render("Main Menu", True, BLACK)
    
    try_again_button = pygame.Rect((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2), (200, 50))
    menu_button = pygame.Rect((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 70), (200, 50))
    
    screen.blit(text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 3))
    pygame.draw.rect(screen, GREEN, try_again_button)
    pygame.draw.rect(screen, GREEN, menu_button)
    screen.blit(try_again_text, (try_again_button.x + 25, try_again_button.y + 10))
    screen.blit(menu_text, (menu_button.x + 25, menu_button.y + 10))
    
    # Display final score
    if game_mode == "continuous":
        score_text = font_small.render(f"Final Score: {continuous_score} seconds", True, BLACK)
    else:
        score_text = font_small.render(f"Final Score: {score}", True, BLACK)
    screen.blit(score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
    
    pygame.display.flip()
    
    # Reset enemy state and gates_cleared on game over
    enemy_rect.topleft = (SCREEN_WIDTH - 150, SCREEN_HEIGHT // 2 - 45)
    is_lunging = False
    lunge_timer = 0
    gates_cleared = 0
    enemy_active = False
    lives = 3
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if try_again_button.collidepoint(event.pos):
                    if game_mode == "continuous":
                        state = "continuous"
                        init_continuous_mode()
                    else:
                        state = "traditional"
                    waiting = False
                if menu_button.collidepoint(event.pos):
                    state = "menu"
                    waiting = False

# Main Game Loop
running = True
while running:
    if state == "menu":
        start_button, credits_button, quit_button = show_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    state = "mode_select"
                if credits_button.collidepoint(event.pos):
                    show_credits()
                if quit_button.collidepoint(event.pos):
                    running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    game_volume = max(0.0, game_volume - 0.05)
                    jump_sound.set_volume(game_volume)
                if event.key == pygame.K_UP:
                    game_volume = min(1.0, game_volume + 0.05)
                    jump_sound.set_volume(game_volume)

    elif state == "mode_select":
        traditional_button, continuous_button, back_button = show_mode_select()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if traditional_button.collidepoint(event.pos):
                    state = "traditional"
                    game_mode = "traditional"
                if continuous_button.collidepoint(event.pos):
                    state = "continuous"
                    game_mode = "continuous"
                    init_continuous_mode()
                if back_button.collidepoint(event.pos):
                    state = "menu"
    
    elif state == "traditional":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Handle input: jump on SPACE press
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and velocity > -5:
            velocity = jump_power
            jump_sound.play(fade_ms=100)

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
            if gates_cleared >= 4 and random.random() < 0.3:  # 30% chance for multi-opening gate after 4 gates
                # Create a multi-opening gate with 3 gaps
                gap_positions = sorted(random.sample(range(100, SCREEN_HEIGHT - 100), 3))
                for i in range(len(gap_positions)):
                    if i == 0:
                        # Top obstacle
                        top_obstacle = pygame.Rect(SCREEN_WIDTH, 0, obstacle_width, gap_positions[i])
                        obstacles.append(top_obstacle)
                    else:
                        # Middle obstacles
                        middle_obstacle = pygame.Rect(SCREEN_WIDTH, gap_positions[i-1] + obstacle_gap, 
                                                   obstacle_width, gap_positions[i] - (gap_positions[i-1] + obstacle_gap))
                        obstacles.append(middle_obstacle)
                # Bottom obstacle
                bottom_obstacle = pygame.Rect(SCREEN_WIDTH, gap_positions[-1] + obstacle_gap, 
                                            obstacle_width, SCREEN_HEIGHT - (gap_positions[-1] + obstacle_gap))
                obstacles.append(bottom_obstacle)
            else:
                # Regular single-gap gate
                obstacle_y = random.randint(100, SCREEN_HEIGHT - obstacle_gap - 100)
                top_obstacle = pygame.Rect(SCREEN_WIDTH, 0, obstacle_width, obstacle_y)
                bottom_obstacle = pygame.Rect(SCREEN_WIDTH, obstacle_y + obstacle_gap, 
                                            obstacle_width, SCREEN_HEIGHT - obstacle_y - obstacle_gap)
                obstacles.append(top_obstacle)
                obstacles.append(bottom_obstacle)

        # Move obstacles leftwards
        for obstacle in obstacles:
            obstacle.x -= obstacle_speed
        obstacles = [obs for obs in obstacles if obs.x + obstacle_width > 0]

        # Scoring: if the player passes the obstacle's right side exactly, increase score
        for obstacle in obstacles[:]:  # Create a copy of the list to safely modify during iteration
            if obstacle.x + obstacle_width == character_rect.x and obstacle != last_scored_obstacle:
                score += 1
                gates_cleared += 1
                last_scored_obstacle = obstacle
                # Don't remove the obstacle, just mark it as scored

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
                    lives -= 1
                    if lives <= 0:
                        game_over_screen()
                        score = 0
                        gates_cleared = 0
                        obstacles = []
                        last_scored_obstacle = None
                        enemy_rect.topleft = (SCREEN_WIDTH - 150, SCREEN_HEIGHT // 2 - 45)
                        enemy_active = False
                    else:
                        # Reset enemy to left and continue
                        enemy_rect.topleft = (SCREEN_WIDTH - 150, SCREEN_HEIGHT // 2 - 45)
                        enemy_direction = [random.uniform(-1, 1), random.uniform(-1, 1)]
                        magnitude = (enemy_direction[0]**2 + enemy_direction[1]**2)**0.5
                        enemy_direction = [enemy_direction[0]/magnitude, enemy_direction[1]/magnitude]

        # Only update/draw enemy if 3 or more gates have been cleared
        if gates_cleared >= 3:
            # Activate enemy if just reached 3 gates
            if not enemy_active:
                # Spawn enemy on the right side of the screen
                enemy_rect.topleft = (SCREEN_WIDTH - 150, SCREEN_HEIGHT // 2 - 45)
                enemy_active = True
                # Initialize random direction
                enemy_direction = [random.uniform(-1, 1), random.uniform(-1, 1)]
                # Normalize direction vector
                magnitude = (enemy_direction[0]**2 + enemy_direction[1]**2)**0.5
                enemy_direction = [enemy_direction[0]/magnitude, enemy_direction[1]/magnitude]

            if enemy_active:
                # Update enemy position based on direction
                enemy_rect.x += enemy_direction[0] * enemy_speed
                enemy_rect.y += enemy_direction[1] * enemy_speed

                # Bounce off screen edges
                if enemy_rect.left <= 0 or enemy_rect.right >= SCREEN_WIDTH:
                    enemy_direction[0] *= -1
                if enemy_rect.top <= 0 or enemy_rect.bottom >= SCREEN_HEIGHT - 100:  # Keep above tunnel
                    enemy_direction[1] *= -1

                # Occasionally change direction randomly
                if random.random() < 0.02:  # 2% chance per frame
                    enemy_direction = [random.uniform(-1, 1), random.uniform(-1, 1)]
                    magnitude = (enemy_direction[0]**2 + enemy_direction[1]**2)**0.5
                    enemy_direction = [enemy_direction[0]/magnitude, enemy_direction[1]/magnitude]

                # Check for collision with character
                if character_rect.colliderect(enemy_rect):
                    lives -= 1
                    if lives <= 0:
                        game_over_screen()
                        score = 0
                        gates_cleared = 0
                        obstacles = []
                        last_scored_obstacle = None
                        enemy_rect.topleft = (SCREEN_WIDTH - 150, SCREEN_HEIGHT // 2 - 45)
                        enemy_active = False
                    else:
                        # Reset enemy position and give new random direction
                        enemy_rect.topleft = (SCREEN_WIDTH - 150, SCREEN_HEIGHT // 2 - 45)
                        enemy_direction = [random.uniform(-1, 1), random.uniform(-1, 1)]
                        magnitude = (enemy_direction[0]**2 + enemy_direction[1]**2)**0.5
                        enemy_direction = [enemy_direction[0]/magnitude, enemy_direction[1]/magnitude]

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

        # Display lives (top left)
        lives_text = font.render(f"Lives: {lives}", True, (200, 0, 0))
        screen.blit(lives_text, (10, 40))

        # Draw volume bar (top right)
        bar_x = SCREEN_WIDTH - 210
        bar_y = 10
        bar_width = 150
        bar_height = 20
        # Draw background bar
        pygame.draw.rect(screen, (180, 180, 180), (bar_x, bar_y, bar_width, bar_height))
        # Draw filled bar
        filled_width = int(bar_width * game_volume)
        pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, filled_width, bar_height))
        # Draw border
        pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)
        # Draw label
        font_small = pygame.font.Font(None, 24)
        label = font_small.render(f"Volume: {int(game_volume*100)}%", True, BLACK)
        screen.blit(label, (bar_x + bar_width + 10, bar_y))

        pygame.display.flip()
        clock.tick(FPS)

    elif state == "continuous":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = "menu"
                    lives = 3
                    velocity = 0
                    character_rect.bottom = continuous_ground_y
                if event.key == pygame.K_SPACE:
                    if not continuous_game_started:
                        continuous_game_started = True
                        continuous_start_time = pygame.time.get_ticks()
                    elif character_rect.bottom >= continuous_ground_y:
                        # First jump
                        velocity = continuous_jump_power
                        continuous_can_double_jump = True
                        continuous_has_double_jumped = False
                    elif continuous_can_double_jump and not continuous_has_double_jumped:
                        # Double jump
                        velocity = continuous_jump_power * 0.8  # Slightly weaker double jump
                        continuous_has_double_jumped = True
                        continuous_can_double_jump = False

        # Update continuous mode only if game has started
        if continuous_game_started:
            state = update_continuous_mode()
            if state == "game_over":
                game_over_screen()
                state = "menu"
                lives = 3
                velocity = 0
                character_rect.bottom = continuous_ground_y

        # Render continuous mode
        screen.fill(WHITE)
        screen.blit(background, (0, 0))
        
        # Draw ground
        pygame.draw.rect(screen, GREEN, (0, continuous_ground_y, SCREEN_WIDTH, continuous_ground_height))
        
        # Draw obstacles only if game has started
        if continuous_game_started:
            for obstacle in continuous_obstacles:
                if obstacle['is_floating']:
                    pygame.draw.rect(screen, (70, 130, 180), obstacle['rect'])  # Blue for floating obstacles
                else:
                    pygame.draw.rect(screen, (139, 69, 19), obstacle['rect'])  # Brown for ground obstacles
        
        # Draw character
        screen.blit(character_img, character_rect.topleft)
        
        # Draw score and lives only if game has started
        if continuous_game_started:
            score_text = font.render(f"Score: {continuous_score}", True, BLACK)
            lives_text = font.render(f"Lives: {lives}", True, (200, 0, 0))
            screen.blit(score_text, (10, 10))
            screen.blit(lives_text, (10, 40))
            
            # Draw speed boost indicator if active
            if continuous_speed_boost_timer > 0:
                boost_text = font.render("Speed Boost!", True, (255, 215, 0))  # Gold color
                screen.blit(boost_text, (SCREEN_WIDTH - 150, 10))
        else:
            # Draw "Press Space to Start" text
            font_large = pygame.font.Font(None, 72)
            start_text = font_large.render("Press Space to Start", True, BLACK)
            text_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(start_text, text_rect)
        
        pygame.display.flip()
        clock.tick(FPS)

pygame.quit() 