import numpy as np
import constants
from fitnesses.abstract_fitness import AbstractFitness

class PreferenceFitness(AbstractFitness):
    """
    사용자 입력 선호도에 맞을수록 높은 점수 부여 (1점 만점)
    국, 주찬만 고려
    """
    def __init__(self, target_preference):
        self.target_preference = target_preference  # 사용자 입력값 (채소, 고기, 해산물, 기타)

    def fitness(self, individual):
        from helper.config import Config
        conf = Config()

        total_score = 0
        num_days = len(individual.days)

        for day in individual.days:
            day_score = 0
            day_score += self.evaluate_dish(day.dish_types, 1)  # 국
            day_score += self.evaluate_dish(day.dish_types, 2)  # 주찬
            total_score += day_score / 2  # 하루 평균 점수

        return 1 - (total_score / num_days)  # 1에서 평균 점수를 빼서 낮을수록 좋은 점수

    def evaluate_dish(self, dish_types, dish_type_index):
        dish_type = dish_types.iloc[dish_type_index]
        preference = dish_type['preference']
        if preference == self.target_preference:
            return 1
        else:
            return 0    

    def get_name(self):
        return "PreferenceFitness"

    def get_description(self):
        return "Evaluate how well the meal's preference matches the user's preference."
