from constraint import Problem

subjects = ["C", "CPP", "JAVA", "Python", "MYSQL"]
days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
periods = [1, 2, 3, 4, 5]

problem = Problem()

slots = []

for d in days:
    for p in periods:
        slot = f"{d}_{p}"
        slots.append(slot)
        problem.addVariable(slot, subjects)


def subject_count_constraint(*values):
    counts = {s: 0 for s in subjects}

    for v in values:
        counts[v] += 1

    return all(counts[s] == 5 for s in subjects)


problem.addConstraint(subject_count_constraint, slots)

# Get only ONE solution
solution = problem.getSolution()

for d in days:
    print(d)
    for p in periods:
        slot = f"{d}_{p}"
        print(f"  Period {p}: {solution[slot]}")
    print()