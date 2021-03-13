import pygame
from pygame import Surface
import requests
import sys

WIN_WIDTH = 600
WIN_HEIGHT = 450
size = (WIN_WIDTH, WIN_HEIGHT)


def load_map(mp):
    map_request = f"http://static-maps.yandex.ru/1.x/?ll={mp.ll()}&z={mp.zoom}&l={mp.types[mp.type]}"
    response = requests.get(map_request)
    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)

    map_file = "map.png"
    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)
    return map_file


def write(screen, text, pos_x, pos_y, color, size):
    font = pygame.font.Font(None, size)
    text = font.render(text, True, color)
    text_y = pos_y - text.get_height() // 2
    screen.blit(text, (pos_x, text_y))
    return


def create_button(screen, size, color, pos, border=None):
    new_button = pygame.Rect(pos[0], pos[1], size[0], size[1])
    if border:
        pygame.draw.rect(screen, color, new_button, border)
    else:
        pygame.draw.rect(screen, color, new_button)


def blurSurf(surface, amt):
    """
    Blur the given surface by the given 'amount'.  Only values 1 and greater
    are valid.  Value 1 = no blur.
    """
    if amt < 1.0:
        raise ValueError("Arg 'amt' must be greater than 1.0, passed in value is %s"%amt)
    scale = 1.0/float(amt)
    surf_size = surface.get_size()
    scale_size = (int(surf_size[0]*scale), int(surf_size[1]*scale))
    surf = pygame.transform.smoothscale(surface, scale_size)
    surf = pygame.transform.smoothscale(surf, surf_size)
    return surf


def update(screen, mp, inter=False):
    map_file = load_map(mp)
    screen.fill('black')
    screen.blit(pygame.image.load(map_file), (0, 0))
    back = screen.subsurface(screen.get_rect())
    screenshot = Surface(size)
    screenshot.blit(back, (0, 0))
    if inter:
        interface(screen, mp.types[mp.type], screenshot)
    return map_file


def interface(screen, mode, screenshot):
    # create_button(screen, (50, 25), (191, 191, 191), (10, 10), 2)
    color_rect = 'white'
    color_text = 'white'
    if mode == 'map':
        text = 'карта'
        w_t = 56
        color_rect = (43, 43, 43)
        color_text = 'white'
    elif mode == 'sat':
        text = 'спутник'
        w_t = 76
        color_rect = 'white'
        color_text = 'black'
    else:
        text = 'гибрид'
        w_t = 72
        color_rect = 'white'
        color_text = 'black'

    # menu_bar
    blur_surf = Surface((WIN_WIDTH, 45), pygame.SRCALPHA)
    blur_surf.blit(screenshot, (0, 0))
    menu_bar = blurSurf(blur_surf, 44)
    screen.blit(menu_bar, (0, 0))

    create_button(screen, (25, 25), color_rect, (10, 10))

    y = 16
    b = 2
    for i in range(3):
        pygame.draw.line(screen, color_text, [14, y], [30, y], b)
        y += 5
    # write(screen, '<', 15, 21, color_text, 38)
    # pygame.draw.lines(screen, color_text, False, [[27, 15], [16, 22], [27, 29]], 2)
    create_button(screen, (w_t, 25), color_rect, (40, 10))
    write(screen, text, 45, 22, color_text, 25)


def pause(screen, screenshot):
    blur_surf = Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
    blur_surf.blit(screenshot, (0, 0))
    new_serf = blurSurf(blur_surf, 44)
    screen.blit(new_serf, (0, 0))

    w, h = 350, 80

    pygame.draw.rect(screen, pygame.Color('white'), ((WIN_WIDTH // 2) - (w // 2),
                                                     (WIN_HEIGHT // 2) - (h // 2), w, h))

    write(screen, 'Вы уверены, что хотите выйти?', (WIN_WIDTH // 2) - (300 // 2) - 5,
          (WIN_HEIGHT // 2) - 13, (77, 77, 77), 30)

    create_button(screen, (28, 22), (230, 230, 230),
                  ((WIN_WIDTH // 2) + (w // 2) - 90, ((WIN_HEIGHT // 2) + (h // 2) - 30)))
    create_button(screen, (48, 22), (230, 230, 230), ((WIN_WIDTH // 2) + (w // 2) - 55,
                                                      ((WIN_HEIGHT // 2) + (h // 2) - 30)))

    write(screen, 'Нет',
          (WIN_WIDTH // 2) + (w // 2) - 87, ((WIN_HEIGHT // 2) + (h // 2) - 20), (77, 77, 77), 19)
    write(screen, 'Выйти',
          (WIN_WIDTH // 2) + (w // 2) - 52, ((WIN_HEIGHT // 2) + (h // 2) - 20), (77, 77, 77), 19)

