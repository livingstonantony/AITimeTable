# 🎓 AI TimeTable System

A modern Streamlit-based timetable generation system with teacher and student authentication, using Google OR-Tools constraint solver.

## Features

✨ **Authentication System**
- Teacher and Student login/registration
- SQLite-based user management

📅 **TimeTable Management**
- Upload Excel files with teacher and subject requirements
- Auto-generate optimal timetables using constraint satisfaction
- View timetables in grid and detailed formats
- Download generated timetables as Excel files

💾 **Database Integration**
- SQLite database to store all generated timetables
- Track teacher and subject hour requirements
- Full audit trail of generated timetables

🔧 **Admin Panel** (Teachers Only)
- Upload custom Excel files
- Configure timetable parameters (slots, days, max hours)
- Generate and save timetables

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Steps

1. **Create a virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the application**:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Project Structure

```
AITimeTable/
├── app.py                    # Main Streamlit application
├── TimeTable.py             # Timetable generation logic (OR-Tools)
├── database.py              # SQLite database functions
├── requirements.txt         # Python dependencies
├── timetable_data.xlsx      # Sample input file
├── final_timetable.xlsx     # Generated output (example)
└── README.md               # This file
```

## How to Use

### For Teachers:

1. **Login/Register**:
   - Click Register to create a new teacher account
   - Or use existing credentials to login

2. **Generate TimeTable**:
   - Navigate to "Admin Panel"
   - Upload an Excel file with:
     - **Teachers sheet**: Columns: Name, Hours
     - **Subjects sheet**: Columns: Name, Hours
   - Configure parameters:
     - Slots per Day (e.g., 5)
     - Number of Days (e.g., 5)
     - Max Teacher Slots per Day (e.g., 1-2)
     - Max Subject Slots per Day (e.g., 1-2)
   - Click "Generate TimeTable"
   - Download the result or view in app

3. **View TimeTable**:
   - Go to "Home" page
   - Select any generated timetable
   - View in grid or detailed format

### For Students:

1. **Login/Register**:
   - Create a student account

2. **View TimeTable**:
   - Go to "Home" page
   - Select a timetable from the list
   - View the class schedule

## Sample Excel File Format

### Teachers Sheet:
| Name | Hours |
|------|-------|
| Mr. A | 10 |
| Ms. B | 8 |
| Dr. C | 12 |

### Subjects Sheet:
| Name | Hours |
|------|-------|
| Math | 10 |
| English | 8 |
| Science | 12 |

## Database Schema

### users
- id (primary key)
- username (unique)
- password
- role (Teacher/Student)
- name
- created_at

### timetables
- id (primary key)
- name
- days
- slots_per_day
- generated_at
- created_by (foreign key to users)

### timetable_slots
- id (primary key)
- timetable_id (foreign key)
- day
- slot
- teacher
- subject

### teacher_hours & subject_hours
- Store requirements for each timetable

## Constraint Details

The timetable generator respects the following constraints:

1. **Exact Hours**: Each teacher/subject gets exactly their required hours
2. **One Teacher per Slot**: Each time slot has exactly one teacher
3. **One Subject per Slot**: Each time slot has exactly one subject
4. **Max per Day**: Teachers and subjects don't exceed max slots per day
5. **No Consecutive Repetition**: Same teacher/subject not scheduled back-to-back

## Troubleshooting

### "No feasible timetable found"
- Increase the number of days or slots per day
- Reduce teacher or subject hour requirements
- Increase max slots per day for teachers/subjects

### Excel file errors
- Ensure file has "Teachers" and "Subjects" sheets
- Columns must be named exactly: "Name" and "Hours"
- No empty rows

### Database errors
- Delete `timetable.db` to reset database
- Ensure write permissions in the directory

## Future Enhancements

- [ ] Email notifications for generated timetables
- [ ] Multi-class support
- [ ] Conflict detection and resolution
- [ ] Teacher/subject preferences
- [ ] Calendar integration
- [ ] REST API for mobile app
- [ ] Advanced analytics and reports

## License

MIT License

## Support

For issues or questions, please create an issue in the repository.


FILENAME = teacher_timetable_data

SHEET_NAME = Teachers
Name	Hours
Livin	5
Mercy	5
Akash	5
Jency	5
Jecil	5

SHEET_NAME = Subjects
Teacher	Name	Class	Hours
Livin	C	BCA_A	2
Livin	CPP	BCA_B	3
Mercy	JAVA	Bsc	2
Akash	Python	Bsc	3
Mercy	MYSQL	BCA_A	3
Akash	Java_LAB	Bsc	2
Jency	MYSQL_LAB	BCA_B	2
Jency	C_LAB	BCA_A	3
Jecil	CPP_LAB	Bsc	3
Jecil	Python_LAB	Bsc	2


Add another option create timetable for teachers based on the constraints, only admin can do this

e.g, If i log in as particular teacher highlight that slots for teacher can see their slots very easily
