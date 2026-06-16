"""
============================================================
JTCA - Login & Role Selection Dialog
Select between Admin and Trade Analyst roles
Supports Email/Password verification and Registration
============================================================
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

class RoleCard(QFrame):
    """Clickable, visual card representing a user role."""
    clicked = Signal(str)

    def __init__(self, role_id: str, icon: str, title: str, description: str, theme_color: str, parent=None, theme: str = "dark"):
        super().__init__(parent)
        self.role_id = role_id
        self.theme_color = theme_color
        self.theme = theme
        self.selected = False
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumSize(220, 160)
        self.setObjectName("role_card")

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)

        self.icon_lbl = QLabel(icon)
        self.icon_lbl.setStyleSheet("font-size: 36px;")
        self.icon_lbl.setAlignment(Qt.AlignCenter)

        self.title_lbl = QLabel(title)
        self.title_lbl.setAlignment(Qt.AlignCenter)

        self.desc_lbl = QLabel(description)
        self.desc_lbl.setAlignment(Qt.AlignCenter)
        self.desc_lbl.setWordWrap(True)

        layout.addWidget(self.icon_lbl)
        layout.addWidget(self.title_lbl)
        layout.addWidget(self.desc_lbl)

        self._apply_theme_style()

    def _apply_theme_style(self):
        if self.theme == "light":
            bg_color = "#EEF2F8"
            border_color = "#D0D9E8"
            hover_bg = "#E1E8F2"
            text_color = "#0D1B2A"
            desc_color = "#4A5568"
        else: # dark
            bg_color = "#0D1F3C"
            border_color = "#1565C0"
            hover_bg = "#1A3A5C"
            text_color = "#FFFFFF"
            desc_color = "#90CAF9"

        if self.selected:
            border_style = f"3px solid {self.theme_color}"
            current_bg = hover_bg
        else:
            border_style = f"2px solid {border_color}"
            current_bg = bg_color

        self.setStyleSheet(f"""
            QFrame#role_card {{
                background-color: {current_bg};
                border: {border_style};
                border-radius: 12px;
                padding: {15 if self.selected else 16}px;
            }}
            QFrame#role_card:hover {{
                border-color: {self.theme_color};
                background-color: {hover_bg};
            }}
        """)

        self.title_lbl.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {text_color};")
        self.desc_lbl.setStyleSheet(f"font-size: 11px; color: {desc_color};")

    def set_selected(self, selected: bool):
        self.selected = selected
        self._apply_theme_style()

    def mousePressEvent(self, event):
        self.clicked.emit(self.role_id)
        super().mousePressEvent(event)


class LoginDialog(QDialog):
    """Beautiful custom role selection & login modal dialog."""

    def __init__(self, parent=None, theme: str = "dark"):
        super().__init__(parent)
        self.setWindowTitle("Sign In — JTCA Compliance Assistant")
        self.setMinimumSize(560, 560)
        self.setModal(True)
        self.selected_role = None

        # Determine theme from parent or default
        self.theme = theme
        if parent and hasattr(parent, "_current_theme"):
            self.theme = parent._current_theme

        self._apply_dialog_style()
        self._setup_ui()

    def _apply_dialog_style(self):
        if self.theme == "light":
            self.setStyleSheet("""
                QWidget {
                    background-color: transparent;
                    color: #0D1B2A;
                }
                QDialog {
                    background-color: #F7F9FC;
                }
                QLineEdit {
                    background-color: #FFFFFF;
                    border: 1px solid #D0D9E8;
                    border-radius: 6px;
                    padding: 10px 14px;
                    color: #0D1B2A;
                    font-size: 13px;
                }
                QLineEdit:focus {
                    border: 2px solid #2196F3;
                }
                #sign_in_btn {
                    background-color: #0A3D91;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: bold;
                }
                #sign_in_btn:hover {
                    background-color: #1565C0;
                }
                #sign_in_btn:pressed {
                    background-color: #002B66;
                }
                #sign_in_btn:disabled {
                    background-color: #EEF2F8;
                    color: #8A9BB0;
                    border: 1px solid #D0D9E8;
                }
            """)
        else: # dark
            self.setStyleSheet("""
                QWidget {
                    background-color: transparent;
                    color: #E2E8F0;
                }
                QDialog {
                    background-color: #0A1628;
                }
                QLineEdit {
                    background-color: #0D2147;
                    border: 1px solid #1565C0;
                    border-radius: 6px;
                    padding: 10px 14px;
                    color: #E2E8F0;
                    font-size: 13px;
                }
                QLineEdit:focus {
                    border: 2px solid #42A5F5;
                }
                #sign_in_btn {
                    background-color: #0057A8;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: bold;
                }
                #sign_in_btn:hover {
                    background-color: #1976D2;
                }
                #sign_in_btn:pressed {
                    background-color: #003D7A;
                }
                #sign_in_btn:disabled {
                    background-color: #102A45;
                    color: #4A6FA5;
                    border: 1px solid #1565C0;
                }
            """)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(36, 24, 36, 24)

        # ── Header ──────────────────────────────────────
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        header_layout.setAlignment(Qt.AlignCenter)

        jabil_lbl = QLabel("JABIL")
        jabil_lbl.setAlignment(Qt.AlignCenter)

        subtitle_lbl = QLabel("TradeAI Compliance Assistant")
        subtitle_lbl.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(jabil_lbl)
        header_layout.addWidget(subtitle_lbl)
        layout.addLayout(header_layout)

        # Prompt text
        prompt_lbl = QLabel("SELECT YOUR SYSTEM ROLE")
        prompt_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(prompt_lbl)

        # ── Cards Row ───────────────────────────────────
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        self.admin_card = RoleCard(
            role_id="Admin",
            icon="🛡️",
            title="Administrator",
            description="Manage knowledge base, configure crawler, view reports and full logs.",
            theme_color="#42A5F5",
            theme=self.theme
        )
        self.analyst_card = RoleCard(
            role_id="Trade Analyst",
            icon="📋",
            title="Trade Analyst",
            description="Upload incoming supplier invoices, review HS codes, and approve/reject shipments.",
            theme_color="#059669",
            theme=self.theme
        )

        cards_layout.addWidget(self.admin_card)
        cards_layout.addWidget(self.analyst_card)
        layout.addLayout(cards_layout)

        # Connect signals
        self.admin_card.clicked.connect(self._select_role)
        self.analyst_card.clicked.connect(self._select_role)

        # ── Email Input ──────────────────────────────────
        email_lbl = QLabel("EMAIL / USERNAME")
        email_lbl.setObjectName("email_lbl")
        layout.addWidget(email_lbl)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email (e.g. admin@jabil.com)")
        self.email_input.textChanged.connect(self._validate)
        layout.addWidget(self.email_input)

        # ── Password Input ───────────────────────────────
        password_lbl = QLabel("PASSWORD")
        password_lbl.setObjectName("password_lbl")
        layout.addWidget(password_lbl)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.textChanged.connect(self._validate)
        layout.addWidget(self.password_input)

        # ── Register Link ────────────────────────────────
        register_row = QHBoxLayout()
        register_row.setSpacing(4)
        register_row.setAlignment(Qt.AlignLeft)

        no_account_lbl = QLabel("Don't have an account?")
        no_account_lbl.setStyleSheet("font-size: 11px;")
        
        self.register_btn = QPushButton("Register here")
        self.register_btn.setCursor(Qt.PointingHandCursor)
        self.register_btn.clicked.connect(self._on_register_clicked)
        
        register_row.addWidget(no_account_lbl)
        register_row.addWidget(self.register_btn)
        layout.addLayout(register_row)

        layout.addSpacing(4)

        # ── Sign In / Close Buttons ────────────────────
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.close_btn = QPushButton("Exit")
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.reject)

        self.sign_in_btn = QPushButton("Sign In")
        self.sign_in_btn.setObjectName("sign_in_btn")
        self.sign_in_btn.setCursor(Qt.PointingHandCursor)
        self.sign_in_btn.setEnabled(False)
        self.sign_in_btn.clicked.connect(self._on_sign_in)

        # Set specific text/button styles based on the theme
        if self.theme == "light":
            jabil_lbl.setStyleSheet("color: #0A3D91; font-size: 26px; font-weight: 800; letter-spacing: 4px;")
            subtitle_lbl.setStyleSheet("color: #1565C0; font-size: 13px; font-weight: 600; letter-spacing: 0.5px;")
            prompt_lbl.setStyleSheet("color: #4A5568; font-size: 10px; font-weight: 700; letter-spacing: 1.5px;")
            email_lbl.setStyleSheet("color: #4A5568; font-size: 10px; font-weight: 700; letter-spacing: 1.5px;")
            password_lbl.setStyleSheet("color: #4A5568; font-size: 10px; font-weight: 700; letter-spacing: 1.5px;")
            no_account_lbl.setStyleSheet("color: #4A5568; font-size: 11px;")
            self.register_btn.setStyleSheet("""
                QPushButton {
                    background: transparent; border: none; color: #0A3D91;
                    font-size: 11px; font-weight: bold; text-decoration: underline; padding: 0;
                }
                QPushButton:hover { color: #1565C0; }
            """)
            self.close_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #4A5568;
                    border: 1px solid #D0D9E8;
                    border-radius: 8px;
                    padding: 11px 20px;
                    font-size: 13px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #FEE2E2;
                    color: #EF4444;
                    border-color: #EF4444;
                }
            """)
        else: # dark
            jabil_lbl.setStyleSheet("color: #FFFFFF; font-size: 26px; font-weight: 800; letter-spacing: 4px;")
            subtitle_lbl.setStyleSheet("color: #42A5F5; font-size: 13px; font-weight: 600; letter-spacing: 0.5px;")
            prompt_lbl.setStyleSheet("color: #90CAF9; font-size: 10px; font-weight: 700; letter-spacing: 1.5px;")
            email_lbl.setStyleSheet("color: #90CAF9; font-size: 10px; font-weight: 700; letter-spacing: 1.5px;")
            password_lbl.setStyleSheet("color: #90CAF9; font-size: 10px; font-weight: 700; letter-spacing: 1.5px;")
            no_account_lbl.setStyleSheet("color: #90CAF9; font-size: 11px;")
            self.register_btn.setStyleSheet("""
                QPushButton {
                    background: transparent; border: none; color: #42A5F5;
                    font-size: 11px; font-weight: bold; text-decoration: underline; padding: 0;
                }
                QPushButton:hover { color: #64B5F6; }
            """)
            self.close_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #B0C4DE;
                    border: 1px solid #1E3A5F;
                    border-radius: 8px;
                    padding: 11px 20px;
                    font-size: 13px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #450A0A;
                    color: #F87171;
                    border-color: #EF4444;
                }
            """)

        btn_layout.addWidget(self.close_btn)
        btn_layout.addWidget(self.sign_in_btn, stretch=1)
        layout.addLayout(btn_layout)

    def _select_role(self, role_id: str):
        self.selected_role = role_id
        self.admin_card.set_selected(role_id == "Admin")
        self.analyst_card.set_selected(role_id == "Trade Analyst")
        self._validate()

    def _on_register_clicked(self):
        if not self.selected_role:
            QMessageBox.warning(self, "Register", "Please select a system role card first.")
            return

        from ui.register_dialog import RegisterDialog
        dialog = RegisterDialog(selected_role=self.selected_role, parent=self, theme=self.theme)
        if dialog.exec() == QDialog.Accepted:
            self.email_input.setText(dialog.email_input.text().strip())

    def _validate(self):
        email = self.email_input.text().strip()
        password = self.password_input.text()
        has_role = self.selected_role is not None
        has_email = len(email) > 0
        has_password = len(password) >= 6

        self.sign_in_btn.setEnabled(has_role and has_email and has_password)

    def _on_sign_in(self):
        email = self.email_input.text().strip()
        password = self.password_input.text()

        if not self.selected_role:
            QMessageBox.warning(self, "Sign In", "Please select a system role.")
            return
        if not email:
            QMessageBox.warning(self, "Sign In", "Please enter your email.")
            return
        if not password:
            QMessageBox.warning(self, "Sign In", "Please enter your password.")
            return

        try:
            from services.auth import AuthService
            auth_service = AuthService()
            ok = auth_service.login(email, password, self.selected_role)

            if ok:
                display_name = auth_service.get_user_display_name(email)
                from services.session import SessionManager
                SessionManager().login(display_name, self.selected_role, email)
                self.accept()
            else:
                QMessageBox.warning(
                    self, "Authentication Failed",
                    "Invalid email, password, or incorrect system role selected.\n\n"
                    "Please check your credentials or register a new account."
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Authentication service error:\n{e}")
