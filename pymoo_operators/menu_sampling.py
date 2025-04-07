import copy
import pandas as pd
import numpy as np
from pandas import DataFrame
from pymoo.core.sampling import Sampling #pymoo에서 유전 알고리즘 사용할 때 필요한 샘플링 클래스
# 목적: 최적화를 시작하기 위해 n개의 식단 개체 무작위 생성

from solution import Solution, Day

# 초기 식단 개체 생성
class MenuSampling(Sampling):

#n_samples개의 무작위 식단 생성
    def _do(self, problem, n_samples, **kwargs):
        X = np.full((n_samples, 1), None, dtype=object)

        for i in range(n_samples):
            X[i, 0] = self.generate_solution(problem)

        return X


    def generate_solution(self, problem):
        days = []

        for i in range(5):
            sampled_list = [
                problem.first_dish_type.sample(n=1, replace=True),   # 밥
                problem.second_dish_type.sample(n=1),                # 국
                problem.third_dish_type.sample(n=1),                 # 주찬
                problem.fourth_dish_type.sample(n=2),                # 부찬
                problem.fifth_dish_type.sample(n=1, replace=True)    # 김치
            ]

            dish_types = pd.concat(sampled_list, ignore_index=True)  # append → concat
            days += [Day(dish_types)]
            
        sol = Solution(days, fitness_functions=copy.deepcopy(problem.fitness_functions))
        print("[SAMPLE] 새 개체 생성됨:", sol)
        return sol
