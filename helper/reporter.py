import datetime
import os
import pandas as pd
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from pymoo.indicators.gd import GD
from pymoo.indicators.gd_plus import GDPlus
from pymoo.indicators.hv import Hypervolume
from pymoo.indicators.igd import IGD
from pymoo.indicators.kktpm import KKTPM
from pymoo.visualization.scatter import Scatter

import constants
from helper.metric_calculator import MetricCalculator
from solution import Solution

# 식단 솔루션의 결과를 저장, 시각화, 분석하는 기능(리포트 출력)
#최적화 끝난 식단 결과 기반으로 .csv, .html로 출력하고, png 시각화 파일, json 파일로도 출력
class Reporter:
    def __init__(self, config):
        self.pymoo_header = "algorithm, run, iteration, experiment_id, number_of_population, number_of_generation, current_generation, " \
                            "total_fitness, hypervolume, gd, gd_p, igd, igd_p, energy, cho, protein, fat, time"
        self.header = "run, iteration, experiment_id, number_of_population, number_of_generation, current_generation, " \
                      "total_fitness"
                      
        self.csv_text = "{}, {}, {}, {}, {}, {}, {}, {}"
        self.pymoo_csv_text = ", ".join(["{}"] * (18 + len(config.FITNESS_FUNCTIONS))) + "\n"
        
        self.config = config

        for ff in config.FITNESS_FUNCTIONS:
            self.header += ", " + ff.get('function').get_name()
            self.pymoo_header += ", " + ff.get('function').get_name()
            self.csv_text += ", {}"

        self.header += "\n"
        self.pymoo_header += "\n"
        self.csv_text += "\n"
        self.pymoo_csv_text += "\n"

        experiment_id = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(" ", "").replace(":", "")
        self.experiment_id = experiment_id + "-" + config.EXPERIMENT_NAME
        self.file_path = "%s/%s/%s.csv" % (config.OUTPUTS_FOLDER_NAME, config.CSV_FOLDER_NAME, self.experiment_id)
        # self.pymoo_file_path = "%s/%s/%s_pymoo.csv" % (
        #     config.OUTPUTS_FOLDER_NAME, config.CSV_FOLDER_NAME, self.experiment_id)
        
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # 프로젝트 루트
        self.file_path = os.path.join(base_path, config.OUTPUTS_FOLDER_NAME, config.CSV_FOLDER_NAME, self.experiment_id + ".csv")
        self.pymoo_file_path = os.path.join(base_path, config.OUTPUTS_FOLDER_NAME, config.CSV_FOLDER_NAME, self.experiment_id + "_pymoo.csv")

        self.mat_file_path = "%s/%s" % (config.OUTPUTS_FOLDER_NAME, self.experiment_id)

        self.html_file_path = "%s/%s/%s" % (config.OUTPUTS_FOLDER_NAME, config.HTML_FOLDER_NAME, self.experiment_id)
        self.fig_file_path = "%s/%s/%s" % (config.OUTPUTS_FOLDER_NAME, config.FIG_FOLDER_NAME, self.experiment_id)
        self.hyp_file_path = "%s/%s/%s_hypervolume" % (
            config.OUTPUTS_FOLDER_NAME, config.FIG_FOLDER_NAME, self.experiment_id)
        self.gd_file_path = "%s/%s/%s_gd_p" % (config.OUTPUTS_FOLDER_NAME, config.FIG_FOLDER_NAME, self.experiment_id)
        self.gd_p_file_path = "%s/%s/%s_gd_p" % (config.OUTPUTS_FOLDER_NAME, config.FIG_FOLDER_NAME, self.experiment_id)
        self.igd_file_path = "%s/%s/%s_igd" % (config.OUTPUTS_FOLDER_NAME, config.FIG_FOLDER_NAME, self.experiment_id)
        self.igd_p_file_path = "%s/%s/%s_igd_p" % (
            config.OUTPUTS_FOLDER_NAME, config.FIG_FOLDER_NAME, self.experiment_id)
        self.conv_file_path = "%s/%s/%s_mean_conv" % (
            config.OUTPUTS_FOLDER_NAME, config.FIG_FOLDER_NAME, self.experiment_id)
        self.bg_colors = [
            'bg-info',
            'bg-success',
            'bg-warning',
            'bg-danger',
            'bg-primary',
            'bg-secondary',
            'bg-dark',
            'bg-light',
            'bg-white',
        ]
        if not os.path.exists(config.OUTPUTS_FOLDER_NAME):
            os.makedirs(config.OUTPUTS_FOLDER_NAME)

        if not os.path.exists("%s/%s" % (config.OUTPUTS_FOLDER_NAME, config.HTML_FOLDER_NAME)):
            os.makedirs("%s/%s" % (config.OUTPUTS_FOLDER_NAME, config.HTML_FOLDER_NAME))

        # if not os.path.exists("%s/%s" % (config.OUTPUTS_FOLDER_NAME, config.CSV_FOLDER_NAME)):
        #     os.makedirs("%s/%s" % (config.OUTPUTS_FOLDER_NAME, config.CSV_FOLDER_NAME))
        os.makedirs(os.path.join("Outputs", config.CSV_FOLDER_NAME), exist_ok=True)
        if not os.path.exists("%s/%s" % (config.OUTPUTS_FOLDER_NAME, config.FIG_FOLDER_NAME)):
            os.makedirs("%s/%s" % (config.OUTPUTS_FOLDER_NAME, config.FIG_FOLDER_NAME))

        self.html_string_2 = '''
            <html>
              <head><title>Menu</title>
                    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
                    <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
                    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.12.9/dist/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
                    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>           </head>
              <body>
                {table}
                <div class="progress">
                  <div class="progress-bar progress-bar-striped progress-bar-animated bg-success" role="progressbar" style="width: {color_percentage}%" aria-valuenow="{color_percentage}" aria-valuemin="0" aria-valuemax="100">Color: {color}</div>
                </div>
                <div class="progress">
                  <div class="progress-bar progress-bar-striped progress-bar-animated bg-info" role="progressbar" style="width: {consistency_percentage}%" aria-valuenow="{consistency_percentage}" aria-valuemin="0" aria-valuemax="100">Consistency: {consistency}</div>
                </div>
                <div class="progress">
                  <div class="progress-bar progress-bar-striped progress-bar-animated bg-warning" role="progressbar" style="width: {main_ing_percentage}%" aria-valuenow="{main_ing_percentage}" aria-valuemin="0" aria-valuemax="100">Main Ingredients: {main_ing}</div>
                </div>
                <div class="progress">
                  <div class="progress-bar progress-bar-striped progress-bar-animated bg-danger" role="progressbar" style="width: {nutrients_percentage}%" aria-valuenow="{nutrients_percentage}" aria-valuemin="0" aria-valuemax="100">Nutrients: {nutrients}</div>
                </div>
                <div class="progress">
                  <div class="progress-bar progress-bar-striped progress-bar-animated bg-secondary" role="progressbar" style="width: {repetition_percentage}%" aria-valuenow="{repetition_percentage}" aria-valuemin="0" aria-valuemax="100">Repetition: {repetition}</div>
                </div>
                <div class="progress">
                  <div class="progress-bar progress-bar-striped progress-bar-animated bg-success" role="progressbar" style="width: {meal_group_percentage}%" aria-valuenow="{meal_group_percentage}" aria-valuemin="0" aria-valuemax="100">Meal Group: {meal_group}</div>
                </div>
                <div class="progress">
                  <div class="progress-bar progress-bar-striped progress-bar-animated bg-info" role="progressbar" style="width: {footprint_percentage}%" aria-valuenow="{footprint_percentage}" aria-valuemin="0" aria-valuemax="100">Footprint: {footprint}</div>
                </div>
              </body>
            </html>.
            '''
        self.html_string = '''
            <html>
              <head><title>Menu</title>
                    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
                    <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
                    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.12.9/dist/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
                    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>           </head>
              <body>
                {table}
                {progress_bars}
              </body>
            </html>.
            '''

    def write_header(self):
        with open(self.file_path, 'a') as saveRes:
            saveRes.write(self.header)
            saveRes.close()

    def write_pymoo_header(self):
        with open(self.pymoo_file_path, 'a') as saveRes:
            saveRes.write(self.pymoo_header)
            saveRes.close()

    def write_row(self, run_id, it, cur_gen, fitnesses, total_fitness):
        values = [i.value for i in fitnesses]
        csv_text = self.csv_text.format(run_id, it, self.experiment_id, self.config.NUMBER_OF_POPULATION,
                                        self.config.MAXIMUM_EVALUATION, cur_gen, total_fitness, *values)

        with open(self.file_path, 'a') as saveRes:
            saveRes.write(csv_text)
            saveRes.close()

    def write_pymoo_row(self, algorithm, run_id, it, cur_gen, fitnesses, total_fitness,
                    hypervolume, gd, gd_p, igd, igd_p, energy, cho, protein, fat, time):

        float_format = '{:.3f}'

        values = [i.value for i in fitnesses]
        
        print("[DEBUG] fitness values:", values)
        print("[DEBUG] total length:", 18 + len(values))
        print("[DEBUG] format field count:", self.pymoo_csv_text.count('{}'))

        csv_text = self.pymoo_csv_text.format(algorithm, run_id, it, self.experiment_id,
            self.config.NUMBER_OF_POPULATION, self.config.MAXIMUM_EVALUATION, cur_gen,
            total_fitness, hypervolume, gd, gd_p, igd, igd_p,
            float_format.format(energy), float_format.format(cho),
            float_format.format(protein), float_format.format(fat),
            time, *values)

        try:
            with open(self.pymoo_file_path, 'a') as saveRes:
                saveRes.write(csv_text)
                #print(f"[DEBUG ✅] CSV 파일 작성 완료: {self.pymoo_file_path}")
        except Exception as e:
            #print(f"[❌ ERROR] CSV 저장 실패: {e}")


    def highlight_max(self, x, color):
        return np.where(x > np.nanmax(x.to_numpy()), f"color: {color};", None)

    def print_solution(self, solution):
        index = 1
        for day in solution.days:
            print("Day:" + str(index))
            print(day.dish_types)
            index += 1

    def save_solution(self, solution):
        if self.config.SAVE_RESULTS:
            np.save(self.mat_file_path, solution)

    def load_solution(self, file_name):
        return Solution(np.load(file_name))

    def is_in_range(self, x, color):
        values = pd.Series([float(i.strip('%')) for i in x])
        return np.where(np.logical_and(values >= 100 - self.config.TOLERANCE, values <= 100 + self.config.TOLERANCE),
                        f"color: {color};", f"color: red;", )

    def generate_progress_bars(self, solution):
        progress_string = '''
                            <div class="progress">
                              <div class="progress-bar progress-bar-striped progress-bar-animated {color}" role="progressbar" style="width: {percentage}%" aria-valuenow="{percentage}" aria-valuemin="0" aria-valuemax="100">{fitness_name}: {value}</div>
                            </div>
                        '''
        progress_bars = ''
        for idx, fitness in enumerate(solution.fitness_functions):
            progress_bars += progress_string.format(percentage=np.round((1 - fitness.value) * 100, 2),
                                                    fitness_name=fitness.function.get_name(),
                                                    value=np.round(1 - fitness.value, 2),
                                                    color=self.bg_colors[idx % len(self.bg_colors)])
        return progress_bars

    def report(self, solution, run, algorithm, write_to_html=True):
        header = ['Day', 'Menu', 'Energy', 'P_Energy', 'Protein', 'P_Protein', 'Fat', 'P_Fat']
        df = pd.DataFrame(columns=header)
        df.columns = header
        float_format = '{:.2f}'
        float_format_percent = '%{:.2f}'
        for idx, day in enumerate(solution.days):
            meal = day.dish_types[constants.FOOD_INDEX]
            energy = np.round(day.dish_types[constants.ENERGY_INDEX].sum(), 4)
            cho = np.round(day.dish_types[constants.CHO_INDEX].sum(), 4)
            protein = np.round(day.dish_types[constants.PROTEIN_INDEX].sum(), 4)
            fat = np.round(day.dish_types[constants.FAT_INDEX].sum(), 4)

            data = {'Day': idx + 1,
                    'Menu': '\\n'.join(meal),
                    'Energy': float_format.format(energy),
                    'P_Energy': float_format_percent.format((energy / self.config.ENERGY) * 100),
                    'Cho': float_format.format(cho),
                    'P_Cho': float_format_percent.format((cho / self.config.CHO) * 100),
                    'Protein': float_format.format(protein),
                    'P_Protein': float_format_percent.format((protein / self.config.PROTEIN) * 100),
                    'Fat': float_format.format(fat),
                    'P_Fat': float_format_percent.format((fat / self.config.FAT) * 100)}
            df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        out = df.style.apply(self.is_in_range, color='green',
                             subset=["P_Energy", "P_Protein", "P_Fat"]).set_table_attributes(
            'class="table table-striped text-center"')
        if write_to_html:
            with open("{}_{}_{}.html".format(self.html_file_path, run, algorithm), 'w', encoding='utf-8') as f:
                f.write(self.html_string.format(table=out.to_html().replace("\\n", "<br>"),
                                                progress_bars=self.generate_progress_bars(solution)))
        else:
            return self.html_string.format(table=out.to_html().replace("\\n", "<br>"),
                                           progress_bars=self.generate_progress_bars(solution))

    def show_and_save_plot(self, problem, res, run, algorithm):
        plot = Scatter()
        plot.add(problem.pareto_front(), plot_type="line", color="black", alpha=0.7)
        plot.add(res.F, color="red")
        plot.tight_layout = True
        plot.save("{}_{}_{}.png".format(self.fig_file_path, algorithm, run))
        if self.config.SHOW_PLOT:
            plot.show()
        else:
            plot.__del__()

