from pygame import *
from config import * 
from random import *

init()

# TRABAJO CON FUENTES
font.init()
# Fuente grande (tamaño 32) para las estadísticas
f1 = font.SysFont('Arial', 32)

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
            # Si no encuentra la imagen, crea un rectángulo de color para que no crashee
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
        self.direction = direction # 1 para derecha, -1 para izquierda

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.x < 0 or self.rect.x > ANCHO:
            self.kill()

class Player(GameSprite):
    def __init__(self, sprite_img, cord_x, cord_y, width, height, speed=0):
        super().__init__(sprite_img, cord_x, cord_y, width, height, speed)
        self.ammo = 5
        self.lives = 3 # Inicializamos con 3 vidas
        self.last_shot_time = 0
        self.reload_start_time = 0
        self.reloading = False

    def shoot(self, direction, group, bullet_sprite):
        current_time = time.get_ticks()
        
        if not self.reloading:
            # Verificar si ha pasado 1 segundo (1000ms) desde el último tiro
            if self.ammo > 0 and (current_time - self.last_shot_time > 1000):
                
                # --- CORRECCIÓN DE ALTURA ---
                altura_disparo = self.rect.centery - 15
                
                bullet = Bullet(bullet_sprite, self.rect.centerx, altura_disparo, 30, 20, 10, direction)
                group.add(bullet)
                self.ammo -= 1
                self.last_shot_time = current_time
            
            # Si se acaba la munición, iniciar recarga
            if self.ammo == 0:
                self.reloading = True
                self.reload_start_time = current_time

        else:
            # Si han pasado 2.5 segundos (2500ms) recargando
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

# OBJETOS
try:
    background = transform.scale(image.load(BG_IMG), (ANCHO, ALTO))
except:
    background = Surface((ANCHO, ALTO))
    background.fill(BACK_COLOR)

# --- CARGAR LAS DOS IMÁGENES DE VICTORIA ---
try:
    win_p1_img = transform.scale(image.load(WIN_P1), (ANCHO, ALTO))
except:
    win_p1_img = Surface((ANCHO, ALTO))
    win_p1_img.fill((0, 150, 0)) # Respaldo verde si falla

try:
    win_p2_img = transform.scale(image.load(WIN_P2), (ANCHO, ALTO))
except:
    win_p2_img = Surface((ANCHO, ALTO))
    win_p2_img.fill((0, 0, 150)) # Respaldo azul si falla

# Jugador 1: Izquierda | Jugador 2: Derecha
player1 = Player(PLAYER_IMG, 60, (ALTO // 2) - 80, 150, 160, 5)
player2 = Player(PLAYER_IMG2, ANCHO - 210, (ALTO // 2) - 80, 150, 160, 5)

# Separamos los grupos de balas
bullets1 = sprite.Group()
bullets2 = sprite.Group()

# CICLO DE JUEGO
run = True
finish = False
ganador = 0 # 0 = Nadie, 1 = Gana P1, 2 = Gana P2
clock = time.Clock()

while run:
    for e in event.get():
        if e.type == QUIT:
            run = False
        
        if e.type == KEYDOWN:
            # Reiniciar juego completo al presionar 'R'
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
            
            # Solo disparar si la partida sigue activa
            if not finish:
                if e.key == K_SPACE: # P1 dispara COCACOLA
                    player1.shoot(1, bullets1, BULLET)
                
                if e.key == K_RETURN: # P2 dispara DÓLAR
                    player2.shoot(-1, bullets2, BULLET_IMG)

    if not finish:
        screen.blit(background, (0, 0))
        
        # --- SE ELIMINÓ LA LÍNEA BLANCA DIVISORIA AQUÍ ---
        
        # Actualización de posiciones
        player1.update1()
        player2.update2()
        bullets1.update()
        bullets2.update()
        
        # --- SISTEMA DE COLISIONES Y DETERMINACIÓN DEL GANADOR ---
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
        
        # Renderizado de sprites en pantalla
        player1.reset()
        player2.reset()
        bullets1.draw(screen)
        bullets2.draw(screen)

        # --- Renderizado y alineación perfecta de textos extremos ---
        txt_p1 = f1.render(f"Balas: {player1.ammo if not player1.reloading else 'Recargando...'} | Vidas: {player1.lives}", True, WHITE)
        txt_p2 = f1.render(f"Balas: {player2.ammo if not player2.reloading else 'Recargando...'} | Vidas: {player2.lives}", True, WHITE)
        
        # Player 1 se queda fijo a la izquierda (X=30)
        screen.blit(txt_p1, (30, 25))
        
        # Player 2 se calcula dinámicamente restando su propio ancho del borde total (ANCHO - ancho_del_texto - 30)
        screen.blit(txt_p2, (ANCHO - txt_p2.get_width() - 30, 25)) 

    else:
        # --- PANTALLA DE FIN DE JUEGO SELECCIONADA POR GANADOR ---
        if ganador == 1:
            screen.blit(win_p1_img, (0, 0))
        elif ganador == 2:
            screen.blit(win_p2_img, (0, 0))
        
        # Texto de ayuda superpuesto para reiniciar
        txt_restart = f1.render("Presiona 'R' para reiniciar la partida", True, WHITE)
        screen.blit(txt_restart, (ANCHO // 2 - txt_restart.get_width() // 2, ALTO - 60))

    display.update()
    clock.tick(FPS)

quit()