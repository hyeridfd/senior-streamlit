import re

def parse_user_input(text: str):
    try:
        # 성별
        sex = "female" if "female" in text.lower() or "여" in text else "male"

        # 나이 (예: 70)
        age = int(re.search(r"(\d{2})(?=\s*,)", text).group(1))

        # 체중 (예: 60kg)
        weight = float(re.search(r"(\d+)(?=kg)", text).group(1))

        # 키 (예: 1.8m)
        height = float(re.search(r"(\d+\.\d+)(?=m)", text).group(1))

        # 신체 활동 계수 (예: 1.5)
        pa_match = re.search(r"\b1\.\d+\b", text)
        if pa_match:
            pa = float(pa_match.group(0))

        # 허리둘레 (예: 100cm)
        waist = int(re.search(r"(\d+)(?=cm)", text).group(1))

        # 선호 식재료
        if "육류" in text:
            preference = "육류"
        elif "해산물" in text:
            preference = "해산물"
        elif "채소" in text:
            preference = "채소"
        else:
            preference = "선호 없음"

        user_info = {
            "sex": sex,
            "age": age,
            "weight": weight,
            "height": height,
            "pa": pa,
            "waist": waist,
        }

        return user_info, preference

    except Exception as e:
        raise ValueError(f"입력 파싱에 실패했습니다: {e}")