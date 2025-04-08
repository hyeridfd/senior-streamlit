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
st.set_page_config(page_title="시니어 맞춤형 프리미엄 헬스케어 솔루션", page_icon="🧓")
st.title("시니어 맞춤형 프리미엄 헬스케어 솔루션")
st.caption("식단 최적화와 라이프스타일 코칭을 한 번에!")

openai_api_key = st.secrets["OPENAI_API_KEY"]
pinecone_api_key = st.secrets["PINECONE_API_KEY"]

print("✅ openai version:", openai.__version__)

# 세션 상태 초기화
if 'message_list' not in st.session_state:
    st.session_state.message_list = []

if 'mode' not in st.session_state:
    st.session_state.mode = "🥗 개인 맞춤 식단 추천"   

import streamlit as st

# 세션 초기화
if 'mode' not in st.session_state:
    st.session_state.mode = "🥗 개인 맞춤 식단 추천"

# CSS 스타일 삽입
st.sidebar.markdown("""
    <style>
    .custom-button {
        padding: 1rem 1.5rem;
        font-size: 22px;
        font-weight: 600;
        border-radius: 12px;
        margin-bottom: 0.5rem;
        width: 100%;
        border: 1px solid #d0d0d0;
        color: #000000;
        background-color: #f0f2f6;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        transition: all 0.2s ease-in-out;
    }
    .custom-button:hover {
        background-color: #e3f2fd;
        border-color: #2196f3;
        color: #0d47a1;
    }
    .custom-button.selected {
        background-color: #1976d2 !important;
        border-color: #0d47a1 !important;
        color: white !important;
    }
    .custom-button:focus {
        outline: none;
        box-shadow: none;
    }
    </style>
""", unsafe_allow_html=True)

# HTML로 버튼 렌더링
def render_sidebar_button(label, emoji, mode_key):
    selected_class = "selected" if st.session_state.mode == mode_key else ""
    button_html = f"""
        <form action="" method="post">
            <button class="custom-button {selected_class}" name="mode" type="submit" value="{mode_key}">{emoji} {label}</button>
        </form>
    """
    st.sidebar.markdown(button_html, unsafe_allow_html=True)

# 버튼 UI
st.sidebar.title("모드 선택")
st.sidebar.markdown("무엇을 도와드릴까요?")
render_sidebar_button("개인 맞춤 식단 추천", "🥗", "🥗 개인 맞춤 식단 추천")
render_sidebar_button("라이프스타일 코칭", "💬", "💬 라이프스타일 코칭")

if st.session_state.get("mode"):
    st.session_state.mode = st.session_state["mode"]

# ================================
# 🥗 식단 최적화 모드
# ================================
if mode == "🥗 개인 맞춤 식단 추천":
    st.subheader("👩‍⚕️ 개인 정보를 입력해 주세요")
    st.markdown(
        "<p style='font-size:16px;'>성별, 나이, 체중, 키, 활동량, 허리둘레, 선호도, 저작단계를 입력해 주세요</p>",
        unsafe_allow_html=True
    )
    user_input = st.text_input("예: 여성, 70, 60kg, 1.6m, 1.4, 85cm, 채소, 1단계")

    if st.button("식단 최적화 실행"):
        try:
            values = user_input.replace("cm", "").replace("kg", "").replace("m", "").replace("단계", "").split(",")

            sex = values[0].strip()
            if sex == "여성":
                sex = "female"
            elif sex == "남성":
                sex = "male"

            age = int(values[1].strip())
            weight = float(values[2].strip())
            height = float(values[3].strip())
            pa = float(values[4].strip())
            waist = float(values[5].strip())
            preference = values[6].strip()

            preference_map = {
                "육류": 0,
                "수산물": 1,
                "채소": 2,
                "기타": 3
            }
            
            chewing_stage = values[7].strip()

            # 1. 영양 기준 계산
            kcal_range, carbs_range, protein_range, fat_range = get_lunch_nutrient_ranges(
                sex, age, weight, height, pa, waist
            )
            profile = get_lunch_nutrient_profile(sex, age, weight, height, pa, waist)

            st.subheader("🍽️ 한 끼 기준 영양 정보")
            st.text(profile)

            # 2. 최적화 실행
            external_targets = {
                "kcal": sum(kcal_range) / 2,
                "protein": sum(protein_range) / 2,
                "fat": sum(fat_range) / 2,
                "cho": sum(carbs_range) / 2,
                "chewing_stage": int(chewing_stage),
                "preference": preference
            }
            conf = Config(argv=[], external_targets=external_targets)

            st.info("⏳ 식단 최적화 진행 중입니다...")
            best_solution = run_optimization_from_streamlit(conf)

        #     # 3. 결과 출력
        #     st.success("✅ 최적 식단이 도출되었습니다!")
        #     for day_idx, day in enumerate(best_solution.days):
        #         st.markdown(f"**Day {day_idx + 1}**")
        #         for _, row in day.dish_types.iterrows():
        #             st.write(
        #                 f"- {row['meal_name']} (열량: {row['energy']} kcal, 탄수화물: {row['cho']}g, 단백질: {row['protein']}g, 지방: {row['fat']}g, 저작단계: {row['chewing_stage']})"
        #             )

        except Exception as e:
            st.error(f"❌ 오류 발생: {e}")
            st.text(traceback.format_exc())

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
