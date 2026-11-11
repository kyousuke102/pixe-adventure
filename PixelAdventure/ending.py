import pygame
import os
import sys
import subprocess
import random
import math

pygame.init()

WIDTH, HEIGHT = 900, 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Adventure - Ending")
clock = pygame.time.Clock()

folder = os.path.dirname(os.path.abspath(__file__))
assets = os.path.join(folder, "assets")

# Images
background = pygame.image.load(
    os.path.join(assets, "background.png")
).convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

coin_img = pygame.image.load(
    os.path.join(assets, "coin.png")
).convert_alpha()
coin_img = pygame.transform.scale(coin_img, (30, 30))

# Fonts
title_font = pygame.font.Font(None, 85)
big_font = pygame.font.Font(None, 55)
font = pygame.font.Font(None, 36)

WHITE = (255, 255, 255)
GOLD = (255, 220, 70)
BLUE = (60, 130, 220)
GREEN = (50, 170, 100)

# Read final score
try:
    score = int(sys.argv[1])
except (IndexError, ValueError):
    score = 0

# Falling coins
coins = []

for i in range(35):
    coins.append({
        "x": random.randint(0, WIDTH - 30),
        "y": random.randint(-600, 0),
        "speed": random.uniform(2, 5)
    })

# Buttons
play_button = pygame.Rect(170, 440, 250, 70)
menu_button = pygame.Rect(480, 440, 250, 70)

def start_file(filename):
    path = os.path.join(folder, filename)

    if os.path.exists(path):
        subprocess.Popen(
            [sys.executable, path],
            cwd=folder
        )
        return True

    print("Cannot find:", filename)
    return False

running = True
time = 0

while running:
    clock.tick(60)
    time += 1

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:

                if play_button.collidepoint(event.pos):
                    if start_file("level1.py"):
                        running = False

                elif menu_button.collidepoint(event.pos):
                    if start_file("main.py"):
                        running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if start_file("main.py"):
                    running = False

    # Background
    screen.blit(background, (0, 0))

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(140)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    # Falling coins
    for coin in coins:
        coin["y"] += coin["speed"]

        if coin["y"] > HEIGHT:
            coin["y"] = -30
            coin["x"] = random.randint(0, WIDTH - 30)

        screen.blit(
            coin_img,
            (coin["x"], coin["y"])
        )

    # Flashing title
    brightness = int(210 + 45 * math.sin(time * 0.06))
    title_color = (255, brightness, 70)

    title = title_font.render(
        "CONGRATULATIONS!",
        True,
        title_color
    )

    screen.blit(
        title,
        title.get_rect(center=(WIDTH // 2, 150))
    )

    # Win message
    message = big_font.render(
        "YOU COMPLETED PIXEL ADVENTURE!",
        True,
        WHITE
    )

    screen.blit(
        message,
        message.get_rect(center=(WIDTH // 2, 260))
    )

    # Score
    score_text = font.render(
        f"Final Coins: {score}",
        True,
        GOLD
    )

    screen.blit(
        score_text,
        score_text.get_rect(center=(WIDTH // 2, 340))
    )

    # Buttons
    pygame.draw.rect(
        screen, GREEN, play_button, border_radius=15
    )
    pygame.draw.rect(
        screen, BLUE, menu_button, border_radius=15
    )

    play_text = font.render("PLAY AGAIN", True, WHITE)
    menu_text = font.render("MAIN MENU", True, WHITE)

    screen.blit(
        play_text,
        play_text.get_rect(center=play_button.center)
    )

    screen.blit(
        menu_text,
        menu_text.get_rect(center=menu_button.center)
    )

    pygame.display.flip()

pygame.quit()
sys.exit()