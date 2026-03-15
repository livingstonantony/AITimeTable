import pandas as pd
from ortools.sat.python import cp_model
from pathlib import Path


class TeacherTimeTable:

    def __init__(self, excel_path, slots_per_day=5, days=5):

        self.excel_path = excel_path
        self.slots_per_day = slots_per_day
        self.days = days
        self.total_slots = slots_per_day * days

        self.teachers = self._load_teachers()
        self.classes_data = self._load_classes()

        self.classes = list(set(row["Class"] for row in self.classes_data))

        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

        self.assign = {}

    # ---------------- LOAD TEACHERS ----------------
    def _load_teachers(self):

        df = pd.read_excel(
            self.excel_path,
            sheet_name="Teachers",
            engine="openpyxl"
        )

        df.columns = df.columns.str.strip()

        return {
            row["Name"]: int(row["Hours"])
            for _, row in df.iterrows()
        }

    # ---------------- LOAD CLASS DATA ----------------
    def _load_classes(self):

        df = pd.read_excel(
            self.excel_path,
            sheet_name="Classes",
            engine="openpyxl"
        )

        df.columns = df.columns.str.strip()

        return df.to_dict("records")

    # ---------------- BUILD MODEL ----------------
    def build_model(self):

        # Decision variables
        for row in self.classes_data:

            teacher = row["Teacher"]
            subject = row["Name"]
            class_name = row["Class"]

            for slot in range(self.total_slots):

                self.assign[(teacher, subject, class_name, slot)] = \
                    self.model.NewBoolVar(
                        f"{teacher}_{subject}_{class_name}_{slot}"
                    )

        # ---------------- SUBJECT HOURS ----------------
        for row in self.classes_data:

            teacher = row["Teacher"]
            subject = row["Name"]
            class_name = row["Class"]
            hours = row["Hours"]

            self.model.Add(

                sum(
                    self.assign[(teacher, subject, class_name, s)]
                    for s in range(self.total_slots)
                ) == hours

            )

        # ---------------- ONE SUBJECT PER CLASS PER SLOT ----------------
        for class_name in self.classes:

            for slot in range(self.total_slots):

                self.model.Add(

                    sum(
                        self.assign[
                            (
                                row["Teacher"],
                                row["Name"],
                                row["Class"],
                                slot
                            )
                        ]
                        for row in self.classes_data
                        if row["Class"] == class_name
                    ) <= 1

                )

        # ---------------- TEACHER CANNOT TEACH TWO CLASSES SAME TIME ----------------
        for teacher in self.teachers:

            for slot in range(self.total_slots):

                self.model.Add(

                    sum(
                        self.assign[
                            (
                                row["Teacher"],
                                row["Name"],
                                row["Class"],
                                slot
                            )
                        ]
                        for row in self.classes_data
                        if row["Teacher"] == teacher
                    ) <= 1

                )

        # ---------------- TEACHER WEEKLY LIMIT ----------------
        for teacher, max_hours in self.teachers.items():

            self.model.Add(

                sum(
                    self.assign[
                        (
                            row["Teacher"],
                            row["Name"],
                            row["Class"],
                            s
                        )
                    ]
                    for row in self.classes_data
                    if row["Teacher"] == teacher
                    for s in range(self.total_slots)
                ) <= max_hours

            )

        # ---------------- SUBJECT MAX 2 PER DAY ----------------
        for row in self.classes_data:

            teacher = row["Teacher"]
            subject = row["Name"]
            class_name = row["Class"]

            for day in range(self.days):

                self.model.Add(

                    sum(
                        self.assign[
                            (
                                teacher,
                                subject,
                                class_name,
                                day * self.slots_per_day + s
                            )
                        ]
                        for s in range(self.slots_per_day)
                    ) <= 2

                )

    # ---------------- SOLVE ----------------
    def solve(self):

        status = self.solver.Solve(self.model)

        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            raise RuntimeError("No feasible timetable found")

    # ---------------- OUTPUT ----------------
    def to_dataframe(self):

        rows = []

        for slot in range(self.total_slots):

            day = slot // self.slots_per_day
            period = slot % self.slots_per_day

            for row in self.classes_data:

                teacher = row["Teacher"]
                subject = row["Name"]
                class_name = row["Class"]

                if self.solver.Value(
                        self.assign[(teacher, subject, class_name, slot)]
                ) == 1:

                    rows.append({
                        "Day": day + 1,
                        "Slot": period + 1,
                        "Teacher": teacher,
                        "Subject": subject,
                        "Class": class_name
                    })

        return pd.DataFrame(rows)


# ---------------- RUN ----------------
if __name__ == "__main__":

    timetable = TeacherTimeTable(
        excel_path="teacher_timetable_data.xlsx"
    )

    timetable.build_model()
    timetable.solve()

    df = timetable.to_dataframe()

    print(df)

    # Project root = folder where this script exists
    project_root = Path(__file__).resolve().parent

    # outputs directory inside project
    output_dir = project_root / "outputs"
    output_dir.mkdir(exist_ok=True)

    # Save file
    df.to_excel(output_dir / "teacher_timetable_output.xlsx", index=False)