# 최적화 지표 그래프 저장(다양한 다목적 최적화 지표들을 그래프로 저장) > 알고리즘 성능 수치적으로 분석 가능
    def show_and_save_metric_plots(self, res, algorithm, run):
        from pymoo.indicators.igd_plus import IGDPlus

        n_evals = []  # corresponding number of function evaluations\
        hist_F = []  # the objective space values in each generation

        for algo in res.history:
            # store the number of function evaluations
            n_evals = n_evals + [algo.evaluator.n_eval]
            # retrieve the optimum from the algorithm
            opt = algo.opt
            # print("✅ 개체 수:", len(opt))
            # print("✅ opt.get('F'):", opt.get("F"))
            # print("✅ opt.get('feasible'):", opt.get("feasible"))
            # filter out only the feasible and append and objective space values
            feas = np.where(opt.get("feasible"))[0]
            hist_F = hist_F + [opt.get("F")[feas]]

        opt = np.array([np.mean(e.opt[0].F) for e in res.history])
        hypervolume_metric = Hypervolume(ref_point=[1] * self.config.FITNESS_FUNCTIONS.__len__())
        gd_metric = GD(pf=np.array([0] * self.config.FITNESS_FUNCTIONS.__len__()), zero_to_one=False)
        gd_p_metric = GDPlus(pf=np.array([0] * self.config.FITNESS_FUNCTIONS.__len__()), zero_to_one=False)
        igd_metric = IGD(pf=np.array([0] * self.config.FITNESS_FUNCTIONS.__len__()), zero_to_one=False)
        igd_p_metric = IGDPlus(pf=np.array([0] * self.config.FITNESS_FUNCTIONS.__len__()), zero_to_one=False)

        # # 📌 여기서 디버깅!
        # print("📌 GD 계산 디버깅 ------------------")
        # for i, (_F, eval_num) in enumerate(zip(hist_F, n_evals)):
        #     print(f"📘 Generation {i+1} - Function Evaluations: {eval_num}")
        #     print("F 값:\n", _F)
        #     print("→ GD:", gd_metric.do(_F))
        #     print("→ GD+:", gd_p_metric.do(_F))
        #     print("→ IGD:", igd_metric.do(_F))
        #     print("→ IGD+:", igd_p_metric.do(_F))
        #     print("-" * 40)
            
        hypervolume = [hypervolume_metric.do(_F) for _F in hist_F]
        gd = [gd_metric.do(_F) for _F in hist_F]
        gd_p = [gd_p_metric.do(_F) for _F in hist_F]
        igd = [igd_metric.do(_F) for _F in hist_F]
        igd_p = [igd_p_metric.do(_F) for _F in hist_F]

        self.draw_metric_plot(algorithm, n_evals, hypervolume, "Avg. Hypervolume of Pop",
                              "Hypervolume", "{}_{}.png".format(self.hyp_file_path, run))
        self.draw_metric_plot(algorithm, n_evals, gd, "Avg. GD of Pop",
                              "GD", "{}_{}_{}.png".format(self.gd_file_path, algorithm, run))
        self.draw_metric_plot(algorithm, n_evals, gd_p, "Avg. GD+ of Pop",
                              "GD+", "{}_{}_{}.png".format(self.gd_p_file_path, algorithm, run))
        self.draw_metric_plot(algorithm, n_evals, igd, "Avg. IGD of Pop",
                              "IGD", "{}_{}_{}.png".format(self.igd_file_path, algorithm, run))
        self.draw_metric_plot(algorithm, n_evals, igd_p, "Avg. IGD+ of Pop",
                              "IGD+", "{}_{}_{}.png".format(self.igd_p_file_path, algorithm, run))
        self.conv_plot(algorithm, n_evals, opt, run)


    def draw_metric_plot(self, algorithm, n_evals, result, title, metric_name, save_path):
        print(f"[CHECK] {metric_name} 최소값: {np.min(result)}")
        print(f"[DEBUG] result 타입: {type(result)}")
        print(f"[DEBUG] 값들: {result}")
        print(f"[DEBUG] 로그 조건 결과: {np.all(np.array(result) > 0)}")
        plt.clf()
        plt.plot(n_evals, result, color='black', lw=0.7, label=title)
        plt.scatter(n_evals, result, facecolor="none", edgecolor='black', marker="p")
        plt.title("Convergence - {}".format(algorithm))
        plt.xlabel("Function Evaluations")
        plt.ylabel(metric_name, usetex=False)

            # ⚠️ 로그 스케일 조건 검사
        if np.all(np.array(result) > 0):
            plt.yscale("log")
        else:
            print(f"[WARNING] {metric_name} 값에 0 이하가 있어서 로그스케일 생략")
            
        #plt.yscale("log")
        plt.legend()
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        if self.config.SHOW_PLOT:
            plt.show()
        else:
            plt.clf()

