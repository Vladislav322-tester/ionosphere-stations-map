from pydantic import BaseModel
from typing import Optional

class Station(BaseModel):
    id: str
    name: str
    code: Optional[str] = None
    country: Optional[str] = "нет данных"
    latitude: float
    longitude: float

    data_interval: Optional[str] = None
    method: Optional[str] = None
    status: Optional[str] = None
    start_year: Optional[str] = None
    organization: Optional[str] = None
    history: Optional[str] = None
    equipment: Optional[str] = None
    frequency_range: Optional[str] = None

    type: Optional[str] = None
    source: Optional[str] = None
    description: Optional[str] = None