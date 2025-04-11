import streamlit as st
import traceback
import openai

# 🔽 아래 모듈들은 당신이 미리 구현한 걸 가져와 사용합니다
from llm import get_ai_response
from parser import parse_user_input
from nutrient import get_lunch_nutrient_ranges, get_lunch_nutrient_profile
from helper.config import Config
from pymoo_runner import run_optimization_from_streamlit

# 초기 설정
st.set_page_config(page_title="시니어 맞춤형 푸드 솔루션", page_icon="🧓")

st.image("./logo.png", width=150)

st.markdown(
    '<h3 style="color:#226f54; font-size:38px; font-weight:bold;">시니어 맞춤형 푸드 솔루션</h3>',
    unsafe_allow_html=True
)

st.sidebar.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        background-color: #f7fadb !important;
    }

    div.stButton > button {
        padding: 1rem 1.5rem;
        font-size: 24px !important;
        font-weight: 600;
        border-radius: 12px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        transition: all 0.2s ease-in-out;
        background-color: #eaf291;
        border: 1px solid #d6d84c;
        color: #444;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        transition: all 0.2s ease-in-out;
    }

    div.stButton > button:hover {
        background-color: #dce75b;
        border: 1px solid #a3a93d;
        color: #2e2e2e;
    }

    div.stButton > button:focus {
        outline: none;
        box-shadow: none;
        border: 1px solid #d0d0d0;
    }

    .selected-button {
        background-color: #B8BF3D !important;
        border: 1px solid #90972b !important;
        color: white !important;
    }

    h3.sidebar-title {
        color: #B8BF3D;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.caption("시니어의 건강 상태와 저작 능력을 고려한 식단 추천과 라이프스타일 코칭을 제공합니다.")

openai_api_key = st.secrets["OPENAI_API_KEY"]
pinecone_api_key = st.secrets["PINECONE_API_KEY"]

#print("✅ openai version:", openai.__version__)

# 세션 상태 초기화
if 'message_list' not in st.session_state:
    st.session_state.message_list = []

# 세션 초기화
if 'mode' not in st.session_state:
    st.session_state.mode = "🥗 개인 맞춤 식단 추천"

st.sidebar.markdown(
    '<h3 style="color:#226f54; font-size:28px; font-weight:bold; margin-bottom:10px;">모드 선택</h3>',
    unsafe_allow_html=True
)

st.sidebar.markdown("무엇을 도와드릴까요?")

if st.sidebar.button("🥗 개인 맞춤 식단 추천", use_container_width=True):
    st.session_state.mode = "🥗 개인 맞춤 식단 추천"
    st.rerun()

if st.sidebar.button("💬 라이프스타일 코칭", use_container_width=True):
    st.session_state.mode = "💬 라이프스타일 코칭"
    st.rerun()
    
# ================================
# 🥗 식단 최적화 모드
# ================================

if st.session_state.mode == "🥗 개인 맞춤 식단 추천":
    st.markdown(
        '<h3 style="color:#495057; font-size:25px; font-weight:600; margin-top:40px; margin-bottom:20px">👩🏻‍⚕️ 맞춤 식단 추천을 위해 필요한 정보를 입력해 주세요</h3>',
        unsafe_allow_html=True
    )

    with st.form("diet_form"):
        col1, col2 = st.columns(2)

        with col1:
            age = st.number_input("나이", min_value=0, max_value=120, value=67)
            sex = st.selectbox("성별", ["남성", "여성"])
            height = st.number_input("키 (m)", min_value=1.0, max_value=3.0, value=1.65)
            preference = st.selectbox("선호 식재료", ["육류", "수산물", "채소", "기타"])

        with col2:
            weight = st.number_input("체중 (kg)", min_value=20.0, max_value=200.0, value=66.0)
            pa = st.selectbox("활동수준", ["낮음", "보통", "활동적"], index=1)
            waist = st.number_input("허리둘레 (cm)", min_value=50.0, max_value=150.0, value=85.0)
            chewing_stage = st.selectbox("저작 단계", ["1단계", "2단계", "3단계"], index=0)
    
        submitted = st.form_submit_button("식단 설계 실행")


    if submitted:
        try:
            # 성별 및 활동량 매핑
            sex = "female" if sex == "여성" else "male"
            pa_map = {"낮음": 1.2, "보통": 1.4, "활동적": 1.6}
            pa = pa_map[pa]
            chewing_stage_value = int(chewing_stage[0])  # "1단계" → 1

            # 1. 영양 기준 계산
            kcal_range, carbs_range, protein_range, fat_range = get_lunch_nutrient_ranges(
                sex, age, weight, height, pa, waist
            )
            profile = get_lunch_nutrient_profile(sex, age, weight, height, pa, waist, preference, chewing_stage_value)

            st.subheader("🍽️ 한 끼 기준 영양 정보")
            st.text(profile)

            # 2. 최적화 실행
            external_targets = {
                "kcal": sum(kcal_range) / 2,
                "protein": sum(protein_range) / 2,
                "fat": sum(fat_range) / 2,
                "cho": sum(carbs_range) / 2,
                "chewing_stage": chewing_stage_value,
                "preference": preference
            }
            conf = Config(argv=[], external_targets=external_targets)

            st.info("⏳ 식단 설계 진행 중입니다...")
            best_solution = run_optimization_from_streamlit(conf)

        except Exception as e:
            st.error(f"❌ 오류 발생: {e}")
            st.text(traceback.format_exc())


# if st.session_state.mode == "🥗 개인 맞춤 식단 추천":
#     st.subheader("👩‍⚕️ 개인 정보를 입력해 주세요")
#     st.markdown(
#         "<p style='font-size:16px;'>성별, 나이, 체중, 키, 활동량, 허리둘레, 선호도, 저작단계를 입력해 주세요</p>",
#         unsafe_allow_html=True
#     )
#     user_input = st.text_input("예: 여성, 70, 60kg, 1.6m, 1.4, 85cm, 채소, 1단계")

#     if st.button("식단 최적화 실행"):
#         try:
#             values = user_input.replace("cm", "").replace("kg", "").replace("m", "").replace("단계", "").split(",")

#             sex = values[0].strip()
#             if sex == "여성":
#                 sex = "female"
#             elif sex == "남성":
#                 sex = "male"

#             age = int(values[1].strip())
#             weight = float(values[2].strip())
#             height = float(values[3].strip())
#             pa = float(values[4].strip())
#             waist = float(values[5].strip())
#             preference = values[6].strip()

#             preference_map = {
#                 "육류": 0,
#                 "수산물": 1,
#                 "채소": 2,
#                 "기타": 3
#             }
            
#             chewing_stage = values[7].strip()

#             # 1. 영양 기준 계산
#             kcal_range, carbs_range, protein_range, fat_range = get_lunch_nutrient_ranges(
#                 sex, age, weight, height, pa, waist
#             )
#             profile = get_lunch_nutrient_profile(sex, age, weight, height, pa, waist)

#             st.subheader("🍽️ 한 끼 기준 영양 정보")
#             st.text(profile)

#             # 2. 최적화 실행
#             external_targets = {
#                 "kcal": sum(kcal_range) / 2,
#                 "protein": sum(protein_range) / 2,
#                 "fat": sum(fat_range) / 2,
#                 "cho": sum(carbs_range) / 2,
#                 "chewing_stage": int(chewing_stage),
#                 "preference": preference
#             }
#             conf = Config(argv=[], external_targets=external_targets)

#             st.info("⏳ 식단 설계 진행 중입니다...")
#             best_solution = run_optimization_from_streamlit(conf)

#         #     # 3. 결과 출력
#         #     st.success("✅ 최적 식단이 도출되었습니다!")
#         #     for day_idx, day in enumerate(best_solution.days):
#         #         st.markdown(f"**Day {day_idx + 1}**")
#         #         for _, row in day.dish_types.iterrows():
#         #             st.write(
#         #                 f"- {row['meal_name']} (열량: {row['energy']} kcal, 탄수화물: {row['cho']}g, 단백질: {row['protein']}g, 지방: {row['fat']}g, 저작단계: {row['chewing_stage']})"
#         #             )

#         except Exception as e:
#             st.error(f"❌ 오류 발생: {e}")
#             st.text(traceback.format_exc())

# ================================
# 💬 라이프스타일 코칭 모드
# ================================
else:
    st.subheader("💬 건강, 영양, 생활습관에 대해 물어보세요!")

    for message in st.session_state.message_list:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_question := st.chat_input("예: 고령자에게 좋은 단백질 식품은 뭐가 있나요?"):
        with st.chat_message("user"):
            st.markdown(user_question)
        st.session_state.message_list.append({"role": "user", "content": user_question})

        with st.spinner("🔍 답변 생성 중..."):
            ai_response = get_ai_response(
                user_question,
                api_key=st.secrets["OPENAI_API_KEY"],
                pinecone_key=st.secrets["PINECONE_API_KEY"],
                stream=True
            )
            full_text = ""
            with st.chat_message("ai"):
                response_placeholder = st.empty()
                for chunk in ai_response:
                    full_text += chunk
                    response_placeholder.markdown(full_text)
            st.session_state.message_list.append({"role": "ai", "content": full_text})
