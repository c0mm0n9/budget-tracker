import unittest
from app.transaction.transaction_manager import TransactionManager
from app.storage.transaction_model import TransactionModel

def create_test_transaction(
    id: int = 1, 
    timestamp: int = 1716153600, 
    category: str = "Test", 
    amount: float = 100.0, 
    tag: str = "Test"
    ) -> TransactionModel:
    """
    Create a test transaction.
    """
    return TransactionModel(id=id, timestamp=timestamp, category=category, amount=amount, tag=tag)

class TestTransactionManager(unittest.TestCase):
    def setUp(self):
        self.transaction_manager = TransactionManager()

    def test_create_transaction(self):
        transaction = create_test_transaction()
        self.transaction_manager.create_transaction(transaction)
        self.assertEqual(len(self.transaction_manager.transactions), 1)
        self.assertEqual(self.transaction_manager.transactions[0], transaction)

    def test_read_transaction(self):
        transaction = create_test_transaction()
        self.transaction_manager.create_transaction(transaction)

    def test_update_transaction(self):
        transaction = create_test_transaction(id=1, amount=100.0)
        self.transaction_manager.create_transaction(transaction)
        transaction = create_test_transaction(id=1, amount=200.0)
        self.transaction_manager.update_transaction(1, transaction)
        self.assertEqual(self.transaction_manager.read_transaction(1).amount, 200.0)

    def test_delete_transaction(self):
        transaction = create_test_transaction()
        self.transaction_manager.create_transaction(transaction)
        self.transaction_manager.delete_transaction(transaction.id)
        self.assertEqual(len(self.transaction_manager.transactions), 0)
