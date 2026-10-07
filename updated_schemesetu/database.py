import sqlite3
import hashlib
import os
from datetime import datetime

DB_NAME = "schemesetu.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            password_salt TEXT NOT NULL,
            email_verified INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            user_id INTEGER PRIMARY KEY,
            applicant_type TEXT,
            age INTEGER,
            gender TEXT,
            state TEXT,
            district TEXT,
            area_type TEXT,
            annual_income REAL,
            social_category TEXT,
            occupation TEXT,
            bpl_status TEXT,
            marital_status TEXT,
            minority_status TEXT,

            is_student TEXT,
            education_level TEXT,
            course TEXT,
            study_year TEXT,
            institution_type TEXT,

            has_disability TEXT,
            disability_percentage REAL,

            is_farmer TEXT,
            land_ownership TEXT,
            land_size_acres REAL,
            farmer_type TEXT,

            business_type TEXT,
            updated_at TEXT NOT NULL,

            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


def hash_password(password):
    salt = os.urandom(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        260000,
    )
    return password_hash.hex(), salt.hex()


def verify_password(password, stored_hash, stored_salt):
    salt = bytes.fromhex(stored_salt)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        260000,
    ).hex()
    return password_hash == stored_hash


def email_exists(email):
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM users WHERE email = ?",
        (email.lower().strip(),),
    ).fetchone()
    conn.close()
    return row is not None


def create_user(name, email, password):
    password_hash, salt = hash_password(password)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO users
        (name, email, password_hash, password_salt, email_verified, created_at)
        VALUES (?, ?, ?, ?, 1, ?)
        """,
        (
            name.strip(),
            email.lower().strip(),
            password_hash,
            salt,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )

    user_id = cur.lastrowid
    conn.commit()
    conn.close()
    return user_id


def authenticate_user(email, password):
    conn = get_connection()
    row = conn.execute(
        """
        SELECT id, name, email, password_hash, password_salt, email_verified
        FROM users
        WHERE email = ?
        """,
        (email.lower().strip(),),
    ).fetchone()
    conn.close()

    if row is None:
        return None

    if not verify_password(
        password,
        row["password_hash"],
        row["password_salt"],
    ):
        return None

    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "email_verified": bool(row["email_verified"]),
    }


def save_profile(user_id, profile):
    fields = [
        "applicant_type",
        "age",
        "gender",
        "state",
        "district",
        "area_type",
        "annual_income",
        "social_category",
        "occupation",
        "bpl_status",
        "marital_status",
        "minority_status",
        "is_student",
        "education_level",
        "course",
        "study_year",
        "institution_type",
        "has_disability",
        "disability_percentage",
        "is_farmer",
        "land_ownership",
        "land_size_acres",
        "farmer_type",
        "business_type",
    ]

    values = [profile.get(field) for field in fields]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO profiles (
            user_id,
            applicant_type,
            age,
            gender,
            state,
            district,
            area_type,
            annual_income,
            social_category,
            occupation,
            bpl_status,
            marital_status,
            minority_status,
            is_student,
            education_level,
            course,
            study_year,
            institution_type,
            has_disability,
            disability_percentage,
            is_farmer,
            land_ownership,
            land_size_acres,
            farmer_type,
            business_type,
            updated_at
        )
        VALUES (
            ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
        )
        ON CONFLICT(user_id) DO UPDATE SET
            applicant_type=excluded.applicant_type,
            age=excluded.age,
            gender=excluded.gender,
            state=excluded.state,
            district=excluded.district,
            area_type=excluded.area_type,
            annual_income=excluded.annual_income,
            social_category=excluded.social_category,
            occupation=excluded.occupation,
            bpl_status=excluded.bpl_status,
            marital_status=excluded.marital_status,
            minority_status=excluded.minority_status,
            is_student=excluded.is_student,
            education_level=excluded.education_level,
            course=excluded.course,
            study_year=excluded.study_year,
            institution_type=excluded.institution_type,
            has_disability=excluded.has_disability,
            disability_percentage=excluded.disability_percentage,
            is_farmer=excluded.is_farmer,
            land_ownership=excluded.land_ownership,
            land_size_acres=excluded.land_size_acres,
            farmer_type=excluded.farmer_type,
            business_type=excluded.business_type,
            updated_at=excluded.updated_at
        """,
        [
            user_id,
            *values,
            datetime.now().isoformat(timespec="seconds"),
        ],
    )

    conn.commit()
    conn.close()


def get_profile(user_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM profiles WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    conn.close()

    return dict(row) if row else None
