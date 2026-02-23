# Configuration file for AI TimeTable System

# Database
DATABASE_PATH = "timetable.db"

# Streamlit settings
STREAMLIT_PAGE_TITLE = "AI TimeTable"
STREAMLIT_LAYOUT = "wide"
STREAMLIT_INITIAL_SIDEBAR = "expanded"

# Default parameters
DEFAULT_SLOTS_PER_DAY = 5
DEFAULT_DAYS = 5
DEFAULT_MAX_TEACHER_SLOTS = 1
DEFAULT_MAX_SUBJECT_SLOTS = 1

# Solver settings
SOLVER_TIME_LIMIT = 60  # seconds
SOLVER_LOG_SEARCH_PROGRESS = False

# Excel settings
EXCEL_ENGINE = "openpyxl"
ALLOWED_EXTENSIONS = ["xlsx", "xls"]

# UI Settings
THEME_COLOR_PRIMARY = "#FF6B35"
THEME_COLOR_SECONDARY = "#004E89"
