import os
import pygame
import requests
import sys
import math

my_step = 0.001

STOCK_OBJECT = 'Москва, инициативная улица, 1'


geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "geocode": STOCK_OBJECT,
    "format": "json"}

response = requests.get(geocoder_api_server, params=geocoder_params)

if not response:
    # обработка ошибочной ситуации
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

coordinates = ','.join([str(toponym_longitude), str(toponym_lattitude)])


class MapParams(object):
    def __init__(self, coordinates):
        self.lat = coordinates[0]
        self.lon = coordinates[1]
        self.zoom = 16
        self.type = 0
        self.types = ['map', 'sat', 'sat,skl']

    def ll(self):
        return str(self.lon) + "," + str(self.lat)

    def update(self, event):
        if event.key == pygame.K_COMMA and self.zoom < 19:  # Page_UP
            self.zoom += 1
        elif event.key == pygame.K_PERIOD and self.zoom > 2:  # Page_DOWN
            self.zoom -= 1

        elif event.key == pygame.K_LEFT:  # LEFT_ARROW
            self.lon -= my_step * math.pow(2, 15 - self.zoom)
        elif event.key == pygame.K_RIGHT:  # RIGHT_ARROW
            self.lon += my_step * math.pow(2, 15 - self.zoom)
        elif event.key == pygame.K_UP and self.lat < 85:  # UP_ARROW
            self.lat += my_step * math.pow(2, 15 - self.zoom)
        elif event.key == pygame.K_DOWN and self.lat > -85:  # DOWN_ARROW
            self.lat -= my_step * math.pow(2, 15 - self.zoom)


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


def main():
    # Инициализируем pygame
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    mp = MapParams((toponym_lattitude, toponym_longitude))
    map_file = None

    free, pause = 0, 1

    state = free

    process = True

    while process:
        if state == free:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # Выход из программы
                    process = False
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_s:
                        mp.type += 1
                        if mp.type > 2:
                            mp.type -= 3
                    mp.update(event)
            map_file = load_map(mp)
            screen.blit(pygame.image.load(map_file), (0, 0))

        elif state == pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # Выход из программы
                    process = False

        pygame.display.flip()
    pygame.quit()
    os.remove(map_file)


if __name__ == "__main__":
    main()
