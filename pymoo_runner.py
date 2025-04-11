
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import pandas as pd
from matplotlib import pyplot as plt
from pymoo.algorithms.moo.age import AGEMOEA
from pymoo.algorithms.moo.dnsga2 import DNSGA2
from pymoo.algorithms.moo.moead import MOEAD
from pymoo.algorithms.moo.nsga2 import NSGA2, RankAndCrowdingSurvival, binary_tournament
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.algorithms.moo.rnsga2 import RNSGA2
from pymoo.algorithms.moo.sms import SMSEMOA
from pymoo.algorithms.moo.spea2 import SPEA2
from pymoo.core.evaluator import Evaluator
from pymoo.operators.selection.tournament import TournamentSelection
from pymoo.optimize import minimize
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.visualization.scatter import Scatter
from helper.metric_calculator import MetricCalculator
from helper.random import Random
from helper.reporter import Reporter
from pymoo_operators.pymoocrossover import PymooCrossover
from pymoo_operators.duplicates import Duplicates
from pymoo_operators.menu_planning_problem import MenuPlanningProblem
from pymoo_operators.pymoomutation import PymooMutation
from pymoo_operators.menu_sampling import MenuSampling
import timeit
import uuid
from helper.config import Config
from solution import Solution

import matplotlib as mpl
mpl.rcParams['text.usetex'] = False
mpl.rcParams['mathtext.default'] = 'regular'


def get_algorithm(algorithm_name, number_of_population):
    evaluator = Evaluator(evaluate_values_of=["F", "G", "dF", "dG"])

    if algorithm_name == 'NSGA2':
        return NSGA2(pop_size=number_of_population, sampling=MenuSampling(),
                     crossover=PymooCrossover(), mutation=PymooMutation(),
                     eliminate_duplicates=Duplicates(), evaluator=evaluator)
    elif algorithm_name == 'NSGA3':
        ref_dirs = get_reference_directions("das-dennis", 6, n_partitions=number_of_population)
        return NSGA3(pop_size=number_of_population, ref_dirs=ref_dirs,
                     sampling=MenuSampling(), crossover=PymooCrossover(),
                     mutation=PymooMutation(), eliminate_duplicates=Duplicates(),
                     evaluator=evaluator)
    elif algorithm_name == 'SMSEMOA':
        return SMSEMOA(pop_size=number_of_population, sampling=MenuSampling(),
                       crossover=PymooCrossover(), mutation=PymooMutation(),
                       eliminate_duplicates=Duplicates(), evaluator=evaluator)
    elif algorithm_name == 'MOEAD':
        ref_dirs = get_reference_directions("das-dennis", 6, n_partitions=number_of_population)
        return MOEAD(ref_dirs, n_neighbors=number_of_population,
                     sampling=MenuSampling(), crossover=PymooCrossover(),
                     mutation=PymooMutation(), evaluator=evaluator)
    elif algorithm_name == 'AGEMOEA':
        return AGEMOEA(pop_size=number_of_population, sampling=MenuSampling(),
                       crossover=PymooCrossover(), mutation=PymooMutation(),
                       eliminate_duplicates=Duplicates(), evaluator=evaluator)
    elif algorithm_name == 'SPEA2':
        return SPEA2(pop_size=number_of_population, sampling=MenuSampling(),
                     crossover=PymooCrossover(), mutation=PymooMutation(),
                     eliminate_duplicates=Duplicates(), evaluator=evaluator)


