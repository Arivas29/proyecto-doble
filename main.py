from pygame import *
from config import * 
from random import *

init()

# TRABAJO CON FUENTES
font.init()
f1 = font.SysFont('Arial', 32)
# Fuente exclusiva para los botones
font_button = font.SysFont('Arial', 40, bold=True)

# MAIN WINDOW
screen = display.set_mode((ANCHO, ALTO))
display.set_caption(TITULO)

# CLASE PRINCIPAL
class GameSprite(sprite.Sprite):
    def __init__(self, sprite_img, cord_x, cord_y, width, height, speed=0):
        super().__init__()
        self.width = width
        self.height = height
        try:
            self.image = transform.scale(image.load(sprite_img), (self.width, self.height))
        except:
            self.image = Surface((self.width, self.height))
            self.image.fill((200, 200, 0))
            
        self.rect = self.image.get_rect()
        self.rect.x = cord_x
        self.rect.y = cord_y
        self.speed = speed

    def reset(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))

class Bullet(GameSprite):
    def __init__(self, sprite_img, cord_x, cord_y, width, height, speed, direction):
        super().__init__(sprite_img, cord_x, cord_y, width, height, speed)
        self.direction = direction 

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.x < 0 or self.rect.x > ANCHO:
            self.kill()

class Player(GameSprite):
    def __init__(self, sprite_img, cord_x, cord_y, width, height, speed=0):
        super().__init__(sprite_img, cord_x, cord_y, width, height, speed)
        self.ammo = 5
        self.lives = 3 
        self.last_shot_time = 0
        self.reload_start_time = 0
        self.reloading = False

    def shoot(self, direction, group, bullet_sprite):
        current_time = time.get_ticks()
        
        if not self.reloading:
            if self.ammo > 0 and (current_time - self.last_shot_time > 1000):
                altura_disparo = self.rect.centery - 15
                bullet = Bullet(bullet_sprite, self.rect.centerx, altura_disparo, 30, 20, 10, direction)
                group.add(bullet)
                self.ammo -= 1
                self.last_shot_time = current_time
            
            if self.ammo == 0:
                self.reloading = True
                self.reload_start_time = current_time

        else:
            if current_time - self.reload_start_time > 2500:
                self.ammo = 5
                self.reloading = False

    def update1(self): 
        keys = key.get_pressed()
        if keys[K_w] and self.rect.y > 0:
            self.rect.y -= self.speed
        if keys[K_s] and self.rect.y < ALTO - self.rect.h:
            self.rect.y += self.speed
        if keys[K_a] and self.rect.x > 0:
            self.rect.x -= self.speed
        if keys[K_d] and self.rect.x < (ANCHO // 2) - self.rect.w:
            self.rect.x += self.speed

    def update2(self): 
        keys = key.get_pressed()
        if keys[K_UP] and self.rect.y > 0:
            self.rect.y -= self.speed
        if keys[K_DOWN] and self.rect.y < ALTO - self.rect.h:
            self.rect.y += self.speed
        if keys[K_LEFT] and self.rect.x > (ANCHO // 2):
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < ANCHO - self.rect.w:
            self.rect.x += self.speed

# OBJETOS DE FONDOS
try:
    background = transform.scale(image.load(BG_IMG), (ANCHO, ALTO))
except:
    background = Surface((ANCHO, ALTO))
    background.fill(BACK_COLOR)

try:
    menu_background = transform.scale(image.load(MENU_BG_IMG), (ANCHO, ALTO))
except:
    menu_background = Surface((ANCHO, ALTO))
    menu_background.fill((40, 40, 40))

# CARGAR IMÁGENES DE VICTORIA
try:
    win_p1_img = transform.scale(image.load(WIN_P1), (ANCHO, ALTO))
except:
    win_p1_img = Surface((ANCHO, ALTO))
    win_p1_img.fill((0, 150, 0))

try:
    win_p2_img = transform.scale(image.load(WIN_P2), (ANCHO, ALTO))
except:
    win_p2_img = Surface((ANCHO, ALTO))
    win_p2_img.fill((0, 0, 150))

# --- CONFIGURACIÓN DE TODOS LOS BOTONES ---
btn_ancho, btn_alto = 240, 70

# Botón PLAY (Pantalla de inicio)
btn_play_x = (ANCHO // 2) - (btn_ancho // 2)
btn_play_y = ALTO - 150  
play_button_rect = Rect(btn_play_x, btn_play_y, btn_ancho, btn_alto)

# Botones de Fin de Juego (Reiniciar y Menú uno al lado del otro)
distancia_botones = 40 # Espacio de separación entre ambos
total_ancho_botones = (btn_ancho * 2) + distancia_botones
start_x = (ANCHO // 2) - (total_ancho_botones // 2)

btn_restart_rect = Rect(start_x, ALTO - 130, btn_ancho, btn_alto)
btn_menu_rect = Rect(start_x + btn_ancho + distancia_botones, ALTO - 130, btn_ancho, btn_alto)

# CONFIGURACIÓN JUGADORES Y GRUPOS
player1 = Player(PLAYER_IMG, 60, (ALTO // 2) - 80, 150, 160, 5)
player2 = Player(PLAYER_IMG2, ANCHO - 210, (ALTO // 2) - 80, 150, 160, 5)

bullets1 = sprite.Group()
bullets2 = sprite.Group()

# ESTADOS DEL CICLO DE JUEGO
run = True
menu = True    
finish = False
ganador = 0 
clock = time.Clock()

# Función auxiliar para restablecer por completo los valores de una nueva partida
def reset_partida():
    player1.lives = 3
    player2.lives = 3
    player1.ammo = 5
    player2.ammo = 5
    player1.reloading = False
    player2.reloading = False
    player1.rect.x, player1.rect.y = 60, (ALTO // 2) - 80
    player2.rect.x, player2.rect.y = ANCHO - 210, (ALTO // 2) - 80
    bullets1.empty()
    bullets2.empty()

while run:
    mouse_pos = mouse.get_pos()

    for e in event.get():
        if e.type == QUIT:
            run = False
        
        if e.type == MOUSEBUTTONDOWN and e.button == 1:
            # Interacción en la pantalla de inicio (Menú)
            if menu:
                if play_button_rect.collidepoint(mouse_pos):
                    menu = False 

            # Interacción en la pantalla de Fin de Juego (Victoria)
            elif finish:
                if btn_restart_rect.collidepoint(mouse_pos):
                    reset_partida()
                    ganador = 0
                    finish = False # Inicia la partida directamente
                    
                elif btn_menu_rect.collidepoint(mouse_pos):
                    reset_partida()
                    ganador = 0
                    finish = False
                    menu = True # Regresa a la pantalla de inicio

        if e.type == KEYDOWN:
            if not finish and not menu: 
                if e.key == K_SPACE: 
                    player1.shoot(1, bullets1, BULLET)
                if e.key == K_RETURN: 
                    player2.shoot(-1, bullets2, BULLET_IMG)

    # --- 1. RENDERIZADO DEL MENÚ DE INICIO ---
    if menu:
        screen.blit(menu_background, (0, 0))
        
        if play_button_rect.collidepoint(mouse_pos):
            draw.rect(screen, (220, 50, 50), play_button_rect, border_radius=15) 
        else:
            draw.rect(screen, (170, 30, 30), play_button_rect, border_radius=15) 
            
        draw.rect(screen, WHITE, play_button_rect, width=3, border_radius=15)
        text_play = font_button.render("PLAY", True, WHITE)
        screen.blit(text_play, (play_button_rect.centerx - text_play.get_width() // 2, 
                                play_button_rect.centery - text_play.get_height() // 2))

    # --- 2. RENDERIZADO DEL JUEGO ACTIVO ---
    elif not finish:
        screen.blit(background, (0, 0))
        
        player1.update1()
        player2.update2()
        bullets1.update()
        bullets2.update()
        
        if sprite.spritecollide(player2, bullets1, True):
            player2.lives -= 1
            if player2.lives <= 0:
                ganador = 1 
                finish = True

        if sprite.spritecollide(player1, bullets2, True):
            player1.lives -= 1
            if player1.lives <= 0:
                ganador = 2 
                finish = True
        
        player1.reset()
        player2.reset()
        bullets1.draw(screen)
        bullets2.draw(screen)

        txt_p1 = f1.render(f"Balas: {player1.ammo if not player1.reloading else 'Recargando...'} | Vidas: {player1.lives}", True, WHITE)
        txt_p2 = f1.render(f"Balas: {player2.ammo if not player2.reloading else 'Recargando...'} | Vidas: {player2.lives}", True, WHITE)
        screen.blit(txt_p1, (30, 25))
        screen.blit(txt_p2, (ANCHO - txt_p2.get_width() - 30, 25)) 

    # --- 3. PANTALLAS DE FIN DE JUEGO (CON LOS DOS NUEVOS BOTONES) ---
    else:
        if ganador == 1:
            screen.blit(win_p1_img, (0, 0))
        elif ganador == 2:
            screen.blit(win_p2_img, (0, 0))
        
        # --- DIBUJAR BOTÓN REINICIAR ---
        if btn_restart_rect.collidepoint(mouse_pos):
            draw.rect(screen, (50, 180, 50), btn_restart_rect, border_radius=15) # Verde brillante al pasar el mouse
        else:
            draw.rect(screen, (30, 130, 30), btn_restart_rect, border_radius=15) # Verde base
        draw.rect(screen, WHITE, btn_restart_rect, width=3, border_radius=15)
        
        text_restart = font_button.render("Reiniciar", True, WHITE)
        screen.blit(text_restart, (btn_restart_rect.centerx - text_restart.get_width() // 2, 
                                   btn_restart_rect.centery - text_restart.get_height() // 2))

        # --- DIBUJAR BOTÓN MENÚ ---
        if btn_menu_rect.collidepoint(mouse_pos):
            draw.rect(screen, (80, 80, 220), btn_menu_rect, border_radius=15) # Azul brillante al pasar el mouse
        else:
            draw.rect(screen, (50, 50, 160), btn_menu_rect, border_radius=15) # Azul base
        draw.rect(screen, WHITE, btn_menu_rect, width=3, border_radius=15)
        
        text_menu = font_button.render("Menú", True, WHITE)
        screen.blit(text_menu, (btn_menu_rect.centerx - text_menu.get_width() // 2, 
                               btn_menu_rect.centery - text_menu.get_height() // 2))

    display.update()
    clock.tick(FPS)

quit()
