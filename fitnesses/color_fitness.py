import numpy as np

import constants
from fitnesses.abstract_fitness import AbstractFitness


class ColorFitness(AbstractFitness):
    """
    ColorFitness is a fitness function that compares the color of the individual to the color of the target.
    """
# 5일치 식단에 대한 하루하루 색상 다양성 개산 및 평균 점수 도출
    def fitness(self, individual):
        """
        Calculates the fitness of the individual.
        :param conf:
        :param individual: The individual to calculate the fitness of.
        :return: The fitness of the individual.
        """
        sum = 0  #초기화
        for days in individual.days:
            #색상 정보 불러오기
            colors = days.dish_types._get_column_array(constants.COLOR_INDEX)
            # if color is nan discarded to evaluate the fitness
            filtered_colors = colors[~np.isnan(colors)]
            #색상이 없는 날은 점수 1 부여
            if filtered_colors.__len__() == 0:
                sum += 1
            #색상 다양성 계산 [1,2,2] -> 색상 2종류(1,2) -> 2/3 = 0.666 -> 이 비율이 높을수록 색상 다양함
            else:
                values, counts = np.unique(filtered_colors, return_counts=True)
                sum += counts.__len__() / filtered_colors.__len__()
                #sum/수 -> 전체 평균 다양성 -> 1- 평균 (낮은 수치가 더 좋은 식단으로 보이는 것으로 통일함)
        return 1 - (sum / individual.days.__len__())

    def get_name(self):
        return "ColorFitness"

    def get_description(self):
        return "Compare the color of the individual to the color of the target."
