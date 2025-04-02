def create_schedule(study_plan):
    schedule = {}
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    i = 0
    for plan in study_plan:
        day = days[i % len(days)]
        if day not in schedule:
            schedule[day] = []
        schedule[day].append(plan)
        i += 1
    return schedule
