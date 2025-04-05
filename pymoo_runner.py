import sys
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt
from pymoo.algorithms.moo.age import AGEMOEA
from pymoo.algorithms.moo.dnsga2 import DNSGA2
from pymoo.algorithms.moo.moead import MOEAD
from pymoo.algorithms.moo.nsga2 import NSGA2, RankAndCrowdingSurvival, binary_tournament
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.algorithms.moo.rnsga2 import RNSGA2
from pymoo.algorithms.moo.sms import SMSEMOA
from pymoo.core.evaluator import Evaluator
from pymoo.operators.selection.tournament import TournamentSelection
from pymoo.optimize import minimize
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.visualization.scatter import Scatter
from helper import recorder
from helper.metric_calculator import MetricCalculator
from helper.random import Random
from helper.reporter import Reporter
from pymoo_operators.pymoocrossover import PymooCrossover
from pymoo_operators.duplicates import Duplicates
from pymoo_operators.menu_planning_problem import MenuPlanningProblem
from pymoo_operators.pymoomutation import PymooMutation
from pymoo_operators.menu_sampling import MenuSampling
import timeit
from helper.config import Config
from solution import Solution

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
    return algorithm


def run_optimization_from_streamlit(conf):
    print("\U0001F4E6 받은 Config 객체 속성들:", conf.__dict__)
    problem = MenuPlanningProblem(argv=[], external_conf=conf)
    algorithm = get_algorithm(conf.ALGORITHM, conf.NUMBER_OF_POPULATION)
    # 숫자 → 한글 선호도 매핑
    reverse_preference_map = {
        0: "육류",
        1: "수산물",
        2: "채소",
        3: "기타"
    }

    reporter = Reporter(conf)
    rand = Random(conf)
    seed_value = int(rand.random.integers(0, 10000))
    st.write(f"🎲 랜덤 Seed: {seed_value}")

    for run in range(conf.RUN_TIME):
        start = timeit.default_timer()
        res = minimize(problem,
                       algorithm,
                       ('n_evals', conf.MAXIMUM_EVALUATION),
                       seed=seed_value,
                       save_history=True,
                       verbose=False)
        stop = timeit.default_timer()

        for gen_idx, h in enumerate(res.history):
            best_fitness = float('inf')
            best_ind = None
            #st.markdown(f"### 📘 Generation {gen_idx + 1}")

            for i, ind in enumerate(h.pop):
                val = ind.X
                if isinstance(val, np.ndarray) and len(val) > 0:
                    val = val[0]
                if isinstance(val, tuple) and hasattr(val[0], "days"):
                    ind.data["solution"] = val[0]
                    ind.data["total_fitness"] = val[1]

                total_fitness = ind.data.get("total_fitness")
                if total_fitness is not None:
                    st.write(f"👤 개체 {i}: fitness = {total_fitness:.4f}")
                    print(f"[DEBUG] 개체 {i}의 total_fitness: {total_fitness}")
                    if total_fitness < best_fitness:
                        best_fitness = total_fitness
                        best_ind = ind.data["solution"]

                # ✅ 세대 내 최고 적합도 개체 출력
            if best_ind:
                st.success(f"🌟 Generation {gen_idx + 1} 최고 적합도: {best_fitness:.4f}")
                with st.expander("📅 미리보기 (Day 1)"):
                    for day_idx, day in enumerate(best_ind.days[:1]):
                        for _, row in day.dish_types.iterrows():
                            pref_kor = reverse_preference_map.get(row['preference'], "정보없음")
                            st.write(
                                f"- {row['meal_name']} "
                                f"(열량: {row['energy']} kcal, 탄수화물: {row['cho']}g, 단백질: {row['protein']}g, 지방: {row['fat']}g, 선호도: {pref_kor})"
                            )

        F_vals = res.F
        best_idx = np.argmin(np.sum(F_vals, axis=1)) if len(F_vals.shape) > 1 else np.argmin(F_vals)
        best_ind = res.X[best_idx]
        # Check if best_ind is a Solution object, if not, extract the Solution object
        if isinstance(best_ind, np.ndarray) and isinstance(best_ind[0], Solution):
            best_ind = best_ind[0]  # Get the Solution object


        if isinstance(best_ind, np.ndarray) and isinstance(best_ind[0], Solution):
            best_sol = best_ind[0]
        elif isinstance(best_ind, Solution):
            best_sol = best_ind
        else:
            raise ValueError("best_ind가 Solution 형태가 아닙니다.")

        reporter.report(best_sol, run, algorithm.__class__.__name__)
        reporter.history_writer(run, res, algorithm.__class__.__name__, stop - start)
        reporter.show_and_save_plot(problem, res, run, algorithm.__class__.__name__)
        reporter.show_and_save_metric_plots(res, algorithm.__class__.__name__, run)
        recorder.record(res)

        # ✅ 전체 5일치 식단표를 표로 출력
        all_days_data = []
        for day_idx, day in enumerate(best_sol.days):
            df = day.dish_types.copy()
            df["Day"] = f"Day {day_idx + 1}"
            all_days_data.append(df)

        merged_df = pd.concat(all_days_data, ignore_index=True)

        merged_df["preference"] = merged_df["preference"].map(reverse_preference_map).fillna("정보 없음")

        # 열 정렬 및 이름 변경
        preview_df = merged_df[["Day", "meal_name", "energy", "cho", "protein", "fat", "chewing_stage", "preference"]].rename(columns={
            "Day": "🗓️ 날짜",
            "meal_name": "🍱 음식명",
            "energy": "🔥 열량 (kcal)",
            "cho": "🍚 탄수화물 (g)",
            "protein": "🥩 단백질 (g)",
            "fat": "🫒 지방 (g)",
            "chewing_stage": "👄 저작단계",
            "preference": "🍽️ 선호도"
        })

        # 표 출력
        st.markdown("## 🍴 최적화된 5일치 식단표")
        st.dataframe(preview_df, use_container_width=True)

