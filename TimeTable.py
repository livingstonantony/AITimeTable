import pandas as pd
from ortools.sat.python import cp_model


class TimeTable:
    def __init__(
        self,
        excel_path,
        slots_per_day=5,
        days=5,
        max_teacher_slots_per_day=1,
        max_subject_slots_per_day=1
    ):
        self.excel_path = excel_path
        self.slots_per_day = slots_per_day
        self.days = days
        self.total_slots = slots_per_day * days

        self.max_teacher_slots_per_day = max_teacher_slots_per_day
        self.max_subject_slots_per_day = max_subject_slots_per_day

        self.teachers = self._load_sheet("Teachers")
        self.subjects = self._load_sheet("Subjects")

        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

        self.teacher_assign = {}
        self.subject_assign = {}

    # ---------------- LOAD EXCEL ----------------
    def _load_sheet(self, sheet_name):
        df = pd.read_excel(self.excel_path, sheet_name=sheet_name, engine="openpyxl")
        df.columns = df.columns.str.strip()
        return {
            str(row["Name"]).strip(): int(row["Hours"])
            for _, row in df.iterrows()
        }

    # ---------------- VALIDATION ----------------
    def validate_constraints(self):
        errors = []

        for teacher, hours in self.teachers.items():
            max_possible = self.days * self.max_teacher_slots_per_day
            if hours > max_possible:
                errors.append(
                    f"Teacher '{teacher}' needs {hours} hours "
                    f"but max possible is {max_possible}"
                )

        for subject, hours in self.subjects.items():
            max_possible = self.days * self.max_subject_slots_per_day
            if hours > max_possible:
                errors.append(
                    f"Subject '{subject}' needs {hours} hours "
                    f"but max possible is {max_possible}"
                )

        if sum(self.teachers.values()) > self.total_slots:
            errors.append("Total teacher hours exceed total slots")

        if sum(self.subjects.values()) > self.total_slots:
            errors.append("Total subject hours exceed total slots")

        if errors:
            raise ValueError("\n".join(errors))

    # ---------------- BUILD MODEL ----------------
    def build_model(self):
        for teacher in self.teachers:
            for slot in range(self.total_slots):
                self.teacher_assign[(teacher, slot)] = self.model.NewBoolVar(
                    f"{teacher}_{slot}"
                )

        for subject in self.subjects:
            for slot in range(self.total_slots):
                self.subject_assign[(subject, slot)] = self.model.NewBoolVar(
                    f"{subject}_{slot}"
                )

        # Exact hours
        for t, h in self.teachers.items():
            self.model.Add(sum(self.teacher_assign[(t, s)] for s in range(self.total_slots)) == h)

        for s, h in self.subjects.items():
            self.model.Add(sum(self.subject_assign[(s, i)] for i in range(self.total_slots)) == h)

        # One teacher + one subject per slot
        for slot in range(self.total_slots):
            self.model.Add(sum(self.teacher_assign[(t, slot)] for t in self.teachers) == 1)
            self.model.Add(sum(self.subject_assign[(s, slot)] for s in self.subjects) == 1)

        # Max per day
        for t in self.teachers:
            for d in range(self.days):
                self.model.Add(
                    sum(self.teacher_assign[(t, d * self.slots_per_day + s)]
                        for s in range(self.slots_per_day)) <= self.max_teacher_slots_per_day
                )

        for s in self.subjects:
            for d in range(self.days):
                self.model.Add(
                    sum(self.subject_assign[(s, d * self.slots_per_day + i)]
                        for i in range(self.slots_per_day)) <= self.max_subject_slots_per_day
                )

        # No consecutive repetition
        for t in self.teachers:
            for i in range(self.total_slots - 1):
                self.model.Add(
                    self.teacher_assign[(t, i)] +
                    self.teacher_assign[(t, i + 1)] <= 1
                )

        for s in self.subjects:
            for i in range(self.total_slots - 1):
                self.model.Add(
                    self.subject_assign[(s, i)] +
                    self.subject_assign[(s, i + 1)] <= 1
                )

    # ---------------- SOLVE ----------------
    def solve(self):
        status = self.solver.Solve(self.model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            raise RuntimeError("No feasible timetable found")

    # ---------------- DATAFRAME OUTPUT ----------------
    def to_dataframe(self) -> pd.DataFrame:
        rows = []

        for day in range(self.days):
            for slot in range(self.slots_per_day):
                index = day * self.slots_per_day + slot

                teacher = next(
                    t for t in self.teachers
                    if self.solver.Value(self.teacher_assign[(t, index)]) == 1
                )

                subject = next(
                    s for s in self.subjects
                    if self.solver.Value(self.subject_assign[(s, index)]) == 1
                )

                rows.append({
                    "Day": day + 1,
                    "Slot": slot + 1,
                    "Teacher": teacher,
                    "Subject": subject
                })

        return pd.DataFrame(rows)


# ---------------- RUN ----------------
if __name__ == "__main__":
    timetable = TimeTable(
        excel_path="timetable_data.xlsx",
        max_teacher_slots_per_day=1,
        max_subject_slots_per_day=1
    )

    timetable.validate_constraints()
    timetable.build_model()
    timetable.solve()

    df = timetable.to_dataframe()

    # ✅ Show DataFrame
    print(df)

    # ✅ Save to Excel
    df.to_excel("final_timetable.xlsx", index=False)