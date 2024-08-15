import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as f
import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Deep Q Learning agent
class DQN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = f.relu(self.linear1(x))
        x = self.linear2(x)
        return x

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
        self.criterion = nn.MSELoss()

    def trainStep(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype = torch.float32)
        next_state = torch.tensor(next_state, dtype = torch.float32)
        action = torch.tensor(action, dtype=torch.long).unsqueeze(1)
        reward = torch.tensor(reward, dtype=torch.float32)
        done = torch.tensor(done, dtype=torch.bool)

        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = torch.unsqueeze(done, 0)

        pred = self.model(state)
        target = pred.clone()

        for i in range(len(done)):
            q_new = reward[i]
            if not done[i]:
                q_new = reward[i] + self.gamma * torch.max(self.model(next_state[i]))
            action_index = action[i].item() if len(action[i].shape) == 0 else torch.argmax(action[i]).item()#action_index = action[i].item()
            if action_index < target.shape[1]:
                target[i][action_index] = q_new
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()
        self.optimizer.step()


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
