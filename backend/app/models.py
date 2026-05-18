from pydantic import BaseModel
from typing import Optional


class Station(BaseModel):
    id: str
    name: str
    country: str
    latitude: float
    longitude: float
    type: str
    source: str
    description: Optional[str] = None
    # Optional thesis fields
    code: Optional[str] = None
    period: Optional[str] = None
    method: Optional[str] = None
    status: Optional[str] = None
    start_year: Optional[str] = None
    organization: Optional[str] = None
    history: Optional[str] = None
    equipment: Optional[str] = None
