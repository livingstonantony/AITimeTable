import streamlit as st
import pandas as pd
import io
from datetime import datetime
import time
import sys
import os
import streamlit.components.v1 as components

from TeacherTimeTable import TeacherTimeTable

# Add the current directory to the path to import local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import (
    init_db,
    verify_user,
    create_user,
    user_exists,
    save_timetable,
    get_all_timetables,
    get_timetable,
    get_timetable_slots,
    get_timetable_requirements,
    get_user,
    delete_timetable, save_teacher_time_table, get_teacher_timetable_slots, get_teacher_timetable_requirements,
)
from StudentTimeTable import StudentTimeTable

# Initialize database
init_db()

# Configure Streamlit
st.set_page_config(page_title="AI TimeTable", layout="wide", initial_sidebar_state="expanded")

# Initialize session state
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "login"


# ==================== AUTHENTICATION ====================
def login_page():
    """Login/Register page."""
    st.title("🎓 AI TimeTable System")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Login")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        login_role = st.selectbox("Login as", ["Teacher", "Student"], key="login_role")

        if st.button("Login", key="login_btn"):
            user = verify_user(login_username, login_password)
            if user and user["role"].lower() == login_role.lower():
                st.session_state.user = user
                st.session_state.page = "home"
                st.rerun()
            else:
                st.error("Invalid credentials or role mismatch")

    with col2:
        st.subheader("Register")
        reg_username = st.text_input("Username", key="reg_username")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_name = st.text_input("Full Name", key="reg_name")
        reg_role = st.selectbox("Register as", ["Teacher", "Student"], key="reg_role")

        if st.button("Register", key="register_btn"):
            if not reg_username or not reg_password or not reg_name:
                st.error("Please fill all fields")
            elif user_exists(reg_username):
                st.error("Username already exists")
            else:
                if create_user(reg_username, reg_password, reg_role, reg_name):
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Registration failed")


# ==================== HOME PAGE ====================
def home_page():
    """Home page with timetable display."""
    st.title(f"🎓 Welcome, {st.session_state.user['name']}!")

    if st.button("Logout", key="logout_btn"):
        st.session_state.user = None
        st.session_state.page = "login"
        st.rerun()

    st.divider()

    # Show role-based options
    if st.session_state.user["role"].lower() == "teacher":
        st.subheader("Your TimeTable")
        display_timetables()

    elif st.session_state.user["role"].lower() == "student":
        st.subheader("Class TimeTable")
        display_timetables()


def display_timetables():
    """Display available timetables."""
    timetables = get_all_timetables()

    if not timetables:
        st.info("No timetables available yet.")
        return

    # Timetable selection with formatted names showing index
    timetable_names = [f"{idx + 1}: {tt['name']}" for idx, tt in enumerate(timetables)]
    selected_idx = st.selectbox("Select a timetable:", range(len(timetables)), format_func=lambda x: timetable_names[x])

    if selected_idx is not None:
        timetable = timetables[selected_idx]

        # Delete button with confirmation
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("🗑️ Delete", key=f"delete_btn_{timetable['id']}", help="Delete this timetable"):
                if st.session_state.get(f"confirm_delete_{timetable['id']}", False):
                    # Perform deletion
                    if delete_timetable(timetable['id']):
                        st.success("✅ Timetable deleted successfully!")
                        st.session_state[f"confirm_delete_{timetable['id']}"] = False
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete timetable")
                else:
                    st.session_state[f"confirm_delete_{timetable['id']}"] = True
                    st.rerun()

        # Show confirmation dialog
        if st.session_state.get(f"confirm_delete_{timetable['id']}", False):
            st.warning(f"⚠️ Are you sure you want to delete '{timetable['name']}'? This action cannot be undone.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Confirm Delete", key=f"confirm_delete_btn_{timetable['id']}"):
                    if delete_timetable(timetable['id']):
                        st.success("✅ Timetable deleted successfully!")
                        st.session_state[f"confirm_delete_{timetable['id']}"] = False
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete timetable")
            with col2:
                if st.button("❌ Cancel", key=f"cancel_delete_btn_{timetable['id']}"):
                    st.session_state[f"confirm_delete_{timetable['id']}"] = False
                    st.rerun()
        else:
            display_timetable_details(timetable)


