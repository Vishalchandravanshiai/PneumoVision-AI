"""
database.py
------------
This file handles the SQLite database.
It stores the history of scans (predictions).

Usage:
    from database import init_db, add_scan, get_all_scans

    init_db()  # call once when the app starts
    scan_id = add_scan(patient_name="Ram", image_path="uploads/xray1.png",
                        prediction="Pneumonia", confidence=92.5)
    scans = get_all_scans()
"""

import sqlite3
import os
from datetime import datetime

# The database file will be created right here in the backend folder
DB_PATH = os.path.join(os.path.dirname(__file__), "pneumovision.db")


def get_connection():
    """Returns a new database connection."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # so results come back as dict-like objects
    return conn


def init_db():
    """
    Creates the database and table (if they don't already exist).
    Call this once when the app starts.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            image_path TEXT NOT NULL,
            prediction TEXT NOT NULL,
            confidence REAL NOT NULL,
            gradcam_path TEXT,
            report_path TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print(f"[database.py] Database ready at: {DB_PATH}")


def add_scan(patient_name, image_path, prediction, confidence,
             gradcam_path=None, report_path=None):
    """
    Saves a new scan record in the database.
    Returns the id of that scan (scan_id).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO scans (patient_name, image_path, prediction, confidence,
                            gradcam_path, report_path, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        patient_name,
        image_path,
        prediction,
        confidence,
        gradcam_path,
        report_path,
        datetime.now().isoformat()
    ))
    conn.commit()
    scan_id = cursor.lastrowid
    conn.close()
    return scan_id


def get_all_scans():
    """Returns the list of all scans, newest first."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_scan_by_id(scan_id):
    """Returns the details of one specific scan by its id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def delete_scan(scan_id):
    """Deletes a scan record (if needed)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
    conn.commit()
    conn.close()


# For testing: running this file directly will create the database
if __name__ == "__main__":
    init_db()
    print("Database and table created successfully!")