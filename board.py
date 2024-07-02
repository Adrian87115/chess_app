import figures as f

class Board:
    def __init__(self):
        self.width = 8 # top left corner - (0, 0)
        self.height = 8
        self.board = [[f.Rook(0, 0, "black"), f.Knight(1, 0, "black"), f.Bishop(2, 0, "black"), f.Queen(3, 0, "black"), f.King(4, 0, "black"), f.Bishop(5, 0, "black"), f.Knight(6, 0, "black"), f.Rook(7, 0, "black")],
                      [f.Pawn(x, 1, "black") for x in range(8)],
                      [None] * 8,
                      [None] * 8,
                      [None] * 8,
                      [None] * 8,
                      [f.Pawn(x, 6, "white") for x in range(8)],
                      [f.Rook(0, 7, "white"), f.Knight(1, 7, "white"), f.Bishop(2, 7, "white"), f.Queen(3, 7, "white"), f.King(4, 7, "white"), f.Bishop(5, 7, "white"), f.Knight(6, 7, "white"), f.Rook(7, 7, "white")]]

    def displayBoard(self):
        for row in self.board:
            print([str(figure) if figure else "." for figure in row])

    def getFigure(self, x, y):
        return self.board[x][y]