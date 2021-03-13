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


def update(screen, mp, search, inter=False):
    map_file = load_map(mp)
    screen.fill('black')
    screen.blit(pygame.image.load(map_file), (0, 0))
    back = screen.subsurface(screen.get_rect())
    screenshot = Surface(size)
    screenshot.blit(back, (0, 0))
    if inter:
        interface(screen, mp.types[mp.type], screenshot, search)
    return map_file


def search_line(screen, text, search):
    if len(text) < 1 and not search:
        text = 'Поиск мест и адресов'
    write(screen, text, 46, 22, (191, 191, 191), 21)


def interface(screen, mode, screenshot, search):
    color_rect = 'white'
    color_text = 'white'
    if mode == 'map':
        text = 'схема'
        w_t = 63
        color_rect = (43, 43, 43)
        color_text = (43, 43, 43)
        darkness = 12
        ex = 9
    elif mode == 'sat':
        text = 'спутник'
        w_t = 63
        color_rect = (43, 43, 43)
        color_text = 'white'
        darkness = -1
        ex = 0
    else:
        text = 'гибрид'
        w_t = 63
        color_rect = (43, 43, 43)
        color_text = 'white'
        darkness = -1
        ex = 2

    # menu_bar
    blur_surf = Surface((WIN_WIDTH, 68), pygame.SRCALPHA)
    blur_surf.blit(screenshot, (0, 0))
    d = Surface((WIN_WIDTH, 44), pygame.SRCALPHA)
    if darkness < 0:
        d.fill((255, 255, 255, 50))
    else:
        d.fill((0, 0, 0, darkness))
    blur_surf.blit(d, (0, 0))
    menu_bar = blurSurf(blur_surf, 44)
    screen.blit(menu_bar, (0, 0))

    #  white bar
    create_button(screen, (WIN_WIDTH - 10, 34), 'white', (5, 5))

    # menu icon
    y = 16
    b = 2
    for i in range(3):
        pygame.draw.line(screen, color_rect, [14, y], [30, y], b)
        y += 5

    # mode text
    write(screen, text, WIN_WIDTH - 12 - w_t + ex, 22, color_rect, 24)

    write(screen, 'Яндекс.Карты', WIN_WIDTH // 2 - 45, 54, color_text, 18)

    # search line
    if search:
        search_line_width = WIN_WIDTH - 59 - w_t - 52
        create_button(screen, (search_line_width, 24), (240, 240, 240), (40, 10))

        #  to find button
        create_button(screen, (46, 24), (94, 148, 255), (search_line_width + 46, 10))
        write(screen, 'Найти', search_line_width + 50, 22, 'white', 20)

        # cancel
        create_button(screen, (14, 14), (191, 191, 191), (search_line_width + 20, 15))

        pygame.draw.line(screen, 'white', [search_line_width + 24, 15 + 4], [search_line_width + 24 + 5, 15 + 9], 2)

        pygame.draw.line(screen, 'white', [search_line_width + 24, 15 + 9], [search_line_width + 24 + 5, 15 + 4], 2)
    else:
        search_line_width = WIN_WIDTH - 59 - w_t
        create_button(screen, (search_line_width, 24), (240, 240, 240), (40, 10))


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

    button_color = (240, 240, 240)

    create_button(screen, (28, 22), button_color,
                  ((WIN_WIDTH // 2) + (w // 2) - 90, ((WIN_HEIGHT // 2) + (h // 2) - 30)))
    create_button(screen, (48, 22), button_color, ((WIN_WIDTH // 2) + (w // 2) - 55,
                                                      ((WIN_HEIGHT // 2) + (h // 2) - 30)))

    write(screen, 'Нет',
          (WIN_WIDTH // 2) + (w // 2) - 87, ((WIN_HEIGHT // 2) + (h // 2) - 20), (77, 77, 77), 19)
    write(screen, 'Выйти',
          (WIN_WIDTH // 2) + (w // 2) - 52, ((WIN_HEIGHT // 2) + (h // 2) - 20), (77, 77, 77), 19)

