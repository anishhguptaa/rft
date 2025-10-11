from typing import Dict, Any


def get_workout_prompt(data: Dict[str, Any]) -> str:
    """Create a detailed prompt for workout plan generation"""
    prompt = f"""
        You are a professional fitness trainer and nutritionist. Create a comprehensive, personalized workout plan based on the following user information:

        User Profile:
        - Height: {data['height']} cm
        - Weight: {data['weight']} kg
        - Age: {data['age']} years
        - Gender: {data['gender']}
        - Workout Days: {data['workout_days']}
        - Workout Goal: {data['workout_goal']}
        - Goal Timeline: {data['goal_timeline']} weeks
        - Available Equipment: {data['equipment']}
        - Experience Level: {data['experience_level']}

        Please generate a detailed workout plan that includes:

        1. **Overview**: Brief summary of the plan and expected outcomes
        2. **Weekly Schedule**: Day-by-day breakdown of workouts
        3. **Exercise Details**: For each exercise, include:
           - Exercise name
           - Sets and reps
           - Rest periods
           - Difficulty level
           - Equipment needed
           - Proper form tips
        4. **Progression Plan**: How to increase intensity over the {data['goal_timeline']} weeks
        5. **Nutrition Guidelines**: Basic dietary recommendations
        6. **Recovery Tips**: Rest and recovery strategies
        7. **Safety Considerations**: Important safety notes

        Each exercise should have: name, sets, reps, rest_period, difficulty, equipment, form_tips
        """
    return prompt
