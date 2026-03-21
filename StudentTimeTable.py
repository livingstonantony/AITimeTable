import pandas as pd
from ortools.sat.python import cp_model
from pathlib import Path


class StudentTimeTable:
    def __init__(
        self,
        excel_path,
        slots_per_day=5,
        days=5,
        max_subject_slots_per_day=1
    ):
        self.excel_path = excel_path
        self.slots_per_day = slots_per_day
        self.days = days
        self.total_slots = slots_per_day * days
        self.max_subject_slots_per_day = max_subject_slots_per_day

        self.subjects = self._load_sheet("Subjects")

        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

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

        for subject, hours in self.subjects.items():
            max_possible = self.days * self.max_subject_slots_per_day
            if hours > max_possible:
                errors.append(
                    f"Subject '{subject}' needs {hours} hours "
                    f"but max possible is {max_possible}"
                )

        if sum(self.subjects.values()) > self.total_slots:
            errors.append("Total subject hours exceed total slots")

        if errors:
            raise ValueError("\n".join(errors))

    # ---------------- BUILD MODEL ----------------
    def build_model(self):
        for subject in self.subjects:
            for slot in range(self.total_slots):
                self.subject_assign[(subject, slot)] = self.model.NewBoolVar(
                    f"{subject}_{slot}"
                )

        # Exact hours per subject
        for s, h in self.subjects.items():
            self.model.Add(sum(self.subject_assign[(s, i)] for i in range(self.total_slots)) == h)

        # One subject per slot
        for slot in range(self.total_slots):
            self.model.Add(sum(self.subject_assign[(s, slot)] for s in self.subjects) == 1)

        # Max per day
        for s in self.subjects:
            for d in range(self.days):
                self.model.Add(
                    sum(self.subject_assign[(s, d * self.slots_per_day + i)]
                        for i in range(self.slots_per_day)) <= self.max_subject_slots_per_day
                )

        # No consecutive repetition
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

                subject = next(
                    s for s in self.subjects
                    if self.solver.Value(self.subject_assign[(s, index)]) == 1
                )

                rows.append({
                    "Day": day + 1,
                    "Slot": slot + 1,
                    "Subject": subject
                })

        return pd.DataFrame(rows)


# ---------------- RUN ----------------
if __name__ == "__main__":
    timetable = StudentTimeTable(
        excel_path="student_timetable_data_v2.xlsx",
        max_subject_slots_per_day=1
    )

    timetable.validate_constraints()
    timetable.build_model()
    timetable.solve()

    df = timetable.to_dataframe()

    print(df)

    project_root = Path(__file__).resolve().parent
    output_dir = project_root / "outputs"
    output_dir.mkdir(exist_ok=True)
    df.to_excel(output_dir / "student_timetable_output.xlsx", index=False)