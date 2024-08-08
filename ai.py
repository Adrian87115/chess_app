import app as a
import board as b
import pieces as p
import game as g
import random

class ChessAi:
    def __init__(self):
        self.q_table = {}
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.1

    def getRandomMove(self, board, current_turn):
        pieces_to_move = dict()

        if board.isKingInCheck(current_turn):
            valid_moves = board.validMovesWhenCheck(current_turn)
            pieces_to_move = {piece: [move for p, move in valid_moves if p == piece] for piece, move in valid_moves}
        else:
            for row in board.getBoard():
                for piece in row:
                    if piece != "." and piece.color == current_turn:
                        valid_moves = piece.validMoves(board.getBoard(), 1)
                        if valid_moves:
                            pieces_to_move[piece] = valid_moves

        if not pieces_to_move:
            return None
        random_piece = random.choice(list(pieces_to_move.keys()))
        random_move = random.choice(list(pieces_to_move[random_piece]))
        return random_piece, random_move

    def getBestMove(self, board, current_turn):
        state = self.boardToState(board)
        if state not in self.q_table:
            self.q_table[state] = {}

        pieces_to_move = dict()
        for row in board.getBoard():
            for piece in row:
                if piece != "." and piece.color == current_turn:
                    valid_moves = piece.validMoves(board.getBoard(), 1)
                    if valid_moves:
                        pieces_to_move[piece] = valid_moves

        if not pieces_to_move:
            return None

        best_move = None
        best_q_value = float('-inf')

        for piece, moves in pieces_to_move.items():
            for move in moves:
                new_state = self.boardToState(board.simulateMove(piece, move))
                q_value = self.q_table[state].get(new_state, 0)
                if q_value > best_q_value:
                    best_q_value = q_value
                    best_move = (piece, move)

        return best_move

    @staticmethod
    def boardToState(board):
        # Convert the board to a tuple of tuples to ensure immutability and hashability
        state = tuple(tuple(row) for row in board)
        return state

    def updateQValue(self, old_state, action, reward, new_state):
        old_state = self.boardToState(old_state)  # Ensure old_state is a tuple
        new_state = self.boardToState(new_state)  # Ensure new_state is a tuple

        old_q_value = self.q_table.get(old_state, {}).get(action, 0)
        future_q_value = max(self.q_table.get(new_state, {}).values(), default=0)
        new_q_value = old_q_value + self.alpha * (reward + self.gamma * future_q_value - old_q_value)

        if old_state not in self.q_table:
            self.q_table[old_state] = {}
        self.q_table[old_state][action] = new_q_value

    def getReward(self, board, current_turn):
        new_board = board.copy()
        selected_piece, selected_move = self.getBestMove(board, current_turn)
        reward = 0
        selected_tile = board.getBoard()[selected_move[1]][selected_move[0]]
        if selected_tile.title() == "P":
            reward += 1
        elif selected_tile.title() == "R":
            reward += 5
        elif selected_tile.title() == "B" or selected_tile.title() == "Kn":
            reward += 3
        elif selected_tile.title() == "Q":
            reward += 10
        new_board[selected_piece.y][selected_piece.x] = "."
        new_board[selected_move[1]][selected_move[0]] = selected_piece
        if new_board.isCheckmate(current_turn):
            return reward + 100
        else:
            return reward

