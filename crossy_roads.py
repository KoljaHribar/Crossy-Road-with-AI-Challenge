import pygame
import random
import sys

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 50       
PLAYER_SIZE = 40
CAR_HEIGHT = 40

# Colors
COLOR_UI_BG = (0, 0, 0)
COLOR_TEXT = (255, 255, 255)
COLOR_CREAM = (245, 240, 220) # Egg Base
COLOR_SPECKLE = (139, 100, 80) # Egg Spots

FPS = 60
SCROLL_THRESHOLD = 250 
EXPLOSION_SEQUENCE_DURATION = 150 # Frames

CHICKEN_JOKES = [
    "Why did the chicken cross the road?\nTo get to the other side!",
    "Why did the chicken cross the playground?\nTo get to the other slide!",
    "What do you call a bird that's afraid to fly?\nA chicken!",
    "Why did the chicken join a band?\nBecause it had the drumsticks!",
    "How does a chicken send mail?\nIn a hen-velope!",
    "What do you call a crazy chicken?\nA cuckoo cluck!",
    "Why did the robot cross the road?\nBecause the chicken was away!",
    "What do chickens study in school?\nEgg-nomics!",
    "Which day of the week do chickens hate most?\nFry-day!",
    "What do you call a ghost chicken?\nA poultry-geist!",
    "Why did the chicken cross the internet?\nTo get to the other site!",
    "What happens when a chicken eats gunpowder?\nShe lays hand-gren-eggs!"
]

# --- Drawing Helpers ---

def draw_rect_alpha(surface, color, rect):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)

