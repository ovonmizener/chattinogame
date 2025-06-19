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
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 0, 255)
ORANGE = (255, 140, 0)
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
try:
    background = pygame.image.load("background.png")
    character_img = pygame.image.load("jetpack_character.png")
    enemy_img = pygame.image.load("enemy.png")
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    character_img = pygame.transform.scale(character_img, (50, 50))
    enemy_img = pygame.transform.scale(enemy_img, (90, 90))
except Exception as e:
    print(f"Error loading images: {e}")
    # Create fallback colored rectangles
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background.fill((100, 150, 255))  # Blue background
    character_img = pygame.Surface((50, 50))
    character_img.fill((255, 255, 0))  # Yellow character
    enemy_img = pygame.Surface((90, 90))
    enemy_img.fill((255, 0, 0))  # Red enemy

try:
    jump_sound = pygame.mixer.Sound("jump.wav")
    jump_sound.set_volume(0.3)
except Exception as e:
    print(f"Error loading sound: {e}")
    # Create a silent sound as fallback
    jump_sound = pygame.mixer.Sound(pygame.sndarray.make_sound(pygame.surfarray.pixels3d(pygame.Surface((1, 1)))))
    jump_sound.set_volume(0)

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
    screen.fill(BLACK)
    try:
        font_large = pygame.font.Font(pygame.font.match_font('consolas, courier, monospace'), 72)
        font_small = pygame.font.Font(pygame.font.match_font('consolas, courier, monospace'), 40)
    except:
        font_large = pygame.font.Font(None, 72)
        font_small = pygame.font.Font(None, 40)
    title_text = font_large.render("Jetpack Escape", True, NEON_PINK)
    start_text = font_small.render("Start Game", True, NEON_BLUE)
    rules_text = font_small.render("Rules", True, NEON_BLUE)
    credits_text = font_small.render("Credits", True, NEON_BLUE)
    quit_text = font_small.render("Quit", True, NEON_BLUE)
    # Button layout
    button_width, button_height = 320, 70
    button_gap = 30
    total_height = 4 * button_height + 3 * button_gap  # Updated for 4 buttons
    # Move buttons lower to avoid overlap with title
    start_y = SCREEN_HEIGHT // 2 - total_height // 2 + 60
    start_button = pygame.Rect((SCREEN_WIDTH // 2 - button_width // 2, start_y), (button_width, button_height))
    rules_button = pygame.Rect((SCREEN_WIDTH // 2 - button_width // 2, start_y + button_height + button_gap), (button_width, button_height))
    credits_button = pygame.Rect((SCREEN_WIDTH // 2 - button_width // 2, start_y + 2 * (button_height + button_gap)), (button_width, button_height))
    quit_button = pygame.Rect((SCREEN_WIDTH // 2 - button_width // 2, start_y + 3 * (button_height + button_gap)), (button_width, button_height))
    for button in [start_button, rules_button, credits_button, quit_button]:
        pygame.draw.rect(screen, BLACK, button)
        pygame.draw.rect(screen, NEON_BLUE, button, 4)
        shadow = button.copy()
        shadow.x += 4
        shadow.y += 4
        pygame.draw.rect(screen, (40,40,40), shadow, border_radius=10)
    # Move title higher
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 60))
    for rect, text in zip([start_button, rules_button, credits_button, quit_button], [start_text, rules_text, credits_text, quit_text]):
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)
    scanline = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for y in range(0, SCREEN_HEIGHT, 4):
        pygame.draw.line(scanline, (255,255,255,15), (0, y), (SCREEN_WIDTH, y))
    screen.blit(scanline, (0,0))
    pygame.display.flip()
    return start_button, rules_button, credits_button, quit_button

# Mode Selection Screen
def show_mode_select():
    screen.fill(BLACK)
    try:
        font_large = pygame.font.Font(pygame.font.match_font('consolas, courier, monospace'), 64)
        font_small = pygame.font.Font(pygame.font.match_font('consolas, courier, monospace'), 36)
    except:
        font_large = pygame.font.Font(None, 64)
        font_small = pygame.font.Font(None, 36)
    title_text = font_large.render("Select Mode", True, NEON_PINK)
    traditional_text = font_small.render("Traditional", True, NEON_BLUE)
    continuous_text = font_small.render("Continuous", True, NEON_BLUE)
    back_text = font_small.render("Back", True, NEON_BLUE)
    button_width, button_height = 320, 60
    button_gap = 25
    total_height = 3 * button_height + 2 * button_gap
    # Move buttons lower to avoid overlap with title
    start_y = SCREEN_HEIGHT // 2 - total_height // 2 + 40
    traditional_button = pygame.Rect((SCREEN_WIDTH // 2 - button_width // 2, start_y), (button_width, button_height))
    continuous_button = pygame.Rect((SCREEN_WIDTH // 2 - button_width // 2, start_y + button_height + button_gap), (button_width, button_height))
    back_button = pygame.Rect((SCREEN_WIDTH // 2 - button_width // 2, start_y + 2 * (button_height + button_gap)), (button_width, button_height))
    for button in [traditional_button, continuous_button, back_button]:
        pygame.draw.rect(screen, BLACK, button)
        pygame.draw.rect(screen, NEON_BLUE, button, 4)
        shadow = button.copy()
        shadow.x += 4
        shadow.y += 4
        pygame.draw.rect(screen, (40,40,40), shadow, border_radius=10)
    # Move title higher
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
    for rect, text in zip([traditional_button, continuous_button, back_button], [traditional_text, continuous_text, back_text]):
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)
    scanline = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for y in range(0, SCREEN_HEIGHT, 4):
        pygame.draw.line(scanline, (255,255,255,15), (0, y), (SCREEN_WIDTH, y))
    screen.blit(scanline, (0,0))
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
    global continuous_obstacles, continuous_score, velocity
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
                # Normal collision - game over
                return "game_over"
    return "continuous"

# Credits Screen Function
def show_credits():
    running_credits = True
    try:
        font_large = pygame.font.Font(pygame.font.match_font('consolas, courier, monospace'), 36)
        font_medium = pygame.font.Font(pygame.font.match_font('consolas, courier, monospace'), 24)
        font_small = pygame.font.Font(pygame.font.match_font('consolas, courier, monospace'), 20)
    except:
        font_large = pygame.font.Font(None, 36)
        font_medium = pygame.font.Font(None, 24)
        font_small = pygame.font.Font(None, 20)
    # Helper for wrapping text
    def wrap_text(text, font, max_width):
        words = text.split(' ')
        lines = []
        current = ''
        for word in words:
            test = current + (' ' if current else '') + word
            if font.size(test)[0] <= max_width:
                current = test
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines
    while running_credits:
        screen.fill(BLACK)
        credits_title = font_large.render("Credits", True, NEON_PINK)
        body_lines = wrap_text("This game was developed by Oliver von Mizener.", font_small, SCREEN_WIDTH - 80)
        dev_status = wrap_text("Game is actively under development with regular updates on GitHub.", font_small, SCREEN_WIDTH - 80)
        future_plans = wrap_text("Future plans include:", font_small, SCREEN_WIDTH - 80)
        plan1 = wrap_text("• New custom artwork and animations", font_small, SCREEN_WIDTH - 80)
        plan2 = wrap_text("• Story mode with unique levels", font_small, SCREEN_WIDTH - 80)
        plan3 = wrap_text("• Additional game modes and features", font_small, SCREEN_WIDTH - 80)
        note_lines = wrap_text("Current assets are temporary and will be replaced in future updates.", font_small, SCREEN_WIDTH - 80)
        back_text = font_medium.render("Back", True, NEON_BLUE)
        button_width, button_height = 180, 45
        back_button = pygame.Rect((SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT - 60), (button_width, button_height))
        pygame.draw.rect(screen, BLACK, back_button)
        pygame.draw.rect(screen, NEON_BLUE, back_button, 3)
        shadow = back_button.copy()
        shadow.x += 3
        shadow.y += 3
        pygame.draw.rect(screen, (40,40,40), shadow, border_radius=8)
        screen.blit(credits_title, (SCREEN_WIDTH // 2 - credits_title.get_width() // 2, 10))
        # Draw wrapped body lines
        y = 60
        for line in body_lines:
            line_surf = font_small.render(line, True, NEON_BLUE)
            screen.blit(line_surf, (SCREEN_WIDTH // 2 - line_surf.get_width() // 2, y))
            y += 22
        
        y += 8
        for line in dev_status:
            line_surf = font_small.render(line, True, NEON_BLUE)
            screen.blit(line_surf, (SCREEN_WIDTH // 2 - line_surf.get_width() // 2, y))
            y += 22
        
        y += 8
        for line in future_plans:
            line_surf = font_small.render(line, True, NEON_BLUE)
            screen.blit(line_surf, (SCREEN_WIDTH // 2 - line_surf.get_width() // 2, y))
            y += 22
        for line in plan1:
            line_surf = font_small.render(line, True, NEON_BLUE)
            screen.blit(line_surf, (SCREEN_WIDTH // 2 - line_surf.get_width() // 2, y))
            y += 22
        for line in plan2:
            line_surf = font_small.render(line, True, NEON_BLUE)
            screen.blit(line_surf, (SCREEN_WIDTH // 2 - line_surf.get_width() // 2, y))
            y += 22
        for line in plan3:
            line_surf = font_small.render(line, True, NEON_BLUE)
            screen.blit(line_surf, (SCREEN_WIDTH // 2 - line_surf.get_width() // 2, y))
            y += 22
        
        y += 8
        for line in note_lines:
            line_surf = font_small.render(line, True, NEON_BLUE)
            screen.blit(line_surf, (SCREEN_WIDTH // 2 - line_surf.get_width() // 2, y))
            y += 22
        
        text_rect = back_text.get_rect(center=back_button.center)
        screen.blit(back_text, text_rect)
        scanline = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y_scan in range(0, SCREEN_HEIGHT, 4):
            pygame.draw.line(scanline, (255,255,255,15), (0, y_scan), (SCREEN_WIDTH, y_scan))
        screen.blit(scanline, (0,0))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN and back_button.collidepoint(event.pos):
                running_credits = False

# Rules Screen Function
def show_rules():
    running_rules = True
    try:
        font_large = pygame.font.Font(pygame.font.match_font('consolas, courier, monospace'), 36)
        font_medium = pygame.font.Font(pygame.font.match_font('consolas, courier, monospace'), 24)
        font_small = pygame.font.Font(pygame.font.match_font('consolas, courier, monospace'), 20)
    except:
        font_large = pygame.font.Font(None, 36)
        font_medium = pygame.font.Font(None, 24)
        font_small = pygame.font.Font(None, 20)
    
    # Helper for wrapping text
    def wrap_text(text, font, max_width):
        words = text.split(' ')
        lines = []
        current = ''
        for word in words:
            test = current + (' ' if current else '') + word
            if font.size(test)[0] <= max_width:
                current = test
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    while running_rules:
        screen.fill(BLACK)
        rules_title = font_large.render("How to Play", True, NEON_PINK)
        
        # Traditional Mode Rules
        traditional_title = font_medium.render("Traditional Mode:", True, NEON_BLUE)
        traditional_rules = [
            "• Use SPACE to jump and control your character",
            "• Navigate through gates to score points",
            "• You have 3 lives - lose them all and it's game over",
            "• After 3 gates, an enemy appears and moves randomly",
            "• The tunnel at the bottom is safe but cowardly",
            "• Score points by passing through gates",
            "• Using the tunnel deducts points - be brave!"
        ]
        
        # Continuous Mode Rules
        continuous_title = font_medium.render("Continuous Mode:", True, NEON_BLUE)
        continuous_rules = [
            "• Press SPACE to start the game",
            "• Use SPACE to jump and double jump",
            "• Land on floating obstacles to get a speed boost",
            "• One life only - any collision ends the game",
            "• Score is based on survival time in seconds",
            "• Press ESC to return to menu"
        ]
        
        # Controls
        controls_title = font_medium.render("Controls:", True, NEON_BLUE)
        controls = [
            "• SPACE: Jump/Double Jump",
            "• UP/DOWN: Adjust Volume",
            "• ESC: Return to Menu",
            "• Mouse: Navigate Menus"
        ]
        
        back_text = font_medium.render("Back", True, NEON_BLUE)
        button_width, button_height = 180, 45
        back_button = pygame.Rect((SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT - 60), (button_width, button_height))
        
        # Draw title
        screen.blit(rules_title, (SCREEN_WIDTH // 2 - rules_title.get_width() // 2, 10))
        
        # Draw sections with proper spacing
        y = 60
        # Traditional Mode
        screen.blit(traditional_title, (30, y))
        y += 25
        for rule in traditional_rules:
            rule_surf = font_small.render(rule, True, NEON_BLUE)
            screen.blit(rule_surf, (50, y))
            y += 22
        
        y += 10
        # Continuous Mode
        screen.blit(continuous_title, (30, y))
        y += 25
        for rule in continuous_rules:
            rule_surf = font_small.render(rule, True, NEON_BLUE)
            screen.blit(rule_surf, (50, y))
            y += 22
        
        y += 10
        # Controls
        screen.blit(controls_title, (30, y))
        y += 25
        for control in controls:
            control_surf = font_small.render(control, True, NEON_BLUE)
            screen.blit(control_surf, (50, y))
            y += 22
        
        # Draw back button
        pygame.draw.rect(screen, BLACK, back_button)
        pygame.draw.rect(screen, NEON_BLUE, back_button, 3)
        shadow = back_button.copy()
        shadow.x += 3
        shadow.y += 3
        pygame.draw.rect(screen, (40,40,40), shadow, border_radius=8)
        text_rect = back_text.get_rect(center=back_button.center)
        screen.blit(back_text, text_rect)
        
        # Add scanline effect
        scanline = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y_scan in range(0, SCREEN_HEIGHT, 4):
            pygame.draw.line(scanline, (255,255,255,15), (0, y_scan), (SCREEN_WIDTH, y_scan))
        screen.blit(scanline, (0,0))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN and back_button.collidepoint(event.pos):
                running_rules = False

# Game Over Screen Function
def game_over_screen():
    global is_lunging, lunge_timer, gates_cleared, enemy_active, lives, state
    try:
        font_large = pygame.font.Font(pygame.font.match_font('consolas, courier, monospace'), 72)
        font_small = pygame.font.Font(pygame.font.match_font('consolas, courier, monospace'), 36)
    except:
        font_large = pygame.font.Font(None, 72)
        font_small = pygame.font.Font(None, 36)
    screen.fill(BLACK)
    text = font_large.render("Game Over!", True, NEON_PINK)
    try_again_text = font_small.render("Try Again", True, NEON_BLUE)
    menu_text = font_small.render("Main Menu", True, NEON_BLUE)
    button_width, button_height = 260, 60
    button_gap = 30
    try_again_button = pygame.Rect((SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + 40), (button_width, button_height))
    menu_button = pygame.Rect((SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + button_height + button_gap + 40), (button_width, button_height))
    for button in [try_again_button, menu_button]:
        pygame.draw.rect(screen, BLACK, button)
        pygame.draw.rect(screen, NEON_BLUE, button, 4)
        shadow = button.copy()
        shadow.x += 4
        shadow.y += 4
        pygame.draw.rect(screen, (40,40,40), shadow, border_radius=10)
    # Move title higher and add more space before score
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 70))
    if game_mode == "continuous":
        score_text = font_small.render(f"Final Score: {continuous_score} seconds", True, NEON_PINK)
    else:
        score_text = font_small.render(f"Final Score: {score}", True, NEON_PINK)
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 170))
    for rect, text_item in zip([try_again_button, menu_button], [try_again_text, menu_text]):
        text_rect = text_item.get_rect(center=rect.center)
        screen.blit(text_item, text_rect)
    scanline = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for y in range(0, SCREEN_HEIGHT, 4):
        pygame.draw.line(scanline, (255,255,255,15), (0, y), (SCREEN_WIDTH, y))
    screen.blit(scanline, (0,0))
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
        start_button, rules_button, credits_button, quit_button = show_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    state = "mode_select"
                if rules_button.collidepoint(event.pos):
                    show_rules()
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

    elif state == "game_over":
        game_over_screen()

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
            pygame.draw.rect(screen, ORANGE, obstacle)

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
            result = update_continuous_mode()
            if result == "game_over":
                state = "game_over"
                game_over_screen()  # Show game over screen immediately
                continue  # Skip the rest of the rendering for this frame

        # Render continuous mode
        screen.fill(WHITE)
        screen.blit(background, (0, 0))
        # Draw ground
        pygame.draw.rect(screen, GREEN, (0, continuous_ground_y, SCREEN_WIDTH, continuous_ground_height))
        # Draw obstacles only if game has started
        if continuous_game_started:
            for obstacle in continuous_obstacles:
                pygame.draw.rect(screen, ORANGE, obstacle['rect'])
        # Draw character
        screen.blit(character_img, character_rect.topleft)
        # Draw score only if game has started
        if continuous_game_started:
            score_text = font.render(f"Score: {continuous_score}", True, BLACK)
            screen.blit(score_text, (10, 10))
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