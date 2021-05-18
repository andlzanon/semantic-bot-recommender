import numpy as np
from bandit.base_bandit import Bandit


class RandomBandit(Bandit):
    def __init__(self, arms):
        super().__init__(arms)

    def pull(self):
        # select arm randomly
        an = np.random.randint(0, self.narms)
        return an

    def update(self, arm_selected: int, reward: float):
        # update average reward vector for bandit and arm selected
        self.reward.append(self.reward[-1] + ((reward - self.reward[-1]) / self.n))
        self.narms_rmean[arm_selected] = self.narms_rmean[arm_selected] + ((reward - self.narms_rmean[arm_selected]) / self.narms_n[arm_selected])

        # increase counters n of bandit and of arm selected
        self.n = self.n + 1
        self.narms_n[arm_selected] = self.narms_n[arm_selected] + 1