
import pygame
import os
import sys
import subprocess

pygame.init()

# Window
WIDTH, HEIGHT = 900, 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Adventure - Level Select")
clock = pygame.time.Clock()

# Files
folder = os.path.dirname(os.path.abspath(__file__))
assets = os.path.join(folder, "assets")

# Background
background = pygame.image.load(
    os.path.join(assets, "background.png")
).convert()

background = pygame.transform.scale(
    background, (WIDTH, HEIGHT)
)

# Fonts
title_font = pygame.font.Font(None, 85)
button_font = pygame.font.Font(None, 40)
small_font = pygame.font.Font(None, 30)

# Colors
WHITE = (255, 255, 255)
YELLOW = (255, 220, 60)
DARK = (35, 45, 70)
BLUE = (60, 120, 210)
HOVER = (85, 155, 245)

# Buttons
buttons = [
    {
        "name": "LEVEL 1",
        "file": "level1.py",
        "rect": pygame.Rect(110, 300, 200, 100)
    },
    {
        "name": "LEVEL 2",
        "file": "level2.py",
        "rect": pygame.Rect(350, 300, 200, 100)
    },
    {
        "name": "LEVEL 3",
        "file": "level3.py",
        "rect": pygame.Rect(590, 300, 200, 100)
    }
]

def start_level(filename):
    path = os.path.join(folder, filename)

    if not os.path.exists(path):
        print("ERROR: Cannot find", filename)
        return False

    subprocess.Popen(
        [sys.executable, path],
        cwd=folder
    )
    return True

running = True

while running:
    clock.tick(60)

    mouse_pos = pygame.mouse.get_pos()

    # Events
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:

                for button in buttons:
                    if button["rect"].collidepoint(event.pos):

                        if start_level(button["file"]):
                            running = False

                        break

        if event.type == pygame.KEYDOWN:

            # Keyboard shortcuts
            if event.key == pygame.K_1:
                if start_level("level1.py"):
                    running = False

            elif event.key == pygame.K_2:
                if start_level("level2.py"):
                    running = False

            elif event.key == pygame.K_3:
                if start_level("level3.py"):
                    running = False

    # Background
    screen.blit(background, (0, 0))

    # Dark overlay for readability
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(110)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    # Title
    title = title_font.render(
        "PIXEL ADVENTURE",
        True,
        YELLOW
    )

    screen.blit(
        title,
        title.get_rect(center=(WIDTH // 2, 150))
    )

    # Subtitle
    subtitle = button_font.render(
        "SELECT YOUR LEVEL",
        True,
        WHITE
    )

    screen.blit(
        subtitle,
        subtitle.get_rect(center=(WIDTH // 2, 225))
    )

    # Draw buttons
    for button in buttons:

        rect = button["rect"]
        hovered = rect.collidepoint(mouse_pos)

        color = HOVER if hovered else BLUE

        # Button shadow
        shadow = rect.move(0, 6)

        pygame.draw.rect(
            screen,
            DARK,
            shadow,
            border_radius=15
        )

        # Button background
        pygame.draw.rect(
            screen,
            color,
            rect,
            border_radius=15
        )

        # Button border
        pygame.draw.rect(
            screen,
            WHITE,
            rect,
            width=3,
            border_radius=15
        )

        # Button text
        text = button_font.render(
            button["name"],
            True,
            WHITE
        )

        screen.blit(
            text,
            text.get_rect(center=rect.center)
        )

    # Instructions
    hint = small_font.render(
        "Click a level or press 1 / 2 / 3",
        True,
        WHITE
    )

    screen.blit(
        hint,
        hint.get_rect(center=(WIDTH // 2, 480))
    )

    pygame.display.flip()

pygame.uit()
sys.exit()

