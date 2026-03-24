from dotenv import load_dotenv
import os

class Config:
    def __init__(self):
        load_dotenv()
        self.DATA_DIR = os.getenv("DATA_DIR", "data")
        if not os.path.exists(self.DATA_DIR):
            os.makedirs(self.DATA_DIR)
            
        self.BUDGET_FILE = os.getenv("BUDGET_FILE", f"{self.DATA_DIR}/budgets.csv")   
        self.TRANSACTION_FILE = os.getenv("TRANSACTION_FILE", f"{self.DATA_DIR}/transactions.csv")
        self.NOTIFICATION_RULE_FILE = os.getenv("NOTIFICATION_RULE_FILE", f"{self.DATA_DIR}/notification_rules.csv")
        self.NOTIFICATION_FILE = os.getenv("NOTIFICATION_FILE", f"{self.DATA_DIR}/notifications.csv")