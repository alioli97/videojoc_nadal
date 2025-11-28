import pygame
import random
import sys
import os

# --- CONFIGURACIÓN INICIAL ---
pygame.init()

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TORI_RED_FALLBACK = (200, 50, 50)
DARUMA_RED_FALLBACK = (220, 20, 60)
GROUND_COLOR = (40, 65, 95) 
PAPER_COLOR = (250, 245, 230) 
TEXT_COLOR = (20, 20, 40)
BUTTON_HOVER_COLOR = (255, 250, 240) # Un poco más claro al pasar el ratón

# Pantalla Completa
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Misión Japón: Consigue el Libro")

# --- ALTURA DEL SUELO RELATIVA ---
GROUND_HEIGHT = int(HEIGHT * 0.05)
GROUND_Y_POS = HEIGHT - GROUND_HEIGHT

# --- CARGA DE FONDO (.PNG) ---
background_filename = "fondo_fuji.png" 
background_image = None
use_image_bg = False

if os.path.exists(background_filename):
    try:
        loaded_bg = pygame.image.load(background_filename).convert()
        background_image = pygame.transform.smoothscale(loaded_bg, (WIDTH, HEIGHT))
        use_image_bg = True
        print("Fondo cargado correctamente.")
    except:
        print("Error cargando el fondo.")
else:
    print(f"AVISO: No se encuentra '{background_filename}'.")

clock = pygame.time.Clock()
FPS = 60

# --- FUENTES ---
try:
    font_ui = pygame.font.SysFont("georgia", int(HEIGHT * 0.04), bold=True)
    font_title = pygame.font.SysFont("georgia", int(HEIGHT * 0.10), bold=True) # Título Menú
    font_big = pygame.font.SysFont("georgia", int(HEIGHT * 0.12), bold=True)
except:
    font_ui = pygame.font.Font(None, int(HEIGHT * 0.05)) 
    font_title = pygame.font.Font(None, int(HEIGHT * 0.10))
    font_big = pygame.font.Font(None, int(HEIGHT * 0.15)) 

# --- CLASES DEL JUEGO ---

class Player(pygame.sprite.Sprite):
    def __init__(self, char_name):
        super().__init__()
        filename = f"cara_{char_name}.png"
        self.target_height = int(HEIGHT * 0.25) # Ninja grande

        try:
            original_image = pygame.image.load(filename).convert_alpha()
            orig_rect = original_image.get_rect()
            aspect_ratio = orig_rect.width / orig_rect.height
            target_width = int(self.target_height * aspect_ratio)
            self.image = pygame.transform.smoothscale(original_image, (target_width, self.target_height))
        except FileNotFoundError:
            self.image = pygame.Surface((self.target_height, self.target_height))
            self.image.fill((0, 0, 255))

        self.rect = self.image.get_rect()
        self.rect.inflate_ip(-self.rect.width*0.1, -self.rect.height*0.1)
        self.rect.x = WIDTH * 0.1
        self.rect.bottom = GROUND_Y_POS
        
        self.velocity_y = 0
        self.is_jumping = False
        self.gravity = HEIGHT * 0.0018 
        self.jump_force = -HEIGHT * 0.038

    def update(self):
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y
        if self.rect.bottom >= GROUND_Y_POS:
            self.rect.bottom = GROUND_Y_POS
            self.is_jumping = False

    def jump(self):
        if not self.is_jumping:
            self.velocity_y = self.jump_force
            self.is_jumping = True

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, obs_type):
        super().__init__()
        self.type = obs_type
        self.image = None
        if self.type == "Tori":
            target_height_ratio = 0.45 
            filename = "tori.png"
            fallback_color = TORI_RED_FALLBACK
        else:
            target_height_ratio = 0.19
            filename = "daruma.png"
            fallback_color = DARUMA_RED_FALLBACK
        
        target_height = int(HEIGHT * target_height_ratio)
        
        try:
            loaded_img = pygame.image.load(filename).convert_alpha()
            orig_rect = loaded_img.get_rect()
            aspect_ratio = orig_rect.width / orig_rect.height
            target_width = int(target_height * aspect_ratio)
            self.image = pygame.transform.smoothscale(loaded_img, (target_width, target_height))
        except FileNotFoundError:
            s = target_height
            self.image = pygame.Surface((s, s))
            self.image.fill(fallback_color)
            target_width = s
        
        self.rect = self.image.get_rect()
        
        offset_y = int(HEIGHT * 0.015)
        self.rect.bottom = GROUND_Y_POS + offset_y
        
        self.rect.x = WIDTH + random.randint(0, int(WIDTH*0.3))
        self.speed = WIDTH * 0.013
        
        self.mask = pygame.mask.from_surface(self.image)
        if self.type == "Tori":
            collision_surface = pygame.Surface((target_width, target_height), pygame.SRCALPHA)
            top_bar_height = int(target_height * 0.25)
            area_to_copy = pygame.Rect(0, 0, target_width, top_bar_height)
            collision_surface.blit(self.image, (0, 0), area_to_copy)
            self.mask = pygame.mask.from_surface(collision_surface)

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill() 