# best solution 기록 및 평가 -> 각 세대별 가장 좋은 해를 기록
    def history_writer(self, run, res, algorithm, time):
        calculator = MetricCalculator()
        float_format = '{:.2f}'
        float_format_percent = '%{:.2f}'
        if not os.path.exists(self.pymoo_file_path) or os.path.getsize(self.pymoo_file_path) == 0:
            self.write_pymoo_header()
            
        for h in res.history:
            result = h.result()
            # 디버깅: 개체의 X 확인
            for ind in h.pop:
                # print("F value:", ind.F)
                # if (ind.F <= 0).any():
                #     print("⚠️ 음수 또는 0이 있음:", ind.F)
                # print(f"[DEBUG] Generation {h.n_iter} - ind.X type: {type(ind.X)}")

                val = ind.X
                
                # val이 리스트일 경우 내부 값 추출
                if isinstance(val, list) and len(val) > 0:
                    val = val[0]

                # val이 numpy array이고 첫 원소가 Solution인 경우
                if isinstance(val, np.ndarray) and len(val) > 0 and isinstance(val[0], Solution):
                    ind.data["solution"] = val[0]
                    ind.data["total_fitness"] = ind.F[0]
                    #print(f"[DEBUG] → solution 등록 완료 (type: {type(val[0])}, fitness: {ind.F[0]:.4f})")

                # val이 Solution 객체인 경우
                elif isinstance(val, Solution):
                    ind.data["solution"] = val
                    ind.data["total_fitness"] = ind.F[0]
                    #print(f"[DEBUG] → solution 등록 완료 (type: {type(val)}, fitness: {ind.F[0]:.4f})")

                else:
                    #print(f"[DEBUG] → 등록 실패: val type = {type(val)}, val = {val}")
                            # ✅ 등록 실패한 경우
                
            #ind_fitnesses = [x.total_fitness for x in result.X]
            best_ind = result.opt[0] 
            best_sol = best_ind.data["solution"] if "solution" in best_ind.data else None
            if best_sol is None:
                print(f"[SKIP] Generation {h.n_iter} has no solution")
                continue  # 해당 세대는 스킵
            #best_sol = result.X[np.argmin(ind_fitnesses)]
            hyp = calculator.calculate_hypervolume(result)
            gd = calculator.calculate_gd(result)
            gd_p = calculator.calculate_gd_p(result)
            igd = calculator.calculate_igd(result)
            igd_p = calculator.calculate_igd_p(result)
            energy = 0
            cho = 0
            protein = 0
            fat = 0
            for idx, day in enumerate(best_sol.days):
                energy += day.dish_types[constants.ENERGY_INDEX].sum()
                cho += day.dish_types[constants.CHO_INDEX].sum()
                protein += day.dish_types[constants.PROTEIN_INDEX].sum()
                fat += day.dish_types[constants.FAT_INDEX].sum()
            energy = energy / best_sol.days.__len__()
            cho = cho / best_sol.days.__len__()
            protein = protein / best_sol.days.__len__()
            fat = fat / best_sol.days.__len__()

            self.write_pymoo_row(algorithm, run, h.n_iter, h.evaluator.n_eval, best_sol.fitness_functions,
                     best_sol.total_fitness,
                     hyp, gd, gd_p, igd, igd_p, energy, cho, protein, fat, time)


