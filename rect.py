import pygame.display


class Rect:
    def __init__(self, rect=(0, 0, 0, 0)):
        self.rect = rect

    def width(self):
        return self.rect[2]

    def height(self):
        return self.rect[3]

    def pos(self):
        return self.rect[0], self.rect[1]

    def size(self):
        return self.rect[2], self.rect[3]

    def upd_pos(self, x, y):
        self.rect[0], self.rect[1] = x, y

    def upd_rect(self, x, y, w, h):
        self.rect = (x, y, w, h)

    def collide_point(self, x, y):
        return self.rect[0] <= x <= self.rect[0] + self.rect[2] \
               and self.rect[1] <= y <= self.rect[1] + self.rect[3]


def fill(surface, color):
    w, h = surface.get_size()
    for x in range(w):
        for y in range(h):
            if surface.get_at((x, y))[3] > 0:
                surface.set_at((x, y), color)


class Button(Rect):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = list(image.get_rect())
        self.hidden = False
        self.active = False
        self.__action = lambda: None

    def set_color(self, color):
        self.image = self.image.convert_alpha()
        fill(self.image, color)

    def set_action(self, action):
        self.__action = action

    def collide_point(self, x, y):
        return not self.hidden and super().collide_point(x, y)

    def blit(self):
        if not self.hidden:
            pygame.display.get_surface().blit(self.image, self.rect)

    def action(self, as_btn=True):
        if (self.active and not self.hidden) or not as_btn:
            self.__action()
        self.active = False


class Text(Rect):
    def __init__(self, render_text):
        super().__init__()
        self.text = render_text
        self.rect = list(render_text.get_rect())

    def blit(self):
        pygame.display.get_surface().blit(self.text, self.rect)


def blit_text(surface, text, pos, font, color='black'):
    lines = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    x0, y0, width, height = surface.get_rect()
    max_x, max_y = x0 + width, y0 + height
    x, y = x0 + pos[0], y0 + pos[1]
    for line in lines:
        word_width, word_height = 0, 0
        for word in line:
            word_surface = font.render(word, True, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_x and x != x0 + pos[0]:
                x = x0 + pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y), (0, 0, max_x - x, max_y - y))
            x += word_width + space
        x = x0 + pos[0]  # Reset the x.
        y += word_height  # Start on new row.


def blit_button(btn, screen):
    screen.blit(btn.image, btn.rect)
