from ortools.sat.python import cp_model

# Data
subjects = ["C", "CPP", "JAVA", "Python", "MYSQL"]
teachers = ["Livin", "Mercy", "Akash", "Jency", "Jecil"]

subject_teacher = {
    "C": "Livin",
    "CPP": "Mercy",
    "JAVA": "Akash",
    "Python": "Jency",
    "MYSQL": "Jecil"
}

days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
periods = [1,2,3,4,5]

model = cp_model.CpModel()

# ------------------------------------------------
# Schedule variables (day, period, subject)
# ------------------------------------------------

schedule = {}

for day in range(len(days)):
    for period in range(len(periods)):
        for subject in subjects:
            schedule[(day, period, subject)] = model.new_bool_var(
                f"{day}_{period}_{subject}"
            )


# ------------------------------------------------
# Constraint 1: each subject must appear 5 times
# ------------------------------------------------

for subject in subjects:

    total_periods_for_subject = 0

    for day in range(5):
        for period in range(5):
            total_periods_for_subject += schedule[(day, period, subject)]

    model.add(total_periods_for_subject == 5)


# ------------------------------------------------
# Constraint 2: only one subject per slot
# ------------------------------------------------

for day in range(5):
    for period in range(5):

        total_subjects_in_slot = 0

        for subject in subjects:
            total_subjects_in_slot += schedule[(day, period, subject)]

        model.add(total_subjects_in_slot == 1)


# ------------------------------------------------
# Constraint 3: subject max 2 times per day
# ------------------------------------------------

for subject in subjects:
    for day in range(5):

        total_subjects_in_day = 0

        for period in range(5):
            total_subjects_in_day += schedule[(day, period, subject)]

        model.add(total_subjects_in_day <= 2)


# ------------------------------------------------
# Solve
# ------------------------------------------------

solver = cp_model.CpSolver()
status = solver.Solve(model)


# ------------------------------------------------
# Print timetable
# ------------------------------------------------

if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:

    print("\nGenerated Timetable\n")

    for day in range(5):

        print(days[day])

        for period in range(5):

            for subject in subjects:

                if solver.Value(schedule[(day, period, subject)]) == 1:

                    teacher = subject_teacher[subject]

                    print(f"  Period {period+1}: {subject} ({teacher})")

        print()