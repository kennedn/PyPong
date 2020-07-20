import pygame
class Button:
    def __init__(self, display, bg_color, fg_color, rect, pad, b_type, valid_states, function):
        self.display = display
        self.surface = pygame.Surface((rect.width, rect.height))#, pygame.SRCALPHA, 32)
        #self.surface = self.surface.convert_alpha()
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.rect = rect
        self.pad = pad
        self.rect_normal = pygame.Rect(pad, pad, rect.width - pad * 2, rect.height - pad * 2)
        self.b_type = b_type
        self.valid_states = valid_states
        self.function = function
        self.reverse_color = False

    def end_click_event(self, state, x, y):
        self.reverse_color = False

    def start_click_event(self, state, x, y):
        if self.rect.collidepoint(x, y) and state in self.valid_states:
            self.reverse_color = True
            self.function()

    # Handle types, import and draws a list of points for icons (polygon) or render and blit text for text types
    def draw_type(self, debug):
        if self.b_type == 0:
            from icons.up import points
        elif self.b_type == 1:
            from icons.down import points

        pygame.draw.polygon(self.surface, self.fg_color, points)

    def draw(self, debug, state):
        self.surface.fill((0, 0, 0))
        if state in self.valid_states:
            width = 0 if self.reverse_color else 2
            if debug >= 2:
                pygame.draw.rect(self.surface, (128, 0, 128), self.rect, 1)
            pygame.draw.rect(self.surface, self.bg_color, self.rect_normal, width)
            self.draw_type(debug)
        self.display.blit(self.surface, self.rect)
