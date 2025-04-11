# import numpy as np
# import constants
# from fitnesses.abstract_fitness import AbstractFitness

# class ChewingStageFitness(AbstractFitness):
#     """
#     저작 단계 적합성 평가 피트니스 함수.
#     사용자 입력 저작 단계에 맞을수록 높은 점수 부여 (1점 만점)
#     """
#     def __init__(self, target_chewing_level):
#         self.target_chewing_level = target_chewing_level  # 사용자 입력값 (1, 2, 3)

#     def fitness(self, individual):
#         from helper.config import Config
#         conf = Config()
#         total_diff = 0
#         total_count = 0

#         for day in individual.days:
#             chewing_levels = day.dish_types._get_column_array(constants.CHEWING_STAGE)
#             chewing_levels = chewing_levels[~np.isnan(chewing_levels)]

#             if len(chewing_levels) == 0:
#                 continue

#             chewing_levels = chewing_levels.astype(float)

#             # print("🧪 [디버깅] 현재 평가 중인 식단 하루치:")
#             # print("chewing_levels:", chewing_levels)
#             # print("target:", self.target_chewing_level)
#             # print("abs diff:", np.abs(chewing_levels - self.target_chewing_level))
#                         # 각 식재료 저작단계와 사용자 저작단계의 차이가 1 보다 큰 경우 0점 처리 (ex. 1단계인데 3단계 음식 추천해주는 등)
#             if np.any(np.abs(chewing_levels - self.target_chewing_level) > 1):
#                 print("🚨 [경고] 저작단계 차이 2 이상 → 0점 처리")
#                 return 0  # 조건 위반 → 0점 처리

#             # 각 식재료 저작단계와 사용자 저작단계의 차이 합산
#             diffs = np.abs(chewing_levels - self.target_chewing_level)
#             total_diff += np.sum(diffs)
#             total_count += len(diffs)

#         # 평균 차이 계산
#         if total_count == 0:
#             return 0  # 평가할 게 없으면 0점 처리

#         avg_diff = total_diff / total_count  # 0에 가까울수록 좋은 식단

#         # 점수로 변환: 저작단계 최대 차이 2 (예: 1단계 ↔ 3단계)
#         # → 0차이면 1점, 1차이면 0.5점, 2차이면 0점
#         score = 1 - (avg_diff / 2)
#         return max(0, min(1, score))  # 0~1 사이로 제한

#     def get_name(self):
#         return "ChewingStageFitness"

#     def get_description(self):
#         return "Evaluate how well the meal's chewing stage matches the user's chewing ability."
