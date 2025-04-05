import numpy as np

from helper.config import Config

# 전체 코드에서 교차, 변이, 샘플링, 선택과 같은 유전 알고리즘 연산에 랜덤성을 부여할 때 사용됨
def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance

#싱글톤 패턴으로 구성, random객체는 프로그램 전체에서 한 번만 생성되고 계속 재사용됨
#@singleton
class Random:
    #conf.RANDOM_SEED이 FALSE이면, 시드를 고정값으로 설정해서 결과 재현 가능하게 함(ex. Seed = 24일 때, 매번 같은 결과가 나와 실험 비교 쉬움)
    def __init__(self, conf):
        self.random = np.random.default_rng(conf.SEED if not conf.RANDOM_SEED else None)

        # self.random = np.random
        # if not conf.RANDOM_SEED:
        #     self.random.seed(conf.SEED)
#0~1 사이 실수 생성
    def random_float(self):
        return self.random.random()
#True 또는 False 반환
    def random_bool(self, value):
        return self.random.random() < value
#0 이상 max 미만의 정수 하나 반환
    def random_int(self, max):
        return self.random.integers(0, max)
#0~max_size-1중 하나 선택
    def random_choice(self, max_size, selection_probs):
        return self.random.choice(max_size, p=selection_probs)
