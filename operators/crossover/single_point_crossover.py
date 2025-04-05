import copy
import numpy as np
from helper.random import Random
from operators.crossover.abstract_crossover import AbstractCrossover

class SinglePointCrossover(AbstractCrossover):

    # 실제 사용되는 메서드
# SinglePointCrossover 클래스 안에서
    def crossover_with_conf(self, individual_1, individual_2, conf):
        rand = Random(conf)

        # ✅ numpy array일 경우 첫 번째 요소만 추출
        if isinstance(individual_1, np.ndarray):
            individual_1 = individual_1[0]
        if isinstance(individual_2, np.ndarray):
            individual_2 = individual_2[0]

        ind_1 = copy.deepcopy(individual_1)
        ind_2 = copy.deepcopy(individual_2)

        w_dish_types = rand.random_int(conf.DISH_TYPE_SIZE)
        w_days_1 = rand.random_int(conf.NUMBER_OF_DAYS)
        w_days_2 = rand.random_int(conf.NUMBER_OF_DAYS)

        row_1 = ind_1.days[w_days_1].dish_types.iloc[w_dish_types, :]
        row_2 = ind_2.days[w_days_2].dish_types.iloc[w_dish_types, :]

        ind_2.days[w_days_2].dish_types.iloc[w_dish_types, :] = row_1
        ind_1.days[w_days_1].dish_types.iloc[w_dish_types, :] = row_2

        return ind_1, ind_2


    # 추상 메서드 형식만 맞추기
    def crossover(self, a, b):
        raise NotImplementedError("pymoo에서는 crossover_with_conf를 사용합니다.")