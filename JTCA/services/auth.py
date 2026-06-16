"""JTCA Authentication Service (email/password + role).

Implements:
- register(email, password, role)
- login(email, password, role)

Uses PostgreSQL table `app_users` (created if missing).
Passwords are hashed with bcrypt (or SHA256 fallback if bcrypt is missing).
"""

from __future__ import annotations

import logging
import os
import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


# Optional dependencies
try:
    import bcrypt
    HAS_BCRYPT = True
except Exception:
    HAS_BCRYPT = False


from database.postgres_db import get_connection


_ALLOWED_ROLES = {"Admin", "Trade Analyst"}


def _hash_password(password: str) -> str:
    """Hash a password using bcrypt if available, otherwise fall back to SHA-256."""
    if HAS_BCRYPT:
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password_bytes, salt).decode("utf-8")
    else:
        return "sha256:" + hashlib.sha256(password.encode("utf-8")).hexdigest()


def _ensure_users_table():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS app_users (
                    id SERIAL PRIMARY KEY,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    display_name TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
                """
            )
        conn.commit()

        # Check if table is empty
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM app_users")
            row = cur.fetchone()
            count = row["count"] if isinstance(row, dict) else row[0]

        if count == 0:
            # Seed default users
            admin_hash = _hash_password("Admin123!")
            analyst_hash = _hash_password("Analyst123!")

            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO app_users (email, password_hash, role, display_name)
                    VALUES 
                      ('admin@jabil.com', %s, 'Admin', 'Admin User'),
                      ('analyst@jabil.com', %s, 'Trade Analyst', 'Trade Analyst')
                    ON CONFLICT (email) DO NOTHING
                    """,
                    (admin_hash, analyst_hash),
                )
            conn.commit()
            logger.info("Seeded default users (admin@jabil.com and analyst@jabil.com)")
    except Exception as e:
        logger.error(f"Error checking/seeding app_users table: {e}")
    finally:
        conn.close()


@dataclass
class AuthResult:
    ok: bool
    message: str = ""


class AuthService:
    def __init__(self):
        if not HAS_BCRYPT:
            logger.warning("bcrypt is not installed. Falling back to SHA-256 for password hashing.")
        _ensure_users_table()

    @staticmethod
    def _normalize_role(role: str) -> str:
        if role not in _ALLOWED_ROLES:
            return "Trade Analyst"
        return role

    @staticmethod
    def _normalize_email(email: str) -> str:
        return (email or "").strip().lower()

    def register(self, email: str, password: str, role: str) -> bool:
        email_n = self._normalize_email(email)
        role_n = self._normalize_role(role)

        if not email_n:
            raise ValueError("Email is required")
        # Basic email format validation
        if "@" not in email_n or "." not in email_n.split("@", 1)[1]:
            raise ValueError("Email must be in a valid format (example: name@company.com)")
        # Password rule: at least 6 chars AND must include at least 1 symbol.
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters")
        if not any((not ch.isalnum()) for ch in password):
            raise ValueError("Password must include at least 1 symbol")

        password_hash = _hash_password(password)
        display_name = email_n.split("@", 1)[0].replace(".", " ").title() or "User"

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO app_users (email, password_hash, role, display_name)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (email) DO NOTHING
                    """,
                    (email_n, password_hash, role_n, display_name),
                )
            conn.commit()

            with conn.cursor() as cur:
                cur.execute("SELECT id FROM app_users WHERE email=%s", (email_n,))
                row = cur.fetchone()
            return bool(row)
        finally:
            conn.close()

    def login(self, email: str, password: str, role: str) -> bool:
        email_n = self._normalize_email(email)
        role_n = self._normalize_role(role)

        if not email_n or not password:
            return False

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT password_hash, role FROM app_users WHERE email=%s
                    """,
                    (email_n,),
                )
                row = cur.fetchone()

            if not row:
                return False

            stored_hash = row.get("password_hash") if isinstance(row, dict) else row["password_hash"]
            stored_role = row.get("role") if isinstance(row, dict) else row["role"]

            if stored_role != role_n:
                return False

            if stored_hash.startswith("sha256:"):
                hashed = "sha256:" + hashlib.sha256(password.encode("utf-8")).hexdigest()
                ok = (stored_hash == hashed)
            else:
                if HAS_BCRYPT:
                    ok = bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
                else:
                    logger.error("Stored hash uses bcrypt, but bcrypt is not installed.")
                    ok = False
            return bool(ok)
        finally:
            conn.close()

    def user_exists(self, email: str, role: str | None = None) -> bool:
        """Return True if a user exists for this email."""
        email_n = self._normalize_email(email)
        if not email_n:
            return False

        role_n = None if role is None else self._normalize_role(role)

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                if role_n is None:
                    cur.execute("SELECT 1 FROM app_users WHERE email=%s", (email_n,))
                else:
                    cur.execute("SELECT 1 FROM app_users WHERE email=%s AND role=%s", (email_n, role_n))
                row = cur.fetchone()
            return bool(row)
        finally:
            conn.close()

    def get_user_display_name(self, email: str) -> str:
        email_n = self._normalize_email(email)
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT display_name FROM app_users WHERE email=%s", (email_n,))
                row = cur.fetchone()
            if not row:
                return email_n
            return row.get("display_name") if isinstance(row, dict) else row[0]
        finally:
            conn.close()
