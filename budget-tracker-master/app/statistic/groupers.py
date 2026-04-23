from app.storage.transaction_model import TransactionModel

def transactions_by_category(
    transactions: list[TransactionModel],
    category: str
    ) -> list[TransactionModel]:
    """
    Group transactions by category.
    """
    return [
        transaction for transaction in transactions
        if transaction.category == category
    ]

def transactions_by_tag(
    transactions: list[TransactionModel],
    tag: str
    ) -> list[TransactionModel]:
    """
    Group transactions by tag.
    """
    return [
        transaction for transaction in transactions
        if transaction.tag == tag
    ]