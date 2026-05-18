import json
from pathlib import Path
from typing import List, Optional

from app.models import Station


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "stations.json"


def load_stations() -> List[Station]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Station(**item) for item in data]


_CACHE: Optional[List[Station]] = None


def get_all_stations() -> List[Station]:
    global _CACHE
    if _CACHE is None:
        _CACHE = load_stations()
    return _CACHE


def get_station_by_id(station_id: str) -> Optional[Station]:
    stations = get_all_stations()
    for s in stations:
        if s.id == station_id:
            return s
    return None
