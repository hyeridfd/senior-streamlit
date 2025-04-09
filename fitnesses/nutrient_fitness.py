import numpy as np
import constants
from fitnesses.abstract_fitness import AbstractFitness

class NutrientFitness(AbstractFitness):
    def __init__(self, nutrient_bounds):
        # nutrient_bounds = {"kcal": (min, max), ...}
        self.targets = {
            key: np.mean(val)
            for key, val in nutrient_bounds.items()
        }

    def calculate_difference(self, current, target):
        tolerance = 0.05
        sum_of_ing = np.sum(current)
        calc_abs = np.abs(target - sum_of_ing)
        percent_diff = calc_abs / target
        if (1 - tolerance) * target <= sum_of_ing <= (1 + tolerance) * target:
            return 1
        else:
            return 1 - percent_diff

    def fitness(self, individual):
        total_score = 0
        num_days = len(individual.days)

        # 각 영양소별 index 딕셔너리
        nutrient_index_map = {
            "kcal": constants.ENERGY_INDEX,
            "cho": constants.CHO_INDEX,
            "protein": constants.PROTEIN_INDEX,
            "fat": constants.FAT_INDEX
        }

        for day in individual.days:
            daily_scores = []
            for nutrient, target_value in self.targets.items():
                index = nutrient_index_map[nutrient]
                nutrient_val = day.dish_types[index]
                score = self.calculate_difference(nutrient_val, target_value)
                daily_scores.append(score)

            # 평균 점수 계산
            total_score += sum(daily_scores) / len(daily_scores)

        return 1 - (total_score / num_days)

    def get_name(self):
        return "NutrientFitness"

    def get_description(self):
        return "Compare the nutrients of the individual to the nutrient targets."
