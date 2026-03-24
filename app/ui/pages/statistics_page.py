from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from PyQt6.QtCharts import QChart, QChartView, QPieSeries
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from app.ui.controllers.app_controller import AppController
from app.ui.design.components import Card, EmptyState, SectionHeader
from app.ui.utils.formatters import format_currency


class StatisticsPage(QWidget):
    def __init__(
        self,
        controller: AppController | None = None,
        *,
        on_go_to_transactions: Callable[[], None] | None = None,
    ) -> None:
        super().__init__()
        self._controller = controller or AppController()
        self._on_go_to_transactions = on_go_to_transactions

        root = QVBoxLayout()
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)

        root.addWidget(
            SectionHeader(
                "Statistics",
                subtitle="Current month and recent trends",
            )
        )

        row = QWidget(self)
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(16)
        row.setLayout(row_layout)

        # --- Income by category ---
        income_card = Card(self)
        income_layout = income_card.content_layout
        income_layout.setContentsMargins(16, 16, 16, 16)
        income_layout.setSpacing(12)

        income_title = QLabel("Income by Category")
        income_title.setStyleSheet("font-weight: 700; font-size: 14px;")
        income_layout.addWidget(income_title)

        income_body = QWidget(income_card)
        income_body_layout = QVBoxLayout()
        income_body_layout.setContentsMargins(0, 0, 0, 0)
        income_body_layout.setSpacing(8)
        income_body_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        income_body.setLayout(income_body_layout)

        empty_kwargs: dict = {"align_top": True}
        if self._on_go_to_transactions is not None:
            empty_kwargs["action_text"] = "Go to Transactions"
            empty_kwargs["action_callback"] = self._on_go_to_transactions

        self._income_cat_empty = EmptyState("No income transactions yet.", **empty_kwargs)
        self._income_cat_empty.setVisible(False)

        self._income_cat_chart_view = QChartView()
        self._income_cat_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._income_cat_chart_view.setMinimumHeight(280)

        income_body_layout.addWidget(self._income_cat_empty)
        income_body_layout.addWidget(self._income_cat_chart_view, 1)
        income_layout.addWidget(income_body, 1)

        row_layout.addWidget(income_card, 1)

        # --- Expenses by category ---
        expense_card = Card(self)
        expense_layout = expense_card.content_layout
        expense_layout.setContentsMargins(16, 16, 16, 16)
        expense_layout.setSpacing(12)

        expense_title = QLabel("Expenses by Category")
        expense_title.setStyleSheet("font-weight: 700; font-size: 14px;")
        expense_layout.addWidget(expense_title)

        expense_body = QWidget(expense_card)
        expense_body_layout = QVBoxLayout()
        expense_body_layout.setContentsMargins(0, 0, 0, 0)
        expense_body_layout.setSpacing(8)
        expense_body_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        expense_body.setLayout(expense_body_layout)

        self._expense_cat_empty = EmptyState("No expense transactions yet.", **empty_kwargs)
        self._expense_cat_empty.setVisible(False)

        self._expense_cat_chart_view = QChartView()
        self._expense_cat_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._expense_cat_chart_view.setMinimumHeight(280)

        expense_body_layout.addWidget(self._expense_cat_empty)
        expense_body_layout.addWidget(self._expense_cat_chart_view, 1)
        expense_layout.addWidget(expense_body, 1)

        row_layout.addWidget(expense_card, 1)

        root.addWidget(row, 1)

        # --- Monthly overview ---
        overview_card = Card(self)
        overview_layout = overview_card.content_layout
        overview_layout.setContentsMargins(16, 16, 16, 16)
        overview_layout.setSpacing(12)

        top_month_hdr = QLabel("Monthly Overview")
        top_month_hdr.setStyleSheet("font-weight: 700; font-size: 14px;")
        overview_layout.addWidget(top_month_hdr)

        top_month_row = QWidget(overview_card)
        top_month_row_layout = QHBoxLayout()
        top_month_row_layout.setContentsMargins(0, 0, 0, 0)
        top_month_row_layout.setSpacing(12)
        top_month_row.setLayout(top_month_row_layout)

        top_month_title = QLabel("Top Month (last 12)")
        top_month_title.setProperty("muted", "true")
        top_month_title.setStyleSheet("font-size: 12.5px; font-weight: 600;")
        top_month_row_layout.addWidget(top_month_title, 1)

        self._top_month_amount = QLabel(format_currency(0.0))
        self._top_month_amount.setStyleSheet("font-size: 24px; font-weight: 800;")
        top_month_row_layout.addWidget(
            self._top_month_amount, alignment=Qt.AlignmentFlag.AlignRight
        )
        overview_layout.addWidget(top_month_row)

        self._top_month_name = QLabel("—")
        self._top_month_name.setStyleSheet(
            "font-size: 14px; font-weight: 700; padding-top: 2px;"
        )
        overview_layout.addWidget(self._top_month_name)

        avg_row = QWidget(overview_card)
        avg_row_layout = QHBoxLayout()
        avg_row_layout.setContentsMargins(0, 8, 0, 0)
        avg_row_layout.setSpacing(12)
        avg_row.setLayout(avg_row_layout)

        avg_lbl = QLabel("Average Weekly Spend")
        avg_lbl.setProperty("muted", "true")
        avg_lbl.setStyleSheet("font-size: 12.5px; font-weight: 600;")
        avg_row_layout.addWidget(avg_lbl, 1)

        self._avg_amt = QLabel(format_currency(0.0))
        self._avg_amt.setStyleSheet("font-size: 24px; font-weight: 800;")
        avg_row_layout.addWidget(self._avg_amt, alignment=Qt.AlignmentFlag.AlignRight)
        overview_layout.addWidget(avg_row)

        self._month_footer = QLabel()
        self._month_footer.setProperty("muted", "true")
        self._month_footer.setStyleSheet("font-size: 12.5px;")
        overview_layout.addWidget(self._month_footer)

        overview_layout.addStretch(1)

        root.addWidget(overview_card)
        self.setLayout(root)

        self._refresh_all()

    def refresh_view(self) -> None:
        """Reload data when the Statistics page becomes active."""
        self._controller.refresh()
        self._refresh_all()

    def _refresh_all(self) -> None:
        self._refresh_monthly_overview()
        self._refresh_income_category_chart()
        self._refresh_expense_category_chart()

    def _refresh_monthly_overview(self) -> None:
        now = datetime.now()
        top_month_key, top_month_total = self._controller.top_month()
        if top_month_key:
            top_month_label = self._month_key_to_label(top_month_key)
        else:
            top_month_label = "—"

        self._top_month_amount.setText(format_currency(float(top_month_total)))
        self._top_month_name.setText(top_month_label)
        self._avg_amt.setText(
            format_currency(float(self._controller.average_weekly_spend_month(now)))
        )
        self._month_footer.setText(f"Current month: {now.strftime('%B %Y')}")

    @staticmethod
    def _month_key_to_label(key: str) -> str:
        try:
            dt = datetime.strptime(key, "%Y-%m")
            return dt.strftime("%B %Y")
        except ValueError:
            return key

    def _refresh_income_category_chart(self) -> None:
        totals = self._controller.income_category_totals_month()
        series = QPieSeries()
        for category, amount in sorted(totals.items(), key=lambda x: x[1], reverse=True):
            series.append(category, float(amount))

        if not totals or series.count() == 0:
            self._income_cat_empty.setVisible(True)
            self._income_cat_chart_view.hide()
            return

        self._income_cat_empty.setVisible(False)
        self._income_cat_chart_view.show()

        chart = QChart()
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignRight)
        chart.addSeries(series)
        chart.setBackgroundVisible(False)
        self._income_cat_chart_view.setChart(chart)

    def _refresh_expense_category_chart(self) -> None:
        totals = self._controller.expense_category_totals_month()
        series = QPieSeries()
        for category, amount in sorted(totals.items(), key=lambda x: x[1], reverse=True):
            series.append(category, float(amount))

        if not totals or series.count() == 0:
            self._expense_cat_empty.setVisible(True)
            self._expense_cat_chart_view.hide()
            return

        self._expense_cat_empty.setVisible(False)
        self._expense_cat_chart_view.show()

        chart = QChart()
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignRight)
        chart.addSeries(series)
        chart.setBackgroundVisible(False)
        self._expense_cat_chart_view.setChart(chart)
