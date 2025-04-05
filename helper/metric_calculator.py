import numpy as np
from pymoo.indicators.gd import GD
from pymoo.indicators.gd_plus import GDPlus
from pymoo.indicators.hv import HV
from pymoo.indicators.igd import IGD
from pymoo.indicators.igd_plus import IGDPlus

from helper.config import Config

#**다목적 최적화 알고리즘의 성능**을 수치적으로 평가하기 위해 만들어진 도구임
#최적화된 식단 해들(solution)이 얼마나 좋은지 측정하는 점수 계산기

class MetricCalculator:
    def __init__(self):
        conf = Config()
        self.ref_point = np.array([1.2] * conf.FITNESS_FUNCTIONS.__len__())
        #파레토: 각 fitness function의 최솟값을 0으로 간주하고, 그에 대한 거리를 측정함
        self.pareto_front = np.array([0] * conf.FITNESS_FUNCTIONS.__len__())

#hypervolume: 해들이 기준점(ref_point)으로부터 얼마나 넓은 영역을 차지하는지 나타냄(값이 클수록 다양하고 우수한 해들이 많다는 의미임) -> 값이 클수록 좋음 
    def calculate_hypervolume(self, res):
        ind = HV(ref_point=self.ref_point)
        return ind(res.F)
#Generational Distance (GD): 현재 해들이 이상적인 해(pareto front)와 얼마나 가까운지 -> 값이 작을수록 좋음(더 이상적인 해에 가까움)
    def calculate_gd(self, res):
        # calculate the generational distance
        ind = GD(self.pareto_front)
        return ind(res.F)
#GD 개선 버전: 거리뿐 아니라 분포의 다양성도 고려 ->위치 + 다양성, 작을수록 좋음
    def calculate_gd_p(self, res):
        # calculate the generational distance plus
        ind = GDPlus(self.pareto_front)
        return ind(res.F)
#IGD(Inverted Generational Distance): pareto front의 각 점이 얼마나 현재 해에 가까운지 -> 값이 작을수록 좋음
    def calculate_igd(self, res):
        # calculate the inverted generational distance
        ind = IGD(self.pareto_front)
        return ind(res.F)
#IGD의 개선 버전: 다양한 해를 얼마나 잘 포함했는지 평가
    def calculate_igd_p(self, res):
        # calculate the inverted generational distance plus
        ind = IGDPlus(self.pareto_front)
        return ind(res.F)
