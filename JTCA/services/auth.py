"""JTCA Authentication Service (email/password + role).

Implements:
- register(email, password, role)
- login(email, password, role)

Uses PostgreSQL table `app_users` (created if missing).
Passwords are hashed with bcrypt.

If bcrypt/psycopg2 aren't installed or DB isn't available,
this module raises an error; the UI should handle it.
"""

from __future__ import annotations

import logging
import os
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
    finally:
        conn.close()


@dataclass
class AuthResult:
    ok: bool
    message: str = ""


class AuthService:
    def __init__(self):
        if not HAS_BCRYPT:
            raise ImportError("bcrypt not installed. Run: pip install bcrypt")
        _ensure_users_table()

    @staticmethod
    def _normalize_role(role: str) -> str:
        if role not in _ALLOWED_ROLES:
            # default role
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
        # Basic email format validation: must contain '@' and at least one '.' after it.
        if "@" not in email_n or "." not in email_n.split("@", 1)[1]:
            raise ValueError("Email must be in a valid format (example: name@company.com)")
        # Password rule: at least 6 chars AND must include at least 1 symbol.
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters")
        if not any((not ch.isalnum()) for ch in password):
            raise ValueError("Password must include at least 1 symbol")


        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt(rounds=12)
        password_hash = bcrypt.hashpw(password_bytes, salt).decode("utf-8")
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

            # If conflict occurred, rowcount might be 0; detect by checking existence.
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

            # psycopg2 can return either tuples or dict-like rows depending on cursor configuration.
            stored_hash = row.get("password_hash") if isinstance(row, dict) else row["password_hash"]
            stored_role = row.get("role") if isinstance(row, dict) else row["role"]

            if stored_role != role_n:
                return False

            ok = bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
            return bool(ok)
        finally:
            conn.close()

    def user_exists(self, email: str, role: str | None = None) -> bool:
        """Return True if a user exists for this email.

        If `role` is provided, it must match the stored role as well.
        """
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