# --- FUNCIONES DE DIBUJO ---

def draw_paper_box(surface, rect, text_surf=None, image_surf=None, is_hovered=False):
    """Dibuja una caja estilo papel con texto e imagen opcional"""
    color = BUTTON_HOVER_COLOR if is_hovered else PAPER_COLOR
    pygame.draw.rect(surface, color, rect, border_radius=15)
    pygame.draw.rect(surface, TEXT_COLOR, rect, 3, border_radius=15)
    
    center_x = rect.centerx
    current_y = rect.y + 20
    
    if image_surf:
        img_rect = image_surf.get_rect(center=(center_x, rect.centery - 20))
        surface.blit(image_surf, img_rect)
        current_y += img_rect.height + 10
        
    if text_surf:
        # Si hay imagen, ponemos el texto debajo, si no, centrado
        if image_surf:
            text_rect = text_surf.get_rect(center=(center_x, rect.bottom - 40))
        else:
            text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)

def load_face_for_menu(char_name):
    """Carga la cara para mostrarla en el menú"""
    try:
        img = pygame.image.load(f"cara_{char_name}.png").convert_alpha()
        # Escalamos para que quepa en el botón
        h = int(HEIGHT * 0.25) # Tamaño grande para el menú
        w = int(h * (img.get_width() / img.get_height()))
        return pygame.transform.smoothscale(img, (w, h))
    except:
        return None

# --- BUCLE DEL MENÚ ---

