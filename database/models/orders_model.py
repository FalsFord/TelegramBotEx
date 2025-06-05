from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Order(Base):
    __tablename__ = 'orders'

    user_id: Mapped[int] = mapped_column(nullable=False)
    order_name: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)