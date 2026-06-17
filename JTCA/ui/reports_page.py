"""
============================================================
JTCA - Reports & Analytics Page
Statistics, charts summary, and audit log viewer
============================================================
"""

import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QGridLayout, QMessageBox, QFileDialog, QDialog,
    QFormLayout, QTextEdit, QLineEdit,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont

logger = logging.getLogger(__name__)


class AuditDetailDialog(QDialog):
    """
    Pop-up dialog showing full details of a selected audit trail log row.
    """

    def __init__(self, log_entry: tuple, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔍 Audit Trail Details")
        self.setMinimumWidth(540)
        self.setMinimumHeight(440)
        self.setModal(True)
        self.setObjectName("dialog")
        
        # Unpack tuple: (timestamp, shipment_id, action, ai_recommendation, human_decision, reviewer_name, notes)
        timestamp, shipment_id, action, ai_rec, human_dec, reviewer, notes = log_entry
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 20, 24, 20)
        
        # Header card
        header = QFrame()
        header.setObjectName("header_frame")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 12)
        
        title = QLabel("📋  AUDIT LOG ENTRY DETAILS")
        title.setStyleSheet("font-size: 14px; font-weight: 800; letter-spacing: 1px; color: #2196F3;")
        
        subtitle = QLabel(f"Shipment: {shipment_id}")
        subtitle.setStyleSheet("font-size: 11px;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addWidget(header)
        
        # Form details
        form_frame = QFrame()
        form_frame.setObjectName("card")
        form = QFormLayout(form_frame)
        form.setSpacing(12)
        form.setContentsMargins(16, 12, 16, 12)
        
        def add_field(label: str, text: str, is_text_area: bool = False, color: str = None):
            lbl = QLabel(label.upper())
            lbl.setStyleSheet("font-weight: bold; font-size: 10px; color: #718096; letter-spacing: 0.5px;")
            
            if is_text_area:
                val = QTextEdit()
                val.setPlainText(text or "—")
                val.setReadOnly(True)
                val.setMaximumHeight(80)
                val.setStyleSheet("font-size: 12px; padding: 6px;")
            else:
                val = QLineEdit()
                val.setText(text or "—")
                val.setReadOnly(True)
                style = "font-size: 12px; padding: 6px;"
                if color:
                    style = f"font-size: 12px; font-weight: bold; color: {color}; padding: 6px;"
                val.setStyleSheet(style)
            form.addRow(lbl, val)

        action_colors = {
            "AI_PROCESSED": "#42A5F5",
            "HUMAN_APPROVED": "#10B981",
            "HUMAN_REJECTED_OVERRIDE": "#EF4444",
        }
        act_color = action_colors.get(action, "#FFFFFF")
        
        formatted_time = timestamp[:19].replace("T", " ")
        add_field("Time Stamp", formatted_time)
        add_field("Shipment ID", shipment_id)
        add_field("Action Taken", action, color=act_color)
        add_field("AI Recommendation", ai_rec)
        add_field("Human Decision", human_dec)
        add_field("Reviewer", reviewer)
        add_field("Reviewer Notes", notes, is_text_area=True)
        
        layout.addWidget(form_frame)
        
        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setObjectName("btn_secondary")
        close_btn.setMinimumHeight(38)
        close_btn.setMinimumWidth(110)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)


