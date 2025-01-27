import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as f
import os
import matplotlib.pyplot as plt
import numpy as np

# Deep Q Learning agent
class DQN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.norm1 = nn.LayerNorm(hidden_size)
        self.dropout1 = nn.Dropout(p=0.3)
        self.linear2 = nn.Linear(hidden_size, hidden_size)
        self.norm2 = nn.LayerNorm(hidden_size)
        self.dropout2 = nn.Dropout(p=0.3)
        self.residual_linear = nn.Linear(hidden_size, hidden_size)
        self.linear3 = nn.Linear(hidden_size, hidden_size)
        self.norm3 = nn.LayerNorm(hidden_size)
        self.dropout3 = nn.Dropout(p=0.3)
        self.linear4 = nn.Linear(hidden_size, hidden_size)
        self.norm4 = nn.LayerNorm(hidden_size)
        self.dropout4 = nn.Dropout(p=0.3)
        self.output_layer = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = f.relu(self.norm1(self.linear1(x)))
        x = self.dropout1(x)
        x2 = f.relu(self.norm2(self.linear2(x)))
        x2 = self.dropout2(x2)
        res = self.residual_linear(x)
        x2 += res
        x3 = f.relu(self.norm3(self.linear3(x2)))
        x3 = self.dropout3(x3)
        x4 = f.relu(self.norm4(self.linear4(x3)))
        x4 = self.dropout4(x4)
        output = self.output_layer(x4)
        return output

    def saveModel(self, file_name = "model.pth"):
        model_folder = "model"
        if not os.path.exists(model_folder):
            os.makedirs(model_folder)
        file_name = os.path.join(model_folder, file_name)
        torch.save(self.state_dict(), file_name)

class QTrainer:
    def __init__(self, model, lr, gamma, epsilon):
        self.model = model
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.optimizer = optim.Adam(self.model.parameters(), lr = self.lr)
        self.criterion = nn.SmoothL1Loss()
        self.game_count = 0

    def update_learning_rate(self):
        if self.game_count in [50, 100, 150]:
            self.lr *= 0.1
            for param_group in self.optimizer.param_groups:
                param_group['lr'] = self.lr

    def trainStep(self, state, action, reward, next_state, done):
        state = torch.tensor(np.array(state), dtype=torch.float32)
        next_state = torch.tensor(np.array(next_state), dtype=torch.float32)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float32)
        done = torch.tensor(done, dtype=torch.bool)
        if len(state.shape) == 1:
            state = state.unsqueeze(0)
            next_state = next_state.unsqueeze(0)
            action = action.unsqueeze(0)
            reward = reward.unsqueeze(0)
            done = done.unsqueeze(0)
        pred = self.model(state)
        target = pred.clone()

        with torch.no_grad():
            next_q_values = self.model(next_state).max(dim=1)[0]

        for i in range(len(done)):
            q_new = reward[i]
            if not done[i]:
                q_new += self.gamma * next_q_values[i]
            if action[i].dim() > 0 and action[i].numel() > 1:
                action_index = torch.argmax(action[i]).item()
            else:
                action_index = action[i].item()
            if action_index < target.shape[1]:
                target[i][action_index] = q_new
        self.optimizer.zero_grad()
        loss = self.criterion(pred, target)
        loss.backward()
        self.optimizer.step()

    def increment_game_count(self):
        self.game_count += 1

def plot(scores_white, mean_scores_white, scores_black, mean_scores_black):
    plt.clf()
    plt.title('Training')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(scores_white, 'r-', label = 'Scores White')
    plt.plot(mean_scores_white, 'r--', label = 'Mean Scores White')
    plt.plot(scores_black, 'b-', label = 'Scores Black')
    plt.plot(mean_scores_black, 'b--', label = 'Mean Scores Black')
    plt.legend()
    plt.xlim(xmin = 0)
    plt.text(len(scores_white) - 1, scores_white[-1], str(scores_white[-1]), color = 'red')
    plt.text(len(mean_scores_white) - 1, mean_scores_white[-1], str(mean_scores_white[-1]), color = 'red')
    plt.text(len(scores_black) - 1, scores_black[-1], str(scores_black[-1]), color = 'blue')
    plt.text(len(mean_scores_black) - 1, mean_scores_black[-1], str(mean_scores_black[-1]), color = 'blue')
    plt.show(block=False)
    plt.pause(0.1)