# 2. Display meal description
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

        # ✅ 하루별 영양소 섭취량 계산
        st.markdown("## 📊 일별 영양소 섭취량")
        daily_nutrients = {"Day": [], "Energy": [], "Cho": [], "Protein": [], "Fat": []}
        for day_idx, day in enumerate(best_sol.days):
            energy = day.dish_types["energy"].sum()
            cho = day.dish_types["cho"].sum()
            protein = day.dish_types["protein"].sum()
            fat = day.dish_types["fat"].sum()
            daily_nutrients["Day"].append(f"Day {day_idx + 1}")
            daily_nutrients["Energy"].append(energy)
            daily_nutrients["Cho"].append(cho)
            daily_nutrients["Protein"].append(protein)
            daily_nutrients["Fat"].append(fat)

        df_nutrients = pd.DataFrame(daily_nutrients)

        # ✅ 기준값 가져오기
        kcal_min, kcal_max = conf.NUTRIENT_BOUNDS["kcal"]
        cho_min, cho_max = conf.NUTRIENT_BOUNDS["cho"]
        protein_min, protein_max = conf.NUTRIENT_BOUNDS["protein"]
        fat_min, fat_max = conf.NUTRIENT_BOUNDS["fat"]

        fig, axes = plt.subplots(3, 1, figsize=(8, 10))

        nutrient_info = [
            ("Energy", kcal_min, kcal_max, "energy(kcal)"),
            ("Cho", cho_min, cho_max, "cho(g)"),
            ("Protein", protein_min, protein_max, "protein(g)"),
            ("Fat", fat_min, fat_max, "fat(g)")
        ]

        # 영양소 적합도 시각화 추가
        for ax, (key, min_val, max_val, title) in zip(axes, nutrient_info):
            ax.bar(df_nutrients["Day"], df_nutrients[key], color="pink")
            ax.axhline(min_val, color='blue', linestyle='--', label='MAX')
            ax.axhline(max_val, color='red', linestyle='--', label='MIN')
            ax.set_title(title)
            ax.set_ylabel("AMOUNT")
            ax.legend()

        plt.tight_layout()
        st.pyplot(fig)

        # # ✅ 각 일별 영양소 적합도 표시
        # st.markdown("## 🥇 각 날의 영양소 적합도")
        # fit_scores = []
        # for day_idx, day in enumerate(best_sol.days):
        #     score = 0
        #     # Calculate fit score based on nutrient range
        #     if kcal_min <= day.dish_types["energy"].sum() <= kcal_max:
        #         score += 1
        #     if protein_min <= day.dish_types["protein"].sum() <= protein_max:
        #         score += 1
        #     if fat_min <= day.dish_types["fat"].sum() <= fat_max:
        #         score += 1
        #     fit_scores.append(score)

        # 적합도 그래프
        #st.bar_chart(fit_scores)

        return best_sol
    
        # # ✅ 하루별 영양소 섭취량 계산
        # daily_nutrients = {"Day": [], "Energy": [], "Protein": [], "Fat": []}
        # for day_idx, day in enumerate(best_sol.days):
        #     energy = day.dish_types["energy"].sum()
        #     protein = day.dish_types["protein"].sum()
        #     fat = day.dish_types["fat"].sum()
        #     daily_nutrients["Day"].append(f"Day {day_idx + 1}")
        #     daily_nutrients["Energy"].append(energy)
        #     daily_nutrients["Protein"].append(protein)
        #     daily_nutrients["Fat"].append(fat)

        # df_nutrients = pd.DataFrame(daily_nutrients)

        # # ✅ 기준값 가져오기
        # kcal_min, kcal_max = conf.NUTRIENT_BOUNDS["kcal"]
        # protein_min, protein_max = conf.NUTRIENT_BOUNDS["protein"]
        # fat_min, fat_max = conf.NUTRIENT_BOUNDS["fat"]

        # st.markdown("## 일별 영양소 섭취량 vs 기준")

        # fig, axes = plt.subplots(3, 1, figsize=(8, 10))

        # nutrient_info = [
        #     ("Energy", kcal_min, kcal_max, "🔥 에너지 (kcal)"),
        #     ("Protein", protein_min, protein_max, "🥩 단백질 (g)"),
        #     ("Fat", fat_min, fat_max, "🫒 지방 (g)")
        # ]

        # for ax, (key, min_val, max_val, title) in zip(axes, nutrient_info):
        #     ax.bar(df_nutrients["Day"], df_nutrients[key], color="skyblue")
        #     ax.axhline(min_val, color='orange', linestyle='--', label='하한선')
        #     ax.axhline(max_val, color='green', linestyle='--', label='상한선')
        #     ax.set_title(title)
        #     ax.set_ylabel("섭취량")
        #     ax.legend()

        # plt.tight_layout()
        # st.pyplot(fig)

        # return best_sol
