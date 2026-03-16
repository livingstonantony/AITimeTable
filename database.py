import sqlite3
import os
from datetime import datetime
import json

from streamlit import cursor

DB_PATH = "timetable.db"


def get_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with required tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # Users table (teachers and students)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Timetables table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS timetables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            days INTEGER NOT NULL,
            slots_per_day INTEGER NOT NULL,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    """)

    # Timetable slots table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS timetable_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timetable_id INTEGER NOT NULL,
            day INTEGER NOT NULL,
            slot INTEGER NOT NULL,
            teacher TEXT NOT NULL,
            subject TEXT NOT NULL,
            FOREIGN KEY (timetable_id) REFERENCES timetables(id)
        )
    """)

    # Create timetable slot for teachers
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS teacher_timetable_slots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timetable_id INTEGER NOT NULL,
                day INTEGER NOT NULL,
                slot INTEGER NOT NULL,
                teacher TEXT NOT NULL,
                subject TEXT NOT NULL,
                class_name TEXT NOT NULL,
                FOREIGN KEY (timetable_id) REFERENCES timetables(id)
            )
        """)

    # Teacher hours table (for tracking requirements)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teacher_hours (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timetable_id INTEGER NOT NULL,
            teacher_name TEXT NOT NULL,
            required_hours INTEGER NOT NULL,
            FOREIGN KEY (timetable_id) REFERENCES timetables(id)
        )
    """)

    # Subject hours table (for tracking requirements)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subject_hours (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timetable_id INTEGER NOT NULL,
            subject_name TEXT NOT NULL,
            required_hours INTEGER NOT NULL,
            FOREIGN KEY (timetable_id) REFERENCES timetables(id)
        )
    """)
    # Subject teacher hours table (for tracking requirements)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teacher_subject_hours (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timetable_id INTEGER NOT NULL,
            teacher_name TEXT NOT NULL,
            subject_name TEXT NOT NULL,
            class_name TEXT NOT NULL,
            required_hours INTEGER NOT NULL,
            FOREIGN KEY (timetable_id) REFERENCES timetables(id)
        )
    """)


    conn.commit()
    conn.close()


# ==================== USER MANAGEMENT ====================
def create_user(username, password, role, name):
    """Create a new user."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (username, password, role, name)
            VALUES (?, ?, ?, ?)
        """, (username, password, role, name))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def verify_user(username, password):
    """Verify user credentials."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, username, role, name FROM users
        WHERE username = ? AND password = ?
    """, (username, password))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def get_user(user_id):
    """Get user details by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def user_exists(username):
    """Check if user exists."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


# ==================== SAVE TEACHER TIME TABLE ================

