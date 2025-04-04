def generate_study_plan(subjects, past_scores, study_method):
    study_plan = []
    for subject, score in zip(subjects, past_scores):
        if score < 0 or score > 100:
            raise ValueError("Scores must be between 0 and 100.")
        recommended_hours = round(max(1, (100 - score) / 10), 1)  # Example formula
        study_plan.append({'subject': subject, 'hours': recommended_hours})
    return study_plan
