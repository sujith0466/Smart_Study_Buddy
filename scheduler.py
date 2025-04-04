def create_schedule(study_plan):
    schedule = {}
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    for i, plan in enumerate(study_plan):
        day = days[i % len(days)]
        schedule.setdefault(day, []).append(plan)
    
    return schedule
