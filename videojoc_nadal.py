import pygame
import random
import sys
import os
import math
import string

# --- CONFIGURACIÓ GLOBAL ---
pygame.init()
pygame.mixer.init() 

# Colors Generals
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PAPER_COLOR = (250, 245, 230)
TEXT_COLOR = (20, 20, 40)
BUTTON_HOVER = (255, 250, 240)

# Colors Temàtics
CHRISTMAS_RED = (200, 30, 30) 
CHRISTMAS_GREEN = (34, 160, 34)
GOLD = (230, 190, 50)
BLUE_ICE = (100, 180, 255)
DARK_RED = (100, 15, 15)
DARK_GREEN = (15, 70, 15)
DARK_GOLD = (120, 90, 10)
DARK_BLUE = (30, 60, 100)

GROUND_COLOR_JAPAN = (40, 65, 95)
TORI_RED_FALLBACK = (200, 50, 50)
DARUMA_RED_FALLBACK = (220, 20, 60)
BROWN_STICK = (101, 67, 33)
SOUP_HIGHLIGHT = (255, 215, 0, 100)
SOUP_FOUND = (50, 200, 50, 128)

# Configuració de Pantalla
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("JOC DE NADAL DE FAMÍLIA")

clock = pygame.time.Clock()
FPS = 60

# --- FONTS ---
try:
    font_ui = pygame.font.SysFont("georgia", int(HEIGHT * 0.04), bold=True)
    font_title = pygame.font.SysFont("georgia", int(HEIGHT * 0.10), bold=True)
    font_big = pygame.font.SysFont("georgia", int(HEIGHT * 0.12), bold=True)
    font_soup = pygame.font.SysFont("courier new", int(HEIGHT * 0.04), bold=True) 
except:
    font_ui = pygame.font.Font(None, int(HEIGHT * 0.05))
    font_title = pygame.font.Font(None, int(HEIGHT * 0.10))
    font_big = pygame.font.Font(None, int(HEIGHT * 0.15))
    font_soup = pygame.font.Font(None, int(HEIGHT * 0.05))

# --- FUNCIONS AUXILIARS ---

def draw_paper_box(surface, rect, text_surf=None, image_surf=None, is_hovered=False):
    """
    Dibuixa un botó estil paper.
    Soporta text multilinia si 'text_surf' és una llista de superfícies.
    """
    color = BUTTON_HOVER if is_hovered else PAPER_COLOR
    pygame.draw.rect(surface, color, rect, border_radius=15)
    pygame.draw.rect(surface, TEXT_COLOR, rect, 3, border_radius=15)
    
    center_x = rect.centerx
    center_y = rect.centery

    if image_surf:
        img_rect = image_surf.get_rect(center=(center_x, center_y - 20))
        surface.blit(image_surf, img_rect)
        
    if text_surf:
        if isinstance(text_surf, pygame.Surface):
            if image_surf:
                text_rect = text_surf.get_rect(center=(center_x, rect.bottom - 30))
            else:
                text_rect = text_surf.get_rect(center=rect.center)
            surface.blit(text_surf, text_rect)
        elif isinstance(text_surf, list):
            total_h = sum([s.get_height() for s in text_surf])
            start_y = center_y - total_h / 2
            if image_surf:
                start_y = rect.bottom - total_h - 15
            current_y = start_y
            for line_surf in text_surf:
                line_rect = line_surf.get_rect(center=(center_x, current_y + line_surf.get_height()/2))
                surface.blit(line_surf, line_rect)
                current_y += line_surf.get_height()

def render_multiline_text(text, font, color):
    """Converteix un string amb \n en una llista de superfícies"""
    lines = text.split('\n')
    return [font.render(line, True, color) for line in lines]

def load_face(char_name, size):
    """Càrrega i escala la cara del personatge"""
    try:
        img = pygame.image.load(f"cara_{char_name}.png").convert_alpha()
        orig_rect = img.get_rect()
        aspect = orig_rect.width / orig_rect.height
        w = int(size * aspect)
        return pygame.transform.smoothscale(img, (w, size))
    except:
        s = pygame.Surface((size, size))
        s.fill((0, 0, 200))
        return s

