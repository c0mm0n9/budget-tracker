from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtCharts import QChart, QChartView, QCategoryAxis, QLineSeries
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import (
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from app.ui.controllers.app_controller import AppController
from app.ui.design.components import Card, EmptyState, SectionHeader
from app.ui.utils.formatters import format_currency


class DashboardPage(QWidget):
    def __init__(self, controller: AppController | None = None) -> None:
        super().__init__()
        self._controller = controller or AppController()

        root = QVBoxLayout()
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        root.addWidget(SectionHeader("Dashboard"))

        # Metric cards
        metric_row = QWidget(self)
        metric_layout = QHBoxLayout()
        metric_layout.setContentsMargins(0, 0, 0, 0)
        metric_layout.setSpacing(10)
        metric_row.setLayout(metric_layout)

        self._card_total = self._metric_card("Total Spending", "0.00")
        self._card_avg = self._metric_card("Average Transaction", "0.00")
        self._card_count = self._metric_card("Transactions Count", "0")

        metric_layout.addWidget(self._card_total, 1)
        metric_layout.addWidget(self._card_avg, 1)
        metric_layout.addWidget(self._card_count, 1)

        root.addWidget(metric_row)

        # Middle row: trend chart + right column (top items + notifications)
        middle = QWidget(self)
        middle_layout = QHBoxLayout()
        middle_layout.setContentsMargins(0, 0, 0, 0)
        middle_layout.setSpacing(10)
        middle.setLayout(middle_layout)

        # Right column: top income + top spending + notifications
        right_column = QWidget(self)
        right_column_layout = QVBoxLayout()
        right_column_layout.setContentsMargins(0, 0, 0, 0)
        right_column_layout.setSpacing(10)
        right_column.setLayout(right_column_layout)

        # Top income card
        income_card = Card(self)
        income_layout = income_card.content_layout
        income_layout.setContentsMargins(12, 12, 12, 12)
        income_layout.setSpacing(8)
        income_title = QLabel("Top Income")
        income_title.setStyleSheet("font-weight: 700; font-size: 13px;")
        income_layout.addWidget(income_title)

        income_body = QWidget(income_card)
        income_body_layout = QVBoxLayout()
        income_body_layout.setContentsMargins(0, 0, 0, 0)
        income_body_layout.setSpacing(6)
        income_body_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        income_body.setLayout(income_body_layout)

        self._top_income_container = QWidget(income_body)
        self._top_income_layout = QVBoxLayout()
        self._top_income_layout.setContentsMargins(0, 0, 0, 0)
        self._top_income_layout.setSpacing(6)
        self._top_income_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._top_income_container.setLayout(self._top_income_layout)
        income_body_layout.addWidget(self._top_income_container, 1)

        self._top_income_empty = EmptyState("No income transactions yet.", align_top=True)
        income_body_layout.addWidget(self._top_income_empty)
        income_layout.addWidget(income_body, 1)
        self._top_income_empty.setVisible(False)
        right_column_layout.addWidget(income_card, 1)

        # Top spending card
        spending_card = Card(self)
        spending_layout = spending_card.content_layout
        spending_layout.setContentsMargins(12, 12, 12, 12)
        spending_layout.setSpacing(8)
        spending_title = QLabel("Top Spending")
        spending_title.setStyleSheet("font-weight: 700; font-size: 13px;")
        spending_layout.addWidget(spending_title)

        spending_body = QWidget(spending_card)
        spending_body_layout = QVBoxLayout()
        spending_body_layout.setContentsMargins(0, 0, 0, 0)
        spending_body_layout.setSpacing(6)
        spending_body_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        spending_body.setLayout(spending_body_layout)

        self._top_spending_container = QWidget(spending_body)
        self._top_spending_layout = QVBoxLayout()
        self._top_spending_layout.setContentsMargins(0, 0, 0, 0)
        self._top_spending_layout.setSpacing(6)
        self._top_spending_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._top_spending_container.setLayout(self._top_spending_layout)
        spending_body_layout.addWidget(self._top_spending_container, 1)

        self._top_spending_empty = EmptyState("No expense transactions yet.", align_top=True)
        spending_body_layout.addWidget(self._top_spending_empty)
        spending_layout.addWidget(spending_body, 1)
        self._top_spending_empty.setVisible(False)
        right_column_layout.addWidget(spending_card, 1)

        # Left column: spending trend + income trend
        left_column = QWidget(self)
        left_column_layout = QVBoxLayout()
        left_column_layout.setContentsMargins(0, 0, 0, 0)
        left_column_layout.setSpacing(10)
        left_column.setLayout(left_column_layout)

        # Spending trend chart card
        spending_trend_card = Card(self)
        spending_trend_layout = spending_trend_card.content_layout
        spending_trend_layout.setContentsMargins(12, 12, 12, 12)
        spending_trend_layout.setSpacing(8)
        spending_trend_title = QLabel("Spending Trend")
        spending_trend_title.setStyleSheet("font-weight: 700; font-size: 13px;")
        spending_trend_layout.addWidget(spending_trend_title)

        spending_trend_body = QWidget(spending_trend_card)
        spending_trend_body_layout = QVBoxLayout()
        spending_trend_body_layout.setContentsMargins(0, 0, 0, 0)
        spending_trend_body_layout.setSpacing(6)
        spending_trend_body_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        spending_trend_body.setLayout(spending_trend_body_layout)

        self._spending_chart_placeholder = EmptyState(
            "No data available for the selected period.",
            align_top=True,
        )
        self._spending_chart_placeholder.setVisible(False)

        self._spending_chart_view = QChartView()
        self._spending_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._spending_chart_view.setMinimumHeight(160)

        spending_trend_body_layout.addWidget(self._spending_chart_placeholder)
        spending_trend_body_layout.addWidget(self._spending_chart_view, 1)
        spending_trend_layout.addWidget(spending_trend_body, 1)
        left_column_layout.addWidget(spending_trend_card, 1)

        # Income trend chart card
        income_trend_card = Card(self)
        income_trend_layout = income_trend_card.content_layout
        income_trend_layout.setContentsMargins(12, 12, 12, 12)
        income_trend_layout.setSpacing(8)
        income_trend_title = QLabel("Income Trend")
        income_trend_title.setStyleSheet("font-weight: 700; font-size: 13px;")
        income_trend_layout.addWidget(income_trend_title)

        income_trend_body = QWidget(income_trend_card)
        income_trend_body_layout = QVBoxLayout()
        income_trend_body_layout.setContentsMargins(0, 0, 0, 0)
        income_trend_body_layout.setSpacing(6)
        income_trend_body_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        income_trend_body.setLayout(income_trend_body_layout)

        self._income_chart_placeholder = EmptyState(
            "No income data available for the selected period.",
            align_top=True,
        )
        self._income_chart_placeholder.setVisible(False)

        self._income_chart_view = QChartView()
        self._income_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._income_chart_view.setMinimumHeight(160)

        income_trend_body_layout.addWidget(self._income_chart_placeholder)
        income_trend_body_layout.addWidget(self._income_chart_view, 1)
        income_trend_layout.addWidget(income_trend_body, 1)
        left_column_layout.addWidget(income_trend_card, 1)

        middle_layout.addWidget(left_column, 2)

        root.addWidget(middle, 1)

        # Notifications card
        notifications_card = Card(self)
        notifications_layout = notifications_card.content_layout
        notifications_layout.setContentsMargins(12, 12, 12, 12)
        notifications_layout.setSpacing(8)

        notifications_title = QLabel("Notifications")
        notifications_title.setStyleSheet("font-weight: 700; font-size: 13px;")
        notifications_layout.addWidget(notifications_title)

        notifications_body = QWidget(notifications_card)
        notifications_body_layout = QVBoxLayout()
        notifications_body_layout.setContentsMargins(0, 0, 0, 0)
        notifications_body_layout.setSpacing(6)
        notifications_body_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        notifications_body.setLayout(notifications_body_layout)

        self._notifications_container = QWidget(notifications_body)
        self._notifications_list_layout = QVBoxLayout()
        self._notifications_list_layout.setContentsMargins(0, 0, 0, 0)
        self._notifications_list_layout.setSpacing(6)
        self._notifications_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._notifications_container.setLayout(self._notifications_list_layout)
        notifications_body_layout.addWidget(self._notifications_container)

        self._notifications_empty = EmptyState("No notifications right now.", align_top=True)
        notifications_body_layout.addWidget(self._notifications_empty)
        self._notifications_empty.setVisible(False)

        notifications_layout.addWidget(notifications_body, 1)
        right_column_layout.addWidget(notifications_card, 1)

        # Budget usage card
        budget_usage_card = Card(self)
        budget_usage_layout = budget_usage_card.content_layout
        budget_usage_layout.setContentsMargins(12, 12, 12, 12)
        budget_usage_layout.setSpacing(8)

        budget_usage_title = QLabel("Budget Usage")
        budget_usage_title.setStyleSheet("font-weight: 700; font-size: 13px;")
        budget_usage_layout.addWidget(budget_usage_title)

        budget_usage_body = QWidget(budget_usage_card)
        budget_usage_body_layout = QVBoxLayout()
        budget_usage_body_layout.setContentsMargins(0, 0, 0, 0)
        budget_usage_body_layout.setSpacing(6)
        budget_usage_body_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        budget_usage_body.setLayout(budget_usage_body_layout)

        self._budget_usage_container = QWidget(budget_usage_body)
        self._budget_usage_list_layout = QVBoxLayout()
        self._budget_usage_list_layout.setContentsMargins(0, 0, 0, 0)
        self._budget_usage_list_layout.setSpacing(6)
        self._budget_usage_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._budget_usage_container.setLayout(self._budget_usage_list_layout)
        budget_usage_body_layout.addWidget(self._budget_usage_container)

        self._budget_usage_empty = EmptyState("No active budgets right now.", align_top=True)
        budget_usage_body_layout.addWidget(self._budget_usage_empty)
        self._budget_usage_empty.setVisible(False)

        budget_usage_layout.addWidget(budget_usage_body, 1)
        right_column_layout.addWidget(budget_usage_card, 1)

        middle_layout.addWidget(right_column, 1)

        self.setLayout(root)

        self._refresh()

    def refresh_view(self) -> None:
        """
        Reload controller-backed values whenever dashboard becomes active.
        """
        self._controller.refresh()
        self._refresh()

    def _metric_card(self, label: str, value: str) -> QWidget:
        card = Card(self)
        layout = card.content_layout
        layout.setContentsMargins(16, 16, 16, 16)

        lbl = QLabel(label)
        lbl.setProperty("muted", "true")
        lbl.setStyleSheet("font-size: 11.5px; font-weight: 600;")
        val = QLabel(value)
        val.setStyleSheet("font-size: 20px; font-weight: 800;")

        layout.addWidget(lbl)
        layout.addWidget(val)
        layout.addStretch(1)

        # Save references
        card._metric_value_label = val  # type: ignore[attr-defined]
        return card

    def _refresh(self) -> None:
        total = self._controller.total_spending_month()
        avg = self._controller.avg_transaction_month()
        count = self._controller.transactions_count_month()

        self._card_total._metric_value_label.setText(format_currency(total))  # type: ignore[attr-defined]
        self._card_avg._metric_value_label.setText(format_currency(avg))  # type: ignore[attr-defined]
        self._card_count._metric_value_label.setText(str(count))  # type: ignore[attr-defined]

        # Top income
        top_income_txs = self._controller.top_income_transactions_month(limit=5)
        while self._top_income_layout.count():
            item = self._top_income_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        if not top_income_txs:
            self._top_income_empty.setVisible(True)
            self._top_income_container.setVisible(False)
        else:
            self._top_income_empty.setVisible(False)
            self._top_income_container.setVisible(True)

            for tx in top_income_txs:
                line = QLabel(f"{tx.category} ({tx.tag or '-'}): {format_currency(float(tx.amount))}")
                line.setStyleSheet("font-size: 12px;")
                self._top_income_layout.addWidget(line)

        # Top spending
        top_spending_txs = self._controller.top_spending_transactions_month(limit=5)
        while self._top_spending_layout.count():
            item = self._top_spending_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        if not top_spending_txs:
            self._top_spending_empty.setVisible(True)
            self._top_spending_container.setVisible(False)
        else:
            self._top_spending_empty.setVisible(False)
            self._top_spending_container.setVisible(True)

            for tx in top_spending_txs:
                line = QLabel(f"{tx.category} ({tx.tag or '-'}): {format_currency(abs(float(tx.amount)))}")
                line.setStyleSheet("font-size: 12px;")
                self._top_spending_layout.addWidget(line)

        # Spending chart
        spending_labels, spending_totals = self._controller.spending_trend_last_weeks(weeks=6)
        spending_totals = [abs(v) for v in spending_totals]
        if not any(spending_totals):
            self._spending_chart_placeholder.setVisible(True)
            self._spending_chart_view.hide()
        else:
            self._spending_chart_placeholder.setVisible(False)
            self._spending_chart_view.show()

            series = QLineSeries()
            for i, y in enumerate(spending_totals):
                series.append(i, y)

            chart = QChart()
            chart.setBackgroundVisible(False)
            chart.legend().hide()
            chart.addSeries(series)

            axis_x = QCategoryAxis()
            for i, label in enumerate(spending_labels):
                axis_x.append(label, float(i))
            chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            series.attachAxis(axis_x)

            chart.createDefaultAxes()
            self._spending_chart_view.setChart(chart)

        # Income chart
        income_labels, income_totals = self._controller.income_trend_last_weeks(weeks=6)
        if not any(income_totals):
            self._income_chart_placeholder.setVisible(True)
            self._income_chart_view.hide()
        else:
            self._income_chart_placeholder.setVisible(False)
            self._income_chart_view.show()

            series = QLineSeries()
            for i, y in enumerate(income_totals):
                series.append(i, y)

            chart = QChart()
            chart.setBackgroundVisible(False)
            chart.legend().hide()
            chart.addSeries(series)

            axis_x = QCategoryAxis()
            for i, label in enumerate(income_labels):
                axis_x.append(label, float(i))
            chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            series.attachAxis(axis_x)

            chart.createDefaultAxes()
            self._income_chart_view.setChart(chart)

        # Notifications
        while self._notifications_list_layout.count():
            item = self._notifications_list_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        notifications = self._controller.dashboard_notifications()
        if not notifications:
            self._notifications_empty.setVisible(True)
            self._notifications_container.setVisible(False)
        else:
            self._notifications_empty.setVisible(False)
            self._notifications_container.setVisible(True)
            for message in notifications:
                line = QLabel(f"- {message}")
                line.setWordWrap(True)
                line.setStyleSheet("font-size: 12px;")
                self._notifications_list_layout.addWidget(line)

        # Budget usage
        while self._budget_usage_list_layout.count():
            item = self._budget_usage_list_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        budget_usages = self._controller.budget_usage_current()
        if not budget_usages:
            self._budget_usage_empty.setVisible(True)
            self._budget_usage_container.setVisible(False)
        else:
            self._budget_usage_empty.setVisible(False)
            self._budget_usage_container.setVisible(True)
            for name, spent, limit in budget_usages:
                pct = 0.0 if limit <= 0 else (spent / limit) * 100.0
                line = QLabel(
                    f"{name}: {format_currency(spent)} / {format_currency(limit)} ({pct:.0f}%)"
                )
                line.setWordWrap(True)
                line.setStyleSheet("font-size: 12px;")
                self._budget_usage_list_layout.addWidget(line)

