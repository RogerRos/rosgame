import pygame
import random
import sys

# Inicialitzar pygame
pygame.init()

# Configuració de la pantalla
AMPLADA, ALÇADA = 800, 600
BLANC = (255, 255, 255)
NEGRE = (0, 0, 0)
VERMELL = (255, 0, 0)
FPS = 60

# Configuració del joc
GRAVETAT = 0.5
SALT_JUGADOR = -10
VELOCITAT_JUGADOR = 5
AMPLADA_PLATAFORMA = 200
ALÇADA_PLATAFORMA = 20
MIDA_MONEDA = 20

# Crear la finestra
pantalla = pygame.display.set_mode((AMPLADA, ALÇADA))
pygame.display.set_caption("Joc de Plataformes")

# Relotge per controlar la velocitat d'actualització
rellotge = pygame.time.Clock()

# Classe per representar el jugador
class Jugador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 50))
        self.image.fill(BLANC)
        self.rect = self.image.get_rect()
        self.rect.center = (AMPLADA // 2, ALÇADA // 2)
        self.vel_y = 0
        self.saltant = False
        self.comptador_salt = 0  # Comptador de salts realitzats
        self.max_saltar = 4   # Número màxim de salts permessos a l'aire
        self.puntuacio = 0  # Puntuació del jugador
        self.platforma_tocada = False  # Flag per controlar si el jugador ha tocat una plataforma recentment

    def update(self):
        self.vel_y += GRAVETAT
        self.rect.y += self.vel_y
        if self.rect.bottom > ALÇADA:
            self.rect.bottom = ALÇADA
            self.vel_y = 0
            self.saltant = False
            self.comptador_salt = 0  # Reiniciar el comptador de salts

    def saltar(self):
        if not self.saltant or self.comptador_salt < self.max_saltar:
            self.vel_y = SALT_JUGADOR
            self.saltant = True
            self.comptador_salt += 1

    def moure(self, direccio):
        if direccio == "ESQUERRA":
            self.rect.x -= VELOCITAT_JUGADOR
        elif direccio == "DRETA":
            self.rect.x += VELOCITAT_JUGADOR
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > AMPLADA:
            self.rect.right = AMPLADA

# Classe per representar les plataformes
class Plataforma(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((AMPLADA_PLATAFORMA, ALÇADA_PLATAFORMA))
        self.image.fill(BLANC)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Classe per representar les monedes
class Moneda(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((MIDA_MONEDA, MIDA_MONEDA))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

# Funció per generar plataformes aleatòries
def generar_plataformes():
    plataformes = pygame.sprite.Group()
    y = ALÇADA - 200
    for _ in range(4):  # Reduir el nombre de plataformes
        x = random.randrange(AMPLADA - AMPLADA_PLATAFORMA)
        plataforma = Plataforma(x, y)
        plataformes.add(plataforma)
        tots_els_sprites.add(plataforma)
        y -= random.randrange(150, 250)  # Ajustar el rang d'alçada
    return plataformes

# Funció per generar monedes aleatòries
def generar_monedes(plataformes):
    monedes = pygame.sprite.Group()
    for plataforma in plataformes:
        if random.random() < 0.3:
            moneda = Moneda(plataforma.rect.centerx, plataforma.rect.top - 30)
            monedes.add(moneda)
            tots_els_sprites.add(moneda)
    return monedes

# Crear grups de sprites
tots_els_sprites = pygame.sprite.Group()
plataformes = generar_plataformes()
monedes = generar_monedes(plataformes)
jugador = Jugador()
tots_els_sprites.add(jugador)

# Crear la línia vermella al terra
terra = pygame.Rect(0, ALÇADA - 10, AMPLADA, 10)

# Bucle principal del joc
jugant = True
while jugant:
    # Mantenir el bucle a una velocitat constant
    rellotge.tick(FPS)

    # Gestió d'esdeveniments
    for esdeveniment in pygame.event.get():
        if esdeveniment.type == pygame.QUIT:
            jugant = False
        elif esdeveniment.type == pygame.KEYDOWN:
            if esdeveniment.key == pygame.K_SPACE:
                jugador.saltar()

    tecles = pygame.key.get_pressed()
    if tecles[pygame.K_LEFT]:
        jugador.moure("ESQUERRA")
    if tecles[pygame.K_RIGHT]:
        jugador.moure("DRETA")

    # Verificar col·lisions del jugador amb les plataformes
    tocades = pygame.sprite.spritecollide(jugador, plataformes, False)
    if tocades:
        # Si el jugador està caient i toca una plataforma des de dalt,
        # li permetem saltar de nou
        if jugador.vel_y > 0 and jugador.rect.bottom < tocades[0].rect.bottom:
            jugador.rect.bottom = tocades[0].rect.top
            jugador.vel_y = 0
            jugador.saltant = False
            jugador.comptador_salt = 0  # Reiniciar el comptador de salts
            # Si el jugador no ha tocat una plataforma recentment, afegir punts
            if not jugador.platforma_tocada:
                jugador.puntuacio += 10
                jugador.platforma_tocada = True
    else:
        jugador.platforma_tocada = False

    # Verificar col·lisions del jugador amb les monedes
    colisions_monedes = pygame.sprite.spritecollide(jugador, monedes, True)
    # Incrementar puntuació per cada moneda recollida
    if colisions_monedes:
        jugador.puntuacio += 50

    # Verificar si el jugador ha tocat la línia vermella al terra
    if jugador.rect.colliderect(terra):
        jugant = False

    # Actualitzar
    tots_els_sprites.update()

    # Renderitzar
    pantalla.fill(NEGRE)
    pygame.draw.rect(pantalla, VERMELL, terra)  # Dibuixar la línia vermella al terra
    tots_els_sprites.draw(pantalla)

    # Mostrar el marcador de punts
    font = pygame.font.Font(None, 36)
    text = font.render(f"Puntuació: {jugador.puntuacio}", True, BLANC)
    pantalla.blit(text, (10, 10))

    # Mostrar "Roger Ros" amb l'ajuda d'altres pero no ho dire jejeje
    text_by = font.render("Roger Ros", True, BLANC)
    pantalla.blit(text_by, (AMPLADA - 140, ALÇADA - 40))

    # Actualitzar la pantalla
    pygame.display.flip()

pygame.quit()
sys.exit()