def display_timetable_details(timetable):
    """Display timetable in a calendar view."""
    timetable_id = timetable["id"]

    # Header with metadata
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"# 📅 {timetable['name']}")
    with col2:
        st.markdown(f"**ID:** `{timetable_id}`")

    st.markdown(f"*Generated: {timetable['generated_at']}*")
    st.divider()

    # Get slots
    slots = get_timetable_slots(timetable_id)
    teachers_hours, subjects_hours = get_timetable_requirements(timetable_id)

    if str(timetable['name']).startswith("Teacher_"):
        print("teacher_timetable_selected")
        slots = get_teacher_timetable_slots(timetable_id)
        print("slots:", slots)
        teachers_hours, subjects_hours = get_teacher_timetable_requirements(timetable_id)

        print(f"Teacher hours: {teachers_hours}, subject hours: {subjects_hours}")

    if not slots:
        st.warning("⚠️ No slots in this timetable.")

        return

    # Convert to DataFrame
    df = pd.DataFrame(slots)

    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📅 Calendar View", "📋 Table View", "📊 Summary"])

    with tab1:
        st.markdown("## 📅 Weekly College Schedule")

        # Day mapping
        days_map = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}

        # Get unique days and slots
        unique_days = sorted(df["day"].unique())
        unique_slots = sorted(df["slot"].unique())

        # Create color mapping for subjects
        subjects = df["subject"].unique()
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E2"]
        subject_colors = {subject: colors[i % len(colors)] for i, subject in enumerate(subjects)}

        st.markdown("##### 📋 College Timetable Grid - Slots as Columns, Days as Rows")

        st.markdown("""
        <style>
        .timetable {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .timetable th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px;
            text-align: center;
            font-weight: 700;
            border: none;
        }
        .timetable td {
            padding: 10px;
            border: 1px solid #e0e0e0;
            text-align: center;
        }
        .timetable tr:nth-child(even) {
            background: #f8f9ff;
        }
        .timetable tr:nth-child(odd) {
            background: white;
        }
        .day-cell {
            font-weight: 700;
            color: white;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .subject-text {
            font-weight: 700;
            font-size: 14px;
            margin-bottom: 6px;
            display: block;
        }
        .teacher-text {
            font-weight: 600;
            font-size: 12px;
            display: block;
            margin-top: 4px;
        }
        </style>
        """, unsafe_allow_html=True)

        # Create the table as HTML string
        table_html = '<table class="timetable"><thead><tr><th>DAY</th>'

        # Add slot headers
        for slot in unique_slots:
            table_html += f'<th>Slot {int(slot)}</th>'
        table_html += '</tr></thead><tbody>'

        # Add rows for each day
        for day_num in unique_days:
            day_name = days_map.get(int(day_num), f"Day {int(day_num)}")
            table_html += f'<tr><td class="day-cell">{day_name}</td>'

            # Add cells for each period
            for slot in unique_slots:
                class_data = df[(df["day"] == day_num) & (df["slot"] == slot)]

                if len(class_data) > 0:
                    row_data = class_data.iloc[0]

                    class_name = row_data.get("class_name")
                    if class_name:
                        subject = f"{row_data['subject']} ({class_name})"
                    else:
                        subject = row_data["subject"]

                    teacher = row_data["teacher"]
                    color = subject_colors.get(subject, "#667eea")

                    table_html += f'''<td style="border-left: 5px solid {color}; background: linear-gradient(135deg, {color}10 0%, {color}05 100%);">
                        <span class="subject-text" style="color: {color};">{subject}</span>
                        <span class="teacher-text" style="color: #333;">👨‍🏫 {teacher}</span>
                    </td>'''
                else:
                    table_html += '<td style="background: #fafafa; color: #ccc;">-</td>'

            table_html += '</tr>'

        table_html += '</tbody></table>'

        st.markdown(table_html, unsafe_allow_html=True)

        # Legend section
        st.markdown("---")
        st.markdown("### 📚 Subject Color Legend")

        legend_cols = st.columns(min(4, len(subject_colors)))
        for idx, (subject, color) in enumerate(subject_colors.items()):
            with legend_cols[idx % len(legend_cols)]:
                st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, {color} 0%, {color}dd 100%);
                    border-radius: 8px;
                    padding: 12px;
                    color: white;
                    text-align: center;
                    font-weight: 700;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                    font-size: 13px;
                '>
                    {subject}
                </div>
                """, unsafe_allow_html=True)

    with tab2:
        st.markdown("#### Detailed Schedule Table")

        # Prepare data
        display_df = df.copy()
        display_df = display_df[["day", "slot", "teacher", "subject"]].copy()

        # Map day numbers to names
        day_names = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}
        display_df["day"] = display_df["day"].apply(lambda x: day_names.get(int(x), f"Day {int(x)}"))
        display_df["slot"] = display_df["slot"].astype(int)
        display_df = display_df.sort_values(["day", "slot"])

        # Rename columns with emojis
        display_df.columns = ["day", "Slot", "Teacher", "Subject"]

        # Display as dataframe
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Show table statistics
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Classes", len(display_df), help="Total scheduled classes")
        with col2:
            st.metric("Unique Teachers", display_df["Teacher"].nunique(), help="Number of different teachers")
        with col3:
            st.metric("Unique Subjects", display_df["Subject"].nunique(), help="Number of different subjects")

    with tab3:
        st.markdown("#### Summary & Statistics")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 👨‍🏫 Teacher Hours")
            teacher_data = []
            for teacher, hours in teachers_hours.items():
                teacher_data.append({
                    "Teacher": teacher,
                    "Required Hours": hours
                })
            if teacher_data:
                teacher_df = pd.DataFrame(teacher_data)
                st.dataframe(teacher_df, use_container_width=True, hide_index=True)
                st.metric("Total Teacher Hours", sum(teachers_hours.values()))

        with col2:
            st.markdown("##### 📚 Subject Hours")
            subject_data = []
            for subject, hours in subjects_hours.items():
                subject_data.append({
                    "Subject": subject,
                    "Required Hours": hours
                })
            if subject_data:
                subject_df = pd.DataFrame(subject_data)
                st.dataframe(subject_df, use_container_width=True, hide_index=True)
                st.metric("Total Subject Hours", sum(subjects_hours.values()))

        # Statistics
        st.markdown("##### 📊 Schedule Statistics")
        max_slots = int(df["slot"].max())
        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)

        with stats_col1:
            st.metric("Total Days", len(unique_days))

        with stats_col2:
            st.metric("Slots/Day", max_slots)

        with stats_col3:
            st.metric("Total Slots", len(slots))

        with stats_col4:
            st.metric("Total Classes", len(teachers_hours))


# ==================== TEACHER ADMIN PANEL ====================


def teacher_admin_page():
    """Admin panel to generate and manage timetables."""

    st.title("⚙️ Admin Panel - Generate Teacher TimeTable")
    st.write("Upload an Excel file to generate a timetable.")

    uploaded_file_teacher = st.file_uploader(
        "Choose Excel file Teacher", type=["xlsx", "xls"]
    )

    if uploaded_file_teacher is not None:

        try:
            # ---------------- LOAD EXCEL ----------------
            teachers_df = pd.read_excel(uploaded_file_teacher, sheet_name="Teachers")
            # FIX: seek back to 0 before reading the second sheet from the same buffer
            uploaded_file_teacher.seek(0)
            classes_df = pd.read_excel(uploaded_file_teacher, sheet_name="Subjects")

            teachers_df.columns = teachers_df.columns.str.strip()
            classes_df.columns = classes_df.columns.str.strip()

            st.success("✅ Excel file loaded successfully!")

            col1, col2 = st.columns(2)

            with col1:
                st.write("### Teachers")
                st.dataframe(teachers_df, use_container_width=True)

            with col2:
                st.write("### Subjects")
                st.dataframe(classes_df, use_container_width=True)

            # ---------------- PARAMETERS ----------------
            st.divider()
            st.subheader("⚙️ Configure TimeTable Parameters")

            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                slots_per_day = st.number_input(
                    "Slots per Day", min_value=1, max_value=10, value=5
                )
            with col2:
                days = st.number_input(
                    "Days", min_value=1, max_value=7, value=5
                )
            with col3:
                max_teacher_slots = st.number_input(
                    "Max Classes / Teacher / Day", min_value=1, max_value=10, value=5
                )
            with col4:
                max_subject_slots = st.number_input(
                    "Max Subjects / Teacher / Day", min_value=1, max_value=10, value=1
                )
            with col5:
                max_subject_per_class_day = st.number_input(
                    "Max Subject Repeat / Class / Day",
                    min_value=1, max_value=5, value=1
                )

            timetable_name = st.text_input(
                "TimeTable Name",
                value=f"Teacher_TimeTable_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            )

            # ---------------- GENERATE ----------------
            if st.button("🚀 Generate TimeTable"):

                with st.spinner("🤖 Generating timetable..."):

                    try:
                        time.sleep(1)

                        temp_file = "temp_teacher_timetable_input.xlsx"

                        with pd.ExcelWriter(temp_file, engine="openpyxl") as writer:
                            teachers_df.to_excel(writer, sheet_name="Teachers", index=False)
                            classes_df.to_excel(writer, sheet_name="Subjects", index=False)

                        # FIX: pass all 3 configurable params that the class now accepts
                        timetable = TeacherTimeTable(
                            excel_path=temp_file,
                            slots_per_day=int(slots_per_day),
                            days=int(days),
                            max_classes_per_day=int(max_teacher_slots),
                            max_subjects_per_day=int(max_subject_slots),
                            max_subject_per_class_day=int(max_subject_per_class_day),
                        )

                        timetable.build_model()
                        solver_status = timetable.solve()

                        result_df = timetable.to_dataframe()

                        st.success("✅ TimeTable Generated Successfully by AI!")
                        st.dataframe(result_df, use_container_width=True)

                        # ---------------- GRID DISPLAY ----------------
                        st.subheader("📅 Generated Timetable")

                        display_df = result_df.copy()
                        display_df.columns = display_df.columns.str.lower()

                        days_map = {
                            1: "Monday", 2: "Tuesday", 3: "Wednesday",
                            4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday",
                        }

                        unique_days = sorted(display_df["day"].unique())
                        unique_slots = sorted(display_df["slot"].unique())
                        subjects = display_df["subject"].unique()

                        colors = [
                            "#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A",
                            "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E2",
                        ]
                        subject_colors = {
                            subject: colors[i % len(colors)]
                            for i, subject in enumerate(subjects)
                        }

                        # ---------------- HTML TABLE ----------------
                        html = """
                        <style>
                        body { font-family: Arial; }
                        .table-wrapper { width: 100%; overflow-x: auto; }
                        .timetable {
                            width: 100%;
                            border-collapse: collapse;
                            table-layout: fixed;
                            font-size: 13px;
                        }
                        .timetable th {
                            background: #667eea;
                            color: white;
                            padding: 10px;
                            text-align: center;
                        }
                        .timetable td {
                            border: 1px solid #e6e6e6;
                            padding: 8px;
                            text-align: center;
                            vertical-align: top;
                            min-width: 120px;
                        }
                        .day-cell {
                            background: #667eea;
                            color: white;
                            font-weight: 700;
                        }
                        .subject-text {
                            font-weight: 700;
                            display: block;
                            margin-bottom: 2px;
                        }
                        .teacher-text { font-size: 11px; color: #444; }
                        .entry { margin-bottom: 4px; border-bottom: 1px solid #eee; padding-bottom: 4px; }
                        .entry:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
                        </style>
                        """

                        html += '<div class="table-wrapper">'
                        html += '<table class="timetable"><thead><tr><th>DAY</th>'

                        for slot in unique_slots:
                            html += f"<th>Slot {int(slot)}</th>"

                        html += "</tr></thead><tbody>"

                        for day_num in unique_days:
                            day_name = days_map.get(day_num, f"Day {day_num}")
                            html += f'<tr><td class="day-cell">{day_name}</td>'

                            for slot in unique_slots:

                                # FIX: show ALL classes in that slot, not just iloc[0]
                                slot_data = display_df[
                                    (display_df["day"] == day_num) &
                                    (display_df["slot"] == slot)
                                    ]

                                if not slot_data.empty:
                                    cell_html = ""
                                    for _, entry in slot_data.iterrows():
                                        subject = entry["subject"]
                                        teacher = entry["teacher"]
                                        class_name = entry["class"]
                                        color = subject_colors.get(subject, "#667eea")

                                        cell_html += f"""
                                        <div class="entry">
                                            <span class="subject-text" style="color:{color}">
                                                {subject} ({class_name})
                                            </span>
                                            <span class="teacher-text">👨‍🏫 {teacher}</span>
                                        </div>
                                        """

                                    html += f'<td style="border-left:4px solid {subject_colors.get(slot_data.iloc[0]["subject"], "#667eea")}">{cell_html}</td>'
                                else:
                                    html += "<td>-</td>"

                            html += "</tr>"

                        html += "</tbody></table></div>"

                        # FIX: estimate height based on number of rows so it doesn't clip
                        st.markdown(html, unsafe_allow_html=True)

                        # Legend section
                        st.markdown("---")
                        st.markdown("### 📚 Subject Color Legend")

                        legend_cols = st.columns(min(4, len(subject_colors)))
                        for idx, (subject, color) in enumerate(subject_colors.items()):
                            with legend_cols[idx % len(legend_cols)]:
                                st.markdown(f"""
                                <div style='
                                    background: linear-gradient(135deg, {color} 0%, {color}dd 100%);
                                    border-radius: 8px;
                                    padding: 12px;
                                    color: white;
                                    text-align: center;
                                    font-weight: 700;
                                    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                                    font-size: 13px;
                                '>
                                    {subject}
                                </div>
                                """, unsafe_allow_html=True)

                        # Save to database
                        teachers_dict = dict(
                            zip(teachers_df["Name"].str.strip(), teachers_df["Hours"])
                        )
                        print("teachers_dict: ", teachers_dict)

                        subjects_dict = {
                            (teacher.strip(), subject.strip(), class_name.strip()): hours
                            for teacher, subject, class_name, hours in zip(
                                classes_df["Teacher"],
                                classes_df["Name"],
                                classes_df["Class"],
                                classes_df["Hours"],
                            )
                        }

                        print("subjects_dict:", subjects_dict)
                        timetable_id = save_teacher_time_table(
                            name=timetable_name,
                            days=days,
                            slots_per_day=slots_per_day,
                            df=result_df,
                            teachers_hours=teachers_dict,
                            subjects_hours=subjects_dict,
                            user_id=st.session_state.user["id"],
                        )

                        st.success(f"✅ TimeTable saved to database (ID: {timetable_id})")

                        # ---------------- DOWNLOAD ----------------
                        excel_buffer = io.BytesIO()

                        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                            result_df.to_excel(writer, sheet_name="TimeTable", index=False)

                        excel_buffer.seek(0)

                        st.download_button(
                            label="📥 Download TimeTable (Excel)",
                            data=excel_buffer,
                            file_name=f"{timetable_name}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        )

                    except Exception as e:
                        st.error(f"❌ Error generating timetable: {str(e)}")

                    finally:
                        # FIX: always clean up temp file even on error
                        if os.path.exists(temp_file):
                            os.remove(temp_file)

        except Exception as e:
            st.error(f"❌ Error loading Excel file: {str(e)}")


# ==================== STUDENT ADMIN PANEL ====================
def student_admin_page():
    """Admin panel to generate and manage timetables."""
    st.title("⚙️ Admin Panel - Generate TimeTable")

    st.write("Upload an Excel file to generate a timetable.")

    # File uploader
    uploaded_file = st.file_uploader("Choose Excel file", type=["xlsx", "xls"])

    if uploaded_file is not None:
        try:
            # Load Excel file
            teachers_df = pd.read_excel(uploaded_file, sheet_name="Teachers")
            subjects_df = pd.read_excel(uploaded_file, sheet_name="Subjects")

            teachers_df.columns = teachers_df.columns.str.strip()
            subjects_df.columns = subjects_df.columns.str.strip()

            st.success("✅ Excel file loaded successfully!")

            # Display loaded data
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Teachers:**")
                st.dataframe(teachers_df, use_container_width=True)

            with col2:
                st.write("**Subjects:**")
                st.dataframe(subjects_df, use_container_width=True)

            # Parameters configuration
            st.divider()
            st.subheader("Configure TimeTable Parameters")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                slots_per_day = st.number_input(
                    "Slots per Day", min_value=1, max_value=10, value=5
                )

            with col2:
                days = st.number_input("Number of Days", min_value=1, max_value=7, value=5)

            with col3:
                max_teacher_slots = st.number_input(
                    "Max Teacher Slots/Day", min_value=1, max_value=5, value=1
                )

            with col4:
                max_subject_slots = st.number_input(
                    "Max Subject Slots/Day", min_value=1, max_value=5, value=1
                )

            timetable_name = st.text_input("TimeTable Name",
                                           value=f"Student_TimeTable_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

            # Generate timetable
            if st.button("🚀 Generate TimeTable", key="generate_btn"):
                with st.spinner("🤖 AI TimeTable is generating... Please wait"):
                    try:
                        # Add 2 second delay to show loader
                        time.sleep(2)

                        # Create a temporary Excel file
                        temp_file = "temp_timetable_input.xlsx"

                        with pd.ExcelWriter(temp_file, engine="openpyxl") as writer:
                            teachers_df.to_excel(writer, sheet_name="Teachers", index=False)
                            subjects_df.to_excel(writer, sheet_name="Subjects", index=False)

                        # Generate timetable using TimeTable class
                        timetable = StudentTimeTable(
                            excel_path=temp_file,
                            slots_per_day=slots_per_day,
                            days=days,
                            max_teacher_slots_per_day=max_teacher_slots,
                            max_subject_slots_per_day=max_subject_slots,
                        )

                        timetable.validate_constraints()
                        timetable.build_model()
                        timetable.solve()

                        result_df = timetable.to_dataframe()

                        # Success message with celebration
                        st.success("✅ TimeTable Generated Successfully by AI!")
                        st.dataframe(result_df, use_container_width=True)

                        # Display generated timetable in calendar grid view
                        st.subheader("📅 Generated College Timetable Grid")

                        # Prepare DataFrame for display
                        display_df = result_df.copy()

                        # Rename columns to lowercase for consistency
                        display_df.columns = display_df.columns.str.lower()

                        # Day mapping
                        days_map = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday",
                                    6: "Saturday", 7: "Sunday"}

                        # Get unique days and slots
                        unique_days = sorted(display_df["day"].unique())
                        unique_slots = sorted(display_df["slot"].unique())

                        # Create color mapping for subjects
                        subjects = display_df["subject"].unique()
                        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8", "#F7DC6F", "#BB8FCE",
                                  "#85C1E2"]
                        subject_colors = {subject: colors[i % len(colors)] for i, subject in enumerate(subjects)}

                        # CSS styling
                        st.markdown("""
                        <style>
                        .timetable {
                            width: 100%;
                            border-collapse: collapse;
                            margin: 15px 0;
                            background: white;
                            border-radius: 8px;
                            overflow: hidden;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                        }
                        .timetable th {
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            padding: 12px;
                            text-align: center;
                            font-weight: 700;
                            border: none;
                        }
                        .timetable td {
                            padding: 10px;
                            border: 1px solid #e0e0e0;
                            text-align: center;
                        }
                        .timetable tr:nth-child(even) {
                            background: #f8f9ff;
                        }
                        .timetable tr:nth-child(odd) {
                            background: white;
                        }
                        .day-cell {
                            font-weight: 700;
                            color: white;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        }
                        .subject-text {
                            font-weight: 700;
                            font-size: 14px;
                            margin-bottom: 6px;
                            display: block;
                        }
                        .teacher-text {
                            font-weight: 600;
                            font-size: 12px;
                            display: block;
                            margin-top: 4px;
                        }
                        </style>
                        """, unsafe_allow_html=True)

                        # Create the table as HTML string
                        table_html = '<table class="timetable"><thead><tr><th>DAY</th>'

                        # Add slot headers
                        for slot in unique_slots:
                            table_html += f'<th>Slot {int(slot)}</th>'
                        table_html += '</tr></thead><tbody>'

                        # Add rows for each day
                        for day_num in unique_days:
                            day_name = days_map.get(int(day_num), f"Day {int(day_num)}")
                            table_html += f'<tr><td class="day-cell">{day_name}</td>'

                            # Add cells for each slot
                            for slot in unique_slots:
                                class_data = display_df[(display_df["day"] == day_num) & (display_df["slot"] == slot)]

                                if len(class_data) > 0:
                                    row_data = class_data.iloc[0]
                                    subject = row_data["subject"]
                                    teacher = row_data["teacher"]
                                    color = subject_colors.get(subject, "#667eea")

                                    table_html += f'''<td style="border-left: 5px solid {color}; background: linear-gradient(135deg, {color}10 0%, {color}05 100%);">
                                        <span class="subject-text" style="color: {color};">{subject}</span>
                                        <span class="teacher-text" style="color: #333;">👨‍🏫 {teacher}</span>
                                    </td>'''
                                else:
                                    table_html += '<td style="background: #fafafa; color: #ccc;">-</td>'

                            table_html += '</tr>'

                        table_html += '</tbody></table>'

                        st.markdown(table_html, unsafe_allow_html=True)

                        # Legend section
                        st.markdown("---")
                        st.markdown("### 📚 Subject Color Legend")

                        legend_cols = st.columns(min(4, len(subject_colors)))
                        for idx, (subject, color) in enumerate(subject_colors.items()):
                            with legend_cols[idx % len(legend_cols)]:
                                st.markdown(f"""
                                <div style='
                                    background: linear-gradient(135deg, {color} 0%, {color}dd 100%);
                                    border-radius: 8px;
                                    padding: 12px;
                                    color: white;
                                    text-align: center;
                                    font-weight: 700;
                                    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                                    font-size: 13px;
                                '>
                                    {subject}
                                </div>
                                """, unsafe_allow_html=True)

                        # Save to database
                        teachers_dict = dict(
                            zip(teachers_df["Name"].str.strip(), teachers_df["Hours"])
                        )
                        subjects_dict = dict(
                            zip(subjects_df["Name"].str.strip(), subjects_df["Hours"])
                        )

                        timetable_id = save_timetable(
                            name=timetable_name,
                            days=days,
                            slots_per_day=slots_per_day,
                            df=result_df,
                            teachers_hours=teachers_dict,
                            subjects_hours=subjects_dict,
                            user_id=st.session_state.user["id"],
                        )

                        st.success(f"✅ TimeTable saved to database (ID: {timetable_id})")

                        # Download option
                        excel_buffer = io.BytesIO()
                        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                            result_df.to_excel(writer, sheet_name="TimeTable", index=False)
                        excel_buffer.seek(0)

                        st.download_button(
                            label="📥 Download TimeTable (Excel)",
                            data=excel_buffer,
                            file_name=f"{timetable_name}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        )

                        # Clean up temp file
                        if os.path.exists(temp_file):
                            os.remove(temp_file)

                    except ValueError as e:
                        st.error(f"❌ Constraint Validation Error:\n{str(e)}")
                    except RuntimeError as e:
                        st.error(f"❌ Generation Error:\n{str(e)}")
                    except Exception as e:
                        st.error(f"❌ Unexpected Error:\n{str(e)}")

        except Exception as e:
            st.error(f"Error loading Excel file: {str(e)}")


def admin_panel():
    teacher_admin_panel, student_admin_panel = st.tabs(["Teachers", "Students"])

    with teacher_admin_panel:
        teacher_admin_page()

    with student_admin_panel:
        student_admin_page()


# ==================== MAIN APP ====================
def main():
    """Main application logic."""
    if st.session_state.user is None:
        login_page()
    else:
        # Sidebar menu
        with st.sidebar:
            st.title("📚 Menu")

            if st.session_state.user["role"].lower() == "teacher":
                page = st.radio(
                    "Navigate to:",
                    ["Home", "Admin Panel"],
                    key="nav_menu",
                )
            else:
                page = "Home"
                st.write("**Student View**")

            if st.button("Logout", key="sidebar_logout"):
                st.session_state.user = None
                st.session_state.page = "login"
                st.rerun()

        # Route to pages
        if page == "Home":
            home_page()
        elif page == "Admin Panel":
            if st.session_state.user["role"].lower() == "teacher":
                admin_panel()
            else:
                st.error("Only teachers can access the admin panel.")


if __name__ == "__main__":
    main()
