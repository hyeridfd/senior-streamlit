import sys
import os
import matplotlib.pyplot as plt
import plotly.graph_objects as go
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

# 💡 matplotlib LaTeX 렌더링 오류 방지 설정
import matplotlib as mpl
mpl.rcParams['text.usetex'] = False
mpl.rcParams['mathtext.default'] = 'regular'

def get_algorithm(algorithm_name, number_of_population):
    evaluator = Evaluator(evaluate_values_of=["F", "G", "dF", "dG"])
    if algorithm_name == 'NSGA2':
        algorithm = NSGA2(pop_size=number_of_population,
                          sampling=MenuSampling(),
                          crossover=PymooCrossover(),
                          mutation=PymooMutation(),
                          eliminate_duplicates=Duplicates(),
                          evaluator=evaluator)
    elif algorithm_name == 'NSGA3':
        ref_dirs = get_reference_directions("das-dennis", 6, n_partitions=number_of_population)
        algorithm = NSGA3(pop_size=number_of_population,
                          ref_dirs=ref_dirs,
                          sampling=MenuSampling(),
                          crossover=PymooCrossover(),
                          mutation=PymooMutation(),
                          eliminate_duplicates=Duplicates(),
                          evaluator=evaluator)
    elif algorithm_name == 'SMSEMOA':
        algorithm = SMSEMOA(pop_size=number_of_population,
                            sampling=MenuSampling(),
                            crossover=PymooCrossover(),
                            mutation=PymooMutation(),
                            eliminate_duplicates=Duplicates(),
                            evaluator=evaluator)
    elif algorithm_name == 'MOEAD':
        ref_dirs = get_reference_directions("das-dennis", 6, n_partitions=number_of_population)
        algorithm = MOEAD(ref_dirs,
                          n_neighbors=number_of_population,
                          sampling=MenuSampling(),
                          crossover=PymooCrossover(),
                          mutation=PymooMutation(),
                          evaluator=evaluator)
    elif algorithm_name == 'AGEMOEA':
        algorithm = AGEMOEA(pop_size=number_of_population,
                            sampling=MenuSampling(),
                            crossover=PymooCrossover(),
                            mutation=PymooMutation(),
                            eliminate_duplicates=Duplicates(),
                            evaluator=evaluator)
    elif algorithm_name == 'SPEA2':
        algorithm = SPEA2(pop_size=number_of_population,
                          sampling=MenuSampling(),
                          crossover=PymooCrossover(),
                          mutation=PymooMutation(),
                          eliminate_duplicates=Duplicates(),
                          evaluator=evaluator)
    return algorithm

