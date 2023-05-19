def calculate_bmi(weight, height):
    height_in_meters = height / 100  # convert height to meters
    bmi = weight / (height_in_meters ** 2)
    return bmi


def get_nutrition_recommendation(bmi):
    if bmi < 18.5:
        return "You are underweight. It is recommended to increase your calorie " \
               "intake and focus on nutrient-rich foods such as lean proteins, whole " \
               "grains, fruits, vegetables, and healthy fats."
    elif bmi < 25:
        return "Your weight is within the normal range. Maintain a balanced diet " \
               "with a variety of nutrient-rich foods including lean proteins, whole " \
               "grains, fruits, vegetables, and healthy fats."
    elif bmi < 30:
        return "You are overweight. It is recommended to focus on portion control, " \
               "incorporate regular physical activity, and consume a balanced diet with " \
               "reduced calorie intake."
    else:
        return "You are obese. It is important to consult with a healthcare professional " \
               "or registered dietitian for personalized nutrition advice and a comprehensive" \
               " weight management plan."
