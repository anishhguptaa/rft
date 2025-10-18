from typing import Dict, Any
from .prompts_text import FIRST_WORKOUT_PROMPT_TEMPLATE, REQUEST_FEASIBILITY_PROMPT_TEMPLATE, ADJUST_WORKOUT_PLAN_PROMPT_TEMPLATE


def get_first_workout_prompt(data: Dict[str, Any]) -> str:
    """Create an optimized prompt for workout plan generation using advanced prompt engineering techniques"""
    
    # Format limitations as a readable list
    limitations_text = ", ".join(data['user_limitations']) if data['user_limitations'] else "None specified"
    
    # Calculate remaining days in the week
    current_day = data['current_day'].lower()
    days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    current_day_index = days_of_week.index(current_day) if current_day in days_of_week else 0
    remaining_days = 7 - current_day_index
    
    template_vars = {
        'height': data['height'],
        'weight': data['weight'],
        'target_weight': data['target_weight'],
        'age': data['age'],
        'gender': data['gender'],
        'workout_goal': data['workout_goal'],
        'goal_timeline': data['goal_timeline'],
        'workout_days': data['workout_days'],
        'experience_level': data['experience_level'],
        'equipment': data['equipment'],
        'current_day': data['current_day'],
        'remaining_days': remaining_days,
        'limitations_text': limitations_text,
        'user_remarks': data.get('user_remarks', 'None provided'),
        'current_day_index_plus_one': current_day_index + 1
    }
    
    prompt = FIRST_WORKOUT_PROMPT_TEMPLATE.format(**template_vars)
    
    return prompt


def get_feasibility_prompt(data: Dict[str, Any]) -> str:
    """Create a prompt for feasibility assessment using the same input as workout generation"""
    
    limitations_text = ", ".join(data['user_limitations']) if data['user_limitations'] else "None specified"
    
    template_vars = {
        'height': data['height'],
        'weight': data['weight'],
        'target_weight': data['target_weight'],
        'age': data['age'],
        'gender': data['gender'],
        'workout_goal': data['workout_goal'],
        'goal_timeline': data['goal_timeline'],
        'workout_days': data['workout_days'],
        'experience_level': data['experience_level'],
        'equipment': data['equipment'],
        'limitations_text': limitations_text,
        'user_remarks': data.get('user_remarks', 'None provided')
    }
    
    prompt = REQUEST_FEASIBILITY_PROMPT_TEMPLATE.format(**template_vars)
    
    return prompt


def get_adjust_workout_plan_prompt(data: Dict[str, Any]) -> str:
    """Create a prompt for workout plan adjustment using the same input as workout generation"""
    
    template_vars = {
        'remaining_routines': data['remaining_routines'],
        'current_day': data['current_day']
    }
    
    prompt = ADJUST_WORKOUT_PLAN_PROMPT_TEMPLATE.format(**template_vars)
    
    return prompt