#     def conv_plot(self, algorithm, n_evals, opt, run):
#         plt.clf()
#         plt.title("Convergence for {} algoritm".format(algorithm))
#         plt.plot(n_evals, opt, "--")
#         plt.yscale("log")
#         plt.xlabel("Function Evaluations")
#         plt.ylabel("Mean objective value")
#         plt.tight_layout()
#         plt.savefig("{}_{}_{}.png".format(self.conv_file_path, algorithm, run), dpi=300)
#         #if self.config.SHOW_PLOT:
#             #plt.show()
#         #else:
#         plt.clf()

# #JSON 포맷으로 솔루션 만들기
#     def generate_solution_json(self, solution):
#         response_dict = []
#         float_format = '{:.2f}'
#         float_format_percent = '%{:.2f}'
#         fitness_dict = []

#         for fitness in solution.fitness_functions:
#             fitness_dict += [{
#                 'name': fitness.function.get_name(),
#                 'value': np.round(1 - fitness.value, 2),
#                 'percentage': np.round((1 - fitness.value) * 100, 2)
#             }]

#         for idx, day in enumerate(solution.days):
#             meal = day.dish_types[constants.FOOD_INDEX]
#             energy = np.round(day.dish_types[constants.ENERGY_INDEX].sum(), 4)
#             cho = np.round(day.dish_types._get_column_array(constants.CHO_INDEX).sum(), 4)
#             protein = np.round(day.dish_types[constants.PROTEIN_INDEX].sum(), 4)
#             fat = np.round(day.dish_types[constants.FAT_INDEX].sum(), 4)
#             data = {'day': idx + 1,
#                     'menu': [str(m) for m in meal],
#                     'energy': float_format.format(energy),
#                     'p_energy': float_format_percent.format(energy / self.config.ENERGY * 100),
#                     'cho': float_format.format(cho),
#                     'p_cho': float_format_percent.format(cho / self.config.CHO * 100),
#                     'protein': float_format.format(protein),
#                     'p_protein': float_format_percent.format(protein / self.config.PROTEIN * 100),
#                     'fat': float_format.format(fat),
#                     'p_fat': float_format_percent.format(fat / self.config.FAT * 100),
#                     }
#             response_dict += [data]
#         return {
#             'data': response_dict,
#             'algorithm': self.config.ALGORITHM,
#             'fitnesses': fitness_dict,
#             'config': {
#                 'energy': self.config.ENERGY,
#                 'cho': self.config.CHO,
#                 'protein': self.config.PROTEIN,
#                 'fat': self.config.FAT,
#                 'tolerance': self.config.TOLERANCE,
#                 'operators': {
#                     'crossover': self.config.OPERATORS['crossover'].__class__.__name__,
#                     'mutation': self.config.OPERATORS['mutation'].__class__.__name__,
#                     'selection': self.config.OPERATORS['selection'].__class__.__name__,
#                 },
#                 'number_of_population': self.config.NUMBER_OF_POPULATION,
#                 'maximum_evaluation': self.config.MAXIMUM_EVALUATION,
#                 'random_seed': self.config.RANDOM_SEED
#             }
#         }
