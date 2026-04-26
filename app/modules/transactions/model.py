from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    property_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Transaction id={self.id} property={self.property_name} category={self.category}>"