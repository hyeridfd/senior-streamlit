import string
import numpy as np
import pandas as pd
import sys
from pymoo.core.problem import ElementwiseProblem
import constants
import pandas as pd
# from fitnesses.color_fitness import ColorFitness
# from fitnesses.consistency_fitness import ConsistencyFitness
from fitnesses.main_ingredient_fitness import MainIngredientFitness
from fitnesses.nutrient_fitness import NutrientFitness
from fitnesses.chewing_stage_fitness import ChewingStageFitness

from helper.config import Config
from solution import FitnessFunctions

class MenuPlanningProblem(ElementwiseProblem):
    def __init__(self, argv=[], file_path='./data/dataset.csv', df=None, external_conf=None):
        self.conf = external_conf if external_conf else Config(argv)
        super().__init__(n_var=1, n_obj=self.conf.FITNESS_FUNCTIONS.__len__())
        print("[MenuPlanningProblem] 받은 Config 객체의 ENERGY 값:", self.conf.ENERGY)


        try:
            if df is not None:
                self.df = df
            else:
                self.df = pd.read_csv(file_path, encoding='utf-8')
        except Exception as e:
            print("❌ CSV 파일을 불러오는 중 에러 발생:", e)
            sys.exit(1)

        user_chewing_stage = self.conf.CHEWING_STAGE  # ✅ 사용자 저작단계 가져오기
        preferred_ingredient = self.conf.PREFERENCE

        preference_map = {
            "육류": 0,
            "수산물": 1,
            "채소": 2,
            "기타": 3
        }
        preferred_code = preference_map.get(self.conf.PREFERENCE, -1)
        print("[DEBUG] preferred_code (매핑된 숫자):", preferred_code)

        # ✅ 저작단계 필터링 추가
        # 각 dish_type별로 저작단계 조건 추가 (≤ 사용자 입력 단계)
        self.first_dish_type = self.df[
            (self.df['dish_type'] == 0) &
            (self.df['chewing_stage'] <= user_chewing_stage)
        ]
        self.second_dish_type = self.df[
            (self.df['dish_type'] == 1) &
            (self.df['chewing_stage'] <= user_chewing_stage) &
            (self.df['preference'] == preferred_code)
        ]
        self.third_dish_type = self.df[
            (self.df['dish_type'] == 2) &
            (self.df['chewing_stage'] <= user_chewing_stage) &
            (self.df['preference'] == preferred_code)
        ]
        self.fourth_dish_type = self.df[
            (self.df['dish_type'] == 3) &
            (self.df['chewing_stage'] <= user_chewing_stage)
        ]
        self.fifth_dish_type = self.df[
            (self.df['dish_type'] == 4) &
            (self.df['chewing_stage'] <= user_chewing_stage)
        ]
        print("[DEBUG] preferred_ingredient:", preferred_ingredient)
        print("[DEBUG] preferred_ingredient type:", type(preferred_ingredient))
        print("[DEBUG] df['preference'] 유니크 값:", self.df['preference'].unique())
        print("[DEBUG] df['preference'] 타입:", self.df['preference'].dtype)

        # 디버깅용: 각 dish_type별 샘플 가능 음식 수 및 음식명 출력
        print("\n✅ 샘플 가능한 음식 현황:")
        for name, df in [
            ("밥", self.first_dish_type),
            ("국", self.second_dish_type),
            ("주찬", self.third_dish_type),
            ("부찬", self.fourth_dish_type),
            ("김치", self.fifth_dish_type),
        ]:
            count = len(df)
            print(f"[{name}] 개수: {count}")
            if count > 0:
                print(f"→ 음식명 예시: {df['meal_name'].head().tolist()}")
            else:
                print(f"→ 샘플 불가 (조건에 맞는 음식 없음)")

        #self.first_dish_type = self.df[self.df['dish_type'] == 0]  # 밥
        # self.second_dish_type = self.df[self.df['dish_type'] == 1]  # 국
        # self.third_dish_type = self.df[self.df['dish_type'] == 2]  # 주찬
        # self.fourth_dish_type = self.df[self.df['dish_type'] == 3]  # 부찬
        # self.fifth_dish_type = self.df[self.df['dish_type'] == 4]  # 김치
        # append 제거: 리스트 컴프리헨션 사용
        self.fitness_functions = [
            FitnessFunctions(function=ff['function'], weight=ff['weight'])
            for ff in self.conf.FITNESS_FUNCTIONS
        ]
        
    def get_one_dish_type(self, dish_type):
        if dish_type == 0:
            return self.first_dish_type.sample()
        elif dish_type == 1:
            return self.second_dish_type.sample()
        elif dish_type == 2:
            return self.third_dish_type.sample()
        elif dish_type == 3:
            return self.fourth_dish_type.sample()
        elif dish_type == 4:
            return self.fifth_dish_type.sample()
        else:
            raise ValueError(f"Unknown dish_type: {dish_type}")
    #def get_one_dish_type(self, dish_type):
        #return self.df[self.df[constants.DISH_TYPE_INDEX] == dish_type].sample()
    
    def _evaluate(self, x, out, *args, **kwargs):
        # append 제거: 리스트 컴프리헨션으로 한 줄 처리
        fitness_list = [self._evaluate_fitness(ff, x[0]) for ff in x[0].fitness_functions]
        total_fitness = sum(fitness_list) / len(fitness_list)
        x[0].total_fitness = total_fitness
        out["F"] = np.array(fitness_list, dtype=float)
    
    def _evaluate_fitness(self, ff, individual):
        ff.value = ff.function.fitness(individual)
        ff.is_calculated = True
        return ff.value

