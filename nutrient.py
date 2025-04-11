def calculate_eer(sex, age, weight, height, pa):
    if sex in ['남성', 'male']:
        eer = 662 - (9.53 * age) + pa * (15.91 * weight + 539.6 * height)
    elif sex in ['여성', 'female']:
        eer = 354 - (6.91 * age) + pa * (9.36 * weight + 726 * height)
    else:
        raise ValueError("Invalid sex")
    return eer

def calculate_daily_intake(sex, age, weight, height, pa, waist):
    bmi = weight / (height ** 2)
    eer = calculate_eer(sex, age, weight, height, pa)
    if bmi >= 25:
        daily_intake_range = (eer - 400, eer - 200)
    elif 23 <= bmi < 25:
        daily_intake_range = (eer - 400, eer - 200)
    elif 18.5 <= bmi < 23:
        if (sex in ['남성', 'male'] and waist >= 90) or (sex in ['여성', 'female'] and waist >= 85):
            daily_intake_range = (eer - 400, eer - 200)
        else:
            daily_intake_range = (eer + 300, eer + 500)
    else:
        daily_intake_range = (eer + 600, eer + 800)
    return daily_intake_range

def calculate_nutrient_distribution(daily_intake_range, sex, age):
    min_intake, max_intake = daily_intake_range
    carbs_min = min_intake * 0.55 / 4
    carbs_max = max_intake * 0.65 / 4
    if sex in ['남성', 'male']:
        protein_min = max(50, min_intake * 0.07 / 4)
    else:
        protein_min = max(40, min_intake * 0.07 / 4)
    protein_max = max_intake * 0.20 / 4
    fat_min = min_intake * 0.15 / 9
    fat_max = max_intake * 0.30 / 9
    return (carbs_min, carbs_max), (protein_min, protein_max), (fat_min, fat_max)

def calculate_fixed_meal_distribution(fixed_value):
    breakfast = fixed_value * 2 / 10
    lunch = fixed_value * 3 / 10
    dinner = fixed_value * 3 / 10
    snacks = fixed_value * 2 / 10
    return breakfast, lunch, dinner, snacks

def calculate_meal_distribution(daily_intake_range):
    min_intake, max_intake = daily_intake_range
    breakfast = (min_intake * 0.2, max_intake * 0.2)
    lunch = (min_intake * 0.3, max_intake * 0.3)
    dinner = (min_intake * 0.3, max_intake * 0.3)
    snacks = (min_intake * 0.2, max_intake * 0.2)
    return breakfast, lunch, dinner, snacks

def get_lunch_nutrient_ranges(sex, age, weight, height, pa, waist):
    daily_range = calculate_daily_intake(sex, age, weight, height, pa, waist)
    kcal_range = (
        calculate_fixed_meal_distribution(daily_range[0])[1],
        calculate_fixed_meal_distribution(daily_range[1])[1],
    )
    carbs_range, protein_range, fat_range = calculate_nutrient_distribution(daily_range, sex, age)
    carbs_range = calculate_meal_distribution(carbs_range)[1]
    protein_range = calculate_meal_distribution(protein_range)[1]
    fat_range = calculate_meal_distribution(fat_range)[1]
    return kcal_range, carbs_range, protein_range, fat_range

def get_lunch_nutrient_profile(sex, age, weight, height, pa, waist, preference, chewing_stage_value):
    daily_range = calculate_daily_intake(sex, age, weight, height, pa, waist)
    lunch_kcal_range = calculate_fixed_meal_distribution(daily_range[0])[1], calculate_fixed_meal_distribution(daily_range[1])[1]

    carbs_min = daily_range[0] * 0.55 / 4
    carbs_max = daily_range[1] * 0.65 / 4
    protein_min = max(50, daily_range[0] * 0.07 / 4) if sex in ['남성', 'male'] else max(40, daily_range[0] * 0.07 / 4)
    protein_max = daily_range[1] * 0.20 / 4
    fat_min = daily_range[0] * 0.15 / 9
    fat_max = daily_range[1] * 0.30 / 9

    lunch_carbs = calculate_meal_distribution((carbs_min, carbs_max))[1]
    lunch_protein = calculate_meal_distribution((protein_min, protein_max))[1]
    lunch_fat = calculate_meal_distribution((fat_min, fat_max))[1]

    profile = (
        f"- 에너지: {lunch_kcal_range[0]:.0f}~{lunch_kcal_range[1]:.0f} kcal\n"
        f"- 탄수화물: {lunch_carbs[0]:.0f}~{lunch_carbs[1]:.0f} g\n"
        f"- 단백질: {lunch_protein[0]:.0f}~{lunch_protein[1]:.0f} g\n"
        f"- 지방: {lunch_fat[0]:.0f}~{lunch_fat[1]:.0f} g\n"
        f"- 식재료 선호도: {preference}\n"
        f"- 저작단계: {chewing_stage_value}"
    )
    return profile
