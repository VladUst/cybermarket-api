from datetime import datetime
from sqlalchemy import Boolean, Integer, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=True)
    grade: Mapped[int] = mapped_column(Integer, CheckConstraint('grade >= 1 AND grade <= 5'), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
