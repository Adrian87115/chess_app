import torch
import random
import numpy as np
from collections import deque
import game as g
import model as m

MAX_MEMORY_SIZE = 1000000
BATCH_SIZE = 10000
LEARNING_RATE = 0.1

class Agent1:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.95
        self.memory = deque(maxlen=MAX_MEMORY_SIZE)
        self.model = m.DQN(64, 256, 1)
        # self.loadModel("model/model_white.pth")
        self.trainer = m.QTrainer(self.model, LEARNING_RATE, self.gamma, self.epsilon)

    def loadModel(self, model_path):
        state_dict = torch.load(model_path)
        self.model.load_state_dict(state_dict)
        self.model.eval()

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
                        valid_moves = piece.validMoves(state.board, 1)
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

def convertMoveTo1D(start_row, start_col, end_row, end_col):
    start_1D = start_row * 8 + start_col
    end_1D = end_row * 8 + end_col
    move_1D = end_1D - start_1D
    return move_1D

def train():
    agent_white = Agent1()
    agent_black = Agent1()
    game = g.Game()
    record_white = -500
    record_black = -500
    score_game_white = 0
    score_game_black = 0
    current_turn = "white"
    plot_scores_white = []
    plot_mean_scores_white = []
    total_score_white = 0
    plot_scores_black = []
    plot_mean_scores_black = []
    total_score_black = 0
    n_games = 0
    n_turns = 0

    while True:
        if current_turn == "white":
            agent = agent_white
            opponent = agent_black
        else:
            agent = agent_black
            opponent = agent_white
        state_old = agent.getState(game.board)
        piece, move = agent.getAction(game.board, current_turn)
        reward, done, score = game.playStep(piece, move)
        if game.board.isStalemate("white") or game.board.isStalemate("black") or game.board.isInsufficientMaterial():
            reward -= 10
            score -= 10
        n_turns += 1
        if n_turns >= 350:
            print("Pointless match")
            done = True
            reward -= 100
            score -= 100
        if current_turn == "white":
            score_game_white += score
            score_game_black -= abs(score)
        else:
            score_game_black += score
            score_game_white -= abs(score)
        state_new = agent.getState(game.board)
        move = convertMoveTo1D(piece.x, piece.y, move[0], move[1])
        agent.trainShortMemory(state_old, move, reward, state_new, done)
        agent.remember(state_old, move, reward, state_new, done)
        opponent.trainShortMemory(state_old, move, -(abs(reward)), state_new, done)
        opponent.remember(state_old, move, -(abs(reward)), state_new, done)
        if done:
            n_games += 1
            agent.n_games = n_games
            agent.trainer.increment_game_count()
            agent.trainer.update_learning_rate()
            if n_turns >= 350:
                winner = "None"
            else:
                winner = game.board.findWinner()
            game.resetGame()
            agent_white.trainLongMemory()
            agent_black.trainLongMemory()
            if score_game_black > record_black:
                record_black = score_game_black
            if score_game_white > record_white:
                record_white = score_game_white
            if score_game_black > 250:
                agent_black.model.saveModel("model_black.pth")
            if score_game_white > 250:
                agent_white.model.saveModel("model_white.pth")
            print("Game ", agent.n_games, ", Score white ", score_game_white, ", Score black ", score_game_black, ", Winner: ", winner, ", Record white: ", record_white, ", Record black: ", record_black)
            plot_scores_white.append(score_game_white)
            total_score_white += score_game_white
            mean_score_white = total_score_white / agent.n_games
            plot_mean_scores_white.append(mean_score_white)
            plot_scores_black.append(score_game_black)
            total_score_black += score_game_black
            mean_score_black = total_score_black / agent.n_games
            plot_mean_scores_black.append(mean_score_black)
            m.plot(plot_scores_white, plot_mean_scores_white, plot_scores_black, plot_mean_scores_black)
            current_turn = "white"
            score_game_white = 0
            score_game_black = 0
            n_turns = 0
        current_turn = "black" if current_turn == "white" else "white"

