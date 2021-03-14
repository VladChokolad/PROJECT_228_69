import os
import pygame
import requests
import sys
import math
from pygame import Surface
import resourses
import ctypes

size = (600, 450)

step = 0.001

cur_req = ''
# негроиды
vocab = {113: 'й', 119: 'ц', 101: 'у', 114: 'к', 116: 'е', 121: 'н', 117: 'г',
         105: 'ш', 111: 'щ', 112: 'з', 1093: 'х', 1098: 'ъ', 1105: 'ё', 97: 'ф',
         115: 'ы', 100: 'в', 102: 'а', 103: 'п', 104: 'р', 106: 'о', 107: 'л',
         108: 'д', 1078: 'ж', 1101: 'э', 122: 'я', 120: 'ч', 99: 'с', 118: 'м',
         98: 'и', 110: 'т', 109: 'ь', 1073: 'б', 1102: 'ю',
         49: '1', 50: '2', 51: '3', 52: '4', 53: '5', 54: '6', 55: '7',
         56: '8', 57: '9', 48: '0', 45: '-', 1073741908: '/', 32: ' '
         }

STOCK_OBJECT = 'Москва, инициативная улица, 1'


def req_search(req):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": req,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        pass

    # Преобразуем ответ в json-объект
    json_response = response.json()
    # Получаем первый топоним из ответа геокодера.
    toponym = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и широта:
    toponym_longitude, toponym_lattitude = map(float, toponym_coodrinates.split(" "))

    envelope = toponym['boundedBy']['Envelope']

    left, bottom = map(float, envelope['lowerCorner'].split())
    right, top = map(float, envelope['upperCorner'].split())

    width = float(abs(right - left))
    height = float(abs(top - bottom))

    if width > height:
        pam = width
    else:
        print(1)
        pam = height

    zoom = round((pam * 10) ** 1.2)
    zoom = 19 - zoom
    if zoom < 2:
        zoom = 2
    elif zoom > 17:
        zoom = 17

    print('pam:', pam)
    print('pam*10:', pam * 10)
    print('pam*10 ** 1.5:', (pam * 10) ** 1.1)
    print('zoom:', zoom)
    print()

    coordinates = ','.join([str(toponym_longitude), str(toponym_lattitude)])
    return toponym_longitude, toponym_lattitude, zoom


toponym_longitude, toponym_lattitude, zoom = req_search(STOCK_OBJECT)


def get_layout():
    u = ctypes.windll.LoadLibrary("user32.dll")
    pf = getattr(u, "GetKeyboardLayout")
    if hex(pf(0)) == '0x4190419':
        return 'ru'
    if hex(pf(0)) == '0x4090409':
        return 'en'


class MapParams(object):
    def __init__(self, coordinates, zoom):
        self.lat = coordinates[0]
        self.lon = coordinates[1]
        self.zoom = zoom
        self.type = 0
        self.types = ['map', 'sat', 'sat,skl']

    def ll(self):
        return str(self.lon) + "," + str(self.lat)

    def update(self, event, search):
        global cur_req
        if event.key == 1073741921 and self.zoom < 19:  # Page_UP
            self.zoom += 1
        elif event.key == 1073741915 and self.zoom > 2:  # Page_DOWN
            self.zoom -= 1

        elif event.key == pygame.K_LEFT:  # LEFT_ARROW
            self.lon -= step * math.pow(2, 15 - self.zoom)
        elif event.key == pygame.K_RIGHT:  # RIGHT_ARROW
            self.lon += step * math.pow(2, 15 - self.zoom)
        elif event.key == pygame.K_UP and self.lat < 85:  # UP_ARROW
            self.lat += step * math.pow(2, 15 - self.zoom)
        elif event.key == pygame.K_DOWN and self.lat > -85:  # DOWN_ARROW
            self.lat -= step * math.pow(2, 15 - self.zoom)
        elif event.key in vocab and len(cur_req) < 30 and search:
            cur_req += vocab[event.key]


def main():
    global cur_req
    # Инициализируем pygame
    pygame.init()
    screen = pygame.display.set_mode(size, pygame.SRCALPHA)
    mp = MapParams((toponym_lattitude, toponym_longitude), zoom)
    map_file = None
    screenshot = None

    pygame.display.set_caption("Static Yandex.Map")

    free, pause = 0, 1

    state = free

    process = True

    clock = pygame.time.Clock()

    search = False

    map_file = resourses.update(screen, mp, search)

    while process:
        if state == free:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # Выход из программы
                    process = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s and not search:
                        mp.type += 1
                        if mp.type > 2:
                            mp.type -= 3
                    elif event.key == pygame.K_ESCAPE:
                        screen.fill('black')
                        map_file = resourses.update(screen, mp, search)
                        back = screen.subsurface(screen.get_rect())
                        screenshot = Surface(size)
                        screenshot.blit(back, (0, 0))
                        state = pause
                    elif event.key == pygame.K_BACKSPACE and search:
                        if len(cur_req) > 1:
                            cur_req = cur_req[:-1]
                        else:
                            search = False
                            cur_req = ''
                    elif event.key == 13 and search:
                        mp.lon, mp.lat, mp.zoom = req_search(cur_req)
                    mp.update(event, search)
                    # print(event.key)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if 10 < event.pos[1] < 34:
                        if 10 < event.pos[0] < 35:
                            screen.fill('black')
                            map_file = resourses.update(screen, mp, search)
                            back = screen.subsurface(screen.get_rect())
                            screenshot = Surface(size)
                            screenshot.blit(back, (0, 0))
                            state = pause
                        elif 525 < event.pos[0] < 588:
                            mp.type += 1
                            if mp.type > 2:
                                mp.type -= 3
                        elif 445 < event.pos[0] < 460 and search:
                            search = False
                            cur_req = ''
                        elif 40 < event.pos[0] < 516 and not search:
                            search = True
                    # print(event.pos)
            resourses.update(screen, mp, search, True)
            resourses.search_line(screen, cur_req, search)

        elif state == pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # Выход из программы
                    process = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if 235 < event.pos[1] < 258:
                        if 385 < event.pos[0] < 412:
                            state = free
                        elif 420 < event.pos[0] < 468:
                            process = False
                    print(event.pos)
            screen.fill('black')
            resourses.pause(screen, screenshot)

        clock.tick(20)
        pygame.display.flip()
    pygame.quit()
    os.remove(map_file)


if __name__ == "__main__":
    main()