def run_optimization_from_streamlit(conf):
    problem = MenuPlanningProblem(argv=[], external_conf=conf)
    algorithm = get_algorithm(conf.ALGORITHM, conf.NUMBER_OF_POPULATION)
    reverse_preference_map = {0: "육류", 1: "수산물", 2: "채소", 3: "기타"}
    reporter = Reporter(conf)
    rand = Random(conf)
    seed_value = int(rand.random.integers(0, 10000))

    for run in range(conf.RUN_TIME):
        start = timeit.default_timer()
        res = minimize(problem, algorithm, ('n_evals', conf.MAXIMUM_EVALUATION), seed=seed_value, save_history=True, verbose=False)
        stop = timeit.default_timer()
        F_vals = res.F
        best_idx = np.argmin(np.sum(F_vals, axis=1)) if len(F_vals.shape) > 1 else np.argmin(F_vals)
        best_ind = res.X[best_idx]
        best_sol = best_ind[0] if isinstance(best_ind, np.ndarray) and isinstance(best_ind[0], Solution) else best_ind

        reporter.report(best_sol, run, algorithm.__class__.__name__)
        reporter.history_writer(run, res, algorithm.__class__.__name__, stop - start)
        reporter.show_and_save_plot(problem, res, run, algorithm.__class__.__name__)
        reporter.show_and_save_metric_plots(res, algorithm.__class__.__name__, run)

        if os.path.exists(reporter.pymoo_file_path):
            with open(reporter.pymoo_file_path, "rb") as f:
                st.download_button(label="📥 결과 CSV 다운로드",
                                   data=f,
                                   file_name=os.path.basename(reporter.pymoo_file_path),
                                   mime="text/csv",
                                   key=f"download_result_{uuid.uuid4()}")

        all_days_data = []
        for day_idx, day in enumerate(best_sol.days):
            df = day.dish_types.copy()
            df["Day"] = f"Day {day_idx + 1}"
            all_days_data.append(df)
        merged_df = pd.concat(all_days_data, ignore_index=True)
        merged_df["preference"] = merged_df["preference"].map(reverse_preference_map).fillna("정보 없음")
        preview_df = merged_df[["Day", "meal_name", "energy", "cho", "protein", "fat", "chewing_stage", "preference"]].rename(columns={
            "Day": "날짜", "meal_name": "음식명", "energy": "열량 (kcal)", "cho": "탄수화물 (g)", "protein": "단백질 (g)",
            "fat": "지방 (g)", "chewing_stage": "저작단계", "preference": "선호도"})
        st.markdown("## 🍴 개인 맞춤 식단표")
        st.dataframe(preview_df, use_container_width=True)
        st.markdown(f"### 🎯 총 적합도 점수: **{best_sol.total_fitness:.4f}**")

        st.subheader("🥗 식단 설명")
        for day_idx, day in enumerate(best_ind.days):
            st.markdown(f"**Day {day_idx + 1}**")
            day_description = ""
            day_energy = 0
            day_cho = 0
            day_protein = 0
            day_fat = 0

            for _, row in day.dish_types.iterrows():
                pref_kor = reverse_preference_map.get(row['preference'], "정보없음")
                day_description += f"- {row['meal_name']} (열량: {row['energy']:.2f} kcal, 탄수화물: {row['cho']:.2f}g, 단백질: {row['protein']:.2f}g, 지방: {row['fat']:.2f}g, 저작단계: {row['chewing_stage']}, 선호도: {pref_kor})\n"
                day_energy += row['energy']
                day_cho += row['cho']
                day_protein += row['protein']
                day_fat += row['fat']
            st.text(day_description)
            st.write(f"**Day {day_idx+1} 총 영양소:** 열량 {day_energy:.2f} kcal, 탄수화물 {day_cho:.2f}g, 단백질 {day_protein:.2f}g, 지방 {day_fat:.2f}g")

        st.markdown("## 📊 영양소 섭취량")

        # 1. 데이터 구성
        daily_nutrients = {"Day": [], "Energy": [], "Cho": [], "Protein": [], "Fat": []}
        for day_idx, day in enumerate(best_sol.days):
            daily_nutrients["Day"].append(f"Day {day_idx + 1}")
            daily_nutrients["Energy"].append(day.dish_types["energy"].sum())
            daily_nutrients["Cho"].append(day.dish_types["cho"].sum())
            daily_nutrients["Protein"].append(day.dish_types["protein"].sum())
            daily_nutrients["Fat"].append(day.dish_types["fat"].sum())
        
        df_nutrients = pd.DataFrame(daily_nutrients)
        
        # 2. Streamlit column으로 가로 배치
        cols = st.columns(4)
        
        nutrient_keys = [("Energy", "kcal", "Energy (kcal)"),
                         ("Cho", "cho", "Carbs (g)"),
                         ("Protein", "protein", "Protein (g)"),
                         ("Fat", "fat", "Fat (g)")]
        
        for i, (key, bound_key, label) in enumerate(nutrient_keys):
            min_val, max_val = conf.NUTRIENT_BOUNDS[bound_key]
            fig = go.Figure()
            
            # 바 그래프
            fig.add_trace(go.Bar(
                x=df_nutrients["Day"],
                y=df_nutrients[key],
                name=label,
                marker_color='skyblue'
            ))
            
            # 최소선
            fig.add_trace(go.Scatter(
                x=df_nutrients["Day"],
                y=[min_val]*len(df_nutrients),
                mode='lines',
                name='Min',
                line=dict(color='blue', dash='dash')
            ))
        
            # 최대선
            fig.add_trace(go.Scatter(
                x=df_nutrients["Day"],
                y=[max_val]*len(df_nutrients),
                mode='lines',
                name='Max',
                line=dict(color='red', dash='dash')
            ))
            
            fig.update_layout(
                title=label,
                xaxis_title="Day",
                yaxis_title="Amount",
                height=350,
                margin=dict(t=50, l=30, r=30, b=30)
            )
            
            cols[i].plotly_chart(fig, use_container_width=True)
        
        st.caption("각 영양소 섭취량은 기준선 사이에 있으면 적절한 섭취입니다.")
