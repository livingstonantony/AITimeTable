# 📊 Project Overview & Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT WEB INTERFACE                   │
│                  (app.py - User Dashboard)                   │
└────────────────┬────────────────────────────┬────────────────┘
                 │                            │
        ┌────────▼────────┐         ┌────────▼────────┐
        │ Authentication  │         │  Admin Panel    │
        │  (Login/Reg)    │         │ (Generate TT)   │
        └────────┬────────┘         └────────┬────────┘
                 │                            │
        ┌────────▼────────────────────────────▼────────┐
        │     DATABASE LAYER (database.py)             │
        │  SQLite Database (timetable.db)              │
        │  - Users Management                          │
        │  - TimeTable Storage                         │
        │  - Hour Requirements Tracking                │
        └────────┬─────────────────────────────────────┘
                 │
        ┌────────▼────────────────────────────┐
        │  TIMETABLE GENERATION ENGINE        │
        │  (TimeTable.py)                     │
        │  - Constraint Solver (OR-Tools)     │
        │  - Excel Data Loading               │
        │  - Solution Generation              │
        └────────┬─────────────────────────────┘
                 │
        ┌────────▼────────────────────────────┐
        │   EXTERNAL DEPENDENCIES             │
        │  - Pandas (Excel Operations)        │
        │  - OR-Tools (Solver Engine)         │
        │  - OpenpyXL (Excel I/O)             │
        └─────────────────────────────────────┘
```

## Data Flow

```
INPUT                    PROCESS                   OUTPUT
====================================================================

Excel File          ┌─────────────────┐         Database
(Teachers,    ──→   │  TimeTable.py   │   ──→   (SQLite)
 Subjects)          │  (OR-Tools)     │         
                    └─────────────────┘         Generated
                                                Timetable
                              │
                              ▼
                    ┌─────────────────┐
                    │    Database     │
                    │  (database.py)  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Streamlit UI   │
                    │  (app.py)       │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  User View      │
                    │  Download Excel │
                    └─────────────────┘
```

## Database Schema Diagram

```
users
├── id (PK)
├── username (UNIQUE)
├── password
├── role (Teacher/Student)
├── name
└── created_at
    │
    └──→ timetables
         ├── id (PK)
         ├── name
         ├── days
         ├── slots_per_day
         ├── generated_at
         ├── created_by (FK → users.id)
         │
         ├──→ timetable_slots
         │    ├── id (PK)
         │    ├── timetable_id (FK)
         │    ├── day
         │    ├── slot
         │    ├── teacher
         │    └── subject
         │
         ├──→ teacher_hours
         │    ├── id (PK)
         │    ├── timetable_id (FK)
         │    ├── teacher_name
         │    └── required_hours
         │
         └──→ subject_hours
              ├── id (PK)
              ├── timetable_id (FK)
              ├── subject_name
              └── required_hours
```

## File Organization

```
AITimeTable/
│
├── 🌐 WEB INTERFACE & ROUTING
│   └── app.py                     # Main Streamlit application
│       ├── Login/Registration module
│       ├── Home page module
│       ├── Admin panel module
│       └── Timetable display module
│
├── 🔧 CORE LOGIC
│   ├── TimeTable.py              # Timetable generation engine
│   │   ├── Excel data loading
│   │   ├── Constraint building
│   │   ├── OR-Tools solver integration
│   │   └── Solution formatting
│   │
│   └── database.py               # Database management
│       ├── User authentication
│       ├── Timetable CRUD operations
│       ├── Data persistence
│       └── Query functions
│
├── ⚙️  CONFIGURATION & SETUP
│   ├── config.py                 # Application settings
│   ├── requirements.txt           # Python dependencies
│   ├── setup.sh                  # Linux/macOS setup script
│   └── setup.bat                 # Windows setup script
│
├── 📚 DOCUMENTATION
│   ├── README.md                 # Full documentation
│   ├── QUICKSTART.md             # Quick start guide
│   ├── PROJECT_OVERVIEW.md       # This file
│   └── ARCHITECTURE.md           # Detailed architecture
│
├── 📊 DATA FILES
│   ├── timetable_data.xlsx       # Sample input
│   ├── final_timetable.xlsx      # Example output
│   └── timetable.db              # SQLite database (created on first run)
│
└── 📁 RUNTIME DIRECTORIES
    └── venv/                     # Virtual environment (created by setup)
