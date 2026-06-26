"""
Utility to handle quiz scoring and result calculation.
"""


def calculate_score(user_answers, questions):
    """
    Calculate the quiz score based on user answers.

    Args:
        user_answers (dict): Dictionary mapping question index (int) to user's selected answer (str).
        questions (list): List of question dicts with 'correct_answer' key.

    Returns:
        dict: Contains 'score' (int), 'total' (int), 'percentage' (float),
              'correct_answers' (list of int indices), 'wrong_answers' (list of dicts with details)
    """
    total = len(questions)
    correct_count = 0
    correct_indices = []
    wrong_details = []

    for i, question in enumerate(questions):
        user_answer = user_answers.get(i, "")
        correct_answer = question["correct_answer"]

        if user_answer == correct_answer:
            correct_count += 1
            correct_indices.append(i)
        else:
            wrong_details.append({
                "question_index": i,
                "question": question["question"],
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "explanation": question["explanation"]
            })

    percentage = (correct_count / total) * 100 if total > 0 else 0

    return {
        "score": correct_count,
        "total": total,
        "percentage": round(percentage, 1),
        "correct_indices": correct_indices,
        "wrong_details": wrong_details
    }


def get_grade(percentage):
    """
    Get a letter grade based on percentage score.

    Args:
        percentage (float): Score percentage.

    Returns:
        str: Letter grade (A+, A, B, C, D, F)
    """
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 50:
        return "D"
    else:
        return "F"


def get_performance_message(percentage):
    """
    Get a performance message based on percentage score.

    Args:
        percentage (float): Score percentage.

    Returns:
        str: Performance message.
    """
    if percentage >= 90:
        return "🌟 Excellent! Outstanding performance!"
    elif percentage >= 80:
        return "👏 Great job! Well done!"
    elif percentage >= 70:
        return "👍 Good effort! Keep practicing!"
    elif percentage >= 60:
        return "📚 Fair attempt. Review the material and try again!"
    elif percentage >= 50:
        return "💪 Needs improvement. Keep studying!"
    else:
        return "📖 Better luck next time. Review the content thoroughly!"