def load_christmas_ball(size):
    """Càrrega la imatge de la bola de nadal pel joc de ritme"""
    try:
        img = pygame.image.load("bola_nadal.png").convert_alpha()
        return pygame.transform.smoothscale(img, (size, size))
    except:
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(s, CHRISTMAS_RED, (size//2, size//2), size//2)
        pygame.draw.circle(s, GOLD, (size//2, size//2), size//2, 3) 
        pygame.draw.circle(s, WHITE, (size//3, size//3), size//6)
        pygame.draw.rect(s, GOLD, (size//2 - 5, 0, 10, 10))
        return s

# ==============================================================================
# JOC 1: RECORDS DE JAPÓ (Runner)
# ==============================================================================

def run_japan_game(character_name):
    GROUND_HEIGHT = int(HEIGHT * 0.05)
    GROUND_Y = HEIGHT - GROUND_HEIGHT
    bg_img = None
    if os.path.exists("fondo_fuji.png"):
        bg_img = pygame.transform.smoothscale(pygame.image.load("fondo_fuji.png").convert(), (WIDTH, HEIGHT))

    class RunnerPlayer(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.target_h = int(HEIGHT * 0.25)
            self.image = load_face(character_name, self.target_h)
            self.rect = self.image.get_rect()
            self.rect.inflate_ip(-self.rect.width*0.1, -self.rect.height*0.1)
            self.rect.x = WIDTH * 0.1
            self.rect.bottom = GROUND_Y
            self.vel_y = 0; self.jumping = False; self.gravity = HEIGHT * 0.0018; self.jump_force = -HEIGHT * 0.038
        def update(self):
            self.vel_y += self.gravity; self.rect.y += self.vel_y
            if self.rect.bottom >= GROUND_Y: self.rect.bottom = GROUND_Y; self.jumping = False
        def jump(self):
            if not self.jumping: self.vel_y = self.jump_force; self.jumping = True

    class Obstacle(pygame.sprite.Sprite):
        def __init__(self, o_type):
            super().__init__()
            if o_type == "Tori": ratio = 0.45; name = "tori.png"; color = TORI_RED_FALLBACK
            else: ratio = 0.19; name = "daruma.png"; color = DARUMA_RED_FALLBACK
            h = int(HEIGHT * ratio)
            try:
                img = pygame.image.load(name).convert_alpha()
                w = int(h * (img.get_width()/img.get_height()))
                self.image = pygame.transform.smoothscale(img, (w, h))
            except:
                self.image = pygame.Surface((int(h*0.6), h)); self.image.fill(color)
            self.rect = self.image.get_rect()
            offset = int(HEIGHT * 0.015); self.rect.bottom = GROUND_Y + offset
            self.rect.x = WIDTH + random.randint(0, int(WIDTH*0.3)); self.speed = WIDTH * 0.013
            self.mask = pygame.mask.from_surface(self.image)
            if o_type == "Tori":
                col_surf = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
                top_h = int(h * 0.25)
                col_surf.blit(self.image, (0,0), (0,0, self.rect.width, top_h))
                self.mask = pygame.mask.from_surface(col_surf)
        def update(self):
            self.rect.x -= self.speed
            if self.rect.right < 0: self.kill()

    all_sprites = pygame.sprite.Group(); obstacles = pygame.sprite.Group(); player = RunnerPlayer(); all_sprites.add(player)
    score = 0; target = 3000; game_over = False; won = False
    OBS_EVENT = pygame.USEREVENT + 1; pygame.time.set_timer(OBS_EVENT, 1400)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return
                if event.key == pygame.K_SPACE:
                    if not game_over and not won: player.jump()
                    elif game_over or won: return run_japan_game(character_name)
            if event.type == OBS_EVENT and not game_over and not won: obstacles.add(Obstacle(random.choice(["Tori", "Daruma"])))

        if not game_over and not won:
            obstacles.update(); player.update()
            if pygame.sprite.spritecollide(player, obstacles, False, pygame.sprite.collide_mask): game_over = True
            score += 1; 
            if score >= target: won = True
        
        if bg_img: screen.blit(bg_img, (0,0))
        else: screen.fill((135, 206, 235))
        pygame.draw.rect(screen, GROUND_COLOR_JAPAN, (0, GROUND_Y, WIDTH, GROUND_HEIGHT))
        obstacles.draw(screen); screen.blit(player.image, player.rect)
        draw_paper_box(screen, pygame.Rect(20, 20, 300, 60), font_ui.render(f"Punts: {score}", True, TEXT_COLOR))

        if game_over or won:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); s.fill((0,0,0,180)); screen.blit(s, (0,0))
            msg = "HAS XOCAT!" if game_over else "NIVELL SUPERAT!"; col = PAPER_COLOR if game_over else (255, 215, 0)
            txt = font_big.render(msg, True, col); screen.blit(txt, txt.get_rect(center=(WIDTH//2, HEIGHT//2)))
            sub = font_ui.render("Espai: Reiniciar  |  ESC: Menú", True, WHITE); screen.blit(sub, sub.get_rect(center=(WIDTH//2, HEIGHT//2 + 80)))
        pygame.display.flip(); clock.tick(FPS)

# ==============================================================================
# JOC 2: EL CAGA TIÓ (FPS)
# ==============================================================================

def run_tio_game(character_name):
    bg_img = None
    if os.path.exists("fons_tio.png"): bg_img = pygame.transform.smoothscale(pygame.image.load("fons_tio.png").convert(), (WIDTH, HEIGHT))
    
    tio_img = None; tio_cop_img = None
    if os.path.exists("tio.png"):
        raw = pygame.image.load("tio.png").convert_alpha(); scale = HEIGHT * 0.35; w = int(scale * (raw.get_width() / raw.get_height()))
        tio_img = pygame.transform.flip(pygame.transform.smoothscale(raw, (w, int(scale))), True, False)
    else: tio_img = pygame.Surface((200,100)); tio_img.fill((139,69,19))
    
    if os.path.exists("tio_cop.png"):
        raw = pygame.image.load("tio_cop.png").convert_alpha(); tio_cop_img = pygame.transform.flip(pygame.transform.smoothscale(raw, (w, int(scale))), True, False)
    else: tio_cop_img = tio_img

    stick_img = None; target_stick_len = int(HEIGHT * 0.9); target_stick_w = 60 
    if os.path.exists("pal.png"): stick_img = pygame.transform.smoothscale(pygame.image.load("pal.png").convert_alpha(), (target_stick_w, target_stick_len))
    else: stick_img = pygame.Surface((target_stick_w, target_stick_len), pygame.SRCALPHA); stick_img.fill(BROWN_STICK)
        
    player_mini_img = load_face(character_name, 80)
    hits_needed = 8; hits_current = 0; state = "WAITING"
    timer_next_prompt = pygame.time.get_ticks() + random.randint(2000, 4000); timer_reaction_limit = 0; REACTION_TIME = 900
    stick_rotation = 0; is_hitting_anim = False
    
    while True:
        current_time = pygame.time.get_ticks()
        if state == "WAITING":
            if current_time >= timer_next_prompt: state = "PROMPT"; timer_reaction_limit = current_time + REACTION_TIME
        elif state == "PROMPT":
            if current_time > timer_reaction_limit: state = "MISS"; timer_next_prompt = current_time + 2000
        elif state == "HIT_ANIM":
            if stick_rotation > 0: stick_rotation -= 5 
            else: stick_rotation = 0; is_hitting_anim = False; state = "WAITING"; timer_next_prompt = current_time + random.randint(1500, 3500)
            if hits_current >= hits_needed: state = "WIN"
        elif state == "MISS":
             if current_time >= timer_next_prompt: state = "WAITING"; timer_next_prompt = current_time + random.randint(2000, 4000)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return
                if event.key == pygame.K_SPACE:
                    if state == "PROMPT": hits_current += 1; state = "HIT_ANIM"; is_hitting_anim = True; stick_rotation = 60
                    elif state == "WIN": return run_tio_game(character_name)

        if bg_img: screen.blit(bg_img, (0,0))
        else: screen.fill((200, 180, 160)) 
        
        curr_tio = tio_cop_img if is_hitting_anim else tio_img
        tio_rect = curr_tio.get_rect(); tio_rect.bottomleft = (WIDTH * 0.05, HEIGHT * 0.90)
        draw_x, draw_y = tio_rect.x, tio_rect.y
        if is_hitting_anim: draw_x += random.randint(-5, 5); draw_y += random.randint(-5, 5)
        screen.blit(curr_tio, (draw_x, draw_y))
        
        screen.blit(player_mini_img, (20, 20))
        draw_paper_box(screen, pygame.Rect(20 + player_mini_img.get_width() + 10, 30, 350, 60), font_ui.render(f"Cops: {hits_current} / {hits_needed}", True, TEXT_COLOR))

        if state == "PROMPT":
            ptxt = font_title.render("COP DE BASTÓ!", True, TEXT_COLOR)
            prect = pygame.Rect(0,0, ptxt.get_width()+60, ptxt.get_height()+30); prect.center = (WIDTH//2, HEIGHT*0.3)
            pygame.draw.rect(screen, PAPER_COLOR, prect, border_radius=25); pygame.draw.rect(screen, CHRISTMAS_RED, prect, 8, border_radius=25); screen.blit(ptxt, ptxt.get_rect(center=prect.center))
        if state == "MISS":
            mtxt = font_title.render("Massa lent!", True, CHRISTMAS_RED)
            mrect = pygame.Rect(0,0, mtxt.get_width()+60, mtxt.get_height()+30); mrect.center = (WIDTH//2, HEIGHT*0.3)
            pygame.draw.rect(screen, PAPER_COLOR, mrect, border_radius=25); pygame.draw.rect(screen, CHRISTMAS_RED, mrect, 8, border_radius=25); screen.blit(mtxt, mtxt.get_rect(center=mrect.center))

        cur_ang = 45 + stick_rotation; rot_stick = pygame.transform.rotate(stick_img, cur_ang)
        st_rect = rot_stick.get_rect(); st_rect.bottomright = (WIDTH * 0.75, HEIGHT * 1.1)
        screen.blit(rot_stick, st_rect)

        if state == "WIN":
             s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); s.fill((0,0,0,180)); screen.blit(s, (0,0))
             wtxt = font_big.render("CAAAAAGAAA TIÓ!!!", True, GOLD); gtxt = font_ui.render("Pots obrir el següent regal", True, WHITE)
             screen.blit(wtxt, wtxt.get_rect(center=(WIDTH//2, HEIGHT//2))); screen.blit(gtxt, gtxt.get_rect(center=(WIDTH//2, HEIGHT//2 + 100)))

        pygame.display.flip(); clock.tick(FPS)

# ==============================================================================
# JOC 3: SOPA DE LLETRES
# ==============================================================================

def run_soup_game(character_name):
    ROWS, COLS = 12, 12; CELL_SIZE = int(HEIGHT * 0.065)
    BOARD_W = COLS * CELL_SIZE; BOARD_H = ROWS * CELL_SIZE
    ALL = ["CANELONS", "POLVORONS", "ESCUDELLA", "TORRO", "NEULES", "GALETS", "CAVA", "TORTELL"]
    targets = random.sample(ALL, 5); found = []; found_cells = [] 
    grid = [['' for _ in range(COLS)] for _ in range(ROWS)]
    
    def place(w):
        w = w.upper()
        for _ in range(100):
            d = random.choice([(0,1), (1,0), (1,1)]); sr = random.randint(0, ROWS-1); sc = random.randint(0, COLS-1)
            if 0<=sr+d[0]*(len(w)-1)<ROWS and 0<=sc+d[1]*(len(w)-1)<COLS:
                can = True
                for i in range(len(w)):
                    if grid[sr+d[0]*i][sc+d[1]*i] not in ['', w[i]]: can = False; break
                if can:
                    for i in range(len(w)): grid[sr+d[0]*i][sc+d[1]*i] = w[i]
                    return True
        return False
    for w in targets: place(w)
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for r in range(ROWS):
        for c in range(COLS): 
            if grid[r][c] == '': grid[r][c] = random.choice(chars)

    bg = None
    if os.path.exists("fons_cuina.png"): bg = pygame.transform.smoothscale(pygame.image.load("fons_cuina.png").convert(), (WIDTH, HEIGHT))
    mini = load_face(character_name, 80)
    
    sel_s = None; sel_e = None; selecting = False; won = False
    bx = (WIDTH - BOARD_W) // 2; by = (HEIGHT - BOARD_H) // 2
    
    while True:
        mx, my = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: return
                if e.key == pygame.K_SPACE and won: return run_soup_game(character_name)
            if not won:
                if e.type == pygame.MOUSEBUTTONDOWN and bx<=mx<bx+BOARD_W and by<=my<by+BOARD_H:
                    c=(mx-bx)//CELL_SIZE; r=(my-by)//CELL_SIZE; sel_s=(r,c); sel_e=(r,c); selecting=True
                elif e.type == pygame.MOUSEMOTION and selecting:
                    if bx<=mx<bx+BOARD_W and by<=my<by+BOARD_H: c=(mx-bx)//CELL_SIZE; r=(my-by)//CELL_SIZE; sel_e=(r,c)
                elif e.type == pygame.MOUSEBUTTONUP and selecting:
                    selecting=False; r1,c1=sel_s; r2,c2=sel_e; dr,dc=r2-r1,c2-c1; steps=max(abs(dr),abs(dc)); steps=1 if steps==0 else steps
                    dr=0 if dr==0 else dr//abs(dr); dc=0 if dc==0 else dc//abs(dc)
                    if (dr==0 or dc==0 or abs(dr)==abs(dc)):
                        word=""; coords=[]
                        for i in range(steps+1): cr,cc=r1+dr*i,c1+dc*i; word+=grid[cr][cc]; coords.append((cr,cc))
                        f=False
                        if word in targets and word not in found: found.append(word); f=True
                        elif word[::-1] in targets and word[::-1] not in found: found.append(word[::-1]); f=True
                        if f: found_cells.extend(coords)
                    sel_s=None; sel_e=None
                    if len(found)==len(targets): won=True

        if bg: screen.blit(bg, (0,0))
        else: screen.fill((200,200,200))
        
        s_board_bg = pygame.Surface((BOARD_W + 40, BOARD_H + 40), pygame.SRCALPHA)
        s_board_bg.fill((255, 255, 255, 200)) # Blanco semitransparente
        screen.blit(s_board_bg, (bx - 20, by - 20))
        pygame.draw.rect(screen, BLACK, pygame.Rect(bx - 20, by - 20, BOARD_W + 40, BOARD_H + 40), 4)
        
        for r in range(ROWS):
            for c in range(COLS):
                rect = pygame.Rect(bx+c*CELL_SIZE, by+r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if (r,c) in found_cells: pygame.draw.rect(screen, (144,238,144), rect)
                pygame.draw.rect(screen, BLACK, rect, 1)
                l = font_soup.render(grid[r][c], True, BLACK); screen.blit(l, l.get_rect(center=rect.center))

        if selecting and sel_s and sel_e:
            r1,c1=sel_s; r2,c2=sel_e; dr,dc=r2-r1,c2-c1; steps=max(abs(dr),abs(dc)); steps=1 if steps==0 else steps
            dr=0 if dr==0 else dr//abs(dr); dc=0 if dc==0 else dc//abs(dc)
            if (dr==0 or dc==0 or abs(dr)==abs(dc)):
                for i in range(steps+1):
                    h_rect = pygame.Rect(bx+(c1+dc*i)*CELL_SIZE, by+(r1+dr*i)*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    sh = pygame.Surface((CELL_SIZE,CELL_SIZE), pygame.SRCALPHA); sh.fill(SOUP_HIGHLIGHT); screen.blit(sh, h_rect)

        screen.blit(mini, (20,20))
        draw_paper_box(screen, pygame.Rect(20+mini.get_width()+10, 30, 380, 60), font_ui.render(f"Paraules: {len(found)} / {len(targets)}", True, TEXT_COLOR))
        
        ly = 150; lbw = 350; lbh = 320; lbx = WIDTH - lbw - 30; lby = ly - 20
        sl = pygame.Surface((lbw, lbh), pygame.SRCALPHA); sl.fill((255,255,255,200)); screen.blit(sl, (lbx, lby))
        pygame.draw.rect(screen, BLACK, (lbx, lby, lbw, lbh), 4)
        screen.blit(font_ui.render("LLISTA:", True, BLACK), (lbx+20, ly))
        for i,w in enumerate(targets):
            col = CHRISTMAS_GREEN if w in found else BLACK
            screen.blit(font_ui.render(w, True, col), (lbx+20, ly+40+i*40))

        if won:
             s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); s.fill((0,0,0,180)); screen.blit(s, (0,0))
             screen.blit(font_big.render("MOLT BÉ!!!", True, GOLD), font_big.render("MOLT BÉ!!!", True, GOLD).get_rect(center=(WIDTH//2, HEIGHT//2)))
             sub = font_ui.render("Pots obrir el següent regal", True, WHITE); screen.blit(sub, sub.get_rect(center=(WIDTH//2, HEIGHT//2 + 100)))

        pygame.display.flip(); clock.tick(FPS)

# ==============================================================================
# JOC 4: L'AVENTURA DELS REGALS (PLATAFORMES MARIO STYLE)
# ==============================================================================

def run_platformer_game(character_name):
    GRAVITY = 0.8
    JUMP_POWER = -25
    MOVE_SPEED = 9
    TILE_SIZE = 80 
    
    def load_img(name, scale_w=None, scale_h=None):
        if os.path.exists(name):
            img = pygame.image.load(name).convert_alpha()
            if scale_w and scale_h:
                return pygame.transform.smoothscale(img, (scale_w, scale_h))
            return img
        else:
            s = pygame.Surface((scale_w if scale_w else 50, scale_h if scale_h else 50))
            s.fill((255, 0, 255))
            return s

    bg_img = load_img("fons_neu.png", WIDTH, HEIGHT)
    block_img = load_img("bloc_terra.png", TILE_SIZE, TILE_SIZE)
    plat_img = load_img("bloc_plataforma.png", TILE_SIZE, TILE_SIZE)
    gift_img = load_img("regal.png", 70, 70) 
    santa_img = load_img("papa_noel.png", 200, 200) 
    grinch_img = load_img("grinch.png", 100, 100) 
    player_img = load_face(character_name, 140) 

    class Platform(pygame.sprite.Sprite):
        def __init__(self, x, y, img, is_floating=False):
            super().__init__()
            self.image = img
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.visual_y_offset = 0 
            if is_floating:
                offset = 40 
                self.rect = pygame.Rect(x, y + offset, TILE_SIZE, TILE_SIZE - offset)
                self.visual_y_offset = offset

    class Enemy(pygame.sprite.Sprite):
        def __init__(self, x, y, limit_left, limit_right):
            super().__init__()
            self.image = grinch_img
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.bottom = y
            self.speed = 3
            self.limit_left = limit_left
            self.limit_right = limit_right
            self.vel_y = 0 
            self.on_ground = False
            self.jump_power = JUMP_POWER * 0.65 

        def update(self, blocks):
            self.rect.x += self.speed
            if self.rect.right > self.limit_right or self.rect.left < self.limit_left:
                self.speed *= -1
                self.image = pygame.transform.flip(self.image, True, False)
            self.vel_y += GRAVITY
            self.rect.y += self.vel_y
            self.on_ground = False
            hits = pygame.sprite.spritecollide(self, blocks, False)
            for block in hits:
                if self.vel_y > 0:
                    self.rect.bottom = block.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = block.rect.bottom
                    self.vel_y = 0
            if self.on_ground and random.random() < 0.02: 
                self.vel_y = self.jump_power

    class Gift(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.image = gift_img
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y

    class Goal(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.image = santa_img
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.bottom = y

    class Player(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.image = player_img
            self.rect = self.image.get_rect()
            self.rect.inflate_ip(-20, -10) 
            self.rect.x = x
            self.rect.bottom = y
            self.vel_y = 0
            self.on_ground = False
            self.facing_right = True
            
        def update(self, keys, blocks):
            dx = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -MOVE_SPEED
                if self.facing_right:
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.facing_right = False
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = MOVE_SPEED
                if not self.facing_right:
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.facing_right = True
            self.rect.x += dx
            hits = pygame.sprite.spritecollide(self, blocks, False)
            for block in hits:
                if dx > 0: self.rect.right = block.rect.left
                elif dx < 0: self.rect.left = block.rect.right
            self.vel_y += GRAVITY
            self.rect.y += self.vel_y
            self.on_ground = False
            hits = pygame.sprite.spritecollide(self, blocks, False)
            for block in hits:
                if self.vel_y > 0:
                    self.rect.bottom = block.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = block.rect.bottom
                    self.vel_y = 0

        def jump(self):
            if self.on_ground:
                self.vel_y = JUMP_POWER

    # --- DISSSENY DE NIVELL (USER MAP) ---
    level_map = [
        "                                                                                                                                                                                                     ",
        "                                                                                                                                                                                                     ",
        "                          R                                                                                                                                                                          ",
        "                         ###                                               R           R                         R                                                                                   ",
        "        R                                               R                 ###         ###     G           G            G                                R                                            ",
        "       ###          ###                                ###                           ###              #########       #####                        ##########                                        ",
        "                                     R                              G              R                                                          R                            R                         ",
        " P            G                   #######        G                 ###            XXXXXXXXXX         G                                                                     G                    S    ",
        "XXXXX     XXXXXXXXXX     XXXXX               XXXXXXXXX     XXXXX        XXXXX     XXXXXXXXXX     XXXXXXXXXXX                 XXXXXXXXXX     XXXXX             G        XXXXXXXXXXXX     XXXXXXXXXXXXX",
        "XXXXX     XXXXXXXXXX     XXXXX               XXXXXXXXX     XXXXX        XXXXX     XXXXXXXXXX     XXXXXXXXXXX     XXXXX       XXXXXXXXXX     XXXXX          XXXXXXX     XXXXXXXXXXXX     XXXXXXXXXXXXX",
        "XXXXX     XXXXXXXXXX     XXXXX               XXXXXXXXX     XXXXX        XXXXX     XXXXXXXXXX     XXXXXXXXXXX     XXXXX       XXXXXXXXXX     XXXXX          XXXXXXX     XXXXXXXXXXXX     XXXXXXXXXXXXX",
        "XXXXX     XXXXXXXXXX     XXXXX               XXXXXXXXX     XXXXX        XXXXX     XXXXXXXXXX     XXXXXXXXXXX     XXXXX       XXXXXXXXXX     XXXXX          XXXXXXX     XXXXXXXXXXXX     XXXXXXXXXXXXX",
        "XXXXX     XXXXXXXXXX     XXXXX               XXXXXXXXX     XXXXX        XXXXX     XXXXXXXXXX     XXXXXXXXXXX     XXXXX       XXXXXXXXXX     XXXXX          XXXXXXX     XXXXXXXXXXXX     XXXXXXXXXXXXX",
        "XXXXX     XXXXXXXXXX     XXXXX               XXXXXXXXX     XXXXX        XXXXX     XXXXXXXXXX     XXXXXXXXXXX     XXXXX       XXXXXXXXXX     XXXXX          XXXXXXX     XXXXXXXXXXXX     XXXXXXXXXXXXX",
    ]
    
    all_sprites = pygame.sprite.Group(); blocks = pygame.sprite.Group(); enemies = pygame.sprite.Group()
    gifts = pygame.sprite.Group(); goals = pygame.sprite.Group()
    
    player = None
    level_width = len(level_map[0]) * TILE_SIZE
    
    # Ajustar posició inicial del dibuixat (Offset Y)
    map_start_y = HEIGHT - (len(level_map) * TILE_SIZE) 
    
    for row_idx, row in enumerate(level_map):
        for col_idx, cell in enumerate(row):
            x = col_idx * TILE_SIZE
            y = map_start_y + (row_idx * TILE_SIZE) 
            
            if cell == 'X':
                p = Platform(x, y, block_img, is_floating=False); blocks.add(p); all_sprites.add(p)
            elif cell == '#':
                p = Platform(x, y, plat_img, is_floating=True); blocks.add(p); all_sprites.add(p)
            elif cell == 'P':
                player = Player(x, y + TILE_SIZE); all_sprites.add(player)
            elif cell == 'G':
                e = Enemy(x, y + TILE_SIZE, x - 200, x + 200); enemies.add(e); all_sprites.add(e)
            elif cell == 'R':
                g = Gift(x + 20, y + 20); gifts.add(g); all_sprites.add(g)
            elif cell == 'S':
                s = Goal(x, y + TILE_SIZE); goals.add(s); all_sprites.add(s)

    # --- Càmera ---
    camera_x = 0
    camera_y = 0 
    
    score = 0
    total_gifts = len(gifts)
    game_over = False; won = False
    
    while True:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return
                if event.key == pygame.K_SPACE:
                    if not game_over and not won: player.jump()
                    elif game_over or won: return run_platformer_game(character_name)

        if not game_over and not won:
            player.update(keys, blocks)
            enemies.update(blocks)
            
            enemy_hits = pygame.sprite.spritecollide(player, enemies, False)
            for enemy in enemy_hits:
                if player.vel_y > 0 and player.rect.bottom < enemy.rect.centery + 40:
                    enemy.kill(); player.vel_y = -12 
                else: game_over = True
            
            if pygame.sprite.spritecollide(player, gifts, True): score += 1
            if pygame.sprite.spritecollide(player, goals, False) and score >= total_gifts: won = True
            if player.rect.top > HEIGHT + 1000: game_over = True

            target_cam_x = player.rect.centerx - WIDTH // 2
            target_cam_x = max(0, min(target_cam_x, level_width - WIDTH))
            camera_x += (target_cam_x - camera_x) * 0.1

        if bg_img: screen.blit(bg_img, (0, 0))
        else: screen.fill((135, 206, 235))
        
        for sprite in all_sprites:
            y_offset = getattr(sprite, "visual_y_offset", 0)
            screen.blit(sprite.image, (sprite.rect.x - camera_x, sprite.rect.y - camera_y - y_offset))
            
        score_text = font_ui.render(f"Regals: {score} / {total_gifts}", True, BLACK)
        draw_paper_box(screen, pygame.Rect(20, 20, 300, 60), score_text)
        
        if game_over:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); s.fill((0,0,0,180)); screen.blit(s, (0,0))
            
            txt_surf = font_big.render("OH NO! T'HAN ATRAPAT!", True, PAPER_COLOR)
            txt_rect = txt_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            screen.blit(txt_surf, txt_rect)
            
            sub_surf = font_ui.render("Espai per reiniciar", True, WHITE)
            sub_rect = sub_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
            screen.blit(sub_surf, sub_rect)

        if won:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); s.fill((0,0,0,180)); screen.blit(s, (0,0))
            
            txt_surf = font_big.render("GRÀCIES PER L'AJUDA!", True, GOLD)
            txt_rect = txt_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            screen.blit(txt_surf, txt_rect)
            
            sub_surf = font_ui.render("Has salvat el Nadal!", True, WHITE)
            sub_rect = sub_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
            screen.blit(sub_surf, sub_rect)

        pygame.display.flip(); clock.tick(FPS)

# ==============================================================================
# JOC 5: RITME DE NADAL (Taiko Style - Custom Beat Map)
# ==============================================================================

def run_rhythm_game(character_name):
    # --- CONFIGURACIÓ DEL MAPA DE RITME (BEAT MAP) ---
    BEAT_MAP = [
        4000, 4520, 5040,
        8100, 8620, 9140,
        10650, 11600, 12600, 13050,
        14100, 15100, 16100,
        17500, 18020, 18540
    ]
    # ----------------------------------------------------
    
    bg_img = None
    if os.path.exists("fons_musica.png"):
        bg_img = pygame.transform.smoothscale(pygame.image.load("fons_musica.png").convert(), (WIDTH, HEIGHT))
        
    HIT_ZONE_COLOR = (200, 200, 200)
    
    song_loaded = False
    try:
        if os.path.exists("nadal_song.mp3"):
            pygame.mixer.music.load("nadal_song.mp3")
            song_loaded = True
        elif os.path.exists("nadal_song.wav"):
            pygame.mixer.music.load("nadal_song.wav")
            song_loaded = True
    except:
        print("Error carregant música.")

    # --- Elements del Joc ---
    NOTE_Y = int(HEIGHT * 0.5)
    HIT_X = int(WIDTH * 0.2)
    HIT_RADIUS = int(HEIGHT * 0.08)
    NOTE_RADIUS = int(HEIGHT * 0.06)
    NOTE_SPEED = int(WIDTH * 0.010) 
    
    SPAWN_X = WIDTH + 50
    travel_dist = SPAWN_X - HIT_X
    travel_time_ms = (travel_dist / NOTE_SPEED) * (1000 / FPS)
    
    active_notes = [] 
    score = 0
    combo = 0
    max_combo = 0
    
    current_note_index = 0
    start_time = 0
    music_started = False
    
    feedback_text = ""
    feedback_timer = 0
    feedback_color = WHITE
    hit_effect_timer = 0 
    
    game_finished = False
    won = False
    
    note_img = load_christmas_ball(NOTE_RADIUS * 2)
    
    running = True
    while running:
        current_ticks = pygame.time.get_ticks()
        
        if not music_started:
            if song_loaded: pygame.mixer.music.play()
            start_time = current_ticks
            music_started = True
            
        song_time = current_ticks - start_time
        
        if song_time >= 18800 and not game_finished:
            if song_loaded: pygame.mixer.music.stop()
            game_finished = True
            won = (score >= 1000)
        
        if not game_finished and current_note_index < len(BEAT_MAP):
            next_beat_time = BEAT_MAP[current_note_index]
            if song_time >= next_beat_time - travel_time_ms:
                active_notes.append({'x': float(SPAWN_X), 'hit_time': next_beat_time, 'active': True})
                current_note_index += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if song_loaded: pygame.mixer.music.stop()
                    return
                if game_finished and not won and event.key == pygame.K_SPACE:
                    return run_rhythm_game(character_name)
                
                if not game_finished and event.key == pygame.K_SPACE:
                    hit_effect_timer = current_ticks + 100
                    hit_made = False
                    for note in active_notes:
                        if note['active']:
                            dist = abs(note['x'] - HIT_X)
                            if dist < HIT_RADIUS * 0.5:
                                score += 100; combo += 1
                                feedback_text = "PERFECTE!"; feedback_color = GOLD
                                feedback_timer = current_ticks + 500
                                note['active'] = False; hit_made = True; break
                            elif dist < HIT_RADIUS * 1.2:
                                score += 50; combo += 1
                                feedback_text = "BÉ!"; feedback_color = CHRISTMAS_GREEN
                                feedback_timer = current_ticks + 500
                                note['active'] = False; hit_made = True; break
                    if not hit_made: combo = 0 

        if not game_finished:
            for note in active_notes:
                note['x'] -= NOTE_SPEED
                if note['x'] < HIT_X - HIT_RADIUS * 2 and note['active']:
                    note['active'] = False
                    combo = 0
                    feedback_text = "MISS..."; feedback_color = (150, 150, 150)
                    feedback_timer = current_ticks + 500

            active_notes = [n for n in active_notes if n['x'] > -100]
            if combo > max_combo: max_combo = combo

        if bg_img: screen.blit(bg_img, (0,0))
        else: screen.fill((30, 30, 50))
        
        # Carril
        lane_rect = pygame.Rect(0, NOTE_Y - HIT_RADIUS - 10, WIDTH, HIT_RADIUS * 2 + 20)
        s = pygame.Surface((WIDTH, lane_rect.height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 100))
        screen.blit(s, (0, lane_rect.y))
        
        # Fons Tambor (Sense límit)
        s_drum = pygame.Surface((HIT_RADIUS*2, HIT_RADIUS*2), pygame.SRCALPHA)
        pygame.draw.circle(s_drum, (0, 0, 0, 150), (HIT_RADIUS, HIT_RADIUS), HIT_RADIUS)
        screen.blit(s_drum, (HIT_X - HIT_RADIUS, NOTE_Y - HIT_RADIUS))

        # Tambor Flash (Sense límit)
        if current_ticks < hit_effect_timer:
             pygame.draw.circle(screen, (255, 255, 200), (HIT_X, NOTE_Y), HIT_RADIUS)

        for note in active_notes:
            if note['active']:
                r = note_img.get_rect(center=(int(note['x']), NOTE_Y))
                screen.blit(note_img, r)

        ui_rect = pygame.Rect(20, 20, 300, 120)
        draw_paper_box(screen, ui_rect)
        screen.blit(font_ui.render(f"Punts: {score}", True, TEXT_COLOR), (40, 35))
        screen.blit(font_ui.render(f"Combo: {combo}", True, CHRISTMAS_RED), (40, 80))
        
        if current_ticks < feedback_timer:
            fb_surf = font_ui.render(feedback_text, True, feedback_color)
            fb_w = fb_surf.get_width() + 40
            fb_h = 60
            fb_rect = pygame.Rect(0, 0, fb_w, fb_h)
            fb_rect.center = (HIT_X, NOTE_Y - 150)
            draw_paper_box(screen, fb_rect, fb_surf)

        if game_finished:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); s.fill((0,0,0,180)); screen.blit(s, (0,0))
            if won:
                txt_surf = font_big.render("MOLT BÉ!!!", True, GOLD)
                txt_rect = txt_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
                screen.blit(txt_surf, txt_rect)
                
                sub_surf = font_ui.render("Pots obrir el següent regal", True, WHITE)
                sub_rect = sub_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
                screen.blit(sub_surf, sub_rect)
            else:
                txt_surf = font_big.render("TORNA-HO A PROVAR!", True, CHRISTMAS_RED)
                txt_rect = txt_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
                screen.blit(txt_surf, txt_rect)
                
                sub_surf = font_ui.render("Prem ESPAI per reiniciar", True, WHITE)
                sub_rect = sub_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
                screen.blit(sub_surf, sub_rect)
        else:
            txt_inst = font_ui.render("Prem ESPAI al ritme!", True, WHITE)
            screen.blit(txt_inst, txt_inst.get_rect(center=(WIDTH//2, HEIGHT - 50)))

        pygame.display.flip()
        clock.tick(FPS)


# ==============================================================================
# HUB DE JOCS (Menú Selecció - 5 JOCS)
# ==============================================================================

def game_hub(character_name):
    img_player = load_face(character_name, 100)
    title_text = font_title.render("JOC DE NADAL DE FAMÍLIA", True, PAPER_COLOR)
    
    # Disseny: 3 Dalt, 2 Avall
    btn_w = int(WIDTH * 0.22) # Una mica més estrets per cabre-hi 3
    btn_h = int(HEIGHT * 0.15)
    
    y1 = HEIGHT * 0.35
    x1 = WIDTH * 0.15
    x2 = WIDTH * 0.39
    x3 = WIDTH * 0.63
    
    y2 = HEIGHT * 0.55
    x4 = WIDTH * 0.27
    x5 = WIDTH * 0.51
    
    rect_g1 = pygame.Rect(x1, y1, btn_w, btn_h) # Runner
    rect_g2 = pygame.Rect(x2, y1, btn_w, btn_h) # Tió
    rect_g3 = pygame.Rect(x3, y1, btn_w, btn_h) # Sopa
    rect_g4 = pygame.Rect(x4, y2, btn_w, btn_h) # Plataformas
    rect_g5 = pygame.Rect(x5, y2, btn_w, btn_h) # Ritmo (Taiko)
    
    rect_back = pygame.Rect(WIDTH*0.35, HEIGHT*0.8, WIDTH*0.3, 60)

    hub_running = True
    while hub_running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "EXIT"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if rect_g1.collidepoint(mouse_pos): run_japan_game(character_name)
                elif rect_g2.collidepoint(mouse_pos): run_tio_game(character_name)
                elif rect_g3.collidepoint(mouse_pos): run_soup_game(character_name)
                elif rect_g4.collidepoint(mouse_pos): run_platformer_game(character_name)
                elif rect_g5.collidepoint(mouse_pos): run_rhythm_game(character_name)
                elif rect_back.collidepoint(mouse_pos): return "BACK" 

        if os.path.exists("fondo_fuji.png"): 
             bg = pygame.transform.smoothscale(pygame.image.load("fondo_fuji.png").convert(), (WIDTH, HEIGHT))
             screen.blit(bg, (0,0))
             overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); overlay.fill((0,0,0,150))
             screen.blit(overlay, (0,0))
        else: screen.fill((50, 20, 20))

        t_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT*0.15))
        screen.blit(title_text, t_rect)
        screen.blit(img_player, (20, 20))
        name_txt = font_ui.render(f"Jugador: {character_name.capitalize()}", True, WHITE)
        screen.blit(name_txt, (140, 50))
        
        draw_paper_box(screen, rect_g1, render_multiline_text("RECORDS\nDE JAPÓ", font_ui, TEXT_COLOR), None, rect_g1.collidepoint(mouse_pos))
        draw_paper_box(screen, rect_g2, render_multiline_text("EL CAGA TIÓ", font_ui, TEXT_COLOR), None, rect_g2.collidepoint(mouse_pos))
        draw_paper_box(screen, rect_g3, render_multiline_text("SOPA DE\nLLETRES", font_ui, TEXT_COLOR), None, rect_g3.collidepoint(mouse_pos))
        draw_paper_box(screen, rect_g4, render_multiline_text("AVENTURA\nREGALS", font_ui, TEXT_COLOR), None, rect_g4.collidepoint(mouse_pos))
        draw_paper_box(screen, rect_g5, render_multiline_text("RITME\nDE NADAL", font_ui, TEXT_COLOR), None, rect_g5.collidepoint(mouse_pos))
        
        draw_paper_box(screen, rect_back, font_ui.render("CANVIAR PERSONATGE", True, TEXT_COLOR), None, rect_back.collidepoint(mouse_pos))

        pygame.display.flip()
        clock.tick(FPS)


# ==============================================================================
# SELELECCIÓ DE PERSONATGE
# ==============================================================================

def char_select_screen():
    face_size = int(HEIGHT * 0.2) 
    img_marti = load_face("marti", face_size)
    img_marta = load_face("marta", face_size)
    img_josepm = load_face("josepm", face_size)
    img_esther = load_face("esther", face_size)
    img_arnau = load_face("arnau", face_size)
    
    title = font_big.render("QUI ETS?", True, PAPER_COLOR)
    
    btn_w = int(WIDTH * 0.2)
    btn_h = int(HEIGHT * 0.3)
    
    y_row1 = int(HEIGHT * 0.25)
    y_row2 = int(HEIGHT * 0.60)
    
    x_r1_1 = int(WIDTH * 0.15); x_r1_2 = int(WIDTH * 0.40); x_r1_3 = int(WIDTH * 0.65)
    x_r2_1 = int(WIDTH * 0.275); x_r2_2 = int(WIDTH * 0.525)
    
    rect_marti = pygame.Rect(x_r1_1, y_row1, btn_w, btn_h)
    rect_marta = pygame.Rect(x_r1_2, y_row1, btn_w, btn_h)
    rect_josepm = pygame.Rect(x_r1_3, y_row1, btn_w, btn_h)
    rect_esther = pygame.Rect(x_r2_1, y_row2, btn_w, btn_h)
    rect_arnau = pygame.Rect(x_r2_2, y_row2, btn_w, btn_h)
    
    rect_quit = pygame.Rect(WIDTH - 220, HEIGHT - 80, 200, 60)
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if rect_marti.collidepoint(mouse_pos): return "marti"
                if rect_marta.collidepoint(mouse_pos): return "marta"
                if rect_josepm.collidepoint(mouse_pos): return "josepm"
                if rect_esther.collidepoint(mouse_pos): return "esther"
                if rect_arnau.collidepoint(mouse_pos): return "arnau"
                if rect_quit.collidepoint(mouse_pos): return None
        
        screen.fill((30, 30, 50)) 
        t_rect = title.get_rect(center=(WIDTH//2, HEIGHT*0.12))
        screen.blit(title, t_rect)
        
        draw_paper_box(screen, rect_marti, font_ui.render("MARTÍ", True, TEXT_COLOR), img_marti, rect_marti.collidepoint(mouse_pos))
        draw_paper_box(screen, rect_marta, font_ui.render("MARTA", True, TEXT_COLOR), img_marta, rect_marta.collidepoint(mouse_pos))
        draw_paper_box(screen, rect_josepm, font_ui.render("JOSEP M", True, TEXT_COLOR), img_josepm, rect_josepm.collidepoint(mouse_pos))
        draw_paper_box(screen, rect_esther, font_ui.render("ESTHER", True, TEXT_COLOR), img_esther, rect_esther.collidepoint(mouse_pos))
        draw_paper_box(screen, rect_arnau, font_ui.render("ARNAU", True, TEXT_COLOR), img_arnau, rect_arnau.collidepoint(mouse_pos))
        draw_paper_box(screen, rect_quit, font_ui.render("SORTIR", True, TEXT_COLOR), None, rect_quit.collidepoint(mouse_pos))
        
        pygame.display.flip()
        clock.tick(FPS)

# --- EXECUCIÓ PRINCIPAL ---
if __name__ == "__main__":
    while True:
        player_name = char_select_screen()
        if not player_name: break 
        result = game_hub(player_name)
        if result == "EXIT": break

    pygame.quit()
    sys.exit()
