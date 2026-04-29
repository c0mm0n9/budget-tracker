from __future__ import annotations

from datetime import date as py_date
from datetime import datetime, timedelta
from typing import Dict, List, Sequence, Tuple

from app.budget.budget_manager import BudgetManager
from app.storage.budget_model import BudgetModel
from app.storage.notification_rule import NotificationRuleModel
from app.transaction.transaction_manager import TransactionManager
from app.warnings.notification_rules_manager import NotificationRulesManager


class AppController:
    """
    UI controller facade.

    Real UI will call refresh methods and CRUD operations.
    This is a placeholder until `controller-layer` is implemented.
    """

    def __init__(self) -> None:
        self.budgets_manager = BudgetManager()
        self.transactions_manager = TransactionManager()
        self.rules_manager = NotificationRulesManager()

    def refresh(self) -> None:
        self.transactions_manager.load_transactions()
        self.budgets_manager.load_budgets()
        self.rules_manager.load_notification_rules()

    def get_transactions(self):
        return self.transactions_manager.get_all_transactions()

    def get_budgets(self) -> list[BudgetModel]:
        return self.budgets_manager.get_all_budgets()

    def get_rules(self) -> list[NotificationRuleModel]:
        return self.rules_manager.get_all_notification_rules()

    def dashboard_notifications(self) -> list[str]:
        transactions = self.transactions_manager.get_all_transactions()
        budgets = self.budgets_manager.get_all_budgets()
        return self.rules_manager.check_all_notifications(transactions, budgets)

    # ----------------------------
    # Derived stats for dashboard
    # ----------------------------

    def transactions_this_month(self, now: datetime | None = None) -> Sequence:
        now = now or datetime.now()
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # "Date-only" range, safe without timezone complexity.
        end = start + timedelta(days=31)
        return [
            tx
            for tx in self.transactions_manager.get_all_transactions()
            if start <= datetime.fromtimestamp(tx.timestamp) <= end
        ]

    def total_spending_month(self, now: datetime | None = None) -> float:
        txs = self.transactions_this_month(now)
        return float(sum(tx.amount for tx in txs))

    def avg_transaction_month(self, now: datetime | None = None) -> float:
        txs = self.transactions_this_month(now)
        if not txs:
            return 0.0
        return self.total_spending_month(now) / len(txs)

    def transactions_count_month(self, now: datetime | None = None) -> int:
        return len(self.transactions_this_month(now))

    def top_spending_transactions_month(
        self, limit: int = 5, now: datetime | None = None
    ) -> List:
        txs = sorted(
            [tx for tx in self.transactions_this_month(now) if float(tx.amount) < 0],
            key=lambda x: abs(float(x.amount)),
            reverse=True,
        )
        return txs[:limit]

    def top_income_transactions_month(
        self, limit: int = 5, now: datetime | None = None
    ) -> List:
        txs = sorted(
            [tx for tx in self.transactions_this_month(now) if float(tx.amount) > 0],
            key=lambda x: float(x.amount),
            reverse=True,
        )
        return txs[:limit]

    def spending_trend_last_weeks(
        self, weeks: int = 6, now: datetime | None = None
    ) -> Tuple[List[str], List[float]]:
        now = now or datetime.now()
        today = now.date()
        
        date_list = [today - timedelta(days=i) for i in range(29, -1, -1)]

        totals: list[float] = []
        labels: list[str] = []
        all_txs = self.transactions_manager.get_all_transactions()
        
        for target_date in date_list:
            day_total = 0.0
            for tx in all_txs:
                tx_date = datetime.fromtimestamp(tx.timestamp).date()
                amount = float(tx.amount)
                if tx_date == target_date and amount < 0:
                    day_total += abs(amount)
            
            totals.append(day_total)
            labels.append(target_date.strftime("%m-%d"))

        return labels, totals

    def income_trend_last_weeks(
        self, weeks: int = 6, now: datetime | None = None
    ) -> Tuple[List[str], List[float]]:
        now = now or datetime.now()
        today = now.date()
        
        date_list = [today - timedelta(days=i) for i in range(29, -1, -1)]

        totals: list[float] = []
        labels: list[str] = []
        all_txs = self.transactions_manager.get_all_transactions()
        
        for target_date in date_list:
            day_total = 0.0
            for tx in all_txs:
                tx_date = datetime.fromtimestamp(tx.timestamp).date()
                amount = float(tx.amount)
                if tx_date == target_date and amount > 0:
                    day_total += amount
            
            totals.append(day_total)
            labels.append(target_date.strftime("%m-%d"))

        return labels, totals

    def budget_usage_current(self, now: datetime | None = None) -> List[Tuple[str, float, float]]:
        now = now or datetime.now()
        today = now.date()
        active_budgets = [
            b
            for b in self.budgets_manager.get_all_budgets()
            if b.start.date() <= today <= b.end.date()
        ]

        all_txs = self.transactions_manager.get_all_transactions()
        usages: list[Tuple[str, float, float]] = []
        for budget in active_budgets:
            spent = 0.0
            for tx in all_txs:
                tx_date = datetime.fromtimestamp(tx.timestamp).date()
                amount = float(tx.amount)
                if (budget.start.date() <= tx_date <= budget.end.date() and 
                    amount < 0 and 
                    getattr(tx, 'linked_budget', None) == budget.name):
                    spent += abs(amount)
                    
            limit = float(budget.amount)
            usages.append((budget.name, spent, limit))
        return usages

    # ----------------------------
    # Derived stats for statistics
    # ----------------------------

    def category_totals_month(
        self, now: datetime | None = None
    ) -> Dict[str, float]:
        now = now or datetime.now()
        txs = self.transactions_this_month(now)
        totals: dict[str, float] = {}
        for tx in txs:
            totals[tx.category] = totals.get(tx.category, 0.0) + float(tx.amount)
        return totals

    def expense_category_totals_month(
        self, now: datetime | None = None
    ) -> Dict[str, float]:
        now = now or datetime.now()
        txs = self.transactions_this_month(now)
        totals: dict[str, float] = {}
        for tx in txs:
            amount = float(tx.amount)
            if amount < 0:
                totals[tx.category] = totals.get(tx.category, 0.0) + abs(amount)
        return totals

    def income_category_totals_month(
        self, now: datetime | None = None
    ) -> Dict[str, float]:
        now = now or datetime.now()
        txs = self.transactions_this_month(now)
        totals: dict[str, float] = {}
        for tx in txs:
            amount = float(tx.amount)
            if amount > 0:
                totals[tx.category] = totals.get(tx.category, 0.0) + amount
        return totals

    def monthly_totals_last_n_months(
        self, n: int = 12, now: datetime | None = None
    ) -> List[Tuple[str, float]]:
        """
        Return list of (YYYY-MM, total) for last `n` months including current.
        """
        now = now or datetime.now()
        year = now.year
        month = now.month

        # Build month start dates using integer month offsets.
        month_starts: list[py_date] = []
        for i in range(n - 1, -1, -1):
            total_months = year * 12 + (month - 1) - i
            ty = total_months // 12
            tm = total_months % 12 + 1
            month_starts.append(datetime(ty, tm, 1).date())

        month_ends: list[py_date] = []
        for ws in month_starts:
            # First day of next month
            next_m = ws.replace(day=28) + timedelta(days=4)
            next_month_start = next_m.replace(day=1)
            month_ends.append(next_month_start)

        totals: list[Tuple[str, float]] = []
        all_txs = self.transactions_manager.get_all_transactions()
        for ws, we in zip(month_starts, month_ends):
            total = 0.0
            for tx in all_txs:
                d = datetime.fromtimestamp(tx.timestamp).date()
                if ws <= d < we:
                    total += float(tx.amount)
            totals.append((ws.strftime("%Y-%m"), total))

        return totals

    def top_month(
        self, n: int = 12, now: datetime | None = None
    ) -> Tuple[str, float]:
        totals = self.monthly_totals_last_n_months(n=n, now=now)
        if not totals:
            return "", 0.0
        best = max(totals, key=lambda x: x[1])
        return best[0], best[1]

    def average_weekly_spend_month(
        self, now: datetime | None = None
    ) -> float:
        now = now or datetime.now()
        txs = self.transactions_this_month(now)
        total = float(sum(tx.amount for tx in txs))
        if not txs:
            return 0.0

        # Approx average across calendar weeks (ceil to avoid undercounting).
        start_of_month = now.replace(day=1).date()
        next_m = (start_of_month.replace(day=28) + timedelta(days=4)).replace(day=1)
        days_in_month = (next_m - start_of_month).days
        weeks = max(1, (days_in_month + 6) // 7)
        return total / weeks
