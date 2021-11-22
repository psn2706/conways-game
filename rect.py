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

    def set_color(self, color):
        self.image = self.image.convert_alpha()
        fill(self.image, color)

    def blit(self, screen):
        screen.blit(self.image, self.rect)


class Text(Rect):
    def __init__(self, text):
        super().__init__()
        self.text = text
        self.rect = list(text.get_rect())


def blit_text(surface, text, pos, font, color='black'):
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in words:
        word_width, word_height = 0, 0
        for word in line:
            word_surface = font.render(word, True, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row.


def blit_button(btn, screen):
    screen.blit(btn.image, btn.rect)
