from app.storage.transaction_model import TransactionModel
from app.config import Config
from app.storage.csv_handler import read_csv_dicts, write_csv_dicts
from datetime import datetime

class TransactionManager:
    def __init__(self):
        self.transactions: list[TransactionModel] = []
        self.config = Config()
        self.load_transactions()

    def load_transactions(self) -> None:
        self.transactions = []
        for row in read_csv_dicts(self.config.TRANSACTION_FILE):
            try:
                self.transactions.append(TransactionModel(**row))
            except Exception as e:
                print(f"Error loading transaction: {e}")
                continue

    def save_transactions(self) -> None:
        write_csv_dicts(
            self.config.TRANSACTION_FILE,
            [transaction.model_dump() for transaction in self.transactions],
            list(TransactionModel.model_fields.keys()),
        )

    def create_transaction(self, transaction: TransactionModel) -> TransactionModel:
        self.transactions.append(transaction)
        self.save_transactions()
        return transaction

    def read_transaction(self, id: int):
        return next(
            (transaction for transaction in self.transactions 
            if transaction.id == id), None)
    
    def update_transaction(self, id: int, transaction: TransactionModel) -> TransactionModel:
        for i, t in enumerate(self.transactions):
            if t.id == id:
                self.transactions[i] = transaction
                self.save_transactions()
                return self.transactions[i]
        return None
    
    def delete_transaction(self, id: int) -> bool:
        for i, t in enumerate(self.transactions):
            if t.id == id:
                self.transactions.pop(i)
                self.save_transactions()
                return True
        return False
    
    def get_all_transactions(self) -> list[TransactionModel]:
        return self.transactions
    
    def get_transactions_by_date(self, date: datetime) -> list[TransactionModel]:
        return [
            transaction for transaction in self.transactions 
            if datetime.fromtimestamp(transaction.timestamp).date() == date.date()
        ]
    
    def get_transactions_by_category(self, category: str) -> list[TransactionModel]:
        return [
            transaction for transaction in self.transactions 
            if transaction.category == category
        ]
    
    def get_transactions_by_tag(self, tag: str) -> list[TransactionModel]:
        return [
            transaction for transaction in self.transactions 
            if transaction.tag == tag
        ]   
    def get_transactions_by_budget(self, budget_name: str) -> list[TransactionModel]:
        
        return [
            t for t in self.transactions 
            if getattr(t, 'linked_budget', None) == budget_name
        ]