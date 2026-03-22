from app.storage.transaction_model import TransactionModel

class TransactionManager:
    def __init__(self):
        self.transactions = []

    def create_transaction(self, transaction: TransactionModel) -> TransactionModel:
        self.transactions.append(transaction)
        return transaction

    def read_transaction(self, id: int):
        return next(
            (transaction for transaction in self.transactions 
            if transaction.id == id), None)
    
    def update_transaction(self, id: int, transaction: TransactionModel) -> TransactionModel:
        for i, t in enumerate(self.transactions):
            if t.id == id:
                self.transactions[i] = transaction
                return self.transactions[i]
        return None
    
    def delete_transaction(self, id: int) -> bool:
        for i, t in enumerate(self.transactions):
            if t.id == id:
                self.transactions.pop(i)
                return True
        return False
    