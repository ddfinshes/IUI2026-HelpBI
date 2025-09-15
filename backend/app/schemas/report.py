from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ReportData(BaseModel):
    id: str
    title: str
    value: float
    change: float
    change_percent: float
    category: str
    date: datetime

class ReportResponse(BaseModel):
    success: bool
    data: List[ReportData]
    total: int
    message: str = "success"
