import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as f
import os

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
            action_index = action[i].item()
            if action_index < target.shape[1]:
                target[i][action_index] = q_new
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()
        self.optimizer.step()