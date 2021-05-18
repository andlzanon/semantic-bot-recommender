import numpy as np
from bandit.base_bandit import Bandit


class UCBBandit(Bandit):
    def __init__(self, c: float, arms: int):
        """
        UCB Bandit constructor
        :param c: parameter of ucb formula
        """
        super().__init__(arms)
        # c parameter of ucb
        self.c = c

    def pull(self):
        # select arm based on ucb formula
        an = np.argmax(self.narms_rmean + self.c * (np.sqrt(np.log(self.n) / self.narms_n)))
        return an

    def update(self, arm_selected: int, reward: float):
        # update average reward vector for bandit and arm selected
        self.reward.append(self.reward[-1] + ((reward - self.reward[-1]) / self.n))
        self.narms_rmean[arm_selected] = self.narms_rmean[arm_selected] + ((reward - self.narms_rmean[arm_selected]) / self.narms_n[arm_selected])

        # increase counters n of bandit and of arm selected
        self.n = self.n + 1
        self.narms_n[arm_selected] = self.narms_n[arm_selected] + 1