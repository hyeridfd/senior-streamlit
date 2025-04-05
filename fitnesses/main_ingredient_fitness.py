import numpy as np

import constants
from fitnesses.abstract_fitness import AbstractFitness


class MainIngredientFitness(AbstractFitness):
    """
    MainIngredientFitness is a fitness function that compares the main ingredients of the individual to the main ingredients of the target.
    """
#주요 식재료가 얼마나 다양하게 쓰였는지 평가해서 점수를 부여
    def fitness(self, individual):
        """
        Calculates the fitness of the individual.
        :param conf: The configuration of the simulation.
        :param individual: The individual to calculate the fitness of.
        :return: The fitness of the individual.
        """
        # IF day is 1, then the fitness calculated with different main ingredients / total main ingredients
        # IF day is else, then the fitness calculated with different(previous day's main ingredients + main ingredients) / total main ingredients for two days
        from helper.config import Config
        conf = Config()
        sum = 0  #다양성 점수 누적할 sum
        previous_day = None  #어제 사용한 재료 저장하는 변수
        for idx, days in enumerate(individual.days):
            if idx == 0:  #첫 번째 날(비교할 전날이 없을 때)
                #주재료1
                main_ing_1 = days.dish_types._get_column_array(constants.MAIN_INGREDIENTS_INDEX)
                #주재료2
                main_ing_2 = days.dish_types._get_column_array(constants.MAIN_INGREDIENTS_2_INDEX)
                merged_array = np.concatenate((main_ing_1, main_ing_2))  #두개 재료 리스트 합치기
                filtered_ings = merged_array[~np.isnan(merged_array)]  #결측값 제거
                values, counts = np.unique(filtered_ings, return_counts=True)  #중복을 제거한 재료 개수/전체 제료 개수
                sum += counts.__len__() / filtered_ings.__len__()

                previous_day = merged_array #전날 재료 정보 저장
            else:
                main_ing_1 = days.dish_types._get_column_array(constants.MAIN_INGREDIENTS_INDEX)
                main_ing_2 = days.dish_types._get_column_array(constants.MAIN_INGREDIENTS_2_INDEX)
                merged_array = np.concatenate((main_ing_1, main_ing_2))
                merged_array_prev = np.concatenate((main_ing_1, main_ing_2, previous_day))  #오늘 + 전날 재료 목록 합침
                filtered_ings = merged_array_prev[~np.isnan(merged_array_prev)]  #결측값 제거
                values, counts = np.unique(filtered_ings, return_counts=True) 
                sum += counts.__len__() / filtered_ings.__len__()

                previous_day = merged_array

        return 1 - (sum / conf.NUMBER_OF_DAYS)

    def get_name(self):
        return "MainIngredientFitness"

    def get_description(self):
        return "Compare the main ingredients individual to the nutrients of the target."
