from __future__ import annotations


def format_currency(value: float) -> str:
    """
    Simple currency formatting for UI.
    """
    if value < 0:
        return f"-${abs(value):,.2f}"
    return f"${value:,.2f}"

