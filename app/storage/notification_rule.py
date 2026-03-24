from pydantic import BaseModel

class NotificationRuleModel(BaseModel):
    id: int
    name: str
    rule: str
    message: str = ""
    