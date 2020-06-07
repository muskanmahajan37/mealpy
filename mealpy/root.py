#!/usr/bin/env python
# ------------------------------------------------------------------------------------------------------%
# Created by "Thieu Nguyen" at 08:58, 16/03/2020                                                        %
#                                                                                                       %
#       Email:      nguyenthieu2102@gmail.com                                                           %
#       Homepage:   https://www.researchgate.net/profile/Thieu_Nguyen6                                  %
#       Github:     https://github.com/thieunguyen5991                                                  %
# -------------------------------------------------------------------------------------------------------%

from numpy import where, clip, logical_and, maximum, minimum, power, sin, abs, pi, sqrt, sign, ones, ptp, min, sum, array, ceil
from numpy.random import uniform, random, normal, choice
from math import gamma
from copy import deepcopy


class Root:
    """ This is root of all Algorithms """

    ID_MIN_PROB = 0  # min problem
    ID_MAX_PROB = -1  # max problem

    ID_POS = 0  # Position
    ID_FIT = 1  # Fitness

    EPSILON = 10E-10

    def __init__(self, obj_func=None, lb=None, ub=None, problem_size=50, batch_size=10, verbose=True):
        """
        Parameters
        ----------
        obj_func : function
        lb : list
        ub : list
        problem_size : int, optional
        batch_size: int, optional
        verbose : bool, optional
        """
        self.obj_func = obj_func
        if (lb is None) or (ub is None):
            if problem_size is None:
                print("Problem size must be an int number")
                exit(0)
            elif problem_size <=0:
                print("Problem size must > 0")
                exit(0)
            else:
                self.problem_size = int(ceil(problem_size))
                self.lb = -1 * ones(problem_size)
                self.ub = 1 * ones(problem_size)
        else:
            if isinstance(lb, list) and isinstance(ub, list) and not (problem_size is None):
                if (len(lb) == len(ub)) and (problem_size > 0):
                    if len(lb) == 1:
                        self.problem_size = problem_size
                        self.lb = lb[0] * ones(problem_size)
                        self.ub = ub[0] * ones(problem_size)
                    else:
                        self.problem_size = len(lb)
                        self.lb = array(lb)
                        self.ub = array(ub)
                else:
                    print("Lower bound and Upper bound need to be same length. Problem size must > 0")
                    exit(0)
            else:
                print("Lower bound and Upper bound need to be a list. Problem size is an int number")
                exit(0)
        self.batch_size = batch_size
        self.verbose = verbose
        self.epoch, self.pop_size = None, None
        self.solution, self.loss_train = None, []

    def create_solution(self, minmax=0):
        """ Return the position position with 2 element: position of position and fitness of position

        Parameters
        ----------
        minmax
            0 - minimum problem, else - maximum problem

        """
        position = uniform(self.lb, self.ub)
        fitness = self.get_fitness_position(position=position, minmax=minmax)
        return [position, fitness]

    def get_fitness_position(self, position=None, minmax=0):
        """     Assumption that objective function always return the original value
        :param position: 1-D numpy array
        :param minmax: 0- min problem, 1 - max problem
        :return:
        """
        return self.obj_func(position) if minmax == 0 else 1.0 / (self.obj_func(position) + self.EPSILON)

    def get_fitness_solution(self, solution=None, minmax=0):
        return self.get_fitness_position(solution[self.ID_POS], minmax)

    def get_global_best_solution(self, pop=None, id_fit=None, id_best=None):
        """ Sort a copy of population and return the copy of the best position """
        sorted_pop = sorted(pop, key=lambda temp: temp[id_fit])
        return deepcopy(sorted_pop[id_best])

    def get_sorted_pop_and_global_best_solution(self, pop=None, id_fit=None, id_best=None):
        """ Sort population and return the sorted population and the best position """
        sorted_pop = sorted(pop, key=lambda temp: temp[id_fit])
        return sorted_pop, deepcopy(sorted_pop[id_best])

    def amend_position(self, position=None):
        return maximum(self.lb, minimum(self.ub, position))

    def amend_position_faster(self, position=None):
        return clip(position, self.lb, self.ub)

    def amend_position_random(self, position=None):
        for t in range(self.problem_size):
            if position[t] < self.lb[t] or position[t] > self.ub[t]:
                position[t] = uniform(self.lb[t], self.ub[t])
        return position

    def amend_position_random_faster(self, position=None):
        return where(logical_and(self.lb <= position, position <= self.ub), position, uniform(self.lb, self.ub))

    def update_global_best_solution(self, pop=None, id_best=None, g_best=None):
        """ Sort the copy of population and update the current best position. Return the new current best position """
        sorted_pop = sorted(pop, key=lambda temp: temp[self.ID_FIT])
        current_best = sorted_pop[id_best]
        return deepcopy(current_best) if current_best[self.ID_FIT] < g_best[self.ID_FIT] else deepcopy(g_best)

    def update_sorted_population_and_global_best_solution(self, pop=None, id_best=None, g_best=None):
        """ Sort the population and update the current best position. Return the sorted population and the new current best position """
        sorted_pop = sorted(pop, key=lambda temp: temp[self.ID_FIT])
        current_best = sorted_pop[id_best]
        g_best = deepcopy(current_best) if current_best[self.ID_FIT] < g_best[self.ID_FIT] else deepcopy(g_best)
        return sorted_pop, g_best

    def create_opposition_position(self, position=None, g_best=None):
        return self.lb + self.ub - g_best[self.ID_POS] + uniform() * (g_best[self.ID_POS] - position)

    def levy_flight(self, epoch=None, position=None, g_best_position=None, step=0.001, case=0):
        """
        Parameters
        ----------
        epoch (int): current iteration
        position : 1-D numpy array
        g_best_position : 1-D numpy array
        step (float, optional): 0.001
        case (int, optional): 0, 1, 2

        """
        beta = 1
        # muy and v are two random variables which follow normal distribution
        # sigma_muy : standard deviation of muy
        sigma_muy = power(gamma(1 + beta) * sin(pi * beta / 2) / (gamma((1 + beta) / 2) * beta * power(2, (beta - 1) / 2)), 1 / beta)
        # sigma_v : standard deviation of v
        sigma_v = 1
        muy = normal(0, sigma_muy ** 2)
        v = normal(0, sigma_v ** 2)
        s = muy / power(abs(v), 1 / beta)
        LB = step * s * (position - g_best_position)
        levy = uniform(self.lb, self.ub) * LB

        if case == 0:
            return levy
        elif case == 1:
            return position + 1.0 / sqrt(epoch + 1) * sign(random() - 0.5) * levy
        elif case == 2:
            return position + 0.01 * levy

    def levy_flight_2(self, position=None, g_best_position=None):
        alpha = 0.01
        xichma_v = 1
        xichma_u = ((gamma(1 + 1.5) * sin(pi * 1.5 / 2)) / (gamma((1 + 1.5) / 2) * 1.5 * 2 ** ((1.5 - 1) / 2))) ** (1.0 / 1.5)
        levy_b = (normal(0, xichma_u ** 2)) / (sqrt(abs(normal(0, xichma_v ** 2))) ** (1.0 / 1.5))
        return position + alpha * levy_b * (position - g_best_position)

    def get_index_roulette_wheel_selection(self, list_fitness=None):
        """ It can handle negative also. Make sure your list fitness is 1D-numpy array"""
        scaled_fitness = (list_fitness - min(list_fitness)) / ptp(list_fitness)
        minimized_fitness = 1.0 - scaled_fitness
        total_sum = sum(minimized_fitness)
        r = uniform(low=0, high=total_sum)
        for idx, f in enumerate(minimized_fitness):
            r = r + f
            if r > total_sum:
                return idx

    def get_parent_kway_tournament_selection(self, pop=None, k_way=0.2, output=2):
        if 0 < k_way < 1:
            k_way = int(k_way * len(pop))
        list_id = choice(range(len(pop)), k_way, replace=False)
        list_parents = [pop[i] for i in list_id]
        list_parents = sorted(list_parents, key=lambda temp: temp[self.ID_FIT])
        return list_parents[:output]

    def train(self):
        pass
