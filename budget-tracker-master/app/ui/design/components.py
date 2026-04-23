"""
Reusable UI components for consistent layout and UX.

This is intentionally small and strict so pages/dialogs stay uniform.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.ui.design.tokens import (
    APP_STYLESHEET,
    BORDER,
    CONTROL_HEIGHT,
    DANGER_BG,
    DANGER_FG,
    ERROR_BG,
    ERROR_FG,
    MUTED,
    PRIMARY_BG,
    PRIMARY_FG,
    RADIUS,
    SURFACE,
    TEXT,
)


class Card(QFrame):
    """
    Standard "surface" container with border + rounded corners.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        padding: int = 16,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout = QVBoxLayout()
        layout.setContentsMargins(padding, padding, padding, padding)
        layout.setSpacing(12)
        self.setLayout(layout)

    @property
    def content_layout(self) -> QVBoxLayout:
        # Card always has a QVBoxLayout as its layout.
        return self.layout()  # type: ignore[return-value]


class SectionHeader(QWidget):
    def __init__(
        self,
        title: str,
        *,
        subtitle: str | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"font-weight: 700; font-size: 16px; color: {TEXT};")
        layout.addWidget(title_lbl, alignment=Qt.AlignmentFlag.AlignLeft)

        if subtitle:
            sub_lbl = QLabel(subtitle)
            sub_lbl.setProperty("muted", "true")
            sub_lbl.setStyleSheet("font-size: 12.5px;")
            layout.addWidget(sub_lbl, alignment=Qt.AlignmentFlag.AlignLeft)

        self.setLayout(layout)


class PrimaryButton(QPushButton):
    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            f"""
            QPushButton {{
                height: {CONTROL_HEIGHT}px;
                background: {PRIMARY_BG};
                color: {PRIMARY_FG};
                border: 1px solid {PRIMARY_BG};
                border-radius: {RADIUS}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: #0B1220;
            }}
            QPushButton:pressed {{
                background: #070D18;
            }}
            """
        )


class DangerButton(QPushButton):
    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            f"""
            QPushButton {{
                height: {CONTROL_HEIGHT}px;
                background: {DANGER_BG};
                color: {DANGER_FG};
                border: 1px solid {DANGER_BG};
                border-radius: {RADIUS}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: #B91C1C;
                border: 1px solid #B91C1C;
            }}
            """
        )


class EmptyState(QWidget):
    """
    Standard empty state with optional primary action.
    """

    def __init__(
        self,
        text: str,
        *,
        action_text: str | None = None,
        action_callback=None,
        align_top: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        if align_top:
            layout.setAlignment(
                Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
            )
        else:
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        msg = QLabel(text)
        msg.setProperty("muted", "true")
        msg.setStyleSheet("font-size: 13.5px;")
        if align_top:
            msg.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        else:
            msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(msg)

        if action_text and action_callback:
            btn = PrimaryButton(action_text, self)
            btn.clicked.connect(action_callback)
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)


class ErrorBanner(QLabel):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWordWrap(True)
        self.setVisible(False)
        self.setStyleSheet(
            f"""
            QLabel {{
                background: {ERROR_BG};
                color: {ERROR_FG};
                border: 1px solid {ERROR_FG};
                border-radius: 12px;
                padding: 10px 12px;
                font-size: 12.5px;
            }}
            """
        )

    def show_error(self, text: str) -> None:
        self.setText(text)
        self.setVisible(True)

    def clear(self) -> None:
        self.setText("")
        self.setVisible(False)


class StandardDialog(QDialog):
    """
    Shared modal chrome:
    - Title header
    - Content area
    - Optional error banner
    - Consistent Save/Cancel button bar
    """

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setObjectName("StandardDialog")
        self.resize(520, 420)

        root = QVBoxLayout()
        root.setContentsMargins(20, 20, 20, 16)
        root.setSpacing(14)

        header = QLabel(title)
        header.setStyleSheet(f"font-weight: 800; font-size: 18px; color: {TEXT}; padding-bottom: 2px;")
        root.addWidget(header, alignment=Qt.AlignmentFlag.AlignLeft)

        self._error_banner = ErrorBanner(self)
        root.addWidget(self._error_banner)

        self._content_container = QWidget(self)
        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(12)
        self._content_container.setLayout(self._content_layout)
        root.addWidget(self._content_container)

        btn_bar = QDialogButtonBox(self)
        self._save_btn = btn_bar.addButton(
            "Save", QDialogButtonBox.ButtonRole.AcceptRole
        )
        self._cancel_btn = btn_bar.addButton(
            "Cancel", QDialogButtonBox.ButtonRole.RejectRole
        )
        self._save_btn.setProperty("role", "primary")
        self._cancel_btn.setProperty("role", "secondary")
        self._save_btn.style().unpolish(self._save_btn)
        self._save_btn.style().polish(self._save_btn)
        self._cancel_btn.style().unpolish(self._cancel_btn)
        self._cancel_btn.style().polish(self._cancel_btn)
        self._cancel_btn.clicked.connect(self.reject)
        root.addWidget(btn_bar)

        self.setLayout(root)

        # Apply component-related stylesheet early.
        self.setStyleSheet(APP_STYLESHEET)

    @property
    def content_layout(self) -> QVBoxLayout:
        return self._content_layout

    @property
    def save_button(self) -> QPushButton:
        return self._save_btn  # type: ignore[return-value]

    def set_save_text(self, text: str) -> None:
        self._save_btn.setText(text)

    def show_error(self, text: str) -> None:
        self._error_banner.show_error(text)

    def clear_error(self) -> None:
        self._error_banner.clear()


def style_message_box(msg: QMessageBox) -> None:
    """
    Apply consistent popup styling to confirmation dialogs.
    """
    msg.setStyleSheet(APP_STYLESHEET)