class ReportsPage(QWidget):
    """Analytics and audit log viewer."""

    def __init__(self):
        super().__init__()
        self._setup_ui()
        self.apply_permissions()
        self.refresh_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(28, 24, 28, 24)

        # Header
        header = QHBoxLayout()
        title = QLabel("📊  Reports & Analytics")
        title.setObjectName("page_title")
        title.setStyleSheet("font-size: 20px; font-weight: 800;")

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setObjectName("btn_secondary")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setMaximumWidth(110)
        refresh_btn.clicked.connect(self.refresh_data)

        self.delete_btn = QPushButton("🗑️ Delete Log")
        self.delete_btn.setObjectName("btn_secondary")
        self.delete_btn.setCursor(Qt.PointingHandCursor)
        self.delete_btn.setMaximumWidth(130)
        self.delete_btn.clicked.connect(self._delete_selected_log)

        export_btn = QPushButton("📊 Export Report")
        export_btn.setObjectName("btn_primary")
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.setMaximumWidth(140)
        export_btn.clicked.connect(self._export_report)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(refresh_btn)
        header.addWidget(self.delete_btn)
        header.addWidget(export_btn)
        layout.addLayout(header)

        # Stats grid
        stats_frame = QFrame()
        stats_frame.setObjectName("card")
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setSpacing(20)
        stats_layout.setContentsMargins(20, 16, 20, 16)

        stats_title = QLabel("SUMMARY STATISTICS")
        stats_title.setObjectName("section_title")
        stats_title.setStyleSheet(
            "font-size: 11px; font-weight: 700; letter-spacing: 2px;"
        )
        stats_layout.addWidget(stats_title, 0, 0, 1, 4)

        self._stat_labels = {}
        stat_defs = [
            ("total", "Total Shipments", "📦", "#42A5F5"),
            ("approved", "Approved", "✅", "#10B981"),
            ("pending", "Pending Review", "⏳", "#F59E0B"),
            ("rejected", "Rejected", "❌", "#EF4444"),
            ("avg_confidence", "Avg Confidence", "🎯", "#A78BFA"),
            ("total_duties", "Total Duties", "💵", "#FB7185"),
        ]

        for col_idx, (key, label, icon, color) in enumerate(stat_defs):
            col_frame = QFrame()
            col_layout = QVBoxLayout(col_frame)
            col_layout.setSpacing(4)
            col_layout.setContentsMargins(8, 8, 8, 8)

            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet(f"font-size: 20px; color: {color};")
            icon_lbl.setAlignment(Qt.AlignCenter)

            value_lbl = QLabel("—")
            value_lbl.setStyleSheet(
                f"color: {color}; font-size: 22px; font-weight: 800;"
            )
            value_lbl.setAlignment(Qt.AlignCenter)
            self._stat_labels[key] = value_lbl

            name_lbl = QLabel(label)
            name_lbl.setStyleSheet("font-size: 10px; font-weight: 600;")
            name_lbl.setAlignment(Qt.AlignCenter)

            col_layout.addWidget(icon_lbl)
            col_layout.addWidget(value_lbl)
            col_layout.addWidget(name_lbl)
            stats_layout.addWidget(col_frame, 1, col_idx)

        layout.addWidget(stats_frame)

        # Audit log
        audit_header = QHBoxLayout()
        audit_lbl = QLabel("AUDIT TRAIL LOG")
        audit_lbl.setObjectName("section_title")
        audit_lbl.setStyleSheet(
            "font-size: 11px; font-weight: 700; letter-spacing: 2px;"
        )
        audit_header.addWidget(audit_lbl)
        audit_header.addStretch()
        layout.addLayout(audit_header)

        self.audit_table = QTableWidget()
        self.audit_table.setColumnCount(7)
        self.audit_table.setHorizontalHeaderLabels([
            "Time", "Shipment ID", "Action", "AI Recommendation",
            "Human Decision", "Reviewer", "Notes"
        ])
        self.audit_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.audit_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.audit_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.audit_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.audit_table.setSelectionMode(QTableWidget.SingleSelection)
        self.audit_table.verticalHeader().setVisible(False)
        self.audit_table.setShowGrid(False)
        self.audit_table.doubleClicked.connect(self._on_row_double_clicked)
        layout.addWidget(self.audit_table)
        
        hint = QLabel("💡 Double-click any audit log row to view full details")
        hint.setStyleSheet("font-size: 11px; font-style: italic; color: #718096;")
        layout.addWidget(hint)

    def refresh_data(self):
        try:
            from database.db import get_dashboard_stats, get_recent_audit_log

            stats = get_dashboard_stats()
            self._stat_labels["total"].setText(str(stats.get("total", 0)))
            self._stat_labels["approved"].setText(str(stats.get("approved", 0)))
            self._stat_labels["pending"].setText(str(stats.get("pending", 0)))
            self._stat_labels["rejected"].setText(str(stats.get("rejected", 0)))
            self._stat_labels["avg_confidence"].setText(
                f"{stats.get('avg_confidence', 0):.1f}%"
            )
            self._stat_labels["total_duties"].setText(
                f"${stats.get('total_duties', 0):,.2f}"
            )

            # Load audit log using PostgreSQL-safe API
            rows = get_recent_audit_log(limit=200)
            self._audit_rows = rows

            self.audit_table.setRowCount(0)
            for row_idx, row in enumerate(rows):
                self.audit_table.insertRow(row_idx)
                action_colors = {
                    "AI_PROCESSED": "#42A5F5",
                    "HUMAN_APPROVED": "#10B981",
                    "HUMAN_REJECTED_OVERRIDE": "#EF4444",
                }
                display_fields = row[1:]
                for col_idx, value in enumerate(display_fields):
                    val_str = str(value or "")
                    if col_idx == 0:
                        val_str = val_str[:19].replace("T", " ")
                    if col_idx == 1:
                        val_str = val_str[-14:]
                    item = QTableWidgetItem(val_str)
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                    if col_idx == 2:
                        color = action_colors.get(val_str, "#90CAF9")
                        item.setForeground(QColor(color))
                        item.setFont(QFont("Segoe UI", 10, QFont.Bold))
                    self.audit_table.setItem(row_idx, col_idx, item)
                self.audit_table.setRowHeight(row_idx, 40)

        except Exception as e:
            logger.error(f"Reports refresh error: {e}")

    def apply_permissions(self):
        """Enforce role-based restrictions on reports page."""
        from services.session import SessionManager
        session = SessionManager()
        is_admin = session.is_admin()
        self.delete_btn.setVisible(is_admin)

    def _delete_selected_log(self):
        row = self.audit_table.currentRow()
        if row < 0 or not hasattr(self, "_audit_rows") or row >= len(self._audit_rows):
            QMessageBox.warning(self, "Delete Log", "Please select an audit log row from the table first.")
            return

        log_entry = self._audit_rows[row]
        audit_id = log_entry[0]
        shipment_id = log_entry[2]
        timestamp = log_entry[1][:19].replace("T", " ")

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the audit log for shipment {shipment_id} at {timestamp}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                from database.db import delete_audit_log
                success = delete_audit_log(audit_id)
                if success:
                    QMessageBox.information(self, "Deleted", "Audit log entry successfully deleted.")
                    self.refresh_data()
                else:
                    QMessageBox.critical(self, "Error", "Failed to delete the audit log entry from database.")
            except Exception as e:
                logger.error(f"Error deleting audit log: {e}")
                QMessageBox.critical(self, "Error", f"An error occurred while deleting:\n{e}")

    def _on_row_double_clicked(self, index):
        row = index.row()
        if hasattr(self, "_audit_rows") and row < len(self._audit_rows):
            # Pass the 7-tuple to AuditDetailDialog (excluding the ID)
            dialog = AuditDetailDialog(self._audit_rows[row][1:], self)
            dialog.exec()

    def _export_report(self):
        try:
            from database.db import get_all_shipments
            from services.export_excel import export_to_excel
            shipments = get_all_shipments()
            if not shipments:
                QMessageBox.information(self, "No Data", "No shipments to export.")
                return
            path, _ = QFileDialog.getSaveFileName(
                self, "Export Report", "JTAA_Report.xlsx", "Excel Files (*.xlsx)"
            )
            if path:
                result = export_to_excel(shipments, path)
                QMessageBox.information(self, "Done", f"✅ Report exported:\n{result}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
