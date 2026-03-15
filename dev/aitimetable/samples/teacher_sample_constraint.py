from ortools.sat.python import cp_model

# -----------------------------
# Teacher weekly limits
# -----------------------------
teacher_max_hours = {
    "Livin": 5,
    "Mercy": 5,
    "Akash": 5,
    "Jency": 5,
    "Jecil": 5
}

# -----------------------------
# Subjects data
# (Teacher, Subject, Class, Hours)
# -----------------------------
subjects_data = [
    ("Livin", "C", "BCA_A", 2),
    ("Livin", "CPP", "BCA_B", 3),
    ("Mercy", "JAVA", "Bsc", 2),
    ("Akash", "Python", "Bsc", 3),
    ("Mercy", "MYSQL", "BCA_A", 3),
    ("Akash", "Java_LAB", "Bsc", 2),
    ("Jency", "MYSQL_LAB", "BCA_B", 2),
    ("Jency", "C_LAB", "BCA_A", 3),
    ("Jecil", "CPP_LAB", "Bsc", 3),
    ("Jecil", "Python_LAB", "Bsc", 2)
]

days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
periods = [1, 2, 3, 4, 5]

classes = list(set(class_name for _, _, class_name, _ in subjects_data))

# -----------------------------
# Model
# -----------------------------
model = cp_model.CpModel()

# timetable[(day, period, class, subject)]
timetable = {}


# -----------------------------
# Create decision variables
# teacher is not included in the timetable since a teacher can attend multiple classes in different slots
# -----------------------------
for teacher, subject, class_name, required_hours in subjects_data:
    for day in range(len(days)):
        for period in range(len(periods)):
            timetable[(day, period, class_name, subject)] = model.new_bool_var(
                f"{day}_{period}_{class_name}_{subject}"
            )


# -----------------------------
# Constraint 1
# Subject must appear required hours
# -----------------------------
for teacher, subject, class_name, required_hours in subjects_data:

    total_subject_slots = 0

    for day in range(len(days)):
        for period in range(len(periods)):
            total_subject_slots += timetable[(day, period, class_name, subject)]

    model.add(total_subject_slots == required_hours)

# -----------------------------
# Constraint 2
# Only one subject per class per slot
# -----------------------------
for class_name in classes:
    for day in range(len(days)):
        for period in range(len(periods)):

            subjects_in_slot = 0

            for data_teacher, subject, data_class, hours in subjects_data:
                if data_class == class_name:
                    subjects_in_slot += timetable[(day, period, data_class, subject)]

            model.add(subjects_in_slot <= 1)

# -----------------------------
# Constraint 3
# Teacher cannot teach two classes at same time
# -----------------------------
for teacher in teacher_max_hours:
    for day in range(len(days)):
        for period in range(len(periods)):

            teacher_classes_in_slot = 0

            for data_teacher, subject, class_name, hours in subjects_data:
                if data_teacher == teacher:
                    teacher_classes_in_slot += timetable[(day, period, class_name, subject)]

            model.add(teacher_classes_in_slot <= 1)

# -----------------------------
# Constraint 4
# Teacher weekly hour limit
# -----------------------------
for teacher, max_hours in teacher_max_hours.items():

    teacher_total_hours = 0

    for data_teacher, subject, class_name, hours in subjects_data:
        if data_teacher == teacher:

            for day in range(len(days)):
                for period in range(len(periods)):
                    teacher_total_hours += timetable[(day, period, class_name, subject)]

    model.add(teacher_total_hours <= max_hours)

# -----------------------------
# Constraint 5
# Subject max 2 times per day
# -----------------------------
for teacher, subject, class_name, required_hours in subjects_data:
    for day in range(len(days)):

        subject_count_in_day = 0

        for period in range(len(periods)):
            subject_count_in_day += timetable[(day, period, class_name, subject)]

        model.add(subject_count_in_day <= 2)

# -----------------------------
# Solve
# -----------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

# -----------------------------
# Print timetable
# -----------------------------
if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:

    for class_name in classes:

        print("\n====================")
        print("Class:", class_name)
        print("====================")

        for day in range(len(days)):

            print(days[day])

            for period in range(len(periods)):

                for teacher, subject, data_class, hours in subjects_data:

                    if data_class == class_name and solver.Value(
                            timetable[(day, period, class_name, subject)]
                    ) == 1:
                        print(f"  Period {period + 1}: {subject} ({teacher})")

            print()

else:
    print("No solution found.")
