from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class ReadingBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    temperature: float
    humidity: float
    measured_at: datetime