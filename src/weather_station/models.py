from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base

class Measurement(Base):
    __tablename__ = "measurements"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    humidity: Mapped[float] = mapped_column(Float, nullable=False)
    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )