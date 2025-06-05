from pydantic import BaseModel

class OrderBase(BaseModel):
    id: int | None
    user_id: int
    order_name: str
    status: str | None = "Отправлен на проверку"