from time import time
import pygame


class KeyboardKey:
    def __init__(self):
        self.is_pressed = False
        self.seconds = time()
        self.game_pause = True
        self.tick = False

    def down(self):
        self.is_pressed = True
        self.seconds = time()
        self.tick = False

    def up(self):
        self.is_pressed = False
        self.tick = False

    def get_tick(self):
        if not self.tick:
            self.tick = time() - self.seconds >= 0.2
        return self.tick and self.is_pressed

    @staticmethod
    def all_keys():
        lst = []
        lst.extend(list('0123456789qwertyuiopasdfghjklzxcvbnm'))
        lst.extend([f'F{i}' for i in range(1, 13)])
        lst.extend(['ctrl', 'esc', 'space', 'left', 'right', 'up', 'down'])
        return lst


def update_key(e, keyboard):
    if e.type == pygame.KEYDOWN:
        key = get_keyboard_key(e.key)
        if key in keyboard:
            keyboard[key].down()
    if e.type == pygame.KEYUP:
        key = get_keyboard_key(e.key)
        if key in keyboard:
            keyboard[key].up()


def get_keyboard_key(key):
    if key == pygame.K_0:
        return '0'
    if key == pygame.K_1:
        return '1'
    if key == pygame.K_2:
        return '2'
    if key == pygame.K_3:
        return '3'
    if key == pygame.K_4:
        return '4'
    if key == pygame.K_5:
        return '5'
    if key == pygame.K_6:
        return '6'
    if key == pygame.K_7:
        return '7'
    if key == pygame.K_8:
        return '8'
    if key == pygame.K_9:
        return '9'
    if key == pygame.K_a:
        return 'a'
    if key == pygame.K_b:
        return 'b'
    if key == pygame.K_c:
        return 'c'
    if key == pygame.K_d:
        return 'd'
    if key == pygame.K_e:
        return 'e'
    if key == pygame.K_f:
        return 'f'
    if key == pygame.K_g:
        return 'g'
    if key == pygame.K_h:
        return 'h'
    if key == pygame.K_i:
        return 'i'
    if key == pygame.K_j:
        return 'j'
    if key == pygame.K_k:
        return 'k'
    if key == pygame.K_l:
        return 'l'
    if key == pygame.K_m:
        return 'm'
    if key == pygame.K_n:
        return 'n'
    if key == pygame.K_o:
        return 'o'
    if key == pygame.K_p:
        return 'p'
    if key == pygame.K_q:
        return 'q'
    if key == pygame.K_r:
        return 'r'
    if key == pygame.K_s:
        return 's'
    if key == pygame.K_t:
        return 't'
    if key == pygame.K_u:
        return 'u'
    if key == pygame.K_v:
        return 'v'
    if key == pygame.K_w:
        return 'w'
    if key == pygame.K_x:
        return 'x'
    if key == pygame.K_y:
        return 'y'
    if key == pygame.K_z:
        return 'z'
    if key == pygame.K_F1:
        return 'F1'
    if key == pygame.K_F2:
        return 'F2'
    if key == pygame.K_F3:
        return 'F3'
    if key == pygame.K_F4:
        return 'F4'
    if key == pygame.K_F5:
        return 'F5'
    if key == pygame.K_F6:
        return 'F6'
    if key == pygame.K_F7:
        return 'F7'
    if key == pygame.K_F8:
        return 'F8'
    if key == pygame.K_F9:
        return 'F9'
    if key == pygame.K_F10:
        return 'F10'
    if key == pygame.K_F11:
        return 'F11'
    if key == pygame.K_F12:
        return 'F12'
    if key == pygame.K_LCTRL or key == pygame.K_RCTRL:
        return 'ctrl'
    if key == pygame.K_ESCAPE:
        return 'esc'
    if key == pygame.K_SPACE:
        return 'space'
    if key == pygame.K_LEFT:
        return 'left'
    if key == pygame.K_RIGHT:
        return 'right'
    if key == pygame.K_UP:
        return 'up'
    if key == pygame.K_DOWN:
        return 'down'
    return 'None'
