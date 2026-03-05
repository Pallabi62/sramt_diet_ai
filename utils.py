def calculate_calories(height, weight, age, gender, activity_level, goal):
    """
    Calculate BMR using the Mifflin-St Jeor Equation and TDEE based on activity.
    """
    # Mifflin-St Jeor Equation
    if gender.lower() == 'male':
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

    # Activity Multipliers
    activity_multipliers = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very_active': 1.9
    }
    
    tdee = bmr * activity_multipliers.get(activity_level, 1.2)
    
    # Goal Adjustment
    if goal == 'lose':
        target_calories = tdee - 500
    elif goal == 'gain':
        target_calories = tdee + 500
    else:
        target_calories = tdee
        
    return int(bmr), int(tdee), int(target_calories)

def generate_meal_plan(target_calories):
    """
    Generate a simple meal plan based on target calories.
    This is a rule-based mock generator.
    """
    # Simple split: 30% Breakfast, 40% Lunch, 30% Dinner (roughly)
    breakfast_cals = int(target_calories * 0.3)
    lunch_cals = int(target_calories * 0.4)
    dinner_cals = int(target_calories * 0.3)
    
    # Mock Database
    breakfast_options = [
        {"name": "Oatmeal with Berries & Nuts", "base_cal": 350},
        {"name": "Scrambled Eggs on Whole Wheat Toast", "base_cal": 400},
        {"name": "Greek Yogurt Parfait", "base_cal": 300}
    ]
    
    lunch_options = [
        {"name": "Grilled Chicken Salad with Quinoa", "base_cal": 500},
        {"name": "Turkey Wrap with Avocado", "base_cal": 450},
        {"name": "Vegetable Stir-Fry with Tofu", "base_cal": 400}
    ]
    
    dinner_options = [
        {"name": "Baked Salmon with Asparagus", "base_cal": 550},
        {"name": "Lean Beef Stir-Fry", "base_cal": 600},
        {"name": "Lentil Soup with Whole Grain Roll", "base_cal": 450}
    ]
    
    # Simple selection logic (just pick first for now, can be randomized)
    # In a real app, we would match calorie counts more precisely.
    import random
    b_meal = random.choice(breakfast_options)
    l_meal = random.choice(lunch_options)
    d_meal = random.choice(dinner_options)
    
    return {
        "breakfast": {"name": b_meal["name"], "calories": breakfast_cals},
        "lunch": {"name": l_meal["name"], "calories": lunch_cals},
        "dinner": {"name": d_meal["name"], "calories": dinner_cals},
        "total": breakfast_cals + lunch_cals + dinner_cals
    }