def test():
    agent_white = Agent1()
    agent_black = Agent1()
    game = g.Game()
    record_white = -500
    record_black = -500
    score_game_white = 0
    score_game_black = 0
    current_turn = "white"
    plot_scores_white = []
    plot_mean_scores_white = []
    total_score_white = 0
    plot_scores_black = []
    plot_mean_scores_black = []
    total_score_black = 0
    n_games = 0
    n_turns = 0

    while True:
        if current_turn == "white":
            agent = agent_white
        else:
            agent = agent_black
        if current_turn == "white":
            piece, move = agent.getAction(game.board, current_turn)
        else:
            piece, move = agent.getRandomMove(game.board, current_turn)
        reward, done, score = game.playStep(piece, move)
        if game.board.isStalemate("white") or game.board.isStalemate("black") or game.board.isInsufficientMaterial():
            reward -= 10
            score -= 10
        n_turns += 1
        if n_turns >= 350:
            print("Pointless match")
            done = True
            reward -= 100
            score -= 100
        if current_turn == "white":
            score_game_white += score
            score_game_black -= abs(score)
        else:
            score_game_black += score
            score_game_white -= abs(score)
        if done:
            n_games += 1
            if n_turns >= 350:
                winner = "None"
            else:
                winner = game.board.findWinner()
            game.resetGame()
            if score_game_black > record_black:
                record_black = score_game_black
            if score_game_white > record_white:
                record_white = score_game_white
            print("Game ", n_games, ", Score white ", score_game_white, ", Score black ", score_game_black,
                  ", Winner: ", winner, ", Record white: ", record_white, ", Record black: ", record_black)
            plot_scores_white.append(score_game_white)
            total_score_white += score_game_white
            mean_score_white = total_score_white / n_games
            plot_mean_scores_white.append(mean_score_white)
            plot_scores_black.append(score_game_black)
            total_score_black += score_game_black
            mean_score_black = total_score_black / n_games
            plot_mean_scores_black.append(mean_score_black)
            m.plot(plot_scores_white, plot_mean_scores_white, plot_scores_black, plot_mean_scores_black)
            current_turn = "white"
            score_game_white = 0
            score_game_black = 0
            n_turns = 0
        current_turn = "black" if current_turn == "white" else "white"

class MinimaxAgent:
    def __init__(self, depth = 3):
        self.depth = depth
        self.piece_values = {"P": 1, "p": -1, "R": 5, "r": -5, "Kn": 3, "kn": -3, "B": 3, "b": -3, "Q": 9, "q": -9, "Ki": 100, "ki": -100}

    def evaluate(self, board):
        score = 0
        for row in board.getBoard():
            for piece in row:
                if piece != ".":
                    score += self.piece_values.get(piece.shape, 0)
        return score

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0 or board.isGameOver():
            return self.evaluate(board), None
        valid_moves = self.getAllValidMoves(board, "white" if maximizing_player else "black")
        best_move = None
        if maximizing_player:
            max_eval = float('-inf')
            for piece, move in valid_moves:
                new_board = board.simulateMoveObject(piece, move)
                evaluation, _ = self.minimax(new_board, depth - 1, alpha, beta, False)
                if evaluation > max_eval:
                    max_eval = evaluation
                    best_move = (piece, move)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for piece, move in valid_moves:
                new_board = board.simulateMoveObject(piece, move)
                evaluation, _ = self.minimax(new_board, depth - 1, alpha, beta, True)
                if evaluation < min_eval:
                    min_eval = evaluation
                    best_move = (piece, move)
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def getAllValidMoves(self, board, current_turn):
        moves = []
        for row in board.getBoard():
            for piece in row:
                if piece != "." and piece.color == current_turn:
                    valid_moves = piece.validMoves(board.getBoard(), 1)
                    for move in valid_moves:
                        moves.append((piece, move))
        return moves

    def getAction(self, board, current_turn):
        _, best_move = self.minimax(board, self.depth, float('-inf'), float('inf'), current_turn == "white")
        return best_move if best_move else self.getRandomMove(board, current_turn)

    def getRandomMove(self, board, current_turn):
        valid_moves = self.getAllValidMoves(board, current_turn)
        return random.choice(valid_moves) if valid_moves else None
