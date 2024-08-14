import torch
import random
import numpy as np
from collections import deque
import game as g
import pieces as p
from model import DQN, QTrainer

MAX_MEMORY_SIZE = 100000
BATCH_SIZE = 1000
LEARNING_RATE = 0.001

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0
        self.memory = deque(maxlen=MAX_MEMORY_SIZE)
        self.model = DQN(64, 256, 1)  # Adjust input size based on board representation
        self.trainer = QTrainer(self.model, LEARNING_RATE, self.gamma, self.epsilon)

    def getState(self, board):
        return self.boardToArray(board)

    def boardToArray(self, board):
        piece_to_int = {".": 0,
                        "P": 1, "p": -1,
                        "R": 2, "r": -2,
                        "Kn": 3, "kn": -3,
                        "B": 4, "b": -4,
                        "Q": 5, "q": -5,
                        "Ki": 6, "ki": -6}
        board_array = np.zeros((8, 8), dtype=np.float32)
        for i, row in enumerate(board.getBoard()):
            for j, piece in enumerate(row):
                if piece != ".":
                    board_array[i, j] = piece_to_int[piece.shape]
        return board_array.flatten()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def trainShortMemory(self, state, action, reward, next_state, done):
        self.trainer.trainStep(state, action, reward, next_state, done)

    def trainLongMemory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.trainStep(states, actions, rewards, next_states, dones)

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

    def getAction(self, state, current_turn):
        self.epsilon = max(10, 80 - self.n_games)
        pieces_to_move = dict()
        if state.isKingInCheck(current_turn):
            valid_moves = state.validMovesWhenCheck(current_turn)
            pieces_to_move = {piece: [move for p, move in valid_moves if p == piece] for piece, move in valid_moves}
        else:
            for row in state.getBoard():
                for piece in row:
                    if piece != "." and piece.color == current_turn:
                        valid_moves = piece.validMoves(state.getBoard(), 1)
                        if valid_moves:
                            pieces_to_move[piece] = valid_moves
        final_piece = None
        final_move = None

        if random.randint(0, 100) < self.epsilon:
            final_piece = random.choice(list(pieces_to_move.keys()))
            final_move = random.choice(pieces_to_move[final_piece])
        else:
            best_score = float('-inf')
            for piece, moves in pieces_to_move.items():
                for move in moves:
                    new_state = state.simulateMoveObject(piece, move)
                    new_state_board = self.boardToArray(new_state)
                    state_tensor = torch.tensor(new_state_board, dtype = torch.float32).unsqueeze(0)

                    with torch.no_grad():
                        prediction = self.model(state_tensor)

                    score = prediction.item()
                    if score > best_score:
                        best_score = score
                        final_piece = piece
                        final_move = move
        return final_piece, final_move

def train():
    agent = Agent()
    game = g.Game()
    record = 0
    score_game = 0
    current_turn = "white"
    while True:

        state_old = agent.getState(game.board)
        piece, move = agent.getAction(game.board, current_turn)
        reward, done, score = game.playStep(piece, move)
        score_game += score
        state_new = agent.getState(game.board)
        agent.trainShortMemory(state_old, move, reward, state_new, done)
        agent.remember(state_old, move, reward, state_new, done)

        if done:
            game.resetGame()
            agent.n_games += 1
            agent.trainLongMemory()

            if score_game > record:
                record = score_game
                agent.model.saveModel()

            print("Game ", agent.n_games, "Score ", score_game, "record: ", record)
            current_turn = "white"
            score_game = 0
        current_turn = "black" if current_turn == "white" else "white"