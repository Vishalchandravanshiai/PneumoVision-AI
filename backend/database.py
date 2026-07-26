"""
database.py
------------
Yeh file SQLite database handle karti hai.
Isme scans (predictions) ki history save hoti hai.

Use kaise karein:
    from database import init_db, add_scan, get_all_scans

    init_db()  # app start hote hi ek baar call karo
    scan_id = add_scan(patient_name="Ram", image_path="uploads/xray1.png",
                        prediction="Pneumonia", confidence=92.5)
    scans = get_all_scans()
"""

import sqlite3
import os
from datetime import datetime

# Database file yahin backend folder me banegi
DB_PATH = os.path.join(os.path.dirname(__file__), "pneumovision.db")


def get_connection():
    """Ek naya database connection deta hai."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # taaki result dict jaisa mile
    return conn


def init_db():
    """
    Database aur table banata hai (agar pehle se nahi hai to).
    Isko app start hote hi ek baar call karo.
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
    Naya scan record database me save karta hai.
    Return karta hai us scan ki id (scan_id).
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
    """Saare scans ki list deta hai, sabse naya sabse upar."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_scan_by_id(scan_id):
    """Ek specific scan ki details deta hai id se."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def delete_scan(scan_id):
    """Ek scan record delete karta hai (agar zarurat pade)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
    conn.commit()
    conn.close()


# Testing ke liye: agar ye file directly run karo to database ban jayegi
if __name__ == "__main__":
    init_db()
    print("Database aur table successfully ban gaye!")
