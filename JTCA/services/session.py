"""
============================================================
JTCA - Session Management Service
Tracks the currently logged-in user and their active role.
============================================================
"""

class SessionManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
            cls._instance._current_user = None
            cls._instance._current_role = None  # "Admin" or "Trade Analyst"
            cls._instance._current_email = None
        return cls._instance

    def login(self, username: str, role: str, email: str = ""):
        """Log in a user with a specific name and role and email."""
        self._current_user = username.strip() or "Anonymous"
        self._current_role = role
        self._current_email = email.strip()
        # Normalize role names
        if self._current_role not in ("Admin", "Trade Analyst"):
            self._current_role = "Trade Analyst"

    def logout(self):
        """Log out the current user and clear session."""
        self._current_user = None
        self._current_role = None
        self._current_email = None

    def is_admin(self) -> bool:
        """Check if current user is an Admin."""
        return self._current_role == "Admin"

    def is_trade_analyst(self) -> bool:
        """Check if current user is a Trade Analyst."""
        return self._current_role == "Trade Analyst"

    def get_role(self) -> str:
        """Get current user's role."""
        return self._current_role or "Guest"

    def get_username(self) -> str:
        """Get current user's name."""
        return self._current_user or "Guest"

    def get_email(self) -> str:
        """Get current user's email."""
        return self._current_email or ""
