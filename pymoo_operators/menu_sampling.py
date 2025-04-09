import copy
import pandas as pd
import numpy as np
from pandas import DataFrame
from pymoo.core.sampling import Sampling #pymoo에서 유전 알고리즘 사용할 때 필요한 샘플링 클래스
# 목적: 최적화를 시작하기 위해 n개의 식단 개체 무작위 생성

from solution import Solution, Day

# 초기 식단 개체 생성
class MenuSampling(Sampling):

# #n_samples개의 무작위 식단 생성
#     def _do(self, problem, n_samples, **kwargs):
#         X = np.full((n_samples, 1), None, dtype=object)

#         for i in range(n_samples):
#             X[i, 0] = self.generate_solution(problem)

#         return X
    def _do(self, problem, n_samples, **kwargs):
            X = np.full((n_samples, 1), None, dtype=object)
            for i in range(n_samples):
                X[i, 0] = self.generate_solution(problem)
            return X
        
    def generate_solution(self, problem):
            max_attempts = 20
            for _ in range(max_attempts):
                days = []
                for i in range(5):
                    sampled_list = [
                        problem.first_dish_type.sample(n=1, replace=True),
                        problem.second_dish_type.sample(n=1),
                        problem.third_dish_type.sample(n=1),
                        problem.fourth_dish_type.sample(n=2),
                        problem.fifth_dish_type.sample(n=1, replace=True)
                    ]
                    dish_types = pd.concat(sampled_list, ignore_index=True)
                    days.append(Day(dish_types))
    
                sol = Solution(days, fitness_functions=copy.deepcopy(problem.fitness_functions))
                if self.is_within_nutrient_bounds(sol, problem.config.NUTRIENT_BOUNDS):
                    print("[SAMPLE ✅] 기준 만족 식단 생성됨")
                    return sol
                else:
                    print("[SAMPLE ❌] 기준 초과로 재생성")
    
            print("[SAMPLE ⚠️] 기준 초과 개체 반환")
            return sol

    def is_within_nutrient_bounds(self, sol, bounds):
        nutrient_index_map = {
            "kcal": constants.ENERGY_INDEX,
            "cho": constants.CHO_INDEX,
            "protein": constants.PROTEIN_INDEX,
            "fat": constants.FAT_INDEX
        }
        for nutrient, (min_val, max_val) in bounds.items():
            idx = nutrient_index_map[nutrient]
            total = sum([day.dish_types[idx].sum() for day in sol.days])
            if not (min_val * 5 <= total <= max_val * 5):
                return False
        return True

    # def generate_solution(self, problem):
    #     days = []

    #     for i in range(5):
    #         sampled_list = [
    #             problem.first_dish_type.sample(n=1, replace=True),   # 밥
    #             problem.second_dish_type.sample(n=1),                # 국
    #             problem.third_dish_type.sample(n=1),                 # 주찬
    #             problem.fourth_dish_type.sample(n=2),                # 부찬
    #             problem.fifth_dish_type.sample(n=1, replace=True)    # 김치
    #         ]

    #         dish_types = pd.concat(sampled_list, ignore_index=True)  # append → concat
    #         days += [Day(dish_types)]
            
    #     sol = Solution(days, fitness_functions=copy.deepcopy(problem.fitness_functions))
    #     print("[SAMPLE] 새 개체 생성됨:", sol)
    #     return sol