def run_optimization_from_streamlit(conf):
    problem = MenuPlanningProblem(argv=[], external_conf=conf)
    algorithm = get_algorithm(conf.ALGORITHM, conf.NUMBER_OF_POPULATION)

    reverse_preference_map = {0: "육류", 1: "수산물", 2: "채소", 3: "기타"}
    reporter = Reporter(conf)
    rand = Random(conf)
    seed_value = int(rand.random.integers(0, 10000))

    for run in range(conf.RUN_TIME):
        start = timeit.default_timer()
        res = minimize(problem, algorithm, ('n_evals', conf.MAXIMUM_EVALUATION),
                       seed=seed_value, save_history=True, verbose=False)
        stop = timeit.default_timer()

        best_sol = None
        best_fitness = float('inf')

        for gen_idx, h in enumerate(res.history):
            for ind in h.pop:
                val = ind.X
                if isinstance(val, Solution):
                    sol = val
                elif isinstance(val, np.ndarray) and isinstance(val[0], Solution):
                    sol = val[0]
                elif isinstance(val, tuple) and hasattr(val[0], "days"):
                    sol = val[0]
                else:
                    continue

                fitness = getattr(sol, 'total_fitness', None)
                if fitness is not None and fitness < best_fitness:
                    best_fitness = fitness
                    best_sol = sol

        if best_sol is None:
            st.error("최적화 결과에서 유효한 해를 찾을 수 없습니다.")
            return

        reporter.report(best_sol, run, algorithm.__class__.__name__)
        reporter.history_writer(run, res, algorithm.__class__.__name__, stop - start)
        reporter.show_and_save_plot(problem, res, run, algorithm.__class__.__name__)
        reporter.show_and_save_metric_plots(res, algorithm.__class__.__name__, run)

        if os.path.exists(reporter.pymoo_file_path):
            with open(reporter.pymoo_file_path, "rb") as f:
                unique_key = f"download_result_{uuid.uuid4()}"
                st.download_button("📥 결과 CSV 다운로드", data=f,
                                   file_name=os.path.basename(reporter.pymoo_file_path),
                                   mime="text/csv", key=unique_key)

        all_days_data = []
        for day_idx, day in enumerate(best_sol.days):
            df = day.dish_types.copy()
            df["Day"] = f"Day {day_idx + 1}"
            all_days_data.append(df)

        merged_df = pd.concat(all_days_data, ignore_index=True)
        merged_df["preference"] = merged_df["preference"].map(reverse_preference_map).fillna("정보 없음")

        preview_df = merged_df[["Day", "meal_name", "energy", "cho", "protein", "fat", "chewing_stage", "preference"]].rename(columns={
            "Day": "날짜", "meal_name": "음식명", "energy": "열량 (kcal)", "cho": "탄수화물 (g)",
            "protein": "단백질 (g)", "fat": "지방 (g)", "chewing_stage": "저작단계", "preference": "선호도"
        })

        st.markdown("## 🍴 개인 맞춤 식단표")
        st.dataframe(preview_df, use_container_width=True)
        st.markdown(f"### 🎯 총 적합도 점수: **{best_sol.total_fitness:.4f}**")

        st.subheader("🥗 식단 설명")
        for day_idx, day in enumerate(best_sol.days):
            st.markdown(f"**Day {day_idx + 1}**")
            for _, row in day.dish_types.iterrows():
                pref_kor = reverse_preference_map.get(row['preference'], "정보없음")
                st.markdown(f"- {row['meal_name']} (열량: {row['energy']:.2f} kcal, 탄수: {row['cho']:.2f}g, 단백: {row['protein']:.2f}g, 지방: {row['fat']:.2f}g, 저작단계: {row['chewing_stage']}, 선호도: {pref_kor})")

        st.markdown("## 📊 영양소 섭취량")
        daily_nutrients = {"Day": [], "Energy": [], "Cho": [], "Protein": [], "Fat": []}
        for day_idx, day in enumerate(best_sol.days):
            daily_nutrients["Day"].append(f"Day {day_idx + 1}")
            daily_nutrients["Energy"].append(day.dish_types["energy"].sum())
            daily_nutrients["Cho"].append(day.dish_types["cho"].sum())
            daily_nutrients["Protein"].append(day.dish_types["protein"].sum())
            daily_nutrients["Fat"].append(day.dish_types["fat"].sum())

        df_nutrients = pd.DataFrame(daily_nutrients)

        kcal_min, kcal_max = conf.NUTRIENT_BOUNDS["kcal"]
        cho_min, cho_max = conf.NUTRIENT_BOUNDS["cho"]
        protein_min, protein_max = conf.NUTRIENT_BOUNDS["protein"]
        fat_min, fat_max = conf.NUTRIENT_BOUNDS["fat"]

        fig, axes = plt.subplots(4, 1, figsize=(8, 12))
        nutrient_info = [
            ("Energy", kcal_min, kcal_max, "energy(kcal)"),
            ("Cho", cho_min, cho_max, "cho(g)"),
            ("Protein", protein_min, protein_max, "protein(g)"),
            ("Fat", fat_min, fat_max, "fat(g)")
        ]

        for ax, (key, min_val, max_val, title) in zip(axes, nutrient_info):
            ax.bar(df_nutrients["Day"], df_nutrients[key], color="skyblue")
            ax.axhline(max_val, color='red', linestyle='--', label='MAX')
            ax.axhline(min_val, color='blue', linestyle='--', label='MIN')
            ax.set_title(title)
            ax.set_ylabel("AMOUNT")
            ax.legend()

        plt.tight_layout()
        st.pyplot(fig)
