"""
UI design tokens (light theme).

These tokens are used by UI components to ensure consistent spacing, sizing,
and a shared visual language across all pages.
"""

from __future__ import annotations

from typing import Final

SPACING: Final[int] = 8

FONT_FAMILY: Final[str] = "Segoe UI"

# Sizing
CONTROL_HEIGHT: Final[int] = 36
RADIUS: Final[int] = 12
CARD_RADIUS: Final[int] = 16

# Colors (light)
BG: Final[str] = "#F6F7FB"
SURFACE: Final[str] = "#FFFFFF"
SURFACE_ALT: Final[str] = "#F8FAFC"
BORDER: Final[str] = "#E5E7EF"
TEXT: Final[str] = "#0F172A"
MUTED: Final[str] = "#6B7280"
FOCUS_RING: Final[str] = "#93C5FD"

SIDEBAR_BG: Final[str] = "#FFFFFF"
SIDEBAR_HOVER_BG: Final[str] = "#F3F4F6"
SIDEBAR_ACTIVE_BG: Final[str] = "#111827"
SIDEBAR_ACTIVE_FG: Final[str] = "#FFFFFF"

PRIMARY_BG: Final[str] = "#111827"
PRIMARY_FG: Final[str] = "#FFFFFF"
PRIMARY_HOVER_BG: Final[str] = "#0B1220"

DANGER_BG: Final[str] = "#DC2626"
DANGER_FG: Final[str] = "#FFFFFF"
DANGER_HOVER_BG: Final[str] = "#B91C1C"

SUCCESS_BG: Final[str] = "#16A34A"
WARNING_BG: Final[str] = "#F59E0B"

ERROR_FG: Final[str] = "#991B1B"
ERROR_BG: Final[str] = "#FEF2F2"

APP_STYLESHEET: Final[str] = f"""
    QWidget {{
        font-family: "{FONT_FAMILY}";
        color: {TEXT};
    }}

    QMainWindow {{
        background: {BG};
    }}

    QDialog {{
        background: {SURFACE};
    }}

    QFrame#Card {{
        background: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: {CARD_RADIUS}px;
    }}

    QLabel[muted="true"] {{
        color: {MUTED};
    }}

    QLineEdit, QPlainTextEdit, QComboBox, QDateEdit {{
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 7px 10px;
        background: {SURFACE};
        color: {TEXT};
        selection-background-color: {PRIMARY_BG};
        selection-color: {PRIMARY_FG};
    }}

    QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QDateEdit:focus {{
        border: 1px solid {FOCUS_RING};
        outline: none;
    }}

    QComboBox {{
        min-height: {CONTROL_HEIGHT}px;
        padding-right: 28px;
    }}
    QComboBox::drop-down {{
        width: 24px;
        border: none;
        background: transparent;
        subcontrol-origin: padding;
        subcontrol-position: top right;
        border-top-right-radius: 10px;
        border-bottom-right-radius: 10px;
    }}
    QComboBox QAbstractItemView {{
        background: {SURFACE};
        color: {TEXT};
        border: 1px solid {BORDER};
        selection-background-color: #E0E7FF;
        selection-color: {TEXT};
        outline: none;
        padding: 4px;
    }}
    QComboBox QAbstractItemView::item {{
        min-height: 28px;
        padding: 4px 8px;
    }}
    QComboBox QAbstractItemView::item:hover {{
        background: #EEF2FF;
        color: {TEXT};
    }}

    QCalendarWidget QWidget {{
        background: {SURFACE};
        color: {TEXT};
    }}
    QCalendarWidget QToolButton {{
        background: {SURFACE};
        color: {TEXT};
        border: 1px solid transparent;
        border-radius: 8px;
        padding: 4px 8px;
    }}
    QCalendarWidget QToolButton:hover {{
        background: #F3F4F6;
    }}
    QCalendarWidget QMenu {{
        background: {SURFACE};
        color: {TEXT};
        border: 1px solid {BORDER};
    }}
    QCalendarWidget QSpinBox {{
        background: {SURFACE};
        color: {TEXT};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 3px 6px;
    }}
    QCalendarWidget QAbstractItemView:enabled {{
        color: {TEXT};
        background: {SURFACE};
        selection-background-color: #E0E7FF;
        selection-color: {TEXT};
    }}

    QTableView, QTableWidget {{
        background: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 12px;
        gridline-color: {BORDER};
        selection-background-color: #EEF2FF;
        selection-color: {TEXT};
        alternate-background-color: {SURFACE_ALT};
    }}
    QTableCornerButton::section {{
        background: {SURFACE_ALT};
        border: none;
    }}
    QHeaderView::section {{
        background: {SURFACE_ALT};
        padding: 10px 8px;
        border: none;
        font-weight: 600;
        color: #374151;
    }}

    QPushButton {{
        height: {CONTROL_HEIGHT}px;
        padding: 0px 14px;
        border-radius: 12px;
        border: 1px solid {BORDER};
        background: {SURFACE};
        color: {TEXT};
        font-weight: 500;
    }}
    QPushButton:hover {{
        background: #F8FAFC;
        border: 1px solid #D7DCE8;
    }}
    QPushButton:pressed {{
        background: #EEF2F7;
    }}
    QPushButton:disabled {{
        color: #9CA3AF;
        background: #F3F4F6;
        border: 1px solid #E5E7EB;
    }}

    QPushButton[variant="neutral"] {{
        background: #FFFFFF;
        border: 1px solid #DDE2EC;
        color: #111827;
        font-weight: 600;
    }}
    QPushButton[variant="neutral"]:hover {{
        background: #F8FAFC;
    }}

    QPushButton[variant="danger"] {{
        background: #FEF2F2;
        border: 1px solid #FECACA;
        color: #B91C1C;
        font-weight: 600;
    }}
    QPushButton[variant="danger"]:hover {{
        background: #FEE2E2;
    }}

    QMessageBox {{
        background: {SURFACE};
    }}
    QMessageBox QLabel {{
        color: {TEXT};
    }}
    QMessageBox QPushButton {{
        min-width: 88px;
    }}

    QDialogButtonBox QPushButton {{
        min-width: 100px;
        height: {CONTROL_HEIGHT}px;
        border-radius: 12px;
    }}
    QDialogButtonBox QPushButton[role="primary"] {{
        background: {PRIMARY_BG};
        color: {PRIMARY_FG};
        border: 1px solid {PRIMARY_BG};
        font-weight: 700;
    }}
    QDialogButtonBox QPushButton[role="primary"]:hover {{
        background: {PRIMARY_HOVER_BG};
    }}
    QDialogButtonBox QPushButton[role="secondary"] {{
        background: #FFFFFF;
        color: #111827;
        border: 1px solid #DDE2EC;
        font-weight: 600;
    }}
"""

