"""
SQL-shaped notification rules (no SQL engine).

Syntax:
  Optional: SELECT * | SELECT 1
  Required: WHERE <comparison> ( AND <comparison> )*

Comparisons use `transaction.<field>` or `budget.<field>` on either side,
or literals: numbers, single-quoted strings ('it''s' for apostrophe).

Operators: !=, <=, >=, =, <, >
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Union

from app.storage.budget_model import BudgetModel
from app.storage.transaction_model import TransactionModel

TRANSACTION_FIELDS = frozenset(TransactionModel.model_fields.keys())
BUDGET_FIELDS = frozenset(BudgetModel.model_fields.keys())

FIELD_REF = re.compile(r"^(transaction|budget)\.(\w+)\s*$")


@dataclass(frozen=True)
class FieldRef:
    table: Literal["transaction", "budget"]
    name: str


@dataclass(frozen=True)
class LiteralValue:
    value: Union[int, float, str]


Operand = FieldRef | LiteralValue

ParsedRule = list[tuple[Operand, str, Operand]]


class RuleSyntaxError(ValueError):
    pass


def parse_notification_rule(rule: str) -> ParsedRule:
    text = rule.strip()
    if not text:
        raise RuleSyntaxError("Empty rule")
    core = text.rstrip(";").strip()
    if ";" in core:
        raise RuleSyntaxError("Multiple statements are not allowed")

    upper = core.upper()
    if upper.startswith("SELECT"):
        where_at = upper.rfind(" WHERE ")
        if where_at == -1:
            raise RuleSyntaxError("SELECT form must include WHERE")
        core = core[where_at + len(" WHERE ") :].strip()
    elif upper.startswith("WHERE"):
        core = core[5:].strip()
    else:
        raise RuleSyntaxError("Rule must start with WHERE or SELECT ... WHERE")

    if not core:
        raise RuleSyntaxError("Missing condition after WHERE")

    parts = _split_and(core)
    comparisons: ParsedRule = []
    for part in parts:
        if not part:
            raise RuleSyntaxError("Empty AND clause")
        left_s, op, right_s = _split_comparison(part)
        left = _parse_operand(left_s, "left")
        right = _parse_operand(right_s, "right")
        _validate_field_ref(left)
        _validate_field_ref(right)
        comparisons.append((left, op, right))
    return comparisons


def _split_and(s: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    i = 0
    in_quote = False
    while i < len(s):
        c = s[i]
        if c == "'":
            in_quote = not in_quote
            buf.append(c)
            i += 1
            continue
        if not in_quote and s[i : i + 5].upper() == " AND ":
            parts.append("".join(buf).strip())
            buf = []
            i += 5
            continue
        buf.append(c)
        i += 1
    parts.append("".join(buf).strip())
    return parts


def _split_comparison(part: str) -> tuple[str, str, str]:
    in_quote = False
    i = 0
    while i < len(part):
        c = part[i]
        if c == "'":
            in_quote = not in_quote
            i += 1
            continue
        if not in_quote:
            for op in ("!=", "<=", ">=", "=", "<", ">"):
                if part.startswith(op, i):
                    left = part[:i].strip()
                    right = part[i + len(op) :].strip()
                    return left, op, right
        i += 1
    raise RuleSyntaxError(f"No valid operator in: {part!r}")


def _parse_operand(raw: str, side: str) -> Operand:
    s = raw.strip()
    m = FIELD_REF.match(s)
    if m:
        return FieldRef(m.group(1), m.group(2))  # type: ignore[arg-type]

    if s.startswith("'"):
        if len(s) < 2 or not s.endswith("'"):
            raise RuleSyntaxError(f"Unterminated string in {side} operand: {raw!r}")
        inner = s[1:-1].replace("''", "'")
        return LiteralValue(inner)

    try:
        if re.fullmatch(r"-?\d+\.\d+", s) or re.fullmatch(r"-?\d+\.\d+[eE][+-]?\d+", s):
            return LiteralValue(float(s))
        if re.fullmatch(r"-?\d+", s):
            return LiteralValue(int(s))
    except ValueError:
        pass

    raise RuleSyntaxError(f"Invalid {side} operand: {raw!r}")


def _validate_field_ref(op: Operand) -> None:
    if isinstance(op, LiteralValue):
        return
    fields = TRANSACTION_FIELDS if op.table == "transaction" else BUDGET_FIELDS
    if op.name not in fields:
        raise RuleSyntaxError(f"Unknown field {op.table}.{op.name}")


def _resolve(op: Operand, transaction: TransactionModel, budget: BudgetModel):
    if isinstance(op, LiteralValue):
        return op.value
    model = transaction if op.table == "transaction" else budget
    return getattr(model, op.name)


def _coerce_for_compare(a, b):
    if type(a) is type(b):
        return a, b
    if isinstance(a, datetime) and isinstance(b, int):
        return a, datetime.fromtimestamp(b)
    if isinstance(b, datetime) and isinstance(a, int):
        return datetime.fromtimestamp(a), b
    if isinstance(a, float) and isinstance(b, int):
        return a, float(b)
    if isinstance(b, float) and isinstance(a, int):
        return float(a), b
    return a, b


def _apply_op(left, right, op: str) -> bool:
    left, right = _coerce_for_compare(left, right)
    if op == "=":
        return left == right
    if op == "!=":
        return left != right
    if op == "<":
        return left < right
    if op == ">":
        return left > right
    if op == "<=":
        return left <= right
    if op == ">=":
        return left >= right
    raise RuleSyntaxError(f"Unsupported operator: {op}")


def evaluate_rule(parsed: ParsedRule, transaction: TransactionModel, budget: BudgetModel) -> bool:
    for left, op, right in parsed:
        lv = _resolve(left, transaction, budget)
        rv = _resolve(right, transaction, budget)
        if not _apply_op(lv, rv, op):
            return False
    return True
