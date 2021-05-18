import numpy as np
import matplotlib.pyplot as plt


class Bandit():
    def __init__(self, arms: int):
        """
        Base bandit constructor
        :param amrs: probability distribution of each arm
        """
        # quantity of arms
        self.narms = arms
        # times each arm was used
        self.narms_n = np.ones(self.narms)
        # mean reward for each arm
        self.narms_rmean = np.zeros(self.narms)
        # total average reward on each step
        self.reward = [0]
        # n times that any arm was pulled
        self.n = 1

    def pull(self):
        """
        Function that pulls one arm
        """
        pass

    def update(self, arm_selected: int, reward: float):
        """
        Function that updates the total average reward of the bandit and arm average
        """
        pass

    def show_statistics(self):
        """
        Function that plots statistics of the arms
        :param name: subplot name
        :param color: color of the bars of the plots
        """
        print()
        for a in range(self.narms):
            print("ARM: " + str(a))
            print("\t Pulled " + str(self.narms_n[a] - 1) + " times")
            print("\t Average arm reward " + str(self.narms_rmean[a]))

        print("Final system reward = " + str(self.reward[-1]))

        plt.figure(figsize=(14, 8))
        plt.title("Rewards")
        plt.plot(self.reward, label="Rewards")
        plt.legend(bbox_to_anchor=(1.2, 0.5))
        plt.xlabel("Iterations")
        plt.ylabel("Average Reward")
        plt.show()