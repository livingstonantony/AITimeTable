import pandas as pd
from ortools.sat.python import cp_model
from pathlib import Path


class TeacherTimeTable:

    def __init__(
        self,
        excel_path,
        slots_per_day=5,
        days=5,
        max_classes_per_day=5,        # max slots a teacher works per day
        max_subjects_per_day=3,       # max times a subject repeats per day (per teacher+class)
        max_subject_per_class_day=2,  # max times same subject appears for a class per day
    ):
        self.excel_path = excel_path
        self.slots_per_day = slots_per_day
        self.days = days
        self.total_slots = slots_per_day * days

        self.max_classes_per_day = max_classes_per_day
        self.max_subjects_per_day = max_subjects_per_day
        self.max_subject_per_class_day = max_subject_per_class_day

        self.teachers = self._load_teachers()
        self.classes_data = self._load_classes()
        self.classes = list(set(row["Class"] for row in self.classes_data))

        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

        self.assign = {}

    # ---------------- LOAD TEACHERS ----------------
    def _load_teachers(self):

        df = pd.read_excel(self.excel_path, sheet_name="Teachers", engine="openpyxl")
        df.columns = df.columns.str.strip()

        return {
            row["Name"]: int(row["Hours"])
            for _, row in df.iterrows()
        }

    # ---------------- LOAD CLASS DATA ----------------
    def _load_classes(self):

        df = pd.read_excel(self.excel_path, sheet_name="Subjects", engine="openpyxl")
        df.columns = df.columns.str.strip()

        # sheet column is "Teacher Name" (subject name); rename to "Name"
        df = df.rename(columns={"Teacher Name": "Name"})

        return df.to_dict("records")

    # ---------------- BUILD MODEL ----------------
    def build_model(self):

        # ── Decision variables ──────────────────────────────────────────────
        for row in self.classes_data:
            teacher    = row["Teacher"]
            subject    = row["Name"]
            class_name = row["Class"]

            for slot in range(self.total_slots):
                self.assign[(teacher, subject, class_name, slot)] = \
                    self.model.NewBoolVar(f"{teacher}_{subject}_{class_name}_{slot}")

        # ── C1: Each (subject, class) assigned exactly 'hours' slots ────────
        for row in self.classes_data:
            teacher    = row["Teacher"]
            subject    = row["Name"]
            class_name = row["Class"]
            hours      = int(row["Hours"])

            self.model.Add(
                sum(
                    self.assign[(teacher, subject, class_name, s)]
                    for s in range(self.total_slots)
                ) == hours
            )

        # ── C2: A class has at most 1 subject per slot ───────────────────────
        for class_name in self.classes:
            for slot in range(self.total_slots):
                self.model.Add(
                    sum(
                        self.assign[(row["Teacher"], row["Name"], row["Class"], slot)]
                        for row in self.classes_data
                        if row["Class"] == class_name
                    ) <= 1
                )

        # ── C3: A teacher teaches at most 1 class per slot ───────────────────
        for teacher in self.teachers:
            for slot in range(self.total_slots):
                self.model.Add(
                    sum(
                        self.assign[(row["Teacher"], row["Name"], row["Class"], slot)]
                        for row in self.classes_data
                        if row["Teacher"] == teacher
                    ) <= 1
                )

        # ── C4: Teacher weekly hours cap ─────────────────────────────────────
        # Use <= not == to avoid over-constraining the model
        for teacher, max_hours in self.teachers.items():
            self.model.Add(
                sum(
                    self.assign[(row["Teacher"], row["Name"], row["Class"], s)]
                    for row in self.classes_data
                    if row["Teacher"] == teacher
                    for s in range(self.total_slots)
                ) <= max_hours
            )

        # ── C5: Same subject for a class repeats at most N times per day ─────
        for row in self.classes_data:
            teacher    = row["Teacher"]
            subject    = row["Name"]
            class_name = row["Class"]

            for day in range(self.days):
                self.model.Add(
                    sum(
                        self.assign[(teacher, subject, class_name,
                                     day * self.slots_per_day + s)]
                        for s in range(self.slots_per_day)
                    ) <= self.max_subject_per_class_day
                )

        # ── C6: A teacher works at most max_classes_per_day slots per day ────
        for teacher in self.teachers:
            for day in range(self.days):
                self.model.Add(
                    sum(
                        self.assign[(row["Teacher"], row["Name"], row["Class"],
                                     day * self.slots_per_day + s)]
                        for row in self.classes_data
                        if row["Teacher"] == teacher
                        for s in range(self.slots_per_day)
                    ) <= self.max_classes_per_day
                )

        # ── C7: A subject appears at most max_subjects_per_day times per day ─
        for row in self.classes_data:
            teacher    = row["Teacher"]
            subject    = row["Name"]
            class_name = row["Class"]

            for day in range(self.days):
                self.model.Add(
                    sum(
                        self.assign[(teacher, subject, class_name,
                                     day * self.slots_per_day + s)]
                        for s in range(self.slots_per_day)
                    ) <= self.max_subjects_per_day
                )

    # ---------------- SOLVE ----------------
    def solve(self):

        status = self.solver.Solve(self.model)

        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            raise RuntimeError(
                "No feasible timetable found. Try relaxing the constraints "
                "(increase slots/day, days, or weekly hours)."
            )

        return self.solver.StatusName(status)

    # ---------------- OUTPUT ----------------
    def to_dataframe(self):

        rows = []

        for slot in range(self.total_slots):
            day    = slot // self.slots_per_day
            period = slot % self.slots_per_day

            for row in self.classes_data:
                teacher    = row["Teacher"]
                subject    = row["Name"]
                class_name = row["Class"]

                if self.solver.Value(
                    self.assign[(teacher, subject, class_name, slot)]
                ) == 1:
                    rows.append({
                        "Day":     day + 1,
                        "Slot":    period + 1,
                        "Teacher": teacher,
                        "Subject": subject,
                        "Class":   class_name,
                    })

        return pd.DataFrame(rows)


# ---------------- RUN ----------------
if __name__ == "__main__":

    timetable = TeacherTimeTable(excel_path="teacher_timetable_data.xlsx")

    timetable.build_model()
    status = timetable.solve()
    print(f"Status: {status}")

    df = timetable.to_dataframe()
    print(df.to_string(index=False))

    project_root = Path(__file__).resolve().parent
    output_dir   = project_root / "outputs"
    output_dir.mkdir(exist_ok=True)

    df.to_excel(output_dir / "teacher_timetable_output.xlsx", index=False)
    print(f"\nSaved to {output_dir / 'teacher_timetable_output.xlsx'}")