def save_teacher_time_table(name, days, slots_per_day, df, teachers_hours, subjects_hours, user_id):
    """Save teacher timetable to database."""
    conn = get_connection()
    cursor = conn.cursor()

    # Insert timetable
    cursor.execute("""
        INSERT INTO timetables (name, days, slots_per_day, created_by)
        VALUES (?, ?, ?, ?)
    """, (name, days, slots_per_day, user_id))

    timetable_id = cursor.lastrowid

    # Insert slots
    for _, row in df.iterrows():
        cursor.execute("""
                INSERT INTO teacher_timetable_slots (timetable_id, day, slot, teacher, subject, class_name)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (timetable_id, int(row["Day"]), int(row["Slot"]), row["Teacher"], row["Subject"], row["Class"]))


    # Insert teacher hours
    for teacher, hours in teachers_hours.items():
        cursor.execute("""
            INSERT INTO teacher_hours (timetable_id, teacher_name, required_hours)
            VALUES (?, ?, ?)
        """, (timetable_id, teacher, hours))


    print("teacher_subject_hours: start")
    # Insert subject hours
    for (teacher, subject, class_name), hours in subjects_hours.items():
        cursor.execute("""
            INSERT INTO teacher_subject_hours (timetable_id, teacher_name, subject_name, class_name, required_hours)
            VALUES (?, ?, ?, ?, ?)
        """, (timetable_id, teacher, subject, class_name, hours))

    print("teacher_subject_hours: success")

    conn.commit()
    conn.close()
    return timetable_id


# ==================== TIMETABLE MANAGEMENT ====================
def save_timetable(name, days, slots_per_day, df, teachers_hours, subjects_hours, user_id):
    """Save generated timetable to database."""
    conn = get_connection()
    cursor = conn.cursor()

    # Insert timetable
    cursor.execute("""
        INSERT INTO timetables (name, days, slots_per_day, created_by)
        VALUES (?, ?, ?, ?)
    """, (name, days, slots_per_day, user_id))

    timetable_id = cursor.lastrowid

    # Insert slots
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO timetable_slots (timetable_id, day, slot, teacher, subject)
            VALUES (?, ?, ?, ?, ?)
        """, (timetable_id, int(row["Day"]), int(row["Slot"]), row["Teacher"], row["Subject"]))

    # Insert teacher hours
    for teacher, hours in teachers_hours.items():
        cursor.execute("""
            INSERT INTO teacher_hours (timetable_id, teacher_name, required_hours)
            VALUES (?, ?, ?)
        """, (timetable_id, teacher, hours))

    # Insert subject hours
    for subject, hours in subjects_hours.items():
        cursor.execute("""
            INSERT INTO subject_hours (timetable_id, subject_name, required_hours)
            VALUES (?, ?, ?)
        """, (timetable_id, subject, hours))

    conn.commit()
    conn.close()
    return timetable_id


def get_timetable(timetable_id):
    """Get timetable details."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM timetables WHERE id = ?", (timetable_id,))
    timetable = cursor.fetchone()
    conn.close()
    return dict(timetable) if timetable else None


def get_timetable_slots(timetable_id):
    """Get all slots for a timetable."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM timetable_slots
        WHERE timetable_id = ?
        ORDER BY day, slot
    """, (timetable_id,))
    slots = cursor.fetchall()
    conn.close()
    return [dict(slot) for slot in slots]


def get_all_timetables():
    """Get all timetables."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.*, u.name as created_by_name
        FROM timetables t
        LEFT JOIN users u ON t.created_by = u.id
        ORDER BY t.generated_at DESC
    """)
    timetables = cursor.fetchall()
    conn.close()
    return [dict(tt) for tt in timetables]


def get_timetable_requirements(timetable_id):
    """Get teacher and subject hours for a timetable."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT teacher_name, required_hours FROM teacher_hours
        WHERE timetable_id = ?
    """, (timetable_id,))
    teachers = {row["teacher_name"]: row["required_hours"] for row in cursor.fetchall()}

    cursor.execute("""
        SELECT subject_name, required_hours FROM subject_hours
        WHERE timetable_id = ?
    """, (timetable_id,))
    subjects = {row["subject_name"]: row["required_hours"] for row in cursor.fetchall()}

    conn.close()
    return teachers, subjects


def delete_timetable(timetable_id):
    """Delete a timetable and all its associated data."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Delete all related records first (cascade delete)
        cursor.execute("DELETE FROM timetable_slots WHERE timetable_id = ?", (timetable_id,))
        cursor.execute("DELETE FROM teacher_timetable_slots WHERE timetable_id = ?", (timetable_id,))
        cursor.execute("DELETE FROM teacher_hours WHERE timetable_id = ?", (timetable_id,))
        cursor.execute("DELETE FROM subject_hours WHERE timetable_id = ?", (timetable_id,))
        cursor.execute("DELETE FROM teacher_subject_hours WHERE timetable_id = ?", (timetable_id,))
        # Delete the timetable itself
        cursor.execute("DELETE FROM timetables WHERE id = ?", (timetable_id,))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error deleting timetable: {e}")
        return False
    finally:
        conn.close()
