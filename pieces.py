import board

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

    def validMoves(self, board, move_or_king): # move_or_king 1 - for piece movement, 0 - for checking kings possible moves
        pass

    def move(self, new_x, new_y, board):
        if (new_x, new_y) in self.validMoves(board, 1):
            board[self.y][self.x] = "."
            self.x = new_x
            self.y = new_y
            board[self.y][self.x] = self
            return True
        return False

    def threatensKing(self, king_x, king_y, board):
        pass

class Pawn(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.has_moved = False
        if color == "white":
            self.shape = "P"
        else:
            self.shape = "p"

    def validMoves(self, board, move_or_king):
        direction = -1 if self.color == "white" else 1  # 1 - up, -1 down
        valid_moves = []
        curr_x = self.x
        curr_y = self.y

        if not self.has_moved:
            new_x = curr_x
            new_y = curr_y + 2 * direction
            # ahead 2
            if self.isSquareEmpty(new_x, new_y, board) and self.isSquareEmpty(new_x, curr_y + direction, board):
                if not simulateMoveAndCheck(self, (new_x, new_y), board):
                    valid_moves.append((new_x, new_y))

        new_x = curr_x
        new_y = curr_y + direction
        # ahead 1
        if self.isSquareEmpty(new_x, new_y, board):
            if not simulateMoveAndCheck(self, (new_x, new_y), board):
                valid_moves.append((new_x, new_y))

        # capture left
        new_x = curr_x - 1
        new_y = curr_y + direction
        if self.isSquareEnemyPiece(new_x, new_y, board):
            if not simulateMoveAndCheck(self, (new_x, new_y), board):
                valid_moves.append((new_x, new_y))

        # capture right
        new_x = curr_x + 1
        new_y = curr_y + direction
        if self.isSquareEnemyPiece(new_x, new_y, board):
            if not simulateMoveAndCheck(self, (new_x, new_y), board):
                valid_moves.append((new_x, new_y))

        return valid_moves

    def move(self, new_x, new_y, board):
        if (new_x, new_y) in self.validMoves(board, 1):
            board[self.y][self.x] = "."
            self.x = new_x
            self.y = new_y
            board[self.y][self.x] = self
            self.has_moved = True
            return True
        return False

    def threatensKing(self, king_x, king_y, board):
        if self.color == "white":
            moves = [(self.x + 1, self.y - 1), (self.x - 1, self.y - 1)]
        else:
            moves = [(self.x + 1, self.y + 1), (self.x - 1, self.y + 1)]
        return moves

class Rook(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        if color == "white":
            self.shape = "R"
        else:
            self.shape = "r"

    def validMoves(self, board, move_or_king):
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
                    if not move_or_king or not simulateMoveAndCheck(self, (new_x, new_y), board):
                        valid_moves.append((new_x, new_y))
                    new_x += d_x
                    new_y += d_y
                elif self.isSquareEnemyPiece(new_x, new_y, board):
                    if not move_or_king or not simulateMoveAndCheck(self, (new_x, new_y), board):
                        valid_moves.append((new_x, new_y))
                    break
                else:
                    if not move_or_king:
                        valid_moves.append((new_x, new_y))
                    break

        return valid_moves

    def threatensKing(self, king_x, king_y, board):
        moves = []

        dx = abs(self.x - king_x)
        dy = abs(self.y - king_y)

        if not (dx <= 2 or dy <= 2):
            return moves

        moves = self.validMoves(board, 0)

        if self.x == king_x:
            if self.y < king_y:
                moves.append((king_x, king_y + 1))
            else:
                moves.append((king_x, king_y - 1))
        elif self.y == king_y:
            if self.x < king_x:
                moves.append((king_x + 1, king_y))
            else:
                moves.append((king_x - 1, king_y))
        return moves

class Knight(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        if color == "white":
            self.shape = "Kn"
        else:
            self.shape = "kn"

    def validMoves(self, board, move_or_king):
        valid_moves = []
        directions = [(-1, -2), (-1, 2), (1, -2), (1, 2), (-2, -1), (-2, 1), (2, -1), (2, 1)]
        curr_x = self.x
        curr_y = self.y

        for direction in directions:
            d_x, d_y = direction
            new_x = curr_x + d_x
            new_y = curr_y + d_y

            if 0 <= new_x < 8 and 0 <= new_y < 8:
                if move_or_king:
                    if self.isSquareEmpty(new_x, new_y, board) or self.isSquareEnemyPiece(new_x, new_y, board):
                        if not simulateMoveAndCheck(self, (new_x, new_y), board):
                            valid_moves.append((new_x, new_y))
                else:
                    valid_moves.append((new_x, new_y))

        return valid_moves

    def threatensKing(self, king_x, king_y, board):
        moves = self.validMoves(board, 0)
        return moves

class Bishop(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        if color == "white":
            self.shape = "B"
        else:
            self.shape = "b"

    def validMoves(self, board, move_or_king):
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
                    if move_or_king:
                        if not simulateMoveAndCheck(self, (new_x, new_y), board):
                            valid_moves.append((new_x, new_y))
                    else:
                        valid_moves.append((new_x, new_y))
                    new_x += d_x
                    new_y += d_y
                elif self.isSquareEnemyPiece(new_x, new_y, board):
                    if move_or_king:
                        if not simulateMoveAndCheck(self, (new_x, new_y), board):
                            valid_moves.append((new_x, new_y))
                    else:
                        valid_moves.append((new_x, new_y))
                    break
                else:
                    break
        return valid_moves

    def threatensKing(self, king_x, king_y, board):
        moves = []

        dx = abs(self.x - king_x)
        dy = abs(self.y - king_y)

        if not (dx - dy <= 2):
            return moves

        moves = self.validMoves(board, 0)

        if dx == dy:
            d_x = 1 if self.x < king_x else -1
            d_y = 1 if self.y < king_y else -1
            next_x = king_x + d_x
            next_y = king_y + d_y
            moves.append((next_x, next_y))

        return moves

class Queen(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        if color == "white":
            self.shape = "Q"
        else:
            self.shape = "q"

    def validMoves(self, board, move_or_king):
        valid_moves = []
        curr_x = self.x
        curr_y = self.y
        directions_perpendicular = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        directions_diagonal = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for direction in directions_perpendicular + directions_diagonal:
            d_x, d_y = direction
            new_x = curr_x + d_x
            new_y = curr_y + d_y

            while 0 <= new_x < 8 and 0 <= new_y < 8:
                if self.isSquareEmpty(new_x, new_y, board):
                    if move_or_king:
                        if not simulateMoveAndCheck(self, (new_x, new_y), board):
                            valid_moves.append((new_x, new_y))
                    else:
                        valid_moves.append((new_x, new_y))
                    new_x += d_x
                    new_y += d_y
                elif self.isSquareEnemyPiece(new_x, new_y, board):
                    if move_or_king:
                        if not simulateMoveAndCheck(self, (new_x, new_y), board):
                            valid_moves.append((new_x, new_y))
                    else:
                        valid_moves.append((new_x, new_y))
                    break
                else:
                    break
        return valid_moves
    def threatensKing(self, king_x, king_y, board):
        moves = []

        dx = abs(self.x - king_x)
        dy = abs(self.y - king_y)

        if not ((dx <= 2 or dy <= 2) or dx - dy <= 2):
            return moves

        moves = self.validMoves(board, 0)

        if dx == dy:
            d_x = 1 if self.x < king_x else -1
            d_y = 1 if self.y < king_y else -1
            next_x = king_x + d_x
            next_y = king_y + d_y
            moves.append((next_x, next_y))

        if self.x == king_x:
            if self.y < king_y:
                moves.append((king_x, king_y + 1))
            else:
                moves.append((king_x, king_y - 1))
        elif self.y == king_y:
            if self.x < king_x:
                moves.append((king_x + 1, king_y))
            else:
                moves.append((king_x - 1, king_y))

        return moves

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
                    threatened_positions = piece.threatensKing(self.x, self.y, board)
                    for move in threatened_positions:
                        move_x, move_y = move
                        if 0 <= move_x <= 7 and 0 <= move_y <= 7:
                            enemy_moves.add(move)
        return enemy_moves

    def getAllAllyMoves(self, board):
        ally_moves = dict()
        for row in board:
            for piece in row:
                if piece != "." and piece.color == self.color:
                    ally_moves[piece] = piece.validMoves(board, 1)
        return ally_moves

    def threatensKing(self, king_x, king_y, board):
        moves = []
        dx = abs(self.x - king_x)
        dy = abs(self.y - king_y)
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        if not (dx <= 2 and dy <= 2):
            return moves

        for d_x, d_y in directions:
            new_x, new_y = self.x + d_x, self.y + d_y
            if 0 <= new_x < 8 and 0 <= new_y < 8:
                moves.append((new_x, new_y))

        return moves

    def validMoves(self, board, move_or_king):
        valid_moves = []
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        curr_x = self.x
        curr_y = self.y
        invalid_moves = self.getAllEnemyMoves(board)
        for d_x, d_y in directions:
            new_x = curr_x + d_x
            new_y = curr_y + d_y
            if 0 <= new_x < 8 and 0 <= new_y < 8:
                if (new_x, new_y) not in invalid_moves and (
                        self.isSquareEnemyPiece(new_x, new_y, board) or self.isSquareEmpty(new_x, new_y, board)):
                    valid_moves.append((new_x, new_y))

        return valid_moves

    def isCheck(self, board):
        king_x, king_y = self.x, self.y
        enemy_moves = self.getAllEnemyMoves(board)
        return (king_x, king_y) in enemy_moves

def simulateMoveAndCheck(piece, move, board):
    new_board = [row.copy() for row in board]
    curr_x, curr_y = piece.getPosition()
    new_x, new_y = move
    new_board[curr_y][curr_x] = "."
    new_board[new_y][new_x] = piece
    piece.x, piece.y = new_x, new_y
    king = next(p for row in new_board for p in row if isinstance(p, King) and p.color == piece.color)
    result = king.isCheck(new_board)
    piece.x, piece.y = curr_x, curr_y
    new_board[curr_y][curr_x] = piece
    new_board[new_y][new_x] = "."
    return result