import board as b
import pieces as p
import pygame

class Game:
    def __init__(self):
        self.board = b.Board()
        self.current_turn = "white"
        self.images = {"P" : pygame.image.load("images/pawn_white.png"),
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

    def drawBoard(self, screen):
        colors = [pygame.Color(190, 190, 190), pygame.Color(60, 60, 60)]
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                pygame.draw.rect(screen, color, pygame.Rect(col * 65, row * 65, 65, 65))

    def drawPieces(self, board, screen):
        for row in board:
            for piece in row:
                if piece != ".":
                    screen.blit(self.images[piece.shape], (piece.x * 65, piece.y * 65))

    def getSquare(self):
        mouse_pos = pygame.mouse.get_pos()
        x, y = [int(v // 65) for v in mouse_pos]
        return x, y

    def launch(self):
        pygame.init()
        screen = pygame.display.set_mode((520, 600))
        clock = pygame.time.Clock()
        running = True
        selected_piece = "."
        color = {1: "white",
                 0: "black"}
        selected = False
        valid_moves = []
        unvalid_moves_king = []
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not selected:
                        x, y = self.getSquare()
                        if 0 <= x < 8 and 0 <= y < 8:
                            selected_piece = self.board.getFigure(y, x)
                            if selected_piece != "." and selected_piece.color == self.current_turn:
                                print(f"Selected piece at ({x}, {y}): {selected_piece}")
                                selected = True
                                valid_moves = selected_piece.validMoves(self.board.board)

                            else:
                                print("Not a valid piece or not your turn")
                                selected_piece = None
                        else:
                            print("Not part of the board")
                    else:
                        x, y = self.getSquare()
                        if 0 <= x < 8 and 0 <= y < 8:
                            if (x, y) == (selected_piece.x, selected_piece.y):
                                print("Unselected")
                                selected = False
                                valid_moves = []
                            else:
                                did_move = selected_piece.move(x, y, self.board.board)
                                if did_move:
                                    self.current_turn = "black" if self.current_turn == "white" else "white"
                                    print(f"Moved {selected_piece} to ({x}, {y})")
                                    selected = False
                                    valid_moves = []
                                else:
                                    print(f"Invalid move for {selected_piece} to ({x}, {y})")
                        else:
                            print("Not part of the board")


            self.drawBoard(screen)
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
            pygame.display.flip()

            clock.tick(60)

# king when checked then his square is red and has to move, also red square endagered position