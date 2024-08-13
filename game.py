import board as b
import pieces as p
import app as a
import agent as ai
import pygame
import sys

class Game:
    def __init__(self):
        self.board = b.Board()
        self.current_turn = "white"
        self.images = {"P": pygame.image.load("images/pawn_white.png"),
                       "p": pygame.image.load("images/pawn_black.png"),
                       "R": pygame.image.load("images/rook_white.png"),
                       "r": pygame.image.load("images/rook_black.png"),
                       "Kn": pygame.image.load("images/knight_white.png"),
                       "kn": pygame.image.load("images/knight_black.png"),
                       "B": pygame.image.load("images/bishop_white.png"),
                       "b": pygame.image.load("images/bishop_black.png"),
                       "Q": pygame.image.load("images/queen_white.png"),
                       "q": pygame.image.load("images/queen_black.png"),
                       "Ki": pygame.image.load("images/king_white.png"),
                       "ki": pygame.image.load("images/king_black.png")}
        self.messages = []
        self.running = True
        self.selected_piece = None
        self.selected = False
        self.valid_moves = []
        self.king_check = False
        self.king_pos = None

    def drawBoard(self, screen):
        colors = [pygame.Color(160, 160, 160), pygame.Color(60, 60, 60)]
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                pygame.draw.rect(screen, color, pygame.Rect(col * 65, row * 65, 65, 65))

    def drawPieces(self, board, screen):
        for row in board:
            for piece in row:
                if piece != ".":
                    screen.blit(self.images[piece.shape], (piece.x * 65, piece.y * 65))

    def drawScreenReseted(self, screen):
        self.drawBoard(screen)
        self.drawPieces(self.board.board, screen)
        panel = pygame.Rect(520, 0, 50, 600)
        pygame.draw.rect(screen, (128, 128, 128), panel)

    def drawMessages(self, screen):
        font = pygame.font.SysFont(None, 24)
        message_area = pygame.Rect(0, 520, 520, 80)
        pygame.draw.rect(screen, pygame.Color(128, 128, 128), message_area)
        if self.messages:
            last_message = self.messages[-1]
            text_surface = font.render(last_message, True, pygame.Color('white'))
            text_rect = text_surface.get_rect()
            text_rect.center = message_area.center
            screen.blit(text_surface, text_rect)

    def getSquare(self):
        mouse_pos = pygame.mouse.get_pos()
        x, y = [int(v // 65) for v in mouse_pos]
        return x, y

    def resetGame(self):
        self.board = b.Board()
        self.current_turn = "white"
        self.messages = []
        self.running = True
        self.selected_piece = None
        self.selected = False
        self.valid_moves = []
        self.king_check = False
        self.king_pos = None

    def displayPanel(self, screen):
        panel = pygame.Rect(520, 0, 50, 600)
        pygame.draw.rect(screen, (128, 128, 128), panel)
        back_image = pygame.image.load("images/back_white.png")
        back_image_hover = pygame.image.load("images/back_grey.png")
        button_size = 48
        button_rect_back = pygame.Rect(521, 0, button_size, button_size)
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        if button_rect_back.collidepoint(mouse_pos):
            current_image = back_image_hover
            if mouse_click[0]:
                self.resetGame()
                a.App().titleScreen()
                return
        else:
            current_image = back_image
        current_image = pygame.transform.scale(current_image, (button_size, button_size))
        screen.blit(current_image, button_rect_back.topleft)
        reset_image = pygame.image.load("images/reset_white.png")
        reset_image_hover = pygame.image.load("images/reset_grey.png")
        button_rect_reset = pygame.Rect(521, 50, button_size, button_size)
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        if button_rect_reset.collidepoint(mouse_pos):
            current_image = reset_image_hover
            if mouse_click[0]:
                pygame.time.wait(200)
                self.resetGame()
                a.App().startGame()
                self.drawScreenReseted(screen)
                self.messages.append("Game reseted")
                return
        else:
            current_image = reset_image
        current_image = pygame.transform.scale(current_image, (button_size, button_size))
        screen.blit(current_image, button_rect_reset.topleft)

    def displayPromotion(self, screen, x, y, color):
        button_size = 48
        spacing = 5
        panel_width = button_size
        panel_height = 4 * button_size + 3 * spacing
        panel_x = 521
        panel_y = 105
        panel = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        button_rects = {}
        images = {}
        hover_images = {}
        for index, piece in enumerate(['rook', 'knight', 'bishop', 'queen']):
            y_position = panel_y + index * (button_size + spacing)
            rect = pygame.Rect(panel_x, y_position, button_size, button_size)
            button_rects[piece] = rect
            images[piece] = pygame.transform.scale(
                pygame.image.load(f"images/{piece}_{color}.png"),
                (button_size, button_size)
            )
            hover_images[piece] = pygame.transform.scale(
                pygame.image.load(f"images/{piece}_hover.png"),
                (button_size, button_size)
            )
        pygame.draw.rect(screen, (128, 128, 128), panel)
        mouse_pos = pygame.mouse.get_pos()

        for piece, rect in button_rects.items():
            if rect.collidepoint(mouse_pos):
                screen.blit(hover_images[piece], rect.topleft)
            else:
                screen.blit(images[piece], rect.topleft)

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for piece, rect in button_rects.items():
                        if rect.collidepoint(mouse_pos):
                            if piece == "rook":
                                return p.Rook(x, y, color)
                            elif piece == "knight":
                                return p.Knight(x, y, color)
                            elif piece == "bishop":
                                return p.Bishop(x, y, color)
                            elif piece == "queen":
                                return p.Queen(x, y, color)

    def playStep(self, selected_piece, move):
        new_tile_current_piece = self.board.board[move[1]][move[0]]
        for row in self.board.board:
            for piece in row:
                if piece == selected_piece:
                    self.board.board[piece.y][piece.x] = "."
                    self.board.board[selected_piece.y][selected_piece.x] = selected_piece
        reward = 0
        done = False
        score = 0
        if new_tile_current_piece == ".":
            pass
        elif new_tile_current_piece.shape.title() == "P":
            reward += 1
        elif new_tile_current_piece.shape.title() == "R":
            reward += 5
        elif new_tile_current_piece.shape.title() == "B" or new_tile_current_piece.shape.title() == "Kn":
            reward += 3
        elif new_tile_current_piece.shape.title() == "Q":
            reward += 10

        if self.board.isCheckmate(selected_piece.color):
            print("checkmate killed")
            reward += 100
            done = True
        elif self.board.isCheck(selected_piece.color):
            reward += 3
        elif self.board.isStalemate(selected_piece.color):
            print("stalemate killed")
            reward += 1
            done = True
        elif self.board.isInsufficientMaterial():
            print("material killed")
            reward += 1
            done = True
        score = reward
        return reward, done, score


    def humanVsHuman(self, screen, clock):
        promoted_msg = False
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = self.getSquare()
                    if 0 <= x < 8 and 0 <= y < 8:
                        if not self.selected:
                            self.selected_piece = self.board.getFigure(y, x)
                            if self.selected_piece != "." and self.selected_piece.color == self.current_turn:
                                self.king_check = self.board.isKingInCheck(self.current_turn)
                                if self.king_check:
                                    if self.board.isCheckmate(self.current_turn):
                                        self.messages.append(f"Checkmate! {self.current_turn.title()} loses.")
                                    else:
                                        check_resolving_moves = self.board.validMovesWhenCheck(self.current_turn)
                                        pieces_that_can_move = {move[0] for move in check_resolving_moves}

                                        if self.selected_piece not in pieces_that_can_move:
                                            self.messages.append("You must move a piece to resolve the check")
                                            selected_piece = None
                                        else:
                                            self.messages.append(f"Selected piece {self.selected_piece}")
                                            self.selected = True
                                            self.valid_moves = [move[1] for move in check_resolving_moves if move[0] == self.selected_piece]
                                else:
                                    self.messages.append(f"Selected piece {self.selected_piece}")
                                    self.selected = True
                                    self.valid_moves = self.selected_piece.validMoves(self.board.board, 1)
                            else:
                                self.messages.append("Not a valid piece or not your turn")
                                self.selected_piece = None
                        else:
                            if (x, y) == (self.selected_piece.x, self.selected_piece.y):
                                self.messages.append("Unselected")
                                self.selected = False
                                self.valid_moves = []
                            else:
                                if (x, y) in self.valid_moves:
                                    did_move = self.selected_piece.move(x, y, self.board.board)
                                    if did_move:
                                        if isinstance(self.selected_piece, p.Pawn) and (y == 0 or y == 7):
                                            self.messages.append("Select a piece for promotion:")
                                            new_piece = None
                                            while new_piece is None:
                                                for event in pygame.event.get():
                                                    if event.type == pygame.QUIT:
                                                        self.running = False
                                                        pygame.quit()
                                                        sys.exit()

                                                self.displayPanel(screen)
                                                self.drawBoard(screen)
                                                self.drawPieces(self.board.board, screen)
                                                self.drawMessages(screen)
                                                new_piece = self.displayPromotion(
                                                    screen, self.selected_piece.x, self.selected_piece.y, self.selected_piece.color
                                                )

                                                pygame.display.flip()
                                                clock.tick(60)

                                            self.board.board[self.selected_piece.y][self.selected_piece.x] = new_piece
                                            promoted_msg = True

                                        self.current_turn = "black" if self.current_turn == "white" else "white"
                                        self.messages.append(f"Moved {self.selected_piece} to ({x}, {y})")
                                        if promoted_msg:
                                            self.messages.append(
                                                f"Pawn promoted to {new_piece.__class__.__name__} at ({self.selected_piece.x}, {self.selected_piece.y})"
                                            )
                                            promoted_msg = False
                                        self.selected = False
                                        self.valid_moves = []
                                        self.king_check = self.board.isKingInCheck(self.current_turn)

                                        if self.king_check and self.board.isCheckmate(self.current_turn):
                                            self.messages.append(f"Checkmate! {self.current_turn.title()} loses.")
                                        elif not self.king_check and self.board.isStalemate(self.current_turn):
                                            self.messages.append("Stalemate! The game is a draw.")

                                        if self.board.isInsufficientMaterial():
                                            self.messages.append("Draw due to insufficient material.")

                                        self.king_pos = self.board.getKingPosition(self.current_turn) if self.king_check else None
                                    else:
                                        self.messages.append(f"Invalid move for {self.selected_piece}")
                                else:
                                    self.messages.append("Move not allowed")
                    else:
                        self.messages.append("Not part of the board")
            self.displayPanel(screen)
            self.drawBoard(screen)


            if self.king_check and self.king_pos:
                pygame.draw.rect(screen, pygame.Color(255, 0, 0),
                                 pygame.Rect(self.king_pos[0] * 65, self.king_pos[1] * 65, 65, 65), 3)
            if self.selected:
                pygame.draw.rect(screen, pygame.Color(0, 0, 150),
                                 pygame.Rect(self.selected_piece.x * 65, self.selected_piece.y * 65, 65, 65), 3)
            for move in self.valid_moves:
                if self.selected_piece.isSquareEnemyPiece(move[0], move[1], self.board.board):
                    pygame.draw.rect(screen, pygame.Color(255, 101, 0),
                                     pygame.Rect(move[0] * 65, move[1] * 65, 65, 65), 3)
                else:
                    pygame.draw.rect(screen, pygame.Color(0, 255, 0),
                                     pygame.Rect(move[0] * 65, move[1] * 65, 65, 65), 3)
            self.drawPieces(self.board.board, screen)
            self.drawMessages(screen)
            pygame.display.flip()

            clock.tick(60)

    def humanVsComputer(self, screen, clock, player_color):
        pass

    def computerVsComputer(self, screen, clock):
        ai1 = ai.Agent()
        ai2 = ai.Agent()
        self.current_turn = "white"
        last_move_time = pygame.time.get_ticks()
        game_over = False

        while self.running:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - last_move_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if elapsed_time >= 1000 and not game_over:
                if self.current_turn == "white":
                    piece, new_position = ai1.getAction(self.board, self.current_turn)# finally: the problem is with placing figure, sometimes it glitches and causes many figures to move at once, also it may lead to capturing king, and this leads to error where it cant fin d the postion of king so cant fine x and y from the nonetype
                else:
                    piece, new_position = ai2.getAction(self.board, self.current_turn)

                if piece and new_position:
                    x_start, y_start = piece.x, piece.y
                    x_end, y_end = new_position

                    did_move = piece.move(x_end, y_end, self.board.board)
                    if did_move:
                        if isinstance(piece, p.Pawn) and (y_end == 0 or y_end == 7):
                            self.board.board[y_end][x_end] = p.Queen(x_end, y_end, self.current_turn)
                        self.current_turn = "black" if self.current_turn == "white" else "white"
                        # self.messages.append(f"{self.current_turn.title()}'s turn")
                        self.king_check = self.board.isKingInCheck(self.current_turn)
                        if self.king_check:
                            if self.board.isCheckmate(self.current_turn):
                                self.messages.append(f"Checkmate! {self.current_turn.title()} loses.")
                                game_over = True
                            elif self.board.isStalemate(self.current_turn):
                                self.messages.append("Stalemate! The game is a draw.")
                                game_over = True

                        if self.board.isInsufficientMaterial():
                            self.messages.append("Draw due to insufficient material.")
                            game_over = True

                        self.king_pos = self.board.getKingPosition(self.current_turn) if self.king_check else None
                    else:
                        self.messages.append(f"Invalid move for {piece}")
                else:
                    self.messages.append("No valid moves available")
                last_move_time = pygame.time.get_ticks()
            self.displayPanel(screen)
            self.drawBoard(screen)
            self.drawPieces(self.board.board, screen)
            self.drawMessages(screen)
            if self.king_check and self.king_pos:
                pygame.draw.rect(screen, pygame.Color(255, 0, 0),
                                 pygame.Rect(self.king_pos[0] * 65, self.king_pos[1] * 65, 65, 65), 3)
            if game_over:
                self.messages.append("Game Over. Press Q to quit or R to restart.")

                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            pygame.quit()
                            sys.exit()
                        elif event.key == pygame.K_r:
                            self.resetGame()
                            game_over = False

            pygame.display.flip()
            clock.tick(60)