import unittest
from unittest.mock import patch
from datetime import datetime
from app.transaction.transaction_manager import TransactionManager
from tests.commons import create_test_transaction

class TestTransactionManager(unittest.TestCase):
    def setUp(self):
        self._load_patcher = patch.object(
            TransactionManager,
            "load_transactions",
            autospec=True,
        )
        self._save_patcher = patch.object(
            TransactionManager,
            "save_transactions",
            autospec=True,
        )
        self._load_patcher.start()
        self._save_patcher.start()
        self.addCleanup(self._load_patcher.stop)
        self.addCleanup(self._save_patcher.stop)
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
        updated_transaction = self.transaction_manager.update_transaction(1, transaction)
        self.assertEqual(self.transaction_manager.read_transaction(1).amount, 200.0)
        self.assertEqual(updated_transaction, transaction)

    def test_delete_transaction(self):
        transaction = create_test_transaction()
        self.transaction_manager.create_transaction(transaction)
        self.transaction_manager.delete_transaction(transaction.id)
        self.assertEqual(len(self.transaction_manager.transactions), 0)

    def test_get_all_transactions(self):
        transaction = create_test_transaction()
        self.transaction_manager.create_transaction(transaction)
        self.assertEqual(len(self.transaction_manager.get_all_transactions()), 1)
        self.assertEqual(self.transaction_manager.get_all_transactions()[0], transaction)

    def test_get_transactions_by_date(self):
        transaction = create_test_transaction()
        self.transaction_manager.create_transaction(transaction)
        self.assertEqual(len(self.transaction_manager.get_transactions_by_date(datetime.fromtimestamp(transaction.timestamp))), 1)
        self.assertEqual(self.transaction_manager.get_transactions_by_date(datetime.fromtimestamp(transaction.timestamp))[0], transaction)

    def test_get_transactions_by_category(self):
        transaction = create_test_transaction()
        self.transaction_manager.create_transaction(transaction)
        self.assertEqual(len(self.transaction_manager.get_transactions_by_category(transaction.category)), 1)
        self.assertEqual(self.transaction_manager.get_transactions_by_category(transaction.category)[0], transaction)

    def test_get_transactions_by_tag(self):
        transaction = create_test_transaction()
        self.transaction_manager.create_transaction(transaction)
        self.assertEqual(len(self.transaction_manager.get_transactions_by_tag(transaction.tag)), 1)
        self.assertEqual(self.transaction_manager.get_transactions_by_tag(transaction.tag)[0], transaction)