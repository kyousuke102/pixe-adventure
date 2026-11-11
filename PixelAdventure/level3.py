import pygame
import json
import os
import sys
import subprocess

pygame.init()

WIDTH, HEIGHT = 900, 600
WORLD_WIDTH = 8000
GROUND_Y = 530

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Adventure - Level 3")
clock = pygame.time.Clock()

folder = os.path.dirname(os.path.abspath(__file__))
assets = os.path.join(folder, "assets")

def load_image(name, size):
    img = pygame.image.load(
        os.path.join(assets, name)
    ).convert_alpha()
    return pygame.transform.scale(img, size)

background = load_image("background.png", (WIDTH, HEIGHT))
player_img = load_image("player.png", (60, 80))
platform_img = load_image("platform.png", (180, 70))
coin_img = load_image("coin.png", (30, 30))
enemy_img = load_image("enemy.png", (45, 40))
flag_img = load_image("flag.png", (120, 180))

font = pygame.font.Font(None, 34)
big_font = pygame.font.Font(None, 65)

# Load custom map
map_path = os.path.join(folder, "level3_map.json")

if not os.path.exists(map_path):
    print("ERROR: level3_map.json not found!")
    pygame.quit()
    sys.exit()

with open(map_path, "r", encoding="utf-8") as f:
    objects = json.load(f)

platforms = []
coins = []
enemies = []
flags = []

for obj in objects:
    x = obj["x"]
    y = obj["y"]

    if obj["type"] == "platform":
        platforms.append(pygame.Rect(x, y, 180, 40))

    elif obj["type"] == "coin":
        coins.append(pygame.Rect(x, y, 30, 30))

    elif obj["type"] == "enemy":
        enemies.append({
            "rect": pygame.Rect(x, y, 45, 40),
            "start_x": x,
            "direction": 1,
            "alive": True
        })

    elif obj["type"] == "flag":
        flags.append(pygame.Rect(x, y, 120, 180))

ground = pygame.Rect(0, GROUND_Y, WORLD_WIDTH, 70)
blocks = [ground] + platforms

player = pygame.Rect(100, 450, 60, 80)
velocity_y = 0
jump_count = 0
speed = 5
gravity = 0.8

score = 0
lives = 3
invincible = 0
game_over = False
level_complete = False

def respawn():
    global velocity_y, jump_count, lives
    global invincible, game_over

    if invincible > 0:
        return

    lives -= 1

    if lives <= 0:
        game_over = True
    else:
        player.topleft = (100, 450)
        velocity_y = 0
        jump_count = 0
        invincible = 90

def start_ending():
    ending_path = os.path.join(folder, "ending.py")

    if not os.path.exists(ending_path):
        print("ERROR: ending.py not found!")
        return False

    subprocess.Popen(
        [sys.executable, ending_path, str(score)],
        cwd=folder
    )
    return True

running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            # Enter ending after completing Level 3
            if event.key == pygame.K_RETURN and level_complete:
                if start_ending():
                    running = False

            # Restart game
            elif event.key == pygame.K_r and game_over:
                os.execv(sys.executable, [sys.executable] + sys.argv)

            # Double jump
            elif event.key in (pygame.K_SPACE, pygame.K_UP):
                if not game_over and not level_complete:
                    if jump_count < 2:
                        velocity_y = -15
                        jump_count += 1

    if not game_over and not level_complete and running:

        keys = pygame.key.get_pressed()
        dx = 0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -speed

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = speed

        # Horizontal movement
        player.x += dx

        for block in blocks:
            if player.colliderect(block):
                if dx > 0:
                    player.right = block.left
                elif dx < 0:
                    player.left = block.right

        player.x = max(
            0, min(player.x, WORLD_WIDTH - player.width)
        )

        # Gravity
        old_bottom = player.bottom
        velocity_y = min(velocity_y + gravity, 18)
        player.y += round(velocity_y)

        for block in blocks:
            if player.colliderect(block):
                if velocity_y >= 0 and old_bottom <= block.top:
                    player.bottom = block.top
                    velocity_y = 0
                    jump_count = 0

                elif velocity_y < 0:
                    player.top = block.bottom
                    velocity_y = 0

        # Coins
        for coin in coins[:]:
            if player.colliderect(coin):
                coins.remove(coin)
                score += 1

        # Enemies
        for enemy in enemies:
            if not enemy["alive"]:
                continue

            rect = enemy["rect"]
            rect.x += 2 * enemy["direction"]

            if rect.x > enemy["start_x"] + 100:
                enemy["direction"] = -1

            if rect.x < enemy["start_x"] - 100:
                enemy["direction"] = 1

            if player.colliderect(rect):
                if velocity_y > 0 and old_bottom <= rect.top + 12:
                    enemy["alive"] = False
                    player.bottom = rect.top
                    velocity_y = -11
                    jump_count = 1
                    score += 2
                else:
                    respawn()
                    break

        if invincible > 0:
            invincible -= 1

        # Finish
        for flag in flags:
            if player.colliderect(flag):
                level_complete = True

    # Camera
    camera_x = max(
        0,
        min(player.centerx - WIDTH // 2, WORLD_WIDTH - WIDTH)
    )

    screen.blit(background, (0, 0))

    # Ground
    pygame.draw.rect(
        screen, (100, 70, 40),
        (-camera_x, GROUND_Y, WORLD_WIDTH, 70)
    )

    pygame.draw.rect(
        screen, (60, 170, 60),
        (-camera_x, GROUND_Y, WORLD_WIDTH, 10)
    )

    # Platforms
    for platform in platforms:
        screen.blit(
            platform_img,
            (platform.x - camera_x, platform.y - 20)
        )

    # Coins
    for coin in coins:
        screen.blit(
            coin_img,
            (coin.x - camera_x, coin.y)
        )

    # Enemies
    for enemy in enemies:
        if enemy["alive"]:
            rect = enemy["rect"]
            screen.blit(
                enemy_img,
                (rect.x - camera_x, rect.y)
            )

    # Flags
    for flag in flags:
        screen.blit(
            flag_img,
            (flag.x - camera_x, flag.y)
        )

    # Player
    if invincible == 0 or invincible % 10 < 5:
        screen.blit(
            player_img,
            (player.x - camera_x, player.y)
        )

    # UI
    hud = font.render(
        f"Level 3 | Lives: {lives} | Coins: {score}",
        True, (255, 255, 255)
    )
    screen.blit(hud, (20, 20))

    if game_over:
        text = big_font.render(
            "GAME OVER", True, (255, 80, 80)
        )
        screen.blit(
            text,
            text.get_rect(center=(WIDTH // 2, 260))
        )

        hint = font.render(
            "Press R to Restart", True, (255, 255, 255)
        )
        screen.blit(
            hint,
            hint.get_rect(center=(WIDTH // 2, 330))
        )

    if level_complete:
        text = big_font.render(
            "LEVEL 3 COMPLETE!",
            True, (255, 255, 255)
        )
        screen.blit(
            text,
            text.get_rect(center=(WIDTH // 2, 260))
        )

        hint = font.render(
            "Press ENTER to see the Ending",
            True, (255, 255, 255)
        )
        screen.blit(
            hint,
            hint.get_rect(center=(WIDTH // 2, 340))
        )

    pygame.display.flip()

pygame.quit()
sys.exit()