```

## Technology Stack

```
Frontend:         Streamlit (Python web framework)
Backend:          Python 3.8+
Database:         SQLite 3
Solver Engine:    Google OR-Tools
Data Processing:  Pandas
Excel I/O:        Openpyxl
Authentication:   Session-based (SQLite)
```

## Features Overview

### 1️⃣ Authentication System
- **Components**: Login/Registration forms
- **Storage**: SQLite users table
- **Security**: Password-based authentication
- **Roles**: Teacher and Student

### 2️⃣ TimeTable Generation
- **Input**: Excel file (Teachers & Subjects sheets)
- **Parameters**: Days, slots/day, max slots/day constraints
- **Algorithm**: Constraint satisfaction using Google OR-Tools
- **Output**: Optimized schedule respecting all constraints

### 3️⃣ Data Management
- **Database**: SQLite (lightweight, no setup needed)
- **Storage**: Complete timetable history with requirements
- **Access**: Query generation and retrieval functions

### 4️⃣ User Interface
- **Teachers**: Admin panel to generate timetables
- **Students**: View-only access to timetables
- **Display**: Grid and detailed table views

## Constraints Implemented

```
✓ Exact Hours Constraint
  Each teacher teaches exactly their assigned hours
  Each subject is taught exactly the required hours

✓ One Assignment Per Slot
  Each time slot has exactly one teacher
  Each time slot has exactly one subject

✓ Daily Limit Constraint
  Teachers don't exceed max slots per day
  Subjects don't exceed max slots per day

✓ No Consecutive Repetition
  Same teacher can't teach same subject in consecutive periods
```

## How It All Works Together

```
1. USER INTERACTION
   └─→ Teacher/Student logs in via Streamlit UI (app.py)

2. AUTHENTICATION
   └─→ Database checks credentials (database.py)

3. FOR TEACHERS ONLY - GENERATION
   └─→ Upload Excel file with data
       ├─→ TimeTable.py loads and validates data
       ├─→ OR-Tools solver finds optimal schedule
       └─→ Result saved to database

4. DISPLAY
   └─→ Any user can view timetables
       ├─→ Database queries timetable data
       ├─→ Streamlit formats and displays
       └─→ Option to download as Excel

5. PERSISTENCE
   └─→ All data stored in SQLite database
```

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Timetable Generation | 1-30 sec | Depends on complexity & constraints |
| Database Save | <1 sec | Efficient SQLite operations |
| Page Load | <1 sec | Streamlit caching enabled |
| User Login | <100ms | Fast password verification |

## Scalability

✓ Can handle hundreds of teachers/subjects
✓ Unlimited timetable history in database
✓ SQLite suitable for small-to-medium institutions
✓ Easy upgrade to PostgreSQL if needed

## Security Features

✓ SQLite database for secure data storage
✓ Role-based access control (Teacher/Student)
✓ Session management via Streamlit
✓ Unique usernames prevent duplicate accounts

## Future Enhancement Points

1. **Multi-Class Support**: Handle multiple classes simultaneously
2. **Teacher Preferences**: Constraints for preferred time slots
3. **Conflict Detection**: Real-time conflict identification
4. **Analytics Dashboard**: Usage statistics and reports
5. **Mobile App**: REST API for mobile clients
6. **Email Integration**: Notifications for generated timetables
7. **Export Formats**: PDF, iCal, Google Calendar sync

---

**Last Updated**: February 23, 2026
**Version**: 1.0
