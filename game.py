import board as b
import pieces as p
import pygame

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

    def drawMessages(self, screen):
        font = pygame.font.SysFont(None, 24)
        message_area = pygame.Rect(0, 520, 520, 80)
        pygame.draw.rect(screen, pygame.Color(0, 0, 0), message_area)
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

    def launch(self):
        pygame.init()
        screen = pygame.display.set_mode((520, 650))
        clock = pygame.time.Clock()
        running = True
        selected_piece = "."
        color = {1: "white",
                 0: "black"}
        selected = False
        valid_moves = []
        king_check = False
        king_pos = None
        game_over = False

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = self.getSquare()
                    if 0 <= x < 8 and 0 <= y < 8:
                        if not selected:
                            selected_piece = self.board.getFigure(y, x)
                            if selected_piece != "." and selected_piece.color == self.current_turn:
                                king_check = self.board.isKingInCheck(self.current_turn)
                                if king_check:
                                    # Check for checkmate
                                    if self.board.isCheckmate(self.current_turn):
                                        self.messages.append(f"Checkmate! {self.current_turn} loses.")
                                        game_over = True
                                    else:
                                        check_resolving_moves = self.board.validMovesWhenCheck(self.current_turn)
                                        pieces_that_can_move = {move[0] for move in check_resolving_moves}

                                        if selected_piece not in pieces_that_can_move:
                                            self.messages.append("You must move a piece to resolve the check")
                                            selected_piece = None
                                        else:
                                            self.messages.append(f"Selected piece at ({x}, {y}): {selected_piece}")
                                            selected = True
                                            valid_moves = [move[1] for move in check_resolving_moves if
                                                           move[0] == selected_piece]
                                else:
                                    self.messages.append(f"Selected piece at ({x}, {y}): {selected_piece}")
                                    selected = True
                                    valid_moves = selected_piece.validMoves(self.board.board, 1)
                            else:
                                self.messages.append("Not a valid piece or not your turn")
                                selected_piece = None
                        else:
                            if (x, y) == (selected_piece.x, selected_piece.y):
                                self.messages.append("Unselected")
                                selected = False
                                valid_moves = []
                            else:
                                if (x, y) in valid_moves:
                                    did_move = selected_piece.move(x, y, self.board.board)
                                    if did_move:
                                        self.current_turn = "black" if self.current_turn == "white" else "white"
                                        self.messages.append(f"Moved {selected_piece} to ({x}, {y})")
                                        selected = False
                                        valid_moves = []
                                        king_check = self.board.isKingInCheck(self.current_turn)

                                        # Check for checkmate or stalemate
                                        if king_check and self.board.isCheckmate(self.current_turn):
                                            self.messages.append(f"Checkmate! {self.current_turn.title()} loses.")
                                            game_over = True
                                        elif not king_check and self.board.isStalemate(self.current_turn):
                                            self.messages.append("Stalemate! The game is a draw.")
                                            game_over = True

                                        # Check for insufficient material
                                        if self.board.isInsufficientMaterial():
                                            self.messages.append("Draw due to insufficient material.")
                                            game_over = True

                                        king_pos = self.board.getKingPosition(self.current_turn) if king_check else None
                                    else:
                                        self.messages.append(f"Invalid move for {selected_piece} to ({x}, {y})")
                                else:
                                    self.messages.append("Move not allowed")
                    else:
                        self.messages.append("Not part of the board")

            self.drawBoard(screen)
            if king_check and king_pos:
                pygame.draw.rect(screen, pygame.Color(255, 0, 0),
                                 pygame.Rect(king_pos[0] * 65, king_pos[1] * 65, 65, 65), 3)
            if selected:
                pygame.draw.rect(screen, pygame.Color(0, 0, 150),
                    pygame.Rect(selected_piece.x * 65, selected_piece.y * 65, 65, 65), 3)
            for move in valid_moves:
                if selected_piece.isSquareEnemyPiece(move[0], move[1], self.board.board):
                    pygame.draw.rect(screen, pygame.Color(255, 101, 0),
                                     pygame.Rect(move[0] * 65, move[1] * 65, 65, 65), 3)
                else:
                    pygame.draw.rect(screen, pygame.Color(0, 255, 0),
                    pygame.Rect(move[0] * 65, move[1] * 65, 65, 65), 3)
            self.drawPieces(self.board.board, screen)
            self.drawMessages(screen)
            pygame.display.flip()

            clock.tick(60)
        pygame.quit()