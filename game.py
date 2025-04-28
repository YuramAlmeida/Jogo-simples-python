import pgzrun
import random
from pygame import Rect

# Configurações da tela
WIDTH = 1000
HEIGHT = 800

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Estados do jogo
MENU = 0
PLAYING = 1
GAME_OVER = 2
VICTORY = 3
game_state = MENU

# Configurações de áudio
sound_enabled = True
background_music = "background_music"  # Nome do arquivo sem extensão

# Botões do menu
buttons = {
    "start": Rect(WIDTH // 2 - 100, HEIGHT // 2 - 80, 200, 50),
    "sound": Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50),
    "exit":  Rect(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 50)
}

# Inicialização do jogo e dos objetos no mundo
def init_game():
    global player, enemies, camera_offset_x, score, flag
    
    # Jogador
    player = Actor("hero_idle")
    player.x = 100
    player.y = HEIGHT - 100
    player.y_vel = 0
    player.on_ground = False
    
    # Inimigos (lista para melhor controle)
    enemies = [
        {"actor": Actor("enemy_idle"),  "direction": 1,  "speed": 1.5},
        {"actor": Actor("enemy_idle2"), "direction": -1, "speed": 2},    # Inimigo variante
        {"actor": Actor("enemy_idle"),  "direction": 1,  "speed": 1},
        {"actor": Actor("enemy_idle"),  "direction": -1, "speed": 1.8}
    ]
    
    # Posiciona os inimigos
    for i, enemy in enumerate(enemies):
        enemy["actor"].x = 400 + i * 200
        enemy["actor"].y = HEIGHT - 100
    
    # Bandeira de vitória (posição definida em coordenadas do mundo)
    flag = Actor("flag")
    flag.x = WIDTH * 2 - 100
    flag.y = HEIGHT - 100
    
    # Variáveis do jogo
    camera_offset_x = 0
    score = 0

init_game()

# Plataformas definidas em coordenadas do mundo (as existentes, duas próximas à bandeira e duas novas)
platforms = [
    Rect(0, HEIGHT - 50, WIDTH * 2, 50),
    Rect(200, HEIGHT - 150, 150, 20),
    Rect(400, HEIGHT - 250, 150, 20),
    Rect(600, HEIGHT - 350, 150, 20),
    Rect(800, HEIGHT - 450, 150, 20),
    Rect(333, HEIGHT - 250, 150, 20),
    Rect(1000, HEIGHT - 250, 150, 20),
    # Plataformas próximas à bandeira já existentes
    Rect(WIDTH * 2 - 500, HEIGHT - 200, 150, 20),
    Rect(WIDTH * 2 - 300, HEIGHT - 300, 150, 20),
    # Novas plataformas próximas à bandeira:
    Rect(WIDTH * 2 - 250, HEIGHT - 150, 150, 20),
    Rect(WIDTH * 2 - 150, HEIGHT - 250, 150, 20)
]

# Variáveis do jogo
PLAYER_VEL = 5
GRAVITY = 1
JUMP_STRENGTH = 15

def update_music():
    """Controla a reprodusao da música de fundo."""
    if sound_enabled:
        if not music.is_playing(background_music):
            music.play(background_music)
    else:
        music.stop()

