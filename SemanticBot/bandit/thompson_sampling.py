import numpy as np
from bandit.base_bandit import Bandit


class ThompsonSamplingBandit(Bandit):
    def __init__(self, arms: int):
        super().__init__(arms)
        # alpha and beta parameters of beta distribution for each arm
        self.alpha = np.ones(self.narms)
        self.beta = np.ones(self.narms)

    def pull(self):
        # select arm based on ucb formula
        an = np.argmax([np.random.beta(self.alpha[i], self.beta[i]) for i in range(self.narms)])
        return an

    def update(self, arm_selected: int, reward: float):
        # update average reward vector for bandit and arm selected
        self.reward.append(self.reward[-1] + ((reward - self.reward[-1]) / self.n))
        self.narms_rmean[arm_selected] = self.narms_rmean[arm_selected] + ((reward - self.narms_rmean[arm_selected]) / self.narms_n[arm_selected])

        # update beta and alpha for chosen arm
        self.alpha[arm_selected] = self.alpha[arm_selected] + reward
        self.beta[arm_selected] = self.beta[arm_selected] + (1 - reward)

        # increase counters n of bandit and of arm selected
        self.n = self.n + 1
        self.narms_n[arm_selected] = self.narms_n[arm_selected] + 1