# import string
# import numpy as np
# import pandas as pd
# import sys
# from pymoo.core.problem import ElementwiseProblem
# import constants

# #from fitnesses.color_fitness import ColorFitness
# #from fitnesses.consistency_fitness import ConsistencyFitness
# #from fitnesses.main_ingredient_fitness import MainIngredientFitness
# from fitnesses.nutrient_fitness import NutrientFitness
# from helper.config import Config
# from solution import FitnessFunctions

# class MenuPlanningProblem(ElementwiseProblem):
#     def __init__(self, argv=[], file_path='./data/dataset.csv', df=None):
#    #def __init__(self, argv, file_path='./data/dataset.csv', df=None):
#         self.conf = Config(argv)
#         super().__init__(n_var=1, n_obj=self.conf.FITNESS_FUNCTIONS.__len__())

#         try:
#             if df is not None:
#                 self.df = df
#             else:
#                 self.df = pd.read_csv(file_path, encoding='cp949')  # 또는 'cp949'
#         except Exception as e:
#             print("❌ CSV 파일을 불러오는 중 에러 발생:", e)
#             sys.exit(1)  # 확실히 종료
# #요리 분류
#         self.first_dish_type = self.df[self.df['dish_type'] == 0]  #밥
#         self.second_dish_type = self.df[self.df['dish_type'] == 1] #국
#         self.third_dish_type = self.df[self.df['dish_type'] == 2]  #주찬
#         self.fourth_dish_type = self.df[self.df['dish_type'] == 3] #부찬
#         self.fifth_dish_type = self.df[self.df['dish_type'] == 4]  #김치

# #평가기준(fitness 함수 불러오기)
#         self.fitness_functions = list()
#         for ff in self.conf.FITNESS_FUNCTIONS:
#             self.fitness_functions.append(FitnessFunctions(function=ff['function'], weight=ff['weight']))
# #개체 평가(하나의 식단이 얼마나 좋은지 점수 계산)
#     def get_one_dish_type(self, dish_type):
#         return self.df[self.df._get_column_array(constants.DISH_TYPE_INDEX) == dish_type].sample()

#     def _evaluate(self, x, out, *args, **kwargs):
#         fitness_list = []
#         for ff in x[0].fitness_functions:
#             ff.value = ff.function.fitness(x[0])
#             ff.is_calculated = True
#             fitness_list.append(ff.value)
#         x[0].total_fitness = sum(fitness_list) / len(fitness_list)

#         out["F"] = np.array(fitness_list, dtype=float)


