import numpy as np
import constants
from fitnesses.abstract_fitness import AbstractFitness

# class NutrientFitness(AbstractFitness):
#     def __init__(self, nutrient_bounds):
#         # nutrient_bounds = {"kcal": (min, max), ...}
#         self.targets = {
#             key: np.mean(val)
#             for key, val in nutrient_bounds.items()
#         }
class NutrientFitness(AbstractFitness):
    def __init__(self, nutrient_bounds, strict=False):
        self.bounds = nutrient_bounds
        self.strict = strict

    def calculate_difference(self, current, bounds):
        min_val, max_val = bounds
        total = np.sum(current)
        return 1 if min_val <= total <= max_val else 0

    def fitness(self, individual):
        total_score = 0
        num_days = len(individual.days)

        nutrient_index_map = {
            "kcal": constants.ENERGY_INDEX,
            "cho": constants.CHO_INDEX,
            "protein": constants.PROTEIN_INDEX,
            "fat": constants.FAT_INDEX
        }

        for day_idx, day in enumerate(individual.days):
            daily_scores = []
            for nutrient, bounds in self.bounds.items():
                index = nutrient_index_map[nutrient]
                value = day.dish_types[index]
                score = self.calculate_difference(value, bounds)
                print(f"[DEBUG] {nutrient.upper()} ▶️ Day {day_idx+1} | 총합: {np.sum(value):.2f}, 기준: {bounds}, 점수: {score}")
                daily_scores.append(score)

            # 하루 평균 점수
             daily_avg = sum(daily_scores) / len(daily_scores)
        
            if self.strict and daily_avg < 1.0:
                print(f"[STRICT MODE] Day {day_idx+1} 불합격 처리")
                return 1.0  # 최악의 fitness
                
            total_score += daily_avg

        # 전체 평균 → fitness 점수는 낮을수록 좋음 (0에 가까울수록 완벽)
        return 1 - (total_score / num_days)
        
    # def calculate_difference(self, current, target):
    #     tolerance = 0.05
    #     sum_of_ing = np.sum(current)
    #     calc_abs = np.abs(target - sum_of_ing)
    #     percent_diff = calc_abs / target
    #     if (1 - tolerance) * target <= sum_of_ing <= (1 + tolerance) * target:
    #         return 1
    #     else:
    #         return 1 - percent_diff

    # def fitness(self, individual):
    #     total_score = 0
    #     num_days = len(individual.days)

    #     # 각 영양소별 index 딕셔너리
    #     nutrient_index_map = {
    #         "kcal": constants.ENERGY_INDEX,
    #         "cho": constants.CHO_INDEX,
    #         "protein": constants.PROTEIN_INDEX,
    #         "fat": constants.FAT_INDEX
    #     }

    #     for day in individual.days:
    #         daily_scores = []
    #         for nutrient, target_value in self.targets.items():
    #             index = nutrient_index_map[nutrient]
    #             nutrient_val = day.dish_types[index]
    #             score = self.calculate_difference(nutrient_val, target_value)
    #             daily_scores.append(score)

    #         # 평균 점수 계산
    #         total_score += sum(daily_scores) / len(daily_scores)

    #     return 1 - (total_score / num_days)

    def get_name(self):
        return "NutrientFitness"

    def get_description(self):
        return "Compare the nutrients of the individual to the nutrient targets."

# import numpy as np

# import constants
# from fitnesses.abstract_fitness import AbstractFitness


# class NutrientFitness(AbstractFitness):
#     """
#     NutrientFitness is a fitness function that compares the nutrient levels of the individual to the nutrient levels of the target.
#     """
#     def __init__(self, nutrient_bounds):
#         self.energy_target = np.mean(nutrient_bounds["kcal"])
#         self.protein_target = np.mean(nutrient_bounds["protein"])
#         self.fat_target = np.mean(nutrient_bounds["fat"])

#     #실제 식단과 목표 영양기준 차이 계산
#     def calculate_difference(self, current, target):
#         tolerance =   #허용오차
#         sum_of_ing = np.sum(current)  #현재 식단의 총합
#         calc_abs = np.abs(target - sum_of_ing)  #목표와의 차이(절댓값)
#         percent_diff = calc_abs / target  #목표 대비 차이의 비율
#         if (1 - tolerance) * target <= sum_of_ing <= (1 + tolerance) * target:    #허용범위 안이면 만점(1) 
#             return 1
#         else:
#             return 1 - percent_diff #차이가 클수록 점수 낮아짐

#     #fitness: 실제로 식단 전체(5일치)의 영양 적합도를 계산
#     def fitness(self, individual):
#         """
#         Calculates the fitness of the individual.
#         :param individual: The individual to calculate the fitness of.
#         :return: The fitness of the individual.
#         """
#         #from helper.config import Config
#         #conf = Config()  #conf -> 설정한 영양기준
#         sum = 0
#         for days in individual.days:
#             energy = days.dish_types[constants.ENERGY_INDEX]
#             #cho = days.dish_types._get_column_array(constants.CHO_INDEX)
#             protein = days.dish_types[constants.PROTEIN_INDEX]
#             fat = days.dish_types[constants.FAT_INDEX]

#             calc_energy = self.calculate_difference(energy, self.energy_target)
#            #calc_cho = self.calculate_difference(cho, conf.CHO)
#             calc_protein = self.calculate_difference(protein, self.protein_target)
#             calc_fat = self.calculate_difference(fat, self.fat_target)

#             sum += (calc_energy + calc_protein + calc_fat) / 3
#         return 1 - sum / individual.days.__len__()
    
#     #이름 반환
#     def get_name(self):
#         return "NutrientFitness"
    
#     #설명 반환
#     def get_description(self):
#         return "Compare the nutrients individual to the nutrients of the target."
