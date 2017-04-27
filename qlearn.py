# coding:utf-8

import random
import config as cfg


class QLearn:
    """
    Q-learning:
        Q(s, a) += alpha * (reward(s,a) + gamma * max(Q(s', a') - Q(s,a))

        * alpha is the learning rate.
        * gamma is the value of the future reward.
    It use the best next choice of utility in later state to update the former state.
    """
    def __init__(self, actions, alpha=cfg.alpha, gamma=cfg.gamma, epsilon=cfg.epsilon):
        self.q = {}
        self.alpha = alpha
        self.gamma = gamma
        self.actions = actions  # collection of choices
        self.epsilon = epsilon  # exploration constant

    # Get the utility of an action in certain state, default is 0.0.
    def get_utility(self, state, action):
        return self.q.get((state, action), 0.0)

    # When in certain state, find the best action while explore new grid by chance.
    def choose_action(self, state):
        if random.random < self.epsilon:
            action = random.choice(self.actions)
        else:
            q = [self.get_utility(state, act) for act in self.actions]
            max_utility = max(q)
            # In case there're several state-action max values
            # we select a random one among them
            if q.count(max_utility) > 1:
                best_actions = [self.actions[i] for i in xrange(len(self.actions)) if q[i] == max_utility]
                action = random.choice(best_actions)
            else:
                action = self.actions[q.index(max_utility)]
        return action

    # learn
    def learn(self, state1, action, state2, reward):
        old_utility = self.q.get((state1, action), None)
        if old_utility is None:
            self.q[(state1, action)] = reward

        # update utility
        else:
            next_max_utility = max([self.get_utility(state2, a) for a in self.actions])
            self.q[(state1, action)] = old_utility + self.alpha * (reward + self.gamma * next_max_utility - old_utility)
