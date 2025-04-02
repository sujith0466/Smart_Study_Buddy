def generate_study_plan(subjects, past_scores, study_method):
    study_plan = []
    for subject, score in zip(subjects, past_scores):
        recommended_hours = max(1, (100 - score) / 10)  # Example formula
        study_plan.append({'subject': subject, 'hours': recommended_hours})
    return study_plan
