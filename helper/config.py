import sys
import getopt
import configparser
import os

#from fitnesses.color_fitness import ColorFitness
#from fitnesses.consistency_fitness import ConsistencyFitness
from fitnesses.main_ingredient_fitness import MainIngredientFitness
#from fitnesses.meal_group_fitness import MealGroupFitness
from fitnesses.nutrient_fitness import NutrientFitness
from fitnesses.repetition_fitness import RepetitionFitness
#from fitnesses.chewing_stage_fitness import ChewingStageFitness
#from fitnesses.user_preference_fitness import PreferenceFitness


# def singleton(class_):
#     instances = {}

#     def getinstance(*args, **kwargs):
#         if class_ not in instances:
#             instances[class_] = class_(*args, **kwargs)
#         return instances[class_]

#     return getinstance


#@singleton
class Config:
    def __init__(self, argv=[], external_targets=None):
        config = configparser.ConfigParser()
        config.read(os.path.dirname(os.path.abspath(__file__)) + '/conf.ini')

        # ####SETTINGS FILE######
        self.EXPERIMENT_NAME = config['DEFAULT']['ExperimentName']
        self.ALGORITHM = config['DEFAULT']['Algorithm']
        self.SHOW_PLOT = bool(config['REPORT']['ShowPlot'] == 'True')

        self.NUMBER_OF_POPULATION = int(config['CONTROL_PARAMETERS']['NumberOfPopulation'])
        self.MAXIMUM_EVALUATION = int(config['CONTROL_PARAMETERS']['MaximumEvaluation'])
        self.MUTATION_RATE = float(config['CONTROL_PARAMETERS']['MutationRate'])

        self.RUN_TIME = int(config['DEFAULT']['RunTime'])
        self.SHOW_PROGRESS = bool(config['REPORT']['ShowProgress'] == 'True')
        self.PRINT_MENU = bool(config['REPORT']['PrintMenu'] == 'True')
        self.RUN_INFO = bool(config['REPORT']['RunInfo'] == 'True')
        self.SAVE_RESULTS = bool(config['REPORT']['SaveResults'] == 'True')
        self.OUTPUTS_FOLDER_NAME = str(config['REPORT']['OutputsFolderName'])
        self.CSV_FOLDER_NAME = str(config['REPORT']['CsvFolderName'])
        self.HTML_FOLDER_NAME = str(config['REPORT']['HtmlFolderName'])
        self.FIG_FOLDER_NAME = str(config['REPORT']['FigFolderName'])

        self.RANDOM_SEED = config['SEED']['RandomSeed'] == 'True'
        self.SEED = int(config['SEED']['Seed'])

        # ✅ 사용자 정의 영양 기준 적용
        if external_targets is not None: # 추가
            self.ENERGY = external_targets.get("kcal", 600)
            self.PROTEIN = external_targets.get("protein", 20)
            self.FAT = external_targets.get("fat", 17)
            self.CHO = external_targets.get("cho", 100)
            self.CHEWING_STAGE = external_targets.get("chewing_stage", 1)
            self.PREFERENCE = external_targets.get("preference", 1)
            # print("✅ external_targets 들어옴:", external_targets)
            # print("[DEBUG] 설정된 ENERGY:", self.ENERGY)
            # print("현재 self 속성들:", dir(self))

        else:
            self.ENERGY = float(config['MENU']['Energy'])
            self.CHO = float(config['MENU']['Cho'])
            self.PROTEIN = float(config['MENU']['Protein'])
            self.FAT = float(config['MENU']['Fat'])
            self.CHEWING_STAGE = float(config['MENU']['ChewingStage'])
            self.PREFERENCE = float(config['MENU']['Preference'])

        self.NUTRIENT_BOUNDS = {  # 기본 영양 기준
            'kcal': (self.ENERGY * 0.9, self.ENERGY * 1.1),
            'cho': (self.CHO * 0.9, self.CHO * 1.1),
            'protein': (self.PROTEIN * 0.9, self.PROTEIN * 1.1),
            'fat': (self.FAT * 0.9, self.FAT * 1.1),
            }
        # Print NUTRIENT_BOUNDS to verify it is set correctly
        #print(f"[DEBUG] NUTRIENT_BOUNDS: {self.NUTRIENT_BOUNDS}")

        self.NUMBER_OF_DAYS = int(config['MENU']['NumberOfDays'])
        self.DISH_TYPE_SIZE = int(config['MENU']['DishTypeSize'])
        self.TOLERANCE = 5
        self.FITNESS_FUNCTIONS = [
            {
                'function': NutrientFitness({
                    'kcal': (self.ENERGY * 0.9, self.ENERGY * 1.1),
                    'protein': (self.PROTEIN * 0.9, self.PROTEIN * 1.1),
                    'fat': (self.FAT * 0.9, self.FAT * 1.1),
                    'cho': (self.CHO * 0.9, self.CHO * 1.1)
            }), 'weight': 0.5
            },
            {
                'function': MainIngredientFitness(),
                'weight': 0.2
            },
            {
                'function': RepetitionFitness(),
                'weight': 0.3
            }
        ]

        from operators.crossover.single_point_crossover import SinglePointCrossover
        from operators.mutation.mutation import Mutation
        from operators.selection.RouletteSelection import RouletteSelection
        self.OPERATORS = {'crossover': SinglePointCrossover(), 'mutation': Mutation(), 'selection': RouletteSelection()}

        # ####SETTINGS ARGUMENTS######
        try:
            opts, args = getopt.getopt(argv, 'hn:m:r:',
                                       ['help', 'np=', 'max_eval=', 'runtime=',
                                        'output_folder=', 'file_name=', 'res_cycle_folder='])
        except getopt.GetoptError:
            print('Usage: main.py -h or --help')
            sys.exit(2)
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                print('-h or --help : Show Usage')
                print('-n or --np : Number of Population')
                print('-m or --max_eval : Maximum Evaluation')
                print('-r or --runtime : Run Time')
                print('--output_folder= [DEFAULT: Outputs]')
                print('--file_name= [DEFAULT: Run_Results.csv]')
                print('--res_cycle_folder= [DEFAULT: ResultByCycle]')
                sys.exit()
            elif opt in ('-n', '--np'):
                self.NUMBER_OF_POPULATION = int(arg)
            elif opt in ('-m', '--max_eval'):
                self.MAXIMUM_EVALUATION = int(arg)
            elif opt in ('-r', '--runtime'):
                self.RUN_TIME = int(arg)
            elif opt in '--output_folder':
                self.OUTPUTS_FOLDER_NAME = arg
            elif opt in '--csv_folder':
                self.CSV_FOLDER_NAME = arg
            elif opt in '--html_folder':
                self.HTML_FOLDER_NAME = arg
            elif opt in '--fig_folder':
                self.FIG_FOLDER_NAME = arg
