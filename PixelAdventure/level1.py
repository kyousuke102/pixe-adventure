import pygame
import os
import sys
import subprocess

pygame.init()

WIDTH, HEIGHT = 900, 600
LEVEL_WIDTH = 3000

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Adventure - Level 1")
clock = pygame.time.Clock()

folder = os.path.dirname(os.path.abspath(__file__))
assets = os.path.join(folder, "assets")


# Load images
def load_image(name, size, crop=False):
    img = pygame.image.load(
        os.path.join(assets, name)
    ).convert_alpha()

    if crop:
        img = img.subsurface(img.get_bounding_rect()).copy()

    return pygame.transform.scale(img, size)


background = load_image("background.png", (WIDTH, HEIGHT))
player_img = load_image("player.png", (60, 80), True)
coin_img = load_image("coin.png", (30, 30))
platform_img = load_image("platform.png", (220, 70), True)
spike_img = load_image("spike.png", (105, 70), True)
flag_img = load_image("flag.png", (120, 180))

font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 70)


# Player
player = pygame.Rect(100, 450, 60, 80)

speed = 5
vy = 0
gravity = 0.8
on_ground = False
complete = False
score = 0


# Map
ground = pygame.Rect(0, 530, LEVEL_WIDTH, 70)

platforms = [
    pygame.Rect(x, y, 220, 70)
    for x, y in [
        (250, 410),
        (560, 340),
        (900, 410),
        (1240, 320),
        (1580, 390),
        (1920, 300),
        (2260, 390),
        (2550, 310)
    ]
]

blocks = [ground] + platforms

spikes = [
    pygame.Rect(x, 480, 105, 50)
    for x in [480, 1150, 1800, 2400]
]

coins = [
    pygame.Rect(x, y, 30, 30)
    for x, y in [
        (340, 365), (405, 365),
        (650, 295), (715, 295),
        (990, 365), (1055, 365),
        (1330, 275), (1395, 275),
        (1670, 345), (1735, 345),
        (2010, 255), (2075, 255),
        (2350, 345), (2650, 265)
    ]
]

flag = pygame.Rect(2820, 350, 100, 180)


def reset_player():
    global vy, on_ground

    player.topleft = (100, 450)
    vy = 0
    on_ground = False


def start_level2():
    path = os.path.join(folder, "level2.py")

    if not os.path.exists(path):
        print("ERROR: level2.py not found!")
        return False

    subprocess.Popen([sys.executable, path], cwd=folder)
    return True


running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_RETURN and complete:
                if start_level2():
                    running = False

            elif event.key in (pygame.K_SPACE, pygame.K_UP):
                if on_ground and not complete:
                    vy = -15
                    on_ground = False

    if running and not complete:

        keys = pygame.key.get_pressed()
        dx = 0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= speed

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += speed

        # Horizontal movement
        player.x += dx

        for block in blocks:
            if player.colliderect(block):
                if dx > 0:
                    player.right = block.left
                elif dx < 0:
                    player.left = block.right

        player.x = max(
            0, min(player.x, LEVEL_WIDTH - player.width)
        )

        # Gravity
        old_bottom = player.bottom
        vy = min(vy + gravity, 18)
        player.y += round(vy)

        on_ground = False

        # Platform collision
        for block in blocks:
            if player.colliderect(block):

                if vy >= 0 and old_bottom <= block.top:
                    player.bottom = block.top
                    vy = 0
                    on_ground = True

                elif vy < 0:
                    player.top = block.bottom
                    vy = 0

        # Spikes
        for spike in spikes:
            if player.colliderect(spike):
                reset_player()
                break

        # Coins
        for coin in coins[:]:
            if player.colliderect(coin):
                coins.remove(coin)
                score += 1

        # Finish
        if player.colliderect(flag):
            complete = True

    # Camera
    camera = max(
        0,
        min(player.centerx - WIDTH // 2, LEVEL_WIDTH - WIDTH)
    )

    # Background
    screen.blit(background, (0, 0))

    # Ground
    pygame.draw.rect(
        screen, (90, 60, 35),
        (ground.x - camera, ground.y, ground.w, ground.h)
    )

    pygame.draw.rect(
        screen, (60, 170, 60),
        (ground.x - camera, ground.y, ground.w, 10)
    )

    # Platforms
    for platform in platforms:
        screen.blit(
            platform_img,
            (platform.x - camera, platform.y)
        )

    # Spikes
    for spike in spikes:
        screen.blit(
            spike_img,
            (spike.x - camera, spike.y - 20)
        )

    # Coins
    for coin in coins:
        screen.blit(
            coin_img,
            (coin.x - camera, coin.y)
        )

    # Flag
    screen.blit(
        flag_img,
        (flag.x - camera, flag.y)
    )

    # Player
    screen.blit(
        player_img,
        (player.x - camera, player.y)
    )

    # Score
    score_text = font.render(
        f"Coins: {score}",
        True, (255, 255, 255)
    )
    screen.blit(score_text, (20, 20))

    # Level complete
    if complete:
        title = big_font.render(
            "LEVEL COMPLETE!",
            True, (255, 255, 255)
        )

        hint = font.render(
            "Press ENTER for Level 2",
            True, (255, 255, 255)
        )

        screen.blit(
            title,
            title.get_rect(center=(WIDTH // 2, 250))
        )

        screen.blit(
            hint,
            hint.get_rect(center=(WIDTH // 2, 320))
        )

    pygame.display.flip()

pygame.quit()
sys.exit()