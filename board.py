import pieces as p

class Board:
    def __init__(self):
        self.width = 8 # top left corner - (0, 0)
        self.height = 8
        self.board = [[p.Rook(0, 0, "black"), p.Knight(1, 0, "black"), p.Bishop(2, 0, "black"), p.Queen(3, 0, "black"), p.King(4, 0, "black"), p.Bishop(5, 0, "black"), p.Knight(6, 0, "black"), p.Rook(7, 0, "black")],
                      [p.Pawn(x, 1, "black") for x in range(8)],
                      ["."] * 8,
                      ["."] * 8,
                      ["."] * 8,
                      ["."] * 8,
                      [p.Pawn(x, 6, "white") for x in range(8)],
                      [p.Rook(0, 7, "white"), p.Knight(1, 7, "white"), p.Bishop(2, 7, "white"), p.Queen(3, 7, "white"), p.King(4, 7, "white"), p.Bishop(5, 7, "white"), p.Knight(6, 7, "white"), p.Rook(7, 7, "white")]]

    def displayBoard(self):
        for row in self.board:
            print([figure.shape if figure else "." for figure in row])

    def getFigure(self, x, y):
        return self.board[x][y]