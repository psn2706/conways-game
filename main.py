import pygame
import math
import os
import sys
import ast
from win32api import GetSystemMetrics
from time import time
from pathlib import Path
from keyboard import KeyboardKey, update_key, get_keyboard_key
from rect import fill, Button, Text, blit_button, blit_text


def resource_path(relative):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative)
    else:
        return os.path.join(os.path.abspath("."), relative)


def main():
    pygame.init()
    screen = pygame.display.set_mode((GetSystemMetrics(0), GetSystemMetrics(1)), pygame.FULLSCREEN)

    def get_img(s, k=None, size=None, color=None):
        img = pygame.image.load(resource_path(s))
        if k is not None:
            img = pygame.transform.scale(
                img, (img.get_width() * k,
                      img.get_height() * k))
        if size is not None:
            img = pygame.transform.scale(img, (size[0], size[1]))
        if color is not None:
            fill(img, color)
        return img

    class CellStorage:
        x, y = 0, 0  # смещение
        x2, y2 = 0, 0
        size = 64
        size2 = 64
        pause = True
        point_mode = True
        erase_mode = False
        frames = [{}]
        frame = 0
        dict_cell = {}
        new_cells = {}
        del_cells = {}
        colors = {
            "red": (230, 0, 0),
            "green": (0, 200, 0),
            "blue": (0, 0, 200),
            "yellow": (255, 255, 0),
            "black": (0, 0, 0),
            "false": (190, 190, 190),
            "pale red": (255, 180, 180),
            "pale green": (152, 251, 152),
            "pale blue": (175, 238, 238),
            "pale yellow": (255, 255, 102),
            "pale black": (181, 184, 177),
            "pale false": (225, 225, 225),
        }
        color_name = "red"
        neigh = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        point = [(0, 0)]
        figure = [(0, 0)]
        figure_index = 0
        figures = [
            [
                (0, 1),
                (1, 0),
                (-1, -1), (0, -1), (1, -1)
            ],
            [(i, j) for i in range(-1, 2) for j in range(-1, 2)],
            []
        ]

        def __str__(self):
            return f'{CellStorage.x} {CellStorage.y} {CellStorage.size}\n' \
                   f'{str(list(CellStorage.keys()))}\n' \
                   f'{str(list(CellStorage.cell_colors()))}\n' \
                   f'{CellStorage.get_figure_i()}\n' \
                   f'{str(list(CellStorage.figures))}\n' \
                   f'{CellStorage.frame}' \
                   f'{str(list(fr.keys() for fr in CellStorage.frames))}'

        def __init__(self):
            super().__init__(self)

        @staticmethod
        def get(f, full):
            x, y, z = map(float, f.readline().split())
            if full:
                CellStorage.x, CellStorage.y, CellStorage.size = x, y, z
            cords = ast.literal_eval(f.readline())
            colors = ast.literal_eval(f.readline())
            CellStorage.clear()
            for i in range(len(cords)):
                Cell(cords[i][0], cords[i][1], colors[i])
            figure_i = int(f.readline())
            figures = ast.literal_eval(f.readline())
            if full:
                CellStorage.figure_index = figure_i
                CellStorage.figures = figures
            CellStorage.frame = int(f.readline())
            CellStorage.clear()

        @staticmethod
        def rotate(figure=None):
            if figure is None:
                x = CellStorage.figures[CellStorage.figure_index]
                x = [(j, -i) for i, j in x]
                CellStorage.figures[CellStorage.figure_index] = x
                CellStorage.figure = x
            else:
                return [(j, -i) for i, j in figure]

        @staticmethod
        def left_frame():
            if CellStorage.frame >= 1:
                CellStorage.frame -= 1
                CellStorage.dict_cell = CellStorage.frames[CellStorage.frame]

        @staticmethod
        def right_frame():
            if CellStorage.frame == len(CellStorage.frames) - 1:
                CellStorage.new_stage()
            else:
                CellStorage.frame += 1
                CellStorage.dict_cell = CellStorage.frames[CellStorage.frame]

        @staticmethod
        def s_draw(i, j, color, s2=False):
            if not s2:
                x, y = CellStorage.x + i * CellStorage.size, CellStorage.y - j * CellStorage.size
                a, b = screen.get_size()
                if -CellStorage.size <= x <= a and -CellStorage.size <= y <= b:
                    pygame.draw.rect(screen, color,
                                     (x, y, CellStorage.size, CellStorage.size))
            else:
                x, y = CellStorage.x2 + i * CellStorage.size2, CellStorage.y2 - j * CellStorage.size2
                a, b = screen.get_size()
                if -CellStorage.size2 <= x <= a and -CellStorage.size2 <= y <= b:
                    pygame.draw.rect(screen, color,
                                     (x, y, CellStorage.size2, CellStorage.size2))

        @staticmethod
        def draw_pale(i, j):
            if "pale " + CellStorage.color_name in CellStorage.colors:
                for x, y in CellStorage.figure:
                    CellStorage.s_draw(x + i, y + j, CellStorage.colors["pale " + CellStorage.color_name])
            else:
                for x, y in CellStorage.figure:
                    CellStorage.s_draw(x + i, y + j, CellStorage.color_name)

        @staticmethod
        def set_color(color):
            if isinstance(color, str):
                CellStorage.color_name = color

        @staticmethod
        def set_figure_i(i):
            CellStorage.figure_index = i

        @staticmethod
        def get_figure_i():
            return CellStorage.figure_index

        @staticmethod
        def count_neigh(i, j):
            cnt = 0
            for p in CellStorage.neigh:
                cnt += (i + p[0], j + p[1]) in CellStorage.dict_cell
            return cnt

        @staticmethod
        def medium_neigh_color(i, j):
            lst = []
            for p in CellStorage.neigh:
                if (i + p[0], j + p[1]) in CellStorage.dict_cell:
                    lst.append(CellStorage.dict_cell[(i + p[0], j + p[1])])
            r, g, b = 0, 0, 0
            for cell in lst:
                r += cell.color[0] ** 2
                g += cell.color[1] ** 2
                b += cell.color[2] ** 2
            r, g, b = map(lambda x: math.ceil((x // len(lst)) ** 0.5), [r, g, b])
            return r, g, b

        @staticmethod
        def new_stage():
            if CellStorage.frame != len(CellStorage.frames) - 1:
                CellStorage.frame += 1
                CellStorage.dict_cell = CellStorage.frames[CellStorage.frame]
            else:
                CellStorage.frames[CellStorage.frame] = CellStorage.dict_cell.copy()
                for cell in CellStorage.dict_cell.values():
                    cell.update()
                for cell in CellStorage.del_cells:
                    CellStorage.delitem(cell)
                for cell, color in CellStorage.new_cells.items():
                    Cell(cell[0], cell[1], color)
                CellStorage.del_cells, CellStorage.new_cells = {}, {}
                CellStorage.frame += 1
                CellStorage.frames.append(CellStorage.dict_cell.copy())

        @staticmethod
        def mouse_cell_coord(s2=False):
            x, y = pygame.mouse.get_pos()
            i, j = CellStorage.get_ij(x, y, s2)
            return i, j

        @staticmethod
        def resize(k, s2=False):
            if not s2:
                if 1 <= CellStorage.size * k <= 64:
                    x, y = pygame.mouse.get_pos()
                    i, j = CellStorage.mouse_cell_coord()
                    CellStorage.size *= k
                    CellStorage.x = x - i * CellStorage.size
                    CellStorage.y = y + j * CellStorage.size
            else:
                if 1 <= CellStorage.size2 * k <= 64:
                    CellStorage.size2 *= k

        @staticmethod
        def create(i, j):
            for x, y in CellStorage.figure:
                Cell(x + i, y + j)
            CellStorage.frames = CellStorage.frames[:CellStorage.frame + 1]

        @staticmethod
        def create_with_del(i, j):
            for x, y in CellStorage.figure:
                if (x + i, y + j) in CellStorage.dict_cell:
                    CellStorage.delitem(x + i, y + j)
                else:
                    Cell(x + i, y + j)
            CellStorage.frames = CellStorage.frames[:CellStorage.frame + 1]

        @staticmethod
        def del_by_figure(i, j):
            for x, y in CellStorage.figure:
                CellStorage.delitem(x + i, y + j)
            CellStorage.frames = CellStorage.frames[:CellStorage.frame + 1]

        @staticmethod
        def delitem(key, j=None):
            if j is not None:
                key = (key, j)
            if key in CellStorage.dict_cell:
                CellStorage.dict_cell.pop(key)

        @staticmethod
        def get_ij(x, y, s2=False):
            if not s2:
                i = (x - CellStorage.x) // CellStorage.size
                j = (CellStorage.y - y) // CellStorage.size + 1
                return i, j
            else:
                i = (x - CellStorage.x2) // CellStorage.size2
                j = (CellStorage.y2 - y) // CellStorage.size2 + 1
                return i, j

        @staticmethod
        def keys():
            return CellStorage.dict_cell.keys()

        @staticmethod
        def values():
            return CellStorage.dict_cell.values()

        @staticmethod
        def cell_colors():
            return [cell.color for cell in CellStorage.dict_cell.values()]

        @staticmethod
        def clear():
            CellStorage.dict_cell.clear()

        @staticmethod
        def set_point():
            CellStorage.figure = CellStorage.point

        @staticmethod
        def set_figure(i=None, f=None):
            if i is None:
                CellStorage.figure = CellStorage.figures[CellStorage.figure_index]
            elif f is None:
                if isinstance(i, list):
                    CellStorage.figure = i
                if isinstance(i, int):
                    CellStorage.figure = CellStorage.figures[i]
            else:
                CellStorage.figures[i] = f

        @staticmethod
        def set_left_figure():
            CellStorage.figure_index = max(CellStorage.figure_index - 1, 0)
            if not CellStorage.point_mode:
                CellStorage.figure = CellStorage.figures[CellStorage.figure_index]

        @staticmethod
        def set_right_figure(empty_allow=True):
            fi = CellStorage.figure_index
            fs = CellStorage.figures
            if fi == len(fs) - 1 and len(fs[fi]) > 0:
                CellStorage.figures.append([])
            fi = min(fi + 1, len(CellStorage.figures) - 1)
            if not empty_allow and len(CellStorage.figures[fi]) == 0 and fi > 0:
                fi -= 1
            if not CellStorage.point_mode:
                CellStorage.figure = CellStorage.figures[fi]
            CellStorage.figure_index = fi

        @staticmethod
        def get_figure(i=None):
            if i is None:
                return CellStorage.figure
            else:
                return CellStorage.figures[i]

        @staticmethod
        def upd_point(i, j, s2=False):
            if s2:
                if (i, j) in CellStorage.figures[CellStorage.figure_index]:
                    CellStorage.figures[CellStorage.figure_index].remove((i, j))
                else:
                    if not CellStorage.erase_mode:
                        CellStorage.figures[CellStorage.figure_index].append((i, j))

        @staticmethod
        def upd_point_by_motion(s2=False):
            i, j = CellStorage.mouse_cell_coord(s2)
            if (i, j) not in CellStorage.figures[CellStorage.figure_index]:
                if not CellStorage.erase_mode:
                    CellStorage.figures[CellStorage.figure_index].append((i, j))
            if CellStorage.erase_mode:
                if (i, j) in CellStorage.figures[CellStorage.figure_index]:
                    CellStorage.figures[CellStorage.figure_index].remove((i, j))

        @staticmethod
        def upd_figures(new_figures=None):
            if new_figures is None:
                figure = CellStorage.figures[CellStorage.figure_index]
                CellStorage.figures = list(filter(lambda x: len(x) > 0, CellStorage.figures))
                CellStorage.figures.append([])
                CellStorage.figure_index = CellStorage.figures.index(figure)
            else:
                CellStorage.figures = new_figures

        @staticmethod
        def draw_figure(s2=False):
            for i, j in CellStorage.figures[CellStorage.figure_index]:
                CellStorage.s_draw(i, j, CellStorage.colors[CellStorage.color_name], s2)

    class Cell:
        def __init__(self, i=0, j=0, color=None):
            if (i, j) not in CellStorage.dict_cell:
                self.i, self.j = i, j  # нумерация столбцов и строк
                if color is None:
                    self.color = CellStorage.colors[CellStorage.color_name]
                else:
                    self.color = color
                CellStorage.dict_cell[(i, j)] = self

        def draw(self):
            CellStorage.s_draw(self.i, self.j, self.color)

        def update(self):
            i, j = self.i, self.j
            for p in CellStorage.neigh:
                x, y = i + p[0], j + p[1]
                if CellStorage.count_neigh(x, y) == 3:
                    if (x, y) not in CellStorage.new_cells and (x, y) not in CellStorage.dict_cell:
                        CellStorage.new_cells[(x, y)] = CellStorage.medium_neigh_color(x, y)
            cnt = CellStorage.count_neigh(i, j)
            if cnt < 2 or cnt > 3:
                CellStorage.del_cells[(i, j)] = True

    def run():
        class SaveBox(Button):
            def __init__(self, prefix, image, text=''):
                super().__init__(image)
                self.prefix = prefix
                self.text = text
                self.timer = time()
                self.light = False

            def make_file(self):
                f = open(self.prefix + self.text, 'w')
                if self.prefix == '__parameters__':
                    f.write(f'{CellStorage.x} {CellStorage.y} {CellStorage.size}\n')
                    f.write(str(list(CellStorage.keys())) + '\n' + str(CellStorage.cell_colors()) + '\n')
                    CellStorage.upd_figures()
                    f.write(f'{CellStorage.get_figure_i()}\n')
                    f.write(str(list(CellStorage.figures)) + '\n')
                    f.write(f'{dt}\n')
                    f.write(str(list(false_cells.keys())) + '\n')
                    f.write(f'{CellStorage.color_name}\n')
                    f.write(f'{hidden_mode}\n')
                    # f.write(f'{CellStorage.frames()}\n')
                f.close()

            def upd_by_file(self, full=True):
                my_file = Path(self.prefix + self.text)
                if my_file.is_file():
                    f = open(self.prefix + self.text, 'r')
                    try:

                        if self.prefix == '__parameters__':
                            _x, _y, z = map(float, f.readline().split())
                            if full:
                                CellStorage.x, CellStorage.y, CellStorage.size = _x, _y, z
                            cords = ast.literal_eval(f.readline())
                            _colors = ast.literal_eval(f.readline())
                            CellStorage.clear()
                            for _i in range(len(cords)):
                                Cell(cords[_i][0], cords[_i][1], _colors[_i])
                            _x, _y, z = int(f.readline()), ast.literal_eval(f.readline()), float(f.readline())
                            if full:
                                nonlocal dt
                                CellStorage.set_figure_i(_x)
                                CellStorage.upd_figures(_y)
                                dt = z
                            line = f.readline()
                            if full:
                                false_cells.clear()
                                for _cell in ast.literal_eval(line):
                                    false_cells[_cell] = 1
                            color = f.readline().split()[0]
                            if full:
                                CellStorage.set_color(color)
                            line = f.readline()
                            if full:
                                nonlocal hidden_mode
                                hidden_mode = int(line)
                            # CellStorage.read_frames(f.read line())
                    except Exception as exc:
                        print(exc)
                    finally:
                        f.close()

            def launch(self):
                self.timer = time()
                self.make_file()
                self.set_color('red')
                self.light = True

            def dis_light(self):
                if time() - self.timer >= 0.16:
                    self.light = False
                if not self.light:
                    self.set_color('black')

        def screen_quit_1():
            nonlocal left_click_moving_time, right_click_moving
            left_click_moving_time, right_click_moving, CellStorage.erase_mode = 0.0, False, False
            for btn in buttons1:
                btn.hidden = False

        def screen_quit_2():
            CellStorage.upd_figures()
            s2_inv.set_color('black')
            screen_quit_1()

        def screen_quit_3():
            s3_info.set_color('black')
            screen_quit_1()

        def hide_buttons():
            if hidden_mode == 0:
                for btn in buttons1:
                    btn.hidden = False
            elif hidden_mode == 1:
                play_box.hidden = True
            elif hidden_mode == 2:
                for btn in buttons1:
                    btn.hidden = True

        def to_screen(sc):
            nonlocal running_screen
            if running_screen == sc:
                if sc == 2:
                    screen_quit_2()
                elif sc == 3:
                    screen_quit_3()
                running_screen = 1
                return
            elif running_screen == 1:
                screen_quit_1()
            elif running_screen == 2:
                screen_quit_2()
            elif running_screen == 3:
                screen_quit_3()
            running_screen = sc

        pygame.display.set_caption('Convey\'s game of life')
        width, height = GetSystemMetrics(0), GetSystemMetrics(1)
        running = True
        left_click_moving_time, right_click_moving = 0.0, False
        CellStorage.x, CellStorage.y = (width - CellStorage.size) // 2, (height - CellStorage.size) // 2
        CellStorage.x2, CellStorage.y2 = CellStorage.x, CellStorage.y
        t, dt = time(), 1 / 4
        running_screen = 1
        false_drawing = False
        colors = list(CellStorage.colors.keys())
        false_cells = {}
        keyboard = dict([(key, KeyboardKey()) for key in KeyboardKey.all_keys()])
        hidden_mode = 0

        s2_left = Button(get_img('data/left.png', 1 / 6, color='black'))
        s2_left.upd_pos(0, (height - s2_left.height()) // 2)
        s2_right = Button(get_img('data/right.png', 1 / 6))
        s2_right.upd_pos(width - s2_right.width(), (height - s2_left.height()) // 2)
        s2_inv = Button(get_img('data/i.png', 1 / 2))
        __right_height = 12
        s2_inv.upd_pos(99 / 100 * width - s2_inv.width(), __right_height)
        __size__icon__ = s2_inv.size()
        eraser = Button(get_img('data/eraser.png', size=__size__icon__))
        eraser.upd_pos(s2_inv.pos()[0] - eraser.width(), __right_height)
        s3_info = Button(get_img('data/info.png', size=__size__icon__, color='black'))
        s3_info.upd_pos(eraser.pos()[0] - s3_info.width(), __right_height)
        font = pygame.font.Font(None, 48)
        to_s1_text = Text(font.render('Вернуться к полю', True, "black"))
        to_s1_text.upd_pos((width - to_s1_text.width()) // 2 - 10, height - 2 * to_s1_text.height())
        s3_info_text = ('Игра \"жизнь\" Джона Конвея. \n'
                        'Вы расставляете на клетчатом поле живые клетки, далее на каждом шаге происходит: \n'
                        '1) если у живой клетки два или три живых соседа (из 8), то она выживает. \n'
                        '2) иначе живая клетка умирает. \n'
                        '3) мертвая клетка становится живой, если у неё ровно 3 живых соседа. \n'
                        'Теперь об управлении: \n'
                        'ЛКМ - поставить/убрать живую клетку. '
                        'ЛКМ(зажатая) - рисовать линию живых. \n'
                        'ПКМ(зажатая) - перемещение по полю. \n'
                        'Пробел - запустить/приостановить игру Конвея. \n'
                        'Левая/правая стрелочка - замедлить/ускорить игру в два раза. \n'
                        'Колесико мыши - увеличить/уменьшить поле. \n'
                        'Клавиша p или средняя кнопка мыши - вкл/выкл режим шаблона. \n'
                        'Верхняя/нижняя стрелочка - переключиться между шаблонами. \n'
                        'Клавиша r - повернуть шаблон на 90 градусов по часовой стрелке. \n'
                        'Клавиша e или кнопка справа сверху - вкл/выкл режим ластика. \n'
                        '1, 2, 3, 4, 5, 0 - цвета рисования (0 фальшивый: т.е. не участвует в игре). \n'
                        'Клавиша k - очистить поле, ctrl+k - очистить от фальшивого цвета. \n'
                        'Также у вас есть возможность создавать/удалять шаблоны и выбирать их в интентаре '
                        '(используется последний открытый) справа сверху (клавиша i). \n'
                        'Клавиши ctrl+s или кнопка справа сверху - сохранить поле и шаблоны. \n'
                        'Клавиши ctrl+z - откатиться к последнему сохранению. \n'
                        'v, b - путешествия во времени (не сохраняются). \n'
                        'Клавиша h - сменить режим сокрытия иконок (в поле). \n'
                        'Клавиша esc - выйти из текущего окна (в поле: выйти из приложения). \n')
        save = SaveBox('__parameters__', get_img('data/save.png', size=__size__icon__))
        save.upd_rect(s3_info.pos()[0] - s3_info.width(), __right_height, s3_info.width(), s3_info.height())
        save.upd_by_file()
        play_box = Button(get_img('data/play.png', size=__size__icon__))
        play_box.upd_pos(10, __right_height)
        buttons1 = [s2_inv, eraser, s3_info, save, play_box]
        buttons2 = [s2_left, s2_right, s2_inv, eraser, s3_info, save]
        buttons3 = [s2_inv, eraser, s3_info, save]
        s2_left.set_action(CellStorage.set_left_figure)
        s2_right.set_action(CellStorage.set_right_figure)
        s2_inv.set_action(lambda: to_screen(2))
        s3_info.set_action(lambda: to_screen(3))
        save.set_action(save.launch)

        def __upd_pause():
            CellStorage.pause = not CellStorage.pause

        def __upd_erase_mode():
            CellStorage.erase_mode = not CellStorage.erase_mode

        eraser.set_action(__upd_erase_mode)
        play_box.set_action(__upd_pause)

        while running:
            screen.fill((255, 255, 255))  # заполнить белым цветом
            if running_screen == 1:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        running = False

                    update_key(event, keyboard)

                    if event.type == pygame.KEYDOWN:
                        key = get_keyboard_key(event.key)
                        if key in list('12345'):
                            CellStorage.set_color(colors[int(key) - 1])
                            false_drawing = False
                        elif key == '0':
                            CellStorage.set_color('false')
                            false_drawing = True
                        elif key == 'r':
                            CellStorage.rotate()
                        elif key == 'i':
                            s2_inv.action(as_btn=False)
                        elif key == 'h':
                            hidden_mode = (hidden_mode + 1) % 3
                        elif key == 'esc':
                            running = False
                        elif key == 'F1':
                            s3_info.action(as_btn=False)
                        elif key == 'e':
                            eraser.action(as_btn=False)
                        elif key == 'p':
                            CellStorage.point_mode = not CellStorage.point_mode
                            if CellStorage.point_mode:
                                CellStorage.set_point()
                            else:
                                CellStorage.set_figure()
                        elif key == 'space':
                            play_box.action(as_btn=False)
                        elif key == 'left':
                            dt = min(2 * dt, 4)
                        elif key == 'right':
                            dt = max(dt / 2, 1 / 2 ** 7)
                        elif key == 'v':
                            CellStorage.left_frame()
                            keyboard['v'].game_pause = keyboard['b'].game_pause if keyboard['b'].is_pressed \
                                else CellStorage.pause
                        elif key == 'b':
                            CellStorage.right_frame()
                            keyboard['b'].game_pause = keyboard['v'].game_pause if keyboard['v'].is_pressed \
                                else CellStorage.pause

                    if keyboard['ctrl'].is_pressed:
                        if keyboard['k'].is_pressed:
                            false_cells.clear()
                        if keyboard['s'].is_pressed:
                            save.launch()
                        if keyboard['z'].is_pressed:
                            save.upd_by_file(full=False)
                    elif keyboard['k'].is_pressed:
                        CellStorage.clear()

                    if event.type == pygame.KEYUP and event.key == pygame.K_v:
                        CellStorage.pause = keyboard['v'].game_pause
                    if event.type == pygame.KEYUP and event.key == pygame.K_b:
                        CellStorage.pause = keyboard['b'].game_pause

                    if event.type == pygame.KEYDOWN and event.key == pygame.K_UP and not CellStorage.point_mode:
                        CellStorage.set_right_figure(empty_allow=False)
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN and not CellStorage.point_mode:
                        CellStorage.set_left_figure()

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
                        CellStorage.resize(2)
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
                        CellStorage.resize(1 / 2)
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                        CellStorage.point_mode = not CellStorage.point_mode
                        CellStorage.set_point() if CellStorage.point_mode \
                            else CellStorage.set_figure()

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        x, y = event.pos
                        __break = False
                        for btn in buttons1:
                            if btn.collide_point(x, y):
                                btn.active = True
                                __break = True
                        if __break:
                            pass
                        elif false_drawing:
                            i, j = CellStorage.get_ij(x, y)
                            if not CellStorage.erase_mode:
                                ij = (i, j)
                                if CellStorage.point_mode:
                                    if ij in false_cells:
                                        false_cells.pop(ij)
                                    else:
                                        false_cells[ij] = 1
                                else:
                                    for dx, dy in CellStorage.figure:
                                        if (i + dx, j + dy) not in false_cells:
                                            false_cells[(i + dx, j + dy)] = 1
                            else:
                                for dx, dy in CellStorage.figure:
                                    if (i + dx, j + dy) in false_cells:
                                        false_cells.pop((i + dx, j + dy))
                        else:
                            i, j = CellStorage.get_ij(x, y)
                            if CellStorage.erase_mode:
                                CellStorage.del_by_figure(i, j)
                            else:
                                if CellStorage.point_mode:
                                    CellStorage.create_with_del(i, j)
                                else:
                                    CellStorage.create(i, j)
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        left_click_moving_time = time()
                    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        left_click_moving_time = 0.0
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                        right_click_moving = True
                    if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                        right_click_moving = False

                    if event.type == pygame.MOUSEMOTION:
                        if left_click_moving_time > 0 and time() - left_click_moving_time >= 0.1:
                            i, j = CellStorage.mouse_cell_coord()
                            if not false_drawing:
                                if CellStorage.erase_mode:
                                    CellStorage.del_by_figure(i, j)
                                else:
                                    CellStorage.create(i, j)
                            else:
                                if not CellStorage.erase_mode:
                                    for dx, dy in CellStorage.figure:
                                        if (i + dx, j + dy) not in false_cells:
                                            false_cells[(i + dx, j + dy)] = 1
                                else:
                                    for dx, dy in CellStorage.figure:
                                        if (i + dx, j + dy) in false_cells:
                                            false_cells.pop((i + dx, j + dy))
                        if right_click_moving:
                            CellStorage.x += event.rel[0]
                            CellStorage.y += event.rel[1]

                for btn in buttons1:
                    btn.action()

                if running_screen != 1:
                    continue

                hide_buttons()

                if hidden_mode == 0:
                    blit_text(screen, f'{int(1 / dt) if 1 / dt == int(1 / dt) else 1 / dt} кадр/сек',
                              (play_box.pos()[0] + play_box.width(), play_box.pos()[1] + play_box.height() // 4),
                              pygame.font.SysFont('Courier New', 20))

                if not CellStorage.point_mode:
                    i, j = CellStorage.mouse_cell_coord()
                    CellStorage.draw_pale(i, j)

                if time() - t >= dt:
                    if keyboard['v'].get_tick():
                        CellStorage.left_frame()
                        CellStorage.pause = True
                        t = time()
                    if keyboard['b'].get_tick():
                        CellStorage.right_frame()
                        CellStorage.pause = True
                        t = time()
                    if not CellStorage.pause:
                        CellStorage.new_stage()
                        t = time()

                for cell in false_cells.keys():
                    CellStorage.s_draw(cell[0], cell[1], (170, 170, 170))
                for cell in CellStorage.values():
                    cell.draw()

                save.dis_light()
                eraser.set_color("red") if CellStorage.erase_mode else eraser.set_color("black")
                play_box.set_color("black") if CellStorage.pause else play_box.set_color("red")
                for btn in buttons1:
                    btn.blit(screen)
                pygame.display.flip()
            if running_screen == 2:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                    update_key(event, keyboard)

                    if event.type == pygame.KEYDOWN:
                        key = get_keyboard_key(event.key)
                        if key in list('12345'):
                            colors = list(CellStorage.colors.keys())
                            CellStorage.set_color(colors[int(key) - 1])
                            false_drawing = False
                        elif key == '0':
                            CellStorage.set_color('false')
                            false_drawing = True
                        elif key == 'h':
                            hidden_mode = (hidden_mode + 1) % 3
                        elif key == 'r':
                            CellStorage.rotate()
                        elif key == 'i' or key == 'esc':
                            s2_inv.action(as_btn=False)
                        elif key == 'F1':
                            s3_info.action(as_btn=False)
                        elif key == 'e':
                            eraser.action(as_btn=False)
                        elif key == 's' and keyboard['ctrl'].is_pressed:
                            save.action(as_btn=False)
                        elif key == 'k':
                            CellStorage.figures[CellStorage.figure_index].clear()
                        elif key == 'left':
                            CellStorage.set_left_figure()
                        elif key == 'right':
                            CellStorage.set_right_figure()

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        x, y = event.pos[0], event.pos[1]
                        if s2_left.collide_point(x, y):
                            CellStorage.set_left_figure()
                        elif s2_right.collide_point(x, y):
                            CellStorage.set_right_figure()
                        elif to_s1_text.collide_point(x, y) or s2_inv.collide_point(x, y):
                            to_screen(1)
                        elif eraser.collide_point(x, y):
                            CellStorage.erase_mode = not CellStorage.erase_mode
                        elif s3_info.collide_point(x, y):
                            to_screen(3)
                        elif save.collide_point(x, y):
                            save.make_file()
                            save.set_color('red')
                        else:
                            i, j = CellStorage.get_ij(x, y, s2=True)
                            CellStorage.upd_point(i, j, s2=True)

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        left_click_moving_time = time()
                    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        left_click_moving_time = 0.0

                    if event.type == pygame.MOUSEMOTION:
                        if left_click_moving_time > 0 and time() - left_click_moving_time >= 0.1:
                            CellStorage.upd_point_by_motion(s2=True)

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
                        CellStorage.resize(2, s2=True)
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
                        CellStorage.resize(1 / 2, s2=True)
                for btn in buttons2:
                    btn.action()
                if running_screen != 2:
                    continue
                CellStorage.s_draw(0, 0, (222, 222, 222), s2=True)
                CellStorage.draw_figure(s2=True)
                screen.blit(to_s1_text.text, to_s1_text.rect)
                s2_inv.set_color("red")
                eraser.set_color("red") if CellStorage.erase_mode else eraser.set_color("black")
                save.dis_light()
                for btn in buttons2:
                    btn.blit(screen)
                pygame.display.flip()
            if running_screen == 3:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    update_key(event, keyboard)

                    if event.type == pygame.KEYDOWN:
                        key = get_keyboard_key(event.key)
                        if key == 'i':
                            to_screen(2)
                        elif key == 'F1' or key == 'esc':
                            to_screen(1)
                        elif key == 's' and keyboard['ctrl'].is_pressed:
                            save.launch()

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        x, y = event.pos
                        if to_s1_text.collide_point(x, y) or s3_info.collide_point(x, y):
                            screen_quit_3()
                            running_screen = 1
                        elif s2_inv.collide_point(x, y):
                            screen_quit_3()
                            running_screen = 2
                        elif save.collide_point(x, y):
                            save.launch()
                for btn in buttons3:
                    btn.action()
                if running_screen != 3:
                    continue
                eraser.set_color("red") if CellStorage.erase_mode else eraser.set_color("black")
                screen.blit(to_s1_text.text, to_s1_text.rect)
                save.dis_light()
                s3_info.set_color("red")
                blit_text(screen, s3_info_text, (20, 15), pygame.font.SysFont('Courier New', 24))
                for btn in buttons3:
                    btn.blit(screen)
                pygame.display.flip()

        pygame.quit()

    run()


if __name__ == '__main__':
    main()
