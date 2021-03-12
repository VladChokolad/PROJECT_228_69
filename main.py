import os
import pygame
import requests
import sys
import math

my_step = 0.001


# Создайте оконное приложение, отображающее карту по координатам и в масштабе, который задаётся программно.

class MapParams(object):
    def __init__(self):
        self.lat = 61.665279  # Координаты центра карты на старте. Задал координаты университета
        self.lon = 50.813492
        self.zoom = 16  # Масштаб карты на старте. Изменяется от 1 до 19
        self.type = "map"  # Другие значения "sat", "sat,skl"

    # Преобразование координат в параметр ll, требуется без пробелов, через запятую и без скобок
    def ll(self):
        return str(self.lon) + "," + str(self.lat)

    def update(self, event):
        if event.key == pygame.K_PAGEUP and self.zoom < 19:  # Page_UP
            self.zoom += 1
        elif event.key == pygame.K_PAGEDOWN and self.zoom > 2:  # Page_DOWN
            self.zoom -= 1

        elif event.key == pygame.K_LEFT:  # LEFT_ARROW
            self.lon -= my_step * math.pow(2, 15 - self.zoom)
        elif event.key == pygame.K_RIGHT:  # RIGHT_ARROW
            self.lon += my_step * math.pow(2, 15 - self.zoom)
        elif event.key == pygame.K_UP and self.lat < 85:  # UP_ARROW
            self.lat += my_step * math.pow(2, 15 - self.zoom)
        elif event.key == pygame.K_DOWN and self.lat > -85:  # DOWN_ARROW
            self.lat -= my_step * math.pow(2, 15 - self.zoom)

        # Создание карты с соответствующими параметрами.


def load_map(mp):
    map_request = "http://static-maps.yandex.ru/1.x/?ll={ll}&z={z}&l={type}".format(ll=mp.ll(), z=mp.zoom, type=mp.type)
    response = requests.get(map_request)
    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)

    # Запись полученного изображения в файл.
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
    mp = MapParams()

    process = True

    while process:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Выход из программы
                process = False
            elif event.type == pygame.KEYUP:  # Обрабатываем различные нажатые клавиши.
                mp.update(event)

        # Создаем файл
        map_file = load_map(mp)
        # Рисуем картинку, загружаемую из только что созданного файла.
        screen.blit(pygame.image.load(map_file), (0, 0))
        pygame.display.flip()
    pygame.quit()
    # Удаляем файл с изображением.
    os.remove(map_file)


if __name__ == "__main__":
    main()
