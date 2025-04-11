# 파일: pymoo_operators/pymoocrossover.py

from pymoo.core.crossover import Crossover
import numpy as np

class PymooCrossover(Crossover):
    def __init__(self):
        super().__init__(2, 2)  # 부모 2명 → 자식 2명

    def _do(self, problem, X, **kwargs):
        #print("✅ [Before Fix] X.shape:", X.shape)

        # 강제로 X 차원 바꿔주기 (임시 조치)
        if X.shape[1] != 2:
            X = np.transpose(X, (1, 0, 2))  # (2, 10, 1) → (10, 2, 1)
            #print("✅ [After Fix] X.shape:", X.shape)

        n_matings = X.shape[0]
        n_var = problem.n_var
        n_offsprings = self.n_offsprings

        off = np.empty((n_offsprings, n_matings, n_var), dtype=object)

        for k in range(n_matings):
            a = X[k, 0, 0]
            b = X[k, 1, 0]
            off_a, off_b = problem.conf.OPERATORS['crossover'].crossover_with_conf(a, b, problem.conf)

            off[0, k, 0] = off_a
            off[1, k, 0] = off_b

        #print("✅ [Crossover] off.shape:", off.shape)
        return off




# import numpy as np
# from pymoo.core.crossover import Crossover

# #사용자 정의 교차(crossover)연산자 : 부모 식단 두 개를 받아서 자식 식단 두 개를 만드는 역할 = 두 식단을 적절히 섞어 새로운 식단 생성
# class PymooCrossover(Crossover):
#     def __init__(self):
#         # define the crossover: number of parents and number of offsprings
#         super().__init__(2, 2)  #(2,2) -> 부모 2명 -> 자식 2명 생성

#     def _do(self, problem, X, **kwargs):  #실제 교차 연산이 일어나는 부분
#         # The input of has the following shape (n_parents, n_matings, n_var)
#         _, n_matings, n_var = X.shape

#         # The output owith the shape (n_offsprings, n_matings, n_var)
#         # Because there the number of parents and offsprings are equal it keeps the shape of X
#         Y = np.full_like(X, None, dtype=object)

#         # for each mating provided
#         for k in range(n_matings):
#             # get the first and the second parent
#             a, b = X[0, k, 0], X[1, k, 0]

#             # prepare the offsprings
#             off_a, off_b = problem.conf.OPERATORS['crossover'].crossover(a, b, problem.conf)

#             # join the character list and set the output
#             Y[0, k, 0], Y[1, k, 0] = off_a, off_b

#         return Y
