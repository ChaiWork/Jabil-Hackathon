"""JTCA - Register Dialog

Email + password registration for Admin / Trade Analyst.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt

from services.auth import AuthService


class RegisterDialog(QDialog):
    def __init__(self, selected_role: str = "Trade Analyst", parent=None, theme: str = "dark"):
        super().__init__(parent)
        self.setWindowTitle("Register — JTCA")
        self.setMinimumSize(520, 420)
        self.setModal(True)
        self.selected_role = selected_role
        self.theme = theme

        self._apply_style()
        self._setup_ui()

    def _apply_style(self):
        if self.theme == "light":
            self.setStyleSheet("""
                QDialog { background-color: #F7F9FC; }
                QLabel { color: #0D1B2A; }
                QLineEdit {
                    background-color: #FFFFFF;
                    border: 1px solid #D0D9E8;
                    border-radius: 6px;
                    padding: 10px 14px;
                    color: #0D1B2A;
                }
                QLineEdit:focus { border: 2px solid #2196F3; }
                QPushButton {
                    border-radius: 8px;
                    padding: 10px 18px;
                    font-weight: 700;
                }
                #btn_primary {
                    background-color: #0A3D91;
                    color: #FFFFFF;
                    border: none;
                }
                #btn_primary:hover { background-color: #1565C0; }
                #btn_secondary {
                    background-color: transparent;
                    color: #4A5568;
                    border: 1px solid #D0D9E8;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog { background-color: #0A1628; }
                QLabel { color: #E2E8F0; }
                QLineEdit {
                    background-color: #0D2147;
                    border: 1px solid #1565C0;
                    border-radius: 6px;
                    padding: 10px 14px;
                    color: #E2E8F0;
                }
                QLineEdit:focus { border: 2px solid #42A5F5; }
                QPushButton {
                    border-radius: 8px;
                    padding: 10px 18px;
                    font-weight: 700;
                }
                #btn_primary {
                    background-color: #0057A8;
                    color: #FFFFFF;
                    border: none;
                }
                #btn_primary:hover { background-color: #1976D2; }
                #btn_secondary {
                    background-color: transparent;
                    color: #B0C4DE;
                    border: 1px solid #1E3A5F;
                }
            """)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        title = QLabel("Create your JTCA account")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: 800;")
        layout.addWidget(title)

        role_lbl = QLabel(f"Role: {self.selected_role}")
        role_lbl.setAlignment(Qt.AlignCenter)
        role_lbl.setStyleSheet("color: #90CAF9; font-size: 12px; font-weight: 700;")
        layout.addWidget(role_lbl)

        # Email
        layout.addWidget(QLabel("Email"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("name@company.com")
        layout.addWidget(self.email_input)

        # Password
        layout.addWidget(QLabel("Password"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Minimum 6 characters")
        layout.addWidget(self.password_input)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("btn_secondary")
        self.cancel_btn.clicked.connect(self.reject)

        self.register_btn = QPushButton("Register")
        self.register_btn.setObjectName("btn_primary")
        self.register_btn.clicked.connect(self._on_register)

        btn_row.addWidget(self.cancel_btn)
        btn_row.addWidget(self.register_btn)
        layout.addLayout(btn_row)

    def _on_register(self):
        email = self.email_input.text().strip()
        password = self.password_input.text()

        if not email:
            QMessageBox.warning(self, "Register", "Email is required.")
            return
        if not password or len(password) < 6:
            QMessageBox.warning(self, "Register", "Password must be at least 6 characters.")
            return

        try:
            ok = AuthService().register(email=email, password=password, role=self.selected_role)
        except Exception as e:
            QMessageBox.critical(self, "Register", f"Registration failed:\n{e}")
            return

        if not ok:
            QMessageBox.information(self, "Register", "Account already exists (or cannot create).")
            # Still accept so user can log in
            self.accept()
            return

        QMessageBox.information(self, "Register", "Account created successfully. Please sign in.")
        self.accept()

