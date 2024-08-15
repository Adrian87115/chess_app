import pieces as p
import copy

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

        # self.board = [
        #     [".", p.Queen(1, 0, "black"), ".", p.Knight(3, 0, "black"), ".", p.Pawn(5, 0, "white"), ".", "."],
        #     [".", ".", ".", ".", ".", ".", ".", "."],
        #     [".", ".", p.Knight(2, 2, "black"), p.Rook(3, 2, "black"), ".", ".", p.King(6, 2, "black"), "."],
        #     [".", p.Bishop(1, 3, "black"), ".", ".", ".", ".", ".", "."],
        #     [p.Rook(0, 4, "black"), ".", ".", ".", ".", ".", ".", "."],
        #     [".", p.King(1, 5, "white"), ".", ".", p.Bishop(4, 5, "white"), ".", ".", p.Pawn(7, 5, "white")],
        #     [".", ".", ".", ".", ".", ".", ".", p.Pawn(7, 6, "white")],
        #     [".", ".", p.Rook(2, 7, "white"), ".", p.Rook(4, 7, "white"), ".", ".", "."]
        # ]

    def displayBoard(self):
        for row in self.board:
            row_display = ""
            for piece in row:
                if piece == ".":
                    row_display += ". "
                else:
                    row_display += piece.shape + " "
            print(row_display.strip())


    def getFigure(self, x, y):
        return self.board[x][y]

    def isKingInCheck(self, color):
        king_pos = self.getKingPosition(color)
        if not king_pos:
            return False
        king_x, king_y = king_pos

        for row in self.board:
            for piece in row:
                if piece != "." and piece.color != color:
                    if (king_x, king_y) in piece.validMoves(self.board, 1):
                        return True
        return False

    def getKing(self, color):
        for y in range(8):
            for x in range(8):
                piece = self.board[y][x]
                if isinstance(piece, p.King) and piece.color == color:
                    return piece

    def getKingPosition(self, color):
        king = self.getKing(color)
        return king.x, king.y

    def validMovesWhenCheck(self, color):
        king_position = self.getKingPosition(color)
        if not king_position:
            return []
        king_x, king_y = king_position
        king = self.board[king_y][king_x]
        ally_moves = king.getAllAllyMoves(self.board)
        valid_moves = []

        for piece, moves in ally_moves.items():
            original_x, original_y = piece.x, piece.y
            for move in moves:
                target_x, target_y = move
                target_piece = self.board[target_y][target_x]
                self.board[target_y][target_x] = piece
                self.board[original_y][original_x] = "."
                piece.x, piece.y = target_x, target_y
                if not self.isKingInCheck(color):
                    valid_moves.append((piece, move))
                piece.x, piece.y = original_x, original_y
                self.board[original_y][original_x] = piece
                self.board[target_y][target_x] = target_piece

        return valid_moves

    def validMovesForAllPieces(self, color):
        valid_moves_by_piece = {}
        for row in self.board:
            for piece in row:
                if piece != "." and piece.color == color:
                    potential_moves = piece.validMoves(self.board, 1)
                    valid_moves = []
                    for move in potential_moves:
                        target_x, target_y = move
                        original_piece = self.board[target_y][target_x]
                        self.board[target_y][target_x] = piece
                        self.board[piece.y][piece.x] = "."
                        piece.x, piece.y = target_x, target_y
                        if not self.isKingInCheck(color):
                            valid_moves.append(move)
                        piece.x, piece.y = piece.y, piece.x
                        self.board[piece.y][piece.x] = piece
                        self.board[target_y][target_x] = original_piece
                    if valid_moves:
                        valid_moves_by_piece[piece] = valid_moves

        return valid_moves_by_piece

    def isCheckmate(self, color):
        if not self.isCheck(color):
            return False
        valid_moves = self.validMovesWhenCheck(color)
        return len(valid_moves) == 0

    def findWinner(self):
        if self.isCheckmate("black"):
            return "white"
        elif self.isCheckmate("white"):
            return "black"
        else:
            return "draw"

    def isStalemate(self, color):
        if self.isKingInCheck(color):
            return False
        for y in range(8):
            for x in range(8):
                piece = self.board[y][x]
                if piece != "." and piece.color == color:
                    if piece.validMoves(self.board, 1):
                        return False
        return True

    def isInsufficientMaterial(self):
        pieces = []
        for row in self.board:
            for piece in row:
                if piece != ".":
                    pieces.append(piece)
        if len(pieces) == 2:
            return True
        elif len(pieces) == 3:
            piece_shapes = [piece.shape.lower() for piece in pieces]
            if "ki" in piece_shapes and ("bi" in piece_shapes or "kn" in piece_shapes):
                return True
        elif len(pieces) == 4:
            bishops = [piece for piece in pieces if piece.shape.lower() == "bi"]
            if len(bishops) == 2 and (bishops[0].color == bishops[1].color):
                return True
        return False

    def isCheck(self, current_turn):
        for row in self.board:
            for piece in row:
                if piece != "." and piece.shape.title() == "Ki" and piece.color == current_turn:
                    return piece.isCheck(self.board)
        return False

    def canPromote(self):
        for row in self.board:
            for piece in row:
                if isinstance(piece, p.Pawn) and (piece.y == 0 or piece.y == 7):
                    return True
        return False

    def promote(self, piece, new_piece):
        new_piece.x = piece.x
        new_piece.y = piece.y
        new_piece.color = new_piece
        self.board[piece.y][piece.x] = new_piece

    def getBoard(self):
        return self.board

    def copyBoard(self):
        return self.board

    def simulateMove(self, piece, move):
        new_board = self.board
        current_x, current_y = piece.x, piece.y
        target_x, target_y = move
        self.board[target_y][target_x] = piece
        self.board[current_y][current_x] = "."
        piece.x, piece.y = target_x, target_y
        return new_board

    def simulateMoveObject(self, piece, move):
        new_board = copy.deepcopy(self)
        new_piece = copy.deepcopy(piece)
        current_x, current_y = piece.x, piece.y
        target_x, target_y = move
        new_board.board[target_y][target_x] = new_piece
        new_board.board[current_y][current_x] = "."
        new_piece.x, new_piece.y = target_x, target_y
        return new_board