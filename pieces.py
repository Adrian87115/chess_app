class Piece:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.shape = ""
        self.color = color

    def __repr__(self):
        return f"{self.__class__.__name__}({self.x}, {self.y}, {self.color})"

    def getPosition(self):
        return self.x, self.y

    def isSquareEnemyPiece(self, x, y, board):
        if 0 <= x < 8 and 0 <= y < 8:
            return board[y][x] != "." and board[y][x].color != self.color
        return False

    def isSquareEmpty(self, x, y, board):
        if 0 <= x < 8 and 0 <= y < 8:
            return board[y][x] == "."
        return False

    def validMoves(self, board):
        pass

    def move(self, new_x, new_y, board):
        if (new_x, new_y) in self.validMoves(board):
            board[self.y][self.x] = "."
            self.x = new_x
            self.y = new_y
            board[self.y][self.x] = self
            return True
        return False

class Pawn(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.has_moved = False
        if color == "white":
            self.shape = "P"
        else:
            self.shape = "p"

    def validMoves(self, board):
        direction = -1 if self.color == "white" else 1 # 1 - up, -1 down
        valid_moves = []
        curr_x = self.x
        curr_y = self.y

        if not self.has_moved:
            new_x = curr_x
            new_y = curr_y + 2 * direction
            # ahead 2
            if self.isSquareEmpty(new_x, new_y, board) and self.isSquareEmpty(new_x, curr_y + direction, board):
                valid_moves.append((new_x, new_y))

        new_x = curr_x
        new_y = curr_y + direction
        # ahead 1
        if self.isSquareEmpty(new_x, new_y, board):
            valid_moves.append((new_x, new_y))

        # capture left
        new_x = curr_x - 1
        if self.isSquareEnemyPiece(new_x, new_y, board):
            valid_moves.append((new_x, new_y))

        # capture right
        new_x = curr_x + 1
        if self.isSquareEnemyPiece(new_x, new_y, board):
            valid_moves.append((new_x, new_y))
        return valid_moves

    def move(self, new_x, new_y, board):
        if (new_x, new_y) in self.validMoves(board):
            board[self.y][self.x] = "."
            self.x = new_x
            self.y = new_y
            board[self.y][self.x] = self
            self.has_moved = True
            return True
        return False

class Rook(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        if color == "white":
            self.shape = "R"
        else:
            self.shape = "r"

    def validMoves(self, board):
        valid_moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        curr_x = self.x
        curr_y = self.y

        for direction in directions:
            d_x, d_y = direction
            new_x = curr_x + d_x
            new_y = curr_y + d_y

            while 0 <= new_x < 8 and 0 <= new_y < 8:
                if self.isSquareEmpty(new_x, new_y, board):
                    valid_moves.append((new_x, new_y))
                    new_x = new_x + d_x
                    new_y = new_y + d_y
                elif self.isSquareEnemyPiece(new_x, new_y, board):
                    valid_moves.append((new_x, new_y))
                    break
                else:
                    break
        return valid_moves

class Knight(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        if color == "white":
            self.shape = "Kn"
        else:
            self.shape = "kn"

    def validMoves(self, board):
        valid_moves = []
        directions = [(-1, -2), (-1, 2), (1, -2), (1, 2), (-2, -1), (-2, 1), (2, -1), (2, 1)]
        curr_x = self.x
        curr_y = self.y

        for direction in directions:
            d_x, d_y = direction
            new_x = curr_x + d_x
            new_y = curr_y + d_y

            if 0 <= new_x < 8 and 0 <= new_y < 8:
                if self.isSquareEmpty(new_x, new_y, board) or self.isSquareEnemyPiece(new_x, new_y, board):
                    valid_moves.append((new_x, new_y))

        return valid_moves

class Bishop(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        if color == "white":
            self.shape = "B"
        else:
            self.shape = "b"

    def validMoves(self, board):
        valid_moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        curr_x = self.x
        curr_y = self.y

        for direction in directions:
            d_x, d_y = direction
            new_x = curr_x + d_x
            new_y = curr_y + d_y

            while 0 <= new_x < 8 and 0 <= new_y < 8:
                if self.isSquareEmpty(new_x, new_y, board):
                    valid_moves.append((new_x, new_y))
                    new_x = new_x + d_x
                    new_y = new_y + d_y
                elif self.isSquareEnemyPiece(new_x, new_y, board):
                    valid_moves.append((new_x, new_y))
                    break
                else:
                    break
        return valid_moves

class Queen(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        if color == "white":
            self.shape = "Q"
        else:
            self.shape = "q"

    def validMoves(self, board):
        valid_moves = []
        curr_x = self.x
        curr_y = self.y
        directions_perpendicular = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for direction in directions_perpendicular:
            d_x, d_y = direction
            new_x = curr_x + d_x
            new_y = curr_y + d_y
            while 0 <= new_x < 8 and 0 <= new_y < 8:
                if self.isSquareEmpty(new_x, new_y, board):
                    valid_moves.append((new_x, new_y))
                    new_x = new_x + d_x
                    new_y = new_y + d_y
                elif self.isSquareEnemyPiece(new_x, new_y, board):
                    valid_moves.append((new_x, new_y))
                    break
                else:
                    break

        directions_diagonal = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for direction in directions_diagonal:
            d_x, d_y = direction
            new_x = curr_x + d_x
            new_y = curr_y + d_y

            while 0 <= new_x < 8 and 0 <= new_y < 8:
                if self.isSquareEmpty(new_x, new_y, board):
                    valid_moves.append((new_x, new_y))
                    new_x = new_x + d_x
                    new_y = new_y + d_y
                elif self.isSquareEnemyPiece(new_x, new_y, board):
                    valid_moves.append((new_x, new_y))
                    break
                else:
                    break

        return valid_moves

class King(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        if color == "white":
            self.shape = "Ki"
        else:
            self.shape = "ki"

    def getAllEnemyMoves(self, board):
        enemy_moves = set()
        for row in board:
            for piece in row:
                if piece != "." and piece.color != self.color:
                    for move in piece.validMoves(board):
                        enemy_moves.add(move)
        return enemy_moves

    def isCheck(self, board):
        curr_x = self.x
        curr_y = self.y
        for row in board:
            for piece in row:
                if piece != "." and piece.color != self.color:
                    if (curr_x, curr_y) in piece.validMoves(board):
                        return True
        return False

    def causesCheck(self, new_x, new_y, board):
        curr_x = self.x
        curr_y = self.y
        curr_piece = board[new_y][new_x]
        board[new_y][new_x] = self
        board[curr_y][curr_x] = "."
        self.x = new_x
        self.y = new_y
        is_check = self.isCheck(board)
        self.x = curr_x
        self.y = curr_y
        board[new_y][new_x] = curr_piece
        board[curr_y][curr_x] = self
        return is_check

    def validMoves(self, board):
        valid_moves = []
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        curr_x = self.x
        curr_y = self.y

        for d_x, d_y in directions:
            new_x = curr_x + d_x
            new_y = curr_y + d_y

            if 0 <= new_x < 8 and 0 <= new_y < 8:
                if (self.isSquareEmpty(new_x, new_y, board) or self.isSquareEnemyPiece(new_x, new_y, board)) and not self.causesCheck(new_x, new_y, board):
                    valid_moves.append((new_x, new_y))
        return valid_moves