def draw_chicken(surface, rect, facing_right, scale=1.0):
    """ Can now scale the chicken for the narrator view """
    x, y = rect.x, rect.y
    w, h = rect.width * scale, rect.height * scale
    
    # Shadow
    draw_rect_alpha(surface, (0,0,0, 50), (x, y+h-(5*scale), w, 8*scale))

    # Legs 
    pygame.draw.rect(surface, (255, 165, 0), (x + w//2 - (6*scale), y + h - (6*scale), 4*scale, 6*scale))
    pygame.draw.rect(surface, (255, 165, 0), (x + w//2 + (2*scale), y + h - (6*scale), 4*scale, 6*scale))
    
    # Body 
    pygame.draw.rect(surface, (255, 255, 255), (x, y + (4*scale), w, h - (8*scale)))
    pygame.draw.rect(surface, (200, 200, 200), (x, y + h - (10*scale), w, 4*scale))
    
    # Comb
    pygame.draw.rect(surface, (255, 0, 0), (x + w//2 - (4*scale), y, 8*scale, 4*scale))
    
    if facing_right:
        pygame.draw.rect(surface, (255, 165, 0), (x + w - (4*scale), y + (14*scale), 6*scale, 6*scale)) 
        pygame.draw.rect(surface, (0, 0, 0), (x + w - (8*scale), y + (10*scale), 4*scale, 4*scale))    
        pygame.draw.rect(surface, (220, 220, 220), (x + (6*scale), y + (20*scale), 16*scale, 8*scale)) 
    else:
        pygame.draw.rect(surface, (255, 165, 0), (x - (2*scale), y + (14*scale), 6*scale, 6*scale))    
        pygame.draw.rect(surface, (0, 0, 0), (x + (4*scale), y + (10*scale), 4*scale, 4*scale))        
        pygame.draw.rect(surface, (220, 220, 220), (x + w - (22*scale), y + (20*scale), 16*scale, 8*scale)) 

def draw_realistic_egg(surface, x, y):
    """ Draws a high-detail egg """
    w, h = 40, 50
    
    # Create a small surface for the egg to handle per-pixel alpha easily
    egg_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    
    # 1. Base Shape (Cream)
    pygame.draw.ellipse(egg_surf, COLOR_CREAM, (0, 0, w, h))
    
    # 2. Shading (Bottom Right)
    # Draw a black ellipse with low alpha
    shadow_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surf, (0, 0, 0, 40), (2, 5, w-4, h-5))
    egg_surf.blit(shadow_surf, (0,0), special_flags=pygame.BLEND_RGBA_MIN)

    # 3. Highlight (Top Left)
    pygame.draw.ellipse(egg_surf, (255, 255, 255, 100), (5, 5, 15, 20))
    
    # 4. Speckles (Procedural based on location so they stick)
    # Use x,y as seed so speckles don't shimmer
    random.seed(int(x * y)) 
    for _ in range(8):
        sx = random.randint(5, w-5)
        sy = random.randint(5, h-5)
        pygame.draw.circle(egg_surf, COLOR_SPECKLE, (sx, sy), 1)
    random.seed() # Reset seed
    
    surface.blit(egg_surf, (x, y))

def draw_speech_bubble(surface, text, x, y, font):
    """ Draws a speech bubble with multi-line text """
    lines = text.split('\n')
    
    # Calculate box size
    max_w = 0
    total_h = 0
    for line in lines:
        fw, fh = font.size(line)
        max_w = max(max_w, fw)
        total_h += fh
    
    padding = 20
    box_w = max_w + padding * 2
    box_h = total_h + padding * 2
    
    # Draw Bubble Box (White with black outline)
    bubble_rect = pygame.Rect(x, y - box_h, box_w, box_h)
    pygame.draw.rect(surface, (255, 255, 255), bubble_rect, border_radius=10)
    pygame.draw.rect(surface, (0, 0, 0), bubble_rect, 2, border_radius=10)
    
    # Draw Triangle Tail
    pts = [(x + 20, y), (x + 40, y), (x + 20, y + 20)]
    pygame.draw.polygon(surface, (255, 255, 255), pts)
    pygame.draw.line(surface, (0,0,0), pts[0], pts[2], 2)
    pygame.draw.line(surface, (0,0,0), pts[1], pts[2], 2)
    
    # Draw Text
    curr_y = bubble_rect.top + padding
    for line in lines:
        txt_surf = font.render(line, True, (0, 0, 0))
        surface.blit(txt_surf, (bubble_rect.left + padding, curr_y))
        curr_y += font.get_linesize()

# --- Classes ---

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)
        self.life = random.randint(30, 60)
        self.size = random.randint(4, 8)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(0, self.size - 0.1)
        
    def draw(self, surface):
        if self.life > 0:
            pygame.draw.rect(surface, self.color, (self.x, self.y, self.size, self.size))

class Vehicle:
    def __init__(self, x, y, speed, v_type):
        self.type = v_type
        self.speed = speed
        self.y = y
        self.height = CAR_HEIGHT
        
        if self.type == "car":
            self.width = 70
            self.color = random.choice([(220, 20, 60), (0, 100, 255), (255, 215, 0), (255, 69, 0), (148, 0, 211), (50, 205, 50), (0, 255, 255)])
            self.color_top = (min(255, self.color[0]+40), min(255, self.color[1]+40), min(255, self.color[2]+40))
        elif self.type == "truck":
            self.width = random.randint(110, 180)
            self.color = random.choice([(220, 220, 220), (255, 250, 240), (47, 79, 79), (139, 69, 19), (70, 130, 180)])
            self.color_cab = (30, 60, 150) 
        elif self.type == "train":
            self.width = 900
            self.color = (40, 40, 40)

        self.rect = pygame.Rect(x, y, self.width, self.height)

    def update(self):
        self.rect.x += self.speed
        if self.speed > 0 and self.rect.left > SCREEN_WIDTH:
            self.rect.right = 0 - random.randint(10, 100)
        elif self.speed < 0 and self.rect.right < 0:
            self.rect.left = SCREEN_WIDTH + random.randint(10, 100)

    def draw(self, surface):
        x, y = self.rect.x, self.rect.y
        w, h = self.rect.width, self.rect.height
        
        # Shadow
        draw_rect_alpha(surface, (0,0,0, 60), (x+5, y+h-5, w-5, 8))

        if self.type == "car":
            self.draw_car(surface, x, y, w, h)
        elif self.type == "truck":
            self.draw_truck(surface, x, y, w, h)
        elif self.type == "train":
            self.draw_train(surface, x, y, w, h)

    def draw_car(self, surface, x, y, w, h):
        wheel_color = (20, 20, 20)
        pygame.draw.rect(surface, wheel_color, (x+8, y-2, 10, 6))
        pygame.draw.rect(surface, wheel_color, (x+w-18, y-2, 10, 6))
        pygame.draw.rect(surface, wheel_color, (x+8, y+h-4, 10, 6))
        pygame.draw.rect(surface, wheel_color, (x+w-18, y+h-4, 10, 6))

        pygame.draw.rect(surface, self.color, (x, y, w, h))
        pygame.draw.rect(surface, self.color_top, (x+6, y-5, w-12, h-10))
        
        if self.speed > 0: # Right
            pygame.draw.rect(surface, (200, 240, 255), (x+w-19, y-3, 12, h-14))
            pygame.draw.rect(surface, (255, 255, 100), (x + w - 4, y + 2, 4, 6)) 
            pygame.draw.rect(surface, (255, 255, 100), (x + w - 4, y + h - 8, 4, 6))
        else: # Left
            pygame.draw.rect(surface, (200, 240, 255), (x+9, y-3, 12, h-14))
            pygame.draw.rect(surface, (255, 255, 100), (x, y + 2, 4, 6)) 
            pygame.draw.rect(surface, (255, 255, 100), (x, y + h - 8, 4, 6))

    def draw_truck(self, surface, x, y, w, h):
        cab_len = 35
        trailer_len = w - cab_len - 5
        if self.speed > 0: 
            trailer_x, cab_x = x, x + trailer_len + 5
            win_rect = (cab_x + cab_len - 15, y + 4, 10, h - 8)
        else: 
            cab_x, trailer_x = x, x + cab_len + 5
            win_rect = (cab_x + 5, y + 4, 10, h - 8)

        # Wheels
        for i in range(10, trailer_len, 25): 
            pygame.draw.rect(surface, (20,20,20), (trailer_x + i, y-2, 8, 6))
            pygame.draw.rect(surface, (20,20,20), (trailer_x + i, y+h-4, 8, 6))
        
        pygame.draw.rect(surface, self.color, (trailer_x, y, trailer_len, h))
        pygame.draw.rect(surface, (50,50,50), (min(trailer_x, cab_x)+trailer_len, y+10, 5, h-20))
        pygame.draw.rect(surface, self.color_cab, (cab_x, y, cab_len, h))
        pygame.draw.rect(surface, (200, 240, 255), win_rect)

    def draw_train(self, surface, x, y, w, h):
        pygame.draw.rect(surface, self.color, (x, y, w, h))
        pygame.draw.rect(surface, (220, 20, 20), (x, y + 10, w, 5))
        for i in range(20, w, 80): pygame.draw.rect(surface, (255, 255, 150), (x + i, y + 20, 50, 15))
        for i in range(10, w, 60):
            pygame.draw.circle(surface, (10,10,10), (x + i, y + h), 6) 
            pygame.draw.circle(surface, (10,10,10), (x + i + 15, y + h), 6)

class GameOverProp:
    def __init__(self, vehicle):
        self.vehicle = vehicle 
        self.is_egg = False
    
    def draw(self, surface):
        if self.is_egg:
            cx, cy = self.vehicle.rect.centerx - 20, self.vehicle.rect.centery - 25
            draw_realistic_egg(surface, cx, cy)
        else:
            self.vehicle.draw(surface)

class Lane:
    def __init__(self, y_pos, lane_type, difficulty_level=0):
        self.y = y_pos
        self.height = GRID_SIZE
        self.lane_type = lane_type
        self.vehicles = []
        
        # --- GENERATE STATIC TEXTURE SURFACE ---
        self.bg_surface = pygame.Surface((SCREEN_WIDTH, GRID_SIZE))
        self.generate_texture()

        base_speed = random.choice([-5, -4, -3, 3, 4, 5])
        multiplier = 1.0 + (difficulty_level * 0.1)
        self.lane_speed = base_speed * multiplier

        if self.lane_type == 'road':
            if difficulty_level < 3: count = 1 if random.random() < 0.8 else 2
            elif difficulty_level < 6: count = random.randint(1, 2)
            else: count = random.randint(2, 3)

            occupied_x = []
            for _ in range(count):
                for _ in range(10): # attempts
                    start_x = random.randint(0, SCREEN_WIDTH)
                    if all(abs(start_x - ox) > 200 for ox in occupied_x):
                        v_type = "car" if random.random() < 0.7 else "truck"
                        self.vehicles.append(Vehicle(start_x, self.y + 5, self.lane_speed, v_type))
                        occupied_x.append(start_x)
                        break
                
        elif self.lane_type == 'rail':
            train_speed = random.choice([-15, 15]) 
            final_train_speed = train_speed * (1 + difficulty_level * 0.05) 
            start_x = -900 if final_train_speed > 0 else SCREEN_WIDTH + 200
            self.vehicles.append(Vehicle(start_x, self.y + 5, final_train_speed, "train"))

    def generate_texture(self):
        w, h = SCREEN_WIDTH, GRID_SIZE
        
        if self.lane_type == 'grass':
            self.bg_surface.fill((34, 139, 34))
            for _ in range(300):
                gx, gy = random.randint(0, w), random.randint(0, h)
                color = (45, 160, 45) if random.random() < 0.5 else (25, 100, 25)
                pygame.draw.line(self.bg_surface, color, (gx, gy), (gx, min(gy+4, h)), 1)
                
        elif self.lane_type == 'road':
            self.bg_surface.fill((50, 50, 55))
            pygame.draw.rect(self.bg_surface, (200, 200, 200), (0, 0, w, 2))
            pygame.draw.rect(self.bg_surface, (200, 200, 200), (0, h-2, w, 2))
            for i in range(0, w, 40):
                pygame.draw.rect(self.bg_surface, (255, 255, 255), (i, h//2 - 1, 20, 2))
            for _ in range(20):
                ox, oy = random.randint(0, w), random.randint(5, h-5)
                pygame.draw.ellipse(self.bg_surface, (40, 40, 45), (ox, oy, random.randint(10, 30), random.randint(5, 15)))

        elif self.lane_type == 'rail':
            self.bg_surface.fill((100, 100, 100))
            for _ in range(500):
                nx, ny = random.randint(0, w), random.randint(0, h)
                c = random.randint(80, 120)
                self.bg_surface.set_at((nx, ny), (c, c, c))
            for i in range(0, w, 40):
                pygame.draw.rect(self.bg_surface, (80, 50, 20), (i, 2, 12, h-4))
            pygame.draw.rect(self.bg_surface, (30, 30, 30), (0, 8, w, 6)) 
            pygame.draw.rect(self.bg_surface, (180, 180, 180), (0, 8, w, 4)) 
            pygame.draw.rect(self.bg_surface, (30, 30, 30), (0, h-14, w, 6)) 
            pygame.draw.rect(self.bg_surface, (180, 180, 180), (0, h-14, w, 4)) 

    def move_vertical(self, amount):
        self.y += amount
        for v in self.vehicles: v.rect.y += amount

    def update(self):
        for v in self.vehicles: v.update()

    def draw(self, surface):
        surface.blit(self.bg_surface, (0, self.y))
        for v in self.vehicles: v.draw(surface)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT - GRID_SIZE - 5, PLAYER_SIZE, PLAYER_SIZE)
        self.facing_right = True 
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        if dx > 0: self.facing_right = True
        elif dx < 0: self.facing_right = False
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH
    def draw(self, surface):
        draw_chicken(surface, self.rect, self.facing_right)

def get_random_lane_type(difficulty_level):
    rnd = random.random()
    grass_chance = max(0.1, 0.4 - (difficulty_level * 0.03)) 
    rail_chance = min(0.3, 0.1 + (difficulty_level * 0.02))  
    if rnd < rail_chance: return 'rail'
    elif rnd < rail_chance + (1.0 - grass_chance - rail_chance): return 'road'
    else: return 'grass'

# --- Main Game Loop ---

def game_loop(current_high_score):
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 28, bold=True)
    big_font = pygame.font.SysFont("Arial", 80, bold=True) 
    joke_font = pygame.font.SysFont("Arial", 20)

    player = Player()
    lanes = []
    
    # Init Lanes
    for i in range(int(SCREEN_HEIGHT / GRID_SIZE) + 2):
        y = SCREEN_HEIGHT - (i * GRID_SIZE)
        if i < 4: l_type = 'grass'
        else: l_type = get_random_lane_type(0) 
        lanes.append(Lane(y, l_type, 0))

    total_scroll_y = 0 
    score = 0
    running = True
    game_over = False
    scroll_accumulator = 0.0
    start_ticks = pygame.time.get_ticks()

    # Animation State Variables
    game_over_state = "PLAYING" 
    particles = []
    game_over_items = [] 
    
    # Text/Joke Animation Variables
    game_over_str = "GAME OVER"
    scattered_letters = [] 
    anim_timer = 0
    letter_index = 0
    explosion_index = 0
    explosion_timer = 0
    explosion_interval = 0
    current_joke = ""
    narrator_rect = pygame.Rect(30, SCREEN_HEIGHT - 120, 80, 80)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if not game_over:
                    if event.key == pygame.K_LEFT: player.move(-GRID_SIZE, 0)
                    elif event.key == pygame.K_RIGHT: player.move(GRID_SIZE, 0)
                    elif event.key == pygame.K_UP: player.move(0, -GRID_SIZE)
                    elif event.key == pygame.K_DOWN: player.move(0, GRID_SIZE)
                else:
                    if game_over_state == "WAITING" and event.key == pygame.K_SPACE: 
                        return score 

        if not game_over:
            # --- NORMAL GAMEPLAY ---
            difficulty_level = int(score // 100)
            current_time = pygame.time.get_ticks()
            
            # --- AUTO SCROLL (WITH DELAY) ---
            if current_time - start_ticks > 2000:
                auto_scroll_speed = 0.5 + (difficulty_level * 0.1)
                if auto_scroll_speed > 3.0: auto_scroll_speed = 3.0
                
                scroll_accumulator += auto_scroll_speed
                while scroll_accumulator >= 1.0:
                    player.rect.y += 1
                    for lane in lanes: lane.move_vertical(1)
                    scroll_accumulator -= 1.0

            # Player input Scroll
            if player.rect.top < SCROLL_THRESHOLD:
                scroll_amount = SCROLL_THRESHOLD - player.rect.top
                player.rect.y += scroll_amount
                total_scroll_y += scroll_amount
                score = int(total_scroll_y // GRID_SIZE) * 10
                for lane in lanes: lane.move_vertical(scroll_amount)
            
            # Death Check
            if player.rect.bottom >= SCREEN_HEIGHT:
                game_over = True
                game_over_state = "INIT_EXPLOSION"

            # Lane Management
            lanes = [lane for lane in lanes if lane.y < SCREEN_HEIGHT]
            min_y = min(lane.y for lane in lanes)
            if min_y > -GRID_SIZE:
                new_y = min_y - GRID_SIZE
                l_type = get_random_lane_type(difficulty_level)
                lanes.append(Lane(new_y, l_type, difficulty_level))

            # Vehicle Updates
            player_hitbox = player.rect.inflate(-15, -15)
            for lane in lanes:
                lane.update()
                for v in lane.vehicles:
                    if player_hitbox.colliderect(v.rect):
                        game_over = True
                        game_over_state = "INIT_EXPLOSION"
        
        else:
            # --- GAME OVER SEQUENCE ---
            if game_over_state == "INIT_EXPLOSION":
                for lane in lanes:
                    for v in lane.vehicles:
                        if v.rect.bottom > 0 and v.rect.top < SCREEN_HEIGHT:
                            game_over_items.append(GameOverProp(v))
                    lane.vehicles = []
                
                count = len(game_over_items)
                if count > 0:
                    explosion_interval = max(5, int(EXPLOSION_SEQUENCE_DURATION / count))
                else:
                    explosion_interval = 10
                
                for _ in range(20):
                    particles.append(Particle(player.rect.centerx, player.rect.centery, (255, 255, 255)))
                
                game_over_state = "EXPLODING_SEQUENCE"

            elif game_over_state == "EXPLODING_SEQUENCE":
                explosion_timer += 1
                if explosion_index < len(game_over_items):
                    if explosion_timer >= explosion_interval:
                        item = game_over_items[explosion_index]
                        item.is_egg = True
                        v = item.vehicle
                        for _ in range(15): 
                            particles.append(Particle(v.rect.centerx, v.rect.centery, v.color))
                        explosion_index += 1
                        explosion_timer = 0
                else:
                    game_over_state = "TEXT_ANIM"

            elif game_over_state == "TEXT_ANIM":
                anim_timer += 1
                if anim_timer % 20 == 0: 
                    if letter_index < len(game_over_str):
                        char = game_over_str[letter_index]
                        if char != " ": 
                            rx = random.randint(50, SCREEN_WIDTH - 100)
                            ry = random.randint(50, SCREEN_HEIGHT - 100)
                            rc = (random.randint(100, 255), random.randint(50, 255), random.randint(50, 255))
                            scattered_letters.append((char, rx, ry, rc))
                        letter_index += 1
                    else:
                         # TEXT DONE, PICK JOKE
                         game_over_state = "WAITING"
                         current_joke = random.choice(CHICKEN_JOKES)

            for p in particles:
                p.update()

        # --- DRAWING ---
        screen.fill((34, 139, 34)) 
        for lane in lanes: 
            lane.draw(screen) 
        
        if game_over:
            for item in game_over_items:
                item.draw(screen)
        else:
            player.draw(screen)

        for p in particles:
            p.draw(screen)

        if not game_over and player.rect.bottom > SCREEN_HEIGHT - 100:
            s = pygame.Surface((SCREEN_WIDTH, 100))
            s.set_alpha(50 + int((player.rect.bottom - (SCREEN_HEIGHT-100))*1.5))
            s.fill((255, 0, 0))
            screen.blit(s, (0, SCREEN_HEIGHT-100))

        # UI Overlay
        pygame.draw.rect(screen, COLOR_UI_BG, (0, 0, SCREEN_WIDTH, 40))
        score_text = font.render(f"SCORE: {score}", True, (255, 255, 0))
        level_text = font.render(f"LEVEL: {int(score // 100)}", True, (0, 255, 255))
        hs_text = font.render(f"HIGH: {max(score, current_high_score)}", True, (255, 255, 255))
        screen.blit(score_text, (20, 5))
        screen.blit(level_text, (SCREEN_WIDTH // 2 - 50, 5))
        screen.blit(hs_text, (SCREEN_WIDTH - 200, 5))

        # Scattered Letters
        for char, lx, ly, lc in scattered_letters:
            txt = big_font.render(char, True, lc)
            txt_bg = big_font.render(char, True, (0,0,0))
            screen.blit(txt_bg, (lx+4, ly+4)) 
            screen.blit(txt, (lx, ly))

        # Retry Text & Joke
        if game_over_state == "WAITING":
            # Draw Narrator Chicken
            draw_chicken(screen, narrator_rect, True, scale=2.0)
            # Draw Joke
            draw_speech_bubble(screen, current_joke, narrator_rect.right + 10, narrator_rect.top, joke_font)

            if (pygame.time.get_ticks() // 500) % 2 == 0:
                retry = font.render("Press SPACE to Retry", True, (255, 255, 255))
                bg_rect = retry.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                bg_rect.inflate_ip(20, 20)
                pygame.draw.rect(screen, (0,0,0), bg_rect)
                screen.blit(retry, retry.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))

        pygame.display.flip()
        clock.tick(FPS)

def main():
    pygame.init()
    pygame.display.set_caption("Crossy Road - The Joke's On You")
    high_score = 0
    while True:
        last_score = game_loop(high_score)
        if last_score > high_score: high_score = last_score

if __name__ == "__main__":
    main()