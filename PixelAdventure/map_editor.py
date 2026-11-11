
import pygame
import json
import os

pygame.init()

# Window and map settings
WIDTH = 900
HEIGHT = 600
GROUND_Y = 530

LEVEL_WIDTHS = {
    1: 6000,
    2: 8000,
    3: 8000
}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Adventure - Map Editor")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)
small_font = pygame.font.Font(None, 23)

folder = os.path.dirname(os.path.abspath(__file__))
assets = os.path.join(folder, "assets")

# Object sizes
SIZES = {
    "platform": (180, 70),
    "coin": (30, 30),
    "enemy": (45, 40),
    "flag": (120, 180),
    "spike": (105, 70)
}

# Load images
def load_image(name, size):
    path = os.path.join(assets, name + ".png")

    if os.path.exists(path):
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, size)

    # Simple placeholder if an image is missing
    image = pygame.Surface(size, pygame.SRCALPHA)
    colors = {
        "platform": (130, 85, 45),
        "coin": (255, 220, 0),
        "enemy": (220, 60, 60),
        "flag": (50, 220, 100),
        "spike": (180, 180, 180)
    }
    image.fill(colors.get(name, (255, 255, 255)))
    return image


images = {
    name: load_image(name, size)
    for name, size in SIZES.items()
}

background_path = os.path.join(assets, "background.png")

if os.path.exists(background_path):
    background = pygame.image.load(background_path).convert()
    background = pygame.transform.scale(
        background, (WIDTH, HEIGHT)
    )
else:
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill((100, 180, 255))


# Editor variables
level = None
world_width = 8000
camera = 0
objects = []
selected = "platform"
message = "Choose a level"

KEY_TYPES = {
    pygame.K_1: "platform",
    pygame.K_2: "coin",
    pygame.K_3: "enemy",
    pygame.K_4: "flag",
    pygame.K_5: "spike"
}


# Open a level
def open_level(number):
    global level, world_width, camera, objects, message

    level = number
    world_width = LEVEL_WIDTHS[number]
    camera = 0

    filename = f"level{number}_map.json"
    path = os.path.join(folder, filename)

    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, list):
                objects = data
            elif isinstance(data, dict):
                objects = data.get("objects", [])
            else:
                objects = []

            message = f"Loaded {len(objects)} objects"

        except (OSError, ValueError):
            objects = []
            message = "Could not load map"
    else:
        objects = []
        message = "New empty map"


# Save a level
def save_level():
    global message

    if level is None:
        return

    filename = f"level{level}_map.json"
    path = os.path.join(folder, filename)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(objects, file, indent=4)

    message = f"Saved {filename}"


# Draw text
def draw_text(text, x, y, color=(255, 255, 255)):
    image = small_font.render(text, True, color)
    screen.blit(image, (x, y))


running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            # Level selection
            if level is None:
                if event.key == pygame.K_1:
                    open_level(1)

                elif event.key == pygame.K_2:
                    open_level(2)

                elif event.key == pygame.K_3:
                    open_level(3)

            else:
                if event.key == pygame.K_ESCAPE:
                    level = None
                    message = "Choose a level"

                elif event.key in KEY_TYPES:
                    selected = KEY_TYPES[event.key]
                    message = f"Selected {selected}"

                elif event.key == pygame.K_s:
                    save_level()

                elif event.key in (
                    pygame.K_BACKSPACE,
                    pygame.K_DELETE
                ):
                    if objects:
                        objects.pop()
                        message = "Removed last object"

        # Mouse controls
        elif event.type == pygame.MOUSEBUTTONDOWN:

            if level is None:
                continue

            mx, my = event.pos

            if my < 85:
                continue

            world_x = mx + camera

            # Left click: add
            if event.button == 1:

                if selected == "flag":
                    objects = [
                        obj for obj in objects
                        if obj.get("type") != "flag"
                    ]

                objects.append({
                    "type": selected,
                    "x": int(world_x),
                    "y": int(my)
                })

                message = f"Added {selected}"

            # Right click: remove
            elif event.button == 3:

                for i in range(len(objects) - 1, -1, -1):

                    obj = objects[i]
                    obj_type = obj.get("type")

                    if obj_type not in SIZES:
                        continue

                    w, h = SIZES[obj_type]

                    rect = pygame.Rect(
                        obj["x"],
                        obj["y"],
                        w,
                        h
                    )

                    if rect.collidepoint(world_x, my):
                        objects.pop(i)
                        message = "Object deleted"
                        break

    # Camera movement
    if level is not None:

        keys = pygame.key.get_pressed()

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            camera += 15

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            camera -= 15

        max_camera = world_width - WIDTH
        camera = max(0, min(camera, max_camera))

    # Background
    screen.blit(background, (0, 0))

    if level is None:

        title = font.render(
            "PIXEL ADVENTURE - MAP EDITOR",
            True,
            (255, 255, 255)
        )

        screen.blit(title, (245, 160))

        draw_text("Press 1 - Edit Level 1", 330, 250)
        draw_text("Press 2 - Edit Level 2", 330, 300)
        draw_text("Press 3 - Edit Level 3", 330, 350)

    else:

        # Ground
        pygame.draw.rect(
            screen,
            (100, 70, 40),
            (-camera, GROUND_Y, world_width, 70)
        )

        pygame.draw.rect(
            screen,
            (70, 170, 70),
            (-camera, GROUND_Y, world_width, 10)
        )

        # Draw map objects
        for obj in objects:

            obj_type = obj.get("type")

            if obj_type in images:

                x = obj["x"] - camera
                y = obj["y"]

                w, h = SIZES[obj_type]

                if -w < x < WIDTH:
                    screen.blit(images[obj_type], (x, y))

        # Preview object at mouse
        mx, my = pygame.mouse.get_pos()

        if my >= 85:

            preview = images[selected].copy()
            preview.set_alpha(130)

            screen.blit(preview, (mx, my))

        # Toolbar
        pygame.draw.rect(
            screen,
            (25, 35, 50),
            (0, 0, WIDTH, 85)
        )

        draw_text(
            f"LEVEL {level} | MAP WIDTH: {world_width}",
            12, 7,
            (255, 230, 80)
        )

        draw_text(
            "1 Platform | 2 Coin | 3 Enemy | 4 Flag | 5 Spike",
            12, 29
        )

        draw_text(
            "A/D Move | Left Add | Right Delete | S Save | ESC Back",
            12, 51
        )

        draw_text(
            f"Camera: {camera}/{world_width - WIDTH}"
            f" | Selected: {selected}",
            520, 7,
            (100, 255, 150)
        )

        # Status message
        draw_text(
            message,
            12,
            HEIGHT - 28,
            (255, 255, 100)
        )

    pygame.display.flip()

pygame.quit()
