import pygame
import os
import sys
import subprocess

pygame.init()

WIDTH, HEIGHT = 900, 600
WORLD = 3400

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Adventure - Level 2")
clock = pygame.time.Clock()

folder = os.path.dirname(os.path.abspath(__file__))
assets = os.path.join(folder, "assets")

def load_image(name, size):
    img = pygame.image.load(os.path.join(assets, name)).convert_alpha()
    return pygame.transform.scale(img, size)

bg = load_image("background.png", (WIDTH, HEIGHT))
hero_img = load_image("player.png", (60, 80))
coin_img = load_image("coin.png", (30, 30))
platform_img = load_image("platform.png", (180, 70))
flag_img = load_image("flag.png", (120, 180))
enemy_img = load_image("enemy.png", (45, 40))

font = pygame.font.Font(None, 34)
big_font = pygame.font.Font(None, 68)

ground = [
    pygame.Rect(0, 530, 1050, 70),
    pygame.Rect(1220, 530, 830, 70),
    pygame.Rect(2220, 530, 1180, 70)
]

platforms = [
    pygame.Rect(x, y, 180, 40)
    for x, y in [
        (300, 390), (600, 280), (900, 370),
        (1200, 250), (1500, 350),
        (1800, 230), (2100, 330),
        (2400, 210), (2700, 320),
        (3000, 230)
    ]
]

blocks = ground + platforms

coin_positions = [
    (370, 340), (670, 230), (970, 320),
    (1270, 200), (1570, 300),
    (1870, 180), (2170, 280),
    (2470, 160), (2770, 270),
    (3070, 180)
]

enemy_data = [
    (450, 350, 850),
    (850, 730, 1020),
    (1500, 1350, 1780),
    (1900, 1750, 2020),
    (2550, 2350, 2800),
    (3000, 2850, 3250)
]

flag = pygame.Rect(3250, 350, 100, 180)

def reset_game():
    global player, vy, jumps, lives, score
    global coins, enemies, game_over, complete, invincible

    player = pygame.Rect(100, 450, 60, 80)
    vy, jumps = 0, 0
    lives, score = 3, 0
    invincible = 0
    game_over = False
    complete = False

    coins = [
        pygame.Rect(x, y, 30, 30)
        for x, y in coin_positions
    ]

    enemies = [
        {
            "rect": pygame.Rect(x, 490, 45, 40),
            "left": left,
            "right": right,
            "direction": 1,
            "alive": True
        }
        for x, left, right in enemy_data
    ]

def take_damage():
    global lives, vy, jumps, invincible, game_over

    if invincible > 0 or game_over:
        return

    lives -= 1

    if lives <= 0:
        game_over = True
    else:
        player.topleft = (100, 450)
        vy, jumps = 0, 0
        invincible = 90

def start_level3():
    path = os.path.join(folder, "level3.py")

    if not os.path.exists(path):
        print("Cannot find level3.py")
        return False

    subprocess.Popen([sys.executable, path], cwd=folder)
    return True

reset_game()
running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and complete:
                if start_level3():
                    running = False

            elif event.key == pygame.K_r and game_over:
                reset_game()

            elif event.key in (pygame.K_SPACE, pygame.K_UP):
                if not game_over and not complete and jumps < 2:
                    vy = -15
                    jumps += 1

    if running and not game_over and not complete:
        keys = pygame.key.get_pressed()
        dx = 5 * (
            int(keys[pygame.K_d] or keys[pygame.K_RIGHT])
            - int(keys[pygame.K_a] or keys[pygame.K_LEFT])
        )

        player.x += dx

        for block in blocks:
            if player.colliderect(block):
                if dx > 0:
                    player.right = block.left
                elif dx < 0:
                    player.left = block.right

        player.x = max(0, min(player.x, WORLD - player.width))

        old_bottom = player.bottom
        vy = min(vy + 0.8, 18)
        player.y += round(vy)

        for block in blocks:
            if player.colliderect(block):
                if vy >= 0 and old_bottom <= block.top:
                    player.bottom = block.top
                    vy, jumps = 0, 0
                elif vy < 0:
                    player.top = block.bottom
                    vy = 0

        # Falling into a gap
        if player.top > HEIGHT:
            invincible = 0
            take_damage()

        for coin in coins[:]:
            if player.colliderect(coin):
                coins.remove(coin)
                score += 1

        for enemy in enemies:
            if not enemy["alive"]:
                continue

            rect = enemy["rect"]
            distance = player.centerx - rect.centerx

            if abs(distance) < 230:
                enemy["direction"] = 1 if distance > 0 else -1

            rect.x += enemy["direction"] * 3

            if rect.left < enemy["left"]:
                rect.left = enemy["left"]
                enemy["direction"] = 1

            if rect.right > enemy["right"]:
                rect.right = enemy["right"]
                enemy["direction"] = -1

            if player.colliderect(rect):
                if vy > 0 and old_bottom <= rect.top + 12:
                    enemy["alive"] = False
                    player.bottom = rect.top
                    vy, jumps = -11, 1
                    score += 2
                else:
                    take_damage()
                    break

        if invincible > 0:
            invincible -= 1

        if not game_over and player.colliderect(flag):
            complete = True

    camera = max(0, min(player.centerx - WIDTH // 2, WORLD - WIDTH))

    screen.blit(bg, (0, 0))

    for part in ground:
        pygame.draw.rect(
            screen, (105, 73, 43),
            (part.x - camera, part.y, part.w, part.h)
        )
        pygame.draw.rect(
            screen, (65, 175, 65),
            (part.x - camera, part.y, part.w, 10)
        )

    for platform in platforms:
        screen.blit(
            platform_img,
            (platform.x - camera, platform.y - 20)
        )

    for coin in coins:
        screen.blit(coin_img, (coin.x - camera, coin.y))

    for enemy in enemies:
        if enemy["alive"]:
            rect = enemy["rect"]
            screen.blit(enemy_img, (rect.x - camera, rect.y))

    screen.blit(flag_img, (flag.x - camera, flag.y))

    if invincible == 0 or invincible % 10 < 5:
        screen.blit(hero_img, (player.x - camera, player.y))

    hud = font.render(
        f"Level 2 | Lives: {lives} | Coins: {score}",
        True, (255, 255, 255)
    )
    screen.blit(hud, (20, 20))

    hint = font.render(
        "SPACE x2 = Double Jump",
        True, (255, 255, 255)
    )
    screen.blit(hint, (20, 55))

    if game_over:
        title = "GAME OVER"
        message = "Press R to Restart"

    elif complete:
        title = "LEVEL 2 COMPLETE!"
        message = "Press ENTER to start Level 3"

    else:
        title = None

    if title:
        title_img = big_font.render(
            title, True, (255, 255, 255)
        )
        message_img = font.render(
            message, True, (255, 255, 255)
        )

        screen.blit(
            title_img,
            title_img.get_rect(center=(WIDTH // 2, 260))
        )
        screen.blit(
            message_img,
            message_img.get_rect(center=(WIDTH // 2, 340))
        )

    pygame.display.flip()

pygame.quit()
sys.exit()