def update():
    global game_state, camera_offset_x, score

    update_music()

    if game_state == PLAYING:
        # Movimento do jogador
        if keyboard.left:
            player.x -= PLAYER_VEL
        if keyboard.right:
            player.x += PLAYER_VEL
        if keyboard.up and player.on_ground:
            player.y_vel = -JUMP_STRENGTH
            player.on_ground = False

        # Aplicar gravidade ao jogador
        player.y_vel += GRAVITY
        player.y += player.y_vel

        # Verificar colisão do jogador com as plataformas (COORDENADAS DO MUNDO)
        player.on_ground = False
        for plat in platforms:
            if (player.colliderect(plat) and player.y_vel > 0 and 
                (player.y + player.height / 2) > plat.top):
                player.y = plat.top - (player.height / 2)
                player.y_vel = 0
                player.on_ground = True
                break

        # Checa colisão com os inimigos
        for enemy in enemies:
            if player.colliderect(enemy["actor"]):
                game_state = GAME_OVER
                music.stop()

        # Movimento e comportamento dos inimigos
        for enemy in enemies:
            act = enemy["actor"]
            # Inverter direção nas bordas do nível ou aleatoriamente
            if act.x < 50 or act.x > WIDTH * 2 - 50 or random.random() < 0.01:
                enemy["direction"] *= -1
            act.x += enemy["direction"] * enemy["speed"]

            # Aplica gravidade aos inimigos e corrige colisões com plataformas
            act.y += GRAVITY
            for plat in platforms:
                if act.colliderect(plat) and (act.y + act.height / 2) > plat.top:
                    act.y = plat.top - (act.height / 2)
                    break

        # Verifica se alcançou a bandeira
        if player.colliderect(flag):
            game_state = VICTORY
            if sound_enabled:
                sounds.victory.play()

        # Atualiza pontuação
        score += 0.1
        
        # Atualiza a câmera para seguir o jogador (limitando os extremos do mundo)
        camera_offset_x = max(0, player.x - WIDTH // 2)
        camera_offset_x = min(camera_offset_x, WIDTH * 2 - WIDTH)

def draw_menu():
    screen.fill(BLACK)
    screen.draw.text("Jogo de Plataforma", center=(WIDTH // 2, HEIGHT // 4),
                     fontsize=60, color=WHITE)

    for key, btn in buttons.items():
        screen.draw.filled_rect(btn, WHITE)
        if key == "start":
            text = "Comesar"
        elif key == "sound":
            text = "Som: Ligado" if sound_enabled else "Som: Desligado"
        elif key == "exit":
            text = "Sair"
        screen.draw.text(text,
                         center=(btn.x + btn.width // 2, btn.y + btn.height // 2),
                         fontsize=30, color=BLACK)

def draw_game():
    screen.fill(BLUE)

    # Desenha as plataformas (com ajuste da câmera)
    for plat in platforms:
        shifted_plat = plat.move(-camera_offset_x, 0)
        screen.draw.filled_rect(shifted_plat, WHITE)

    # Desenha o jogador com ajuste da câmera
    player_screen_x = player.x - camera_offset_x
    player_screen_y = player.y
    screen.blit(player.image,
                (player_screen_x - player.width / 2, player_screen_y - player.height / 2))

    # Desenha os inimigos com ajuste da câmera
    for enemy in enemies:
        act = enemy["actor"]
        enemy_screen_x = act.x - camera_offset_x
        enemy_screen_y = act.y
        screen.blit(act.image,
                    (enemy_screen_x - act.width / 2, enemy_screen_y - act.height / 2))

    # Desenha a bandeira com posição ajustada
    flag_screen_x = flag.x - camera_offset_x
    flag_screen_y = flag.y
    screen.blit(flag.image,
                (flag_screen_x - flag.width / 2, flag_screen_y - flag.height / 2))
    
    screen.draw.text(f"Pontuasao: {int(score)}", (20, 20), color=WHITE, fontsize=30)

def draw_game_over():
    screen.fill(BLACK)
    screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT // 3),
                     fontsize=80, color=RED)
    screen.draw.text(f"Pontuasao: {int(score)}", center=(WIDTH // 2, HEIGHT // 2),
                     fontsize=50, color=WHITE)
    screen.draw.text("Clique para voltar ao menu", center=(WIDTH // 2, HEIGHT // 2 + 80),
                     fontsize=30, color=WHITE)

def draw_victory():
    screen.fill(GREEN)
    screen.draw.text("VITORIA!", center=(WIDTH // 2, HEIGHT // 3),
                     fontsize=80, color=WHITE)
    screen.draw.text(f"Pontuasao Final: {int(score)}", center=(WIDTH // 2, HEIGHT // 2),
                     fontsize=50, color=WHITE)
    screen.draw.text("Clique para voltar ao menu", center=(WIDTH // 2, HEIGHT // 2 + 80),
                     fontsize=30, color=WHITE)

def draw():
    if game_state == MENU:
        draw_menu()
    elif game_state == PLAYING:
        draw_game()
    elif game_state == GAME_OVER:
        draw_game_over()
    elif game_state == VICTORY:
        draw_victory()

def on_mouse_down(pos):
    global game_state, sound_enabled

    if game_state == MENU:
        if buttons["start"].collidepoint(pos):
            game_state = PLAYING
            init_game()
            if sound_enabled:
                music.play(background_music)
        elif buttons["sound"].collidepoint(pos):
            sound_enabled = not sound_enabled
            update_music()
        elif buttons["exit"].collidepoint(pos):
            exit()
    elif game_state in (GAME_OVER, VICTORY):
        game_state = MENU

pgzrun.go()
