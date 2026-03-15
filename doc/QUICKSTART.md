# 🚀 Quick Start Guide

## One-Minute Setup

### On macOS/Linux:

```bash
# 1. Navigate to the project directory
cd /Users/apple/Downloads/Learning_Projects/Python/AITimeTable/AITimeTable

# 2. Run the setup script
chmod +x setup.sh
./setup.sh

# 3. Run the application
streamlit run app.py
```

### On Windows:

```bash
# 1. Navigate to the project directory
cd <path-to-AITimeTable>

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
streamlit run app.py
```

## First Time Users

### Step 1: Start the Application
After running `streamlit run app.py`, your browser will automatically open to `http://localhost:8501`

### Step 2: Register an Account
- Click on the **Register** section (right side)
- Enter your desired username and password
- Enter your full name
- Select your role: "Teacher" or "Student"
- Click **Register**

### Step 3: Login
- Use your registered credentials to login

### Step 4: For Teachers Only - Generate Your First TimeTable

1. **Go to Admin Panel** (left sidebar, after login)

2. **Upload Excel File**:
   - Click "Choose Excel file"
   - Use the provided `timetable_data.xlsx` as a template or create your own
   - Ensure it has two sheets: "Teachers" and "Subjects"

3. **Configure Parameters**:
   - Slots per Day: 5 (number of time periods)
   - Number of Days: 5 (Monday to Friday)
   - Max Teacher Slots/Day: 1 (max classes per teacher per day)
   - Max Subject Slots/Day: 1 (max periods per subject per day)
   - TimeTable Name: Give it a meaningful name

4. **Generate**:
   - Click "🚀 Generate TimeTable"
   - Wait for the generation to complete
   - Review the result in the displayed table

5. **Download or Use**:
   - Click "📥 Download TimeTable (Excel)" to save as Excel file
   - Or use the generated timetable immediately

### Step 5: View TimeTable (Teachers and Students)

1. Go to **Home** page
2. In the "Select a timetable" dropdown, choose any generated timetable
3. View the schedule in grid format
4. See teacher and subject hour requirements

## Sample Data

A sample `timetable_data.xlsx` file is included. It contains:

**Teachers Sheet**:
- Teacher names in "Name" column
- Required teaching hours in "Hours" column

**Subjects Sheet**:
- Subject names in "Name" column
- Required hours per week in "Hours" column

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| Module not found | Run `pip install -r requirements.txt` |
| Port already in use | Run `streamlit run app.py --server.port 8502` |
| Excel file not recognized | Ensure sheets are named exactly "Teachers" and "Subjects" |
| No feasible solution | Increase days/slots or reduce hour requirements |
| Reset database | Delete `timetable.db` file |

## Default Test Credentials

After first setup, here are some test accounts you can create:

**Teacher Account**:
- Username: `teacher1`
- Password: `pass123`
- Name: `John Doe`

**Student Account**:
- Username: `student1`
- Password: `pass123`
- Name: `Jane Smith`

## File Structure Explanation

```
📁 AITimeTable/
├── 📄 app.py                 ← Main Streamlit application (START HERE)
├── 📄 TimeTable.py           ← Timetable generation engine
├── 📄 database.py            ← SQLite database management
├── 📄 requirements.txt       ← Python packages needed
├── 📄 setup.sh              ← Auto-setup script
├── 📄 README.md             ← Full documentation
├── 📄 QUICKSTART.md         ← This file
├── 📁 venv/                 ← Virtual environment (created by setup.sh)
├── 📁 .venv/                ← Alternative venv location
├── 📄 timetable_data.xlsx   ← Sample input data
├── 📄 final_timetable.xlsx  ← Example output
└── 📄 timetable.db          ← Database file (created on first run)
```

## How the System Works

1. **Upload Excel** → Your teacher/subject requirements
2. **Configure** → Set number of days, slots, and constraints
3. **Generate** → Uses Google OR-Tools to create optimal schedule
4. **Save** → Stores in SQLite database
5. **View** → Teachers and students can view the timetable
6. **Download** → Export as Excel file if needed

## Next Steps

- **Explore**: Try uploading different Excel files with various requirements
- **Customize**: Adjust parameters to see how they affect scheduling
- **Scale**: Use it for your school or institution
- **Integrate**: The database is ready for integration with other systems

## Getting Help

- Check **README.md** for detailed documentation
- Review error messages - they usually explain what went wrong
- Ensure your Excel file matches the required format
- Delete `timetable.db` and start fresh if database issues occur

---

**Happy Scheduling! 🎓📅**
