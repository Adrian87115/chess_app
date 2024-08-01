import board as b
import pieces as p
import game as g
import pygame
import sys

class App:
    def __init__(self, width = 570, height = 600):
        self.width = width
        self.height = height
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Chess")
        self.clock = pygame.time.Clock()
        self.game = g.Game()
        self.mode = ""

    def titleScreen(self):
        button_color = (100, 100, 100)
        button_hover_color = (150, 150, 150)
        button_font = pygame.font.SysFont(None, 36)
        button_padding = 5
        button_labels = ["Two Players",
                         "One Player vs AI (Player White)",
                         "One Player vs AI (Player Black)",
                         "AI vs AI"]
        buttons = {}
        screen_width, screen_height = self.screen.get_size()
        button_height = 0
        total_height = 0

        for label in button_labels:
            text_surface = button_font.render(label, True, (255, 255, 255))
            text_width, text_height = text_surface.get_size()
            button_width = text_width + 2 * button_padding
            button_height = text_height + 2 * button_padding
            buttons[label] = pygame.Rect(0, 0, button_width, button_height)
            total_height += button_height + 10

        start_y = (screen_height - total_height) // 2

        for i, label in enumerate(button_labels):
            button_rect = buttons[label]
            button_rect.centerx = screen_width // 2
            button_rect.y = start_y + i * (button_height + 10)
            buttons[label] = button_rect

        running = True
        while running:
            self.screen.fill((128, 128, 128))
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()

            for button_text, button_rect in buttons.items():
                if button_rect.collidepoint(mouse_pos):
                    current_button_color = button_hover_color
                    if mouse_click[0]:
                        self.mode = button_text
                        self.startGame()
                        return
                else:
                    current_button_color = button_color

                pygame.draw.rect(self.screen, current_button_color, button_rect)
                text_surface = button_font.render(button_text, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center = button_rect.center)
                self.screen.blit(text_surface, text_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.flip()
            self.clock.tick(60)

    def startGame(self):
        if self.mode == "Two Players":
            self.game.humanVsHuman(self.screen, self.clock)
        elif self.mode == "One Player vs AI (Player White)":
            self.game.humanVsComputer(self.screen, self.clock, "white")
        elif self.mode == "One Player vs AI (Player Black)":
            self.game.humanVsComputer(self.screen, self.clock, "black")
        elif self.mode == "AI vs AI":
            self.game.computerVsComputer(self.screen, self.clock)

    def run(self):
        self.titleScreen()