import numpy as np
from bandit.base_bandit import Bandit


class EGreedyBandit(Bandit):
    def __init__(self, eps, arms):
        super().__init__(arms)
        self.eps = eps

    def pull(self):
        # select arm based on e-greedy rule: if random value is less than p, use random arm, else, use best arm so far
        p = np.random.random()

        if p < self.eps or self.n == 0 or self.eps == 0:
            an = np.random.randint(0, self.narms)
        else:
            an = np.argmax(self.narms_rmean)

        return an

    def update(self, arm_selected: int, reward: float):
        # update average reward vector for bandit and arm selected
        self.reward.append(self.reward[-1] + ((reward - self.reward[-1]) / self.n))
        self.narms_rmean[arm_selected] = self.narms_rmean[arm_selected] + ((reward - self.narms_rmean[arm_selected]) / self.narms_n[arm_selected])

        # increase counters n of bandit and of arm selected
        self.n = self.n + 1
        self.narms_n[arm_selected] = self.narms_n[arm_selected] + 1