def main_menu():
    """Muestra la pantalla de inicio y devuelve 'marti', 'marta' o None (salir)"""
    
    # Cargar imágenes para el menú
    img_marti = load_face_for_menu("marti")
    img_marta = load_face_for_menu("marta")
    
    # Textos
    title_surf = font_title.render("JOC DE NADAL DE FAMÍLIA", True, PAPER_COLOR)
    text_marti = font_ui.render("Jugar amb Martí", True, TEXT_COLOR)
    text_marta = font_ui.render("Jugar amb Marta", True, TEXT_COLOR)
    text_exit = font_ui.render("SORTIR DEL JOC", True, TEXT_COLOR)
    
    # Definir Rectángulos de Botones
    button_w = int(WIDTH * 0.25)
    button_h = int(HEIGHT * 0.4)
    button_y = int(HEIGHT * 0.35)
    
    rect_marti = pygame.Rect(int(WIDTH * 0.2), button_y, button_w, button_h)
    rect_marta = pygame.Rect(int(WIDTH * 0.55), button_y, button_w, button_h)
    
    rect_exit = pygame.Rect(0, 0, int(WIDTH * 0.2), int(HEIGHT * 0.08))
    rect_exit.center = (WIDTH // 2, HEIGHT * 0.9)
    
    menu_running = True
    while menu_running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if rect_marti.collidepoint(mouse_pos):
                    return "marti"
                if rect_marta.collidepoint(mouse_pos):
                    return "marta"
                if rect_exit.collidepoint(mouse_pos):
                    return None

        # Dibujar Fondo
        if use_image_bg:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill((135, 206, 235))
            
        # Capa oscura para que resalte el menú
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0,0))
        
        # Dibujar Título (con sombra)
        title_rect = title_surf.get_rect(center=(WIDTH//2, HEIGHT * 0.15))
        # Sombra negra
        title_shadow = font_title.render("JOC DE NADAL DE FAMÍLIA", True, BLACK)
        screen.blit(title_shadow, (title_rect.x + 4, title_rect.y + 4))
        screen.blit(title_surf, title_rect)
        
        # Dibujar Botones
        draw_paper_box(screen, rect_marti, text_marti, img_marti, rect_marti.collidepoint(mouse_pos))
        draw_paper_box(screen, rect_marta, text_marta, img_marta, rect_marta.collidepoint(mouse_pos))
        draw_paper_box(screen, rect_exit, text_exit, None, rect_exit.collidepoint(mouse_pos))
        
        pygame.display.flip()
        clock.tick(FPS)

# --- BUCLE DEL JUEGO ---

def game_loop(character_name):
    """Ejecuta el juego con el personaje seleccionado"""
    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    player = Player(character_name)
    all_sprites.add(player)
    
    score = 0
    target_score = 3000
    game_over = False
    won = False
    
    obstacle_event = pygame.USEREVENT + 1
    pygame.time.set_timer(obstacle_event, 1400)
    
    playing = True
    while playing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Volver al menú
                    return 
                
                if event.key == pygame.K_SPACE:
                    if not game_over and not won:
                        player.jump()
                    elif game_over or won:
                        # Reiniciar partida (mismo personaje)
                        game_over = False
                        won = False
                        score = 0
                        all_sprites.empty()
                        obstacles.empty()
                        player = Player(character_name)
                        all_sprites.add(player)

            if event.type == obstacle_event and not game_over and not won:
                obs_type = random.choice(["Tori", "Daruma"])
                obstacle = Obstacle(obs_type)
                obstacles.add(obstacle)
                all_sprites.add(obstacle)

        if not game_over and not won:
            all_sprites.update()
            if pygame.sprite.spritecollide(player, obstacles, False, pygame.sprite.collide_mask):
                game_over = True
            score += 1
            if score >= target_score:
                won = True

        # --- DIBUJADO ---
        if use_image_bg:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill((135, 206, 235)) 
            
        pygame.draw.rect(screen, GROUND_COLOR, (0, GROUND_Y_POS, WIDTH, GROUND_HEIGHT)) 
        all_sprites.draw(screen)

        # UI
        score_text = f"Punts: {score} / {target_score}"
        text_surface = font_ui.render(score_text, True, TEXT_COLOR)
        padding = 20
        bg_rect = pygame.Rect(WIDTH * 0.03, HEIGHT * 0.03, text_surface.get_width() + padding * 2, text_surface.get_height() + padding)
        pygame.draw.rect(screen, PAPER_COLOR, bg_rect, border_radius=10)
        pygame.draw.rect(screen, TEXT_COLOR, bg_rect, 2, border_radius=10)
        screen.blit(text_surface, (bg_rect.x + padding, bg_rect.y + padding//2))

        # Pantallas finales
        if game_over or won:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)   
            s.fill((0, 0, 0, 180))
            screen.blit(s, (0,0))

        if game_over:
            text_go = font_big.render("HAS XOCAT!", True, PAPER_COLOR)
            text_restart = font_ui.render("Prem ESPAI per tornar-ho a provar", True, PAPER_COLOR)
            text_menu = font_ui.render("Prem ESC per tornar al menú", True, PAPER_COLOR) # Aviso extra
            
            rect_go = text_go.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
            rect_res = text_restart.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
            rect_menu = text_menu.get_rect(center=(WIDTH//2, HEIGHT//2 + 100))
            
            screen.blit(text_go, rect_go)
            screen.blit(text_restart, rect_res)
            screen.blit(text_menu, rect_menu)
        
        if won:
            text_win = font_big.render("¡NIVELL SUPERAT!", True, (255, 215, 0))
            text_gift = font_ui.render("JA POTS OBRIR EL REGAL", True, WHITE)
            rect_win = text_win.get_rect(center=(WIDTH//2, HEIGHT//2 - 40))
            rect_gift = text_gift.get_rect(center=(WIDTH//2, HEIGHT//2 + 60))
            screen.blit(text_win, rect_win)
            screen.blit(text_gift, rect_gift)

        pygame.display.flip()
        clock.tick(FPS)

# --- FLUJO PRINCIPAL DE LA APLICACIÓN ---

# Este bucle controla toda la app (Menú -> Juego -> Menú)
while True:
    # 1. Mostrar Menú y obtener selección
    selected_char = main_menu()
    
    # 2. Si es None, significa que han pulsado SALIR
    if selected_char is None:
        break
    
    # 3. Si han elegido alguien, iniciamos el juego
    game_loop(selected_char)

# Salir
pygame.quit()
sys.exit()
