from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.services.stations_service import get_all_stations, get_station_by_id
from app.models import Station

app = FastAPI(title="Ionosphere Stations API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/stations", response_model=list[Station])
def list_stations():
    return get_all_stations()


@app.get("/api/stations/{station_id}", response_model=Station)
def get_station(station_id: str):
    s = get_station_by_id(station_id)
    if not s:
        raise HTTPException(status_code=404, detail="Station not found")
    return s
