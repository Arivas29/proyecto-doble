from pygame import *
from config import * 
from random import *

init()

# TRABAJO CON FUENTES
font.init()
f1 = font.SysFont('Arial', 32)
# Fuente exclusiva para el botón de Play
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

# --- CARGAR FONDO DE LA PANTALLA DE INICIO ---
try:
    menu_background = transform.scale(image.load(MENU_BG_IMG), (ANCHO, ALTO))
except:
    menu_background = Surface((ANCHO, ALTO))
    menu_background.fill((40, 40, 40)) # Respaldo gris oscuro si falla la imagen

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

# CONFIGURACIÓN DEL BOTÓN DE PLAY (En el medio abajo)
btn_ancho, btn_alto = 220, 70
btn_x = (ANCHO // 2) - (btn_ancho // 2)
btn_y = ALTO - 150  # Ubicado abajo en la pantalla
play_button_rect = Rect(btn_x, btn_y, btn_ancho, btn_alto)

# CONFIGURACIÓN JUGADORES Y GRUPOS
player1 = Player(PLAYER_IMG, 60, (ALTO // 2) - 80, 150, 160, 5)
player2 = Player(PLAYER_IMG2, ANCHO - 210, (ALTO // 2) - 80, 150, 160, 5)

bullets1 = sprite.Group()
bullets2 = sprite.Group()

# ESTADOS DEL CICLO DE JUEGO
run = True
menu = True    # Iniciamos en la pantalla de bienvenida/menú
finish = False
ganador = 0 
clock = time.Clock()

while run:
    # Obtener posición del ratón de forma constante
    mouse_pos = mouse.get_pos()

    for e in event.get():
        if e.type == QUIT:
            run = False
        
        if e.type == MOUSEBUTTONDOWN:
            # Si estamos en el menú y hacemos clic izquierdo sobre el botón de PLAY
            if menu and e.button == 1:
                if play_button_rect.collidepoint(mouse_pos):
                    menu = False # Apagamos el menú y arranca la acción

        if e.type == KEYDOWN:
            if e.key == K_r:
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
                ganador = 0 
                finish = False
                # Quitar el comentario de abajo si deseas que al reiniciar te devuelva al menú de inicio:
                # menu = True 
            
            if not finish and not menu: # Solo dispara si el juego está activo y no está en el menú
                if e.key == K_SPACE: 
                    player1.shoot(1, bullets1, BULLET)
                if e.key == K_RETURN: 
                    player2.shoot(-1, bullets2, BULLET_IMG)

    # --- 1. RENDERIZADO DEL MENÚ DE INICIO ---
    if menu:
        screen.blit(menu_background, (0, 0))
        
        # Efecto visual: Cambiar de color el botón si el cursor está encima (Hover effect)
        if play_button_rect.collidepoint(mouse_pos):
            draw.rect(screen, (220, 50, 50), play_button_rect, border_radius=15) # Rojo más claro
        else:
            draw.rect(screen, (170, 30, 30), play_button_rect, border_radius=15) # Rojo base
            
        # Dibujar borde fino blanco al botón
        draw.rect(screen, WHITE, play_button_rect, width=3, border_radius=15)
        
        # Agregar el texto "PLAY" centrado en el botón
        text_play = font_button.render("PLAY", True, WHITE)
        screen.blit(text_play, (play_button_rect.centerx - text_play.get_width() // 2, 
                                play_button_rect.centery - text_play.get_height() // 2))

    # --- 2. RENDERIZADO DEL JUEGO ACTIVO ---
    elif not finish:
        screen.blit(background, (0, 0))
        
        # Actualización de posiciones
        player1.update1()
        player2.update2()
        bullets1.update()
        bullets2.update()
        
        # Sistema de colisiones
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
        
        # Renderizado de sprites
        player1.reset()
        player2.reset()
        bullets1.draw(screen)
        bullets2.draw(screen)

        # Renderizado de textos en los extremos superiores
        txt_p1 = f1.render(f"Balas: {player1.ammo if not player1.reloading else 'Recargando...'} | Vidas: {player1.lives}", True, WHITE)
        txt_p2 = f1.render(f"Balas: {player2.ammo if not player2.reloading else 'Recargando...'} | Vidas: {player2.lives}", True, WHITE)
        screen.blit(txt_p1, (30, 25))
        screen.blit(txt_p2, (ANCHO - txt_p2.get_width() - 30, 25)) 

    # --- 3. PANTALLAS DE FIN DE JUEGO ---
    else:
        if ganador == 1:
            screen.blit(win_p1_img, (0, 0))
        elif ganador == 2:
            screen.blit(win_p2_img, (0, 0))
        
        txt_restart = f1.render("Presiona 'R' para reiniciar la partida", True, WHITE)
        screen.blit(txt_restart, (ANCHO // 2 - txt_restart.get_width() // 2, ALTO - 60))

    display.update()
    clock.tick(FPS)

quit()
