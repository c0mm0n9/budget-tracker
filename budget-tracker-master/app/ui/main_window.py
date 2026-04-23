from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.ui.controllers.app_controller import AppController
from app.ui.design.tokens import (
    APP_STYLESHEET,
    BORDER,
    SIDEBAR_ACTIVE_BG,
    SIDEBAR_ACTIVE_FG,
    SIDEBAR_BG,
    SIDEBAR_HOVER_BG,
    TEXT,
)
from app.ui.pages.budgets_page import BudgetsPage
from app.ui.pages.dashboard_page import DashboardPage
from app.ui.pages.rules_page import RulesPage
from app.ui.pages.statistics_page import StatisticsPage
from app.ui.pages.transactions_page import TransactionsPage


class _NavButton(QPushButton):
    def __init__(self, label: str, parent: QWidget | None = None) -> None:
        super().__init__(label, parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            f"""
            QPushButton {{
                text-align: left;
                padding: 12px 14px;
                border: 1px solid transparent;
                border-radius: 10px;
                color: {TEXT};
                background: transparent;
                font-weight: 600;
            }}
            QPushButton:checked {{
                background: {SIDEBAR_ACTIVE_BG};
                color: {SIDEBAR_ACTIVE_FG};
            }}
            QPushButton:hover {{
                background: {SIDEBAR_HOVER_BG};
            }}
            QPushButton:checked:hover {{
                background: {SIDEBAR_ACTIVE_BG};
                color: {SIDEBAR_ACTIVE_FG};
            }}
            QPushButton:focus {{
                border: 1px solid #BFDBFE;
            }}
            """
        )


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("BudgetTracker")
        self.resize(1280, 900)
        self.setStyleSheet(APP_STYLESHEET)

        self._controller = AppController()

        # Root layout
        root = QHBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setStyleSheet(
            f"""
            QFrame#Sidebar {{
                background: {SIDEBAR_BG};
                border-right: 1px solid {BORDER};
            }}
            """
        )
        sidebar.setFixedWidth(240)

        sb_layout = QVBoxLayout()
        sb_layout.setContentsMargins(16, 16, 16, 16)
        sb_layout.setSpacing(8)

        brand = QLabel("BudgetTracker")
        brand.setStyleSheet("font-weight: 800; font-size: 18px; padding: 8px 8px;")
        sb_layout.addWidget(brand, alignment=Qt.AlignmentFlag.AlignLeft)

        nav_container = QWidget()
        nav_layout = QVBoxLayout()
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(8)
        nav_container.setLayout(nav_layout)
        sb_layout.addWidget(nav_container)

        self._nav_buttons: dict[str, _NavButton] = {}
        self._page_order = ["Dashboard", "Transactions", "Budgets", "Rules", "Statistics"]
        self._stack = QStackedWidget()

        # Pages
        self._pages: dict[str, QWidget] = {
            "Dashboard": DashboardPage(self._controller),
            "Transactions": TransactionsPage(self._controller),
            "Budgets": BudgetsPage(self._controller),
            "Rules": RulesPage(self._controller),
            "Statistics": StatisticsPage(
                self._controller,
                on_go_to_transactions=lambda: self._set_current_page(
                    self._page_order.index("Transactions")
                ),
            ),
        }
        for key in self._page_order:
            self._stack.addWidget(self._pages[key])

        # Create navigation buttons in the same order as the stack
        for i, key in enumerate(self._page_order):
            btn = _NavButton(key)
            btn.clicked.connect(lambda _checked=False, idx=i: self._set_current_page(idx))
            nav_layout.addWidget(btn)
            self._nav_buttons[key] = btn

        nav_layout.addStretch(1)
        sidebar.setLayout(sb_layout)

        root.addWidget(sidebar)
        root.addWidget(self._stack, 1)

        container = QWidget()
        container.setLayout(root)
        self.setCentralWidget(container)

        self._stack.currentChanged.connect(self._sync_nav_selection)

        # Default selection
        self._set_current_page(0)

    def _set_current_page(self, idx: int) -> None:
        self._stack.setCurrentIndex(idx)
        self._sync_nav_selection(idx)
        page = self._stack.currentWidget()
        if hasattr(page, "refresh_view"):
            page.refresh_view()

    def _sync_nav_selection(self, idx: int) -> None:
        for i, key in enumerate(self._page_order):
            self._nav_buttons[key].setChecked(i == idx)
