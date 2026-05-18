# Ionosphere Globe (MVP)

Prototype web application for visualizing ionospheric stations on an interactive 3D globe. Built as an MVP for a master's thesis.

## Purpose

Provide a minimal, working prototype that shows ionospheric station locations on a 3D globe and displays station details when a marker is clicked.

## Architecture Overview

- Frontend: React + TypeScript + Vite + CesiumJS
- Backend: FastAPI (Python) serving station data from a local JSON file
- Containerization: Docker Compose to run both services easily

## Technologies

- React, TypeScript, Vite
- CesiumJS for 3D globe
- FastAPI, Uvicorn
- Docker & Docker Compose

## Folder Structure

- frontend/ - Vite React app
- backend/ - FastAPI app
- docker-compose.yml - runs both services

## Docker Setup

Requirements: Docker and Docker Compose installed.

To start both services:

```bash
docker compose up --build
```

After startup:

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Swagger: http://localhost:8000/docs

Notes: The frontend dev server serves Cesium assets copied into `public/cesium` during image build.

## Local Setup (without Docker)

Backend:

```bash
python -m venv .venv
.venv\Scripts\activate  # on Windows
pip install -r backend/requirements.txt
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
```

Frontend:

```bash
cd frontend
npm install
npm run dev -- --host
```

Ensure `VITE_API_BASE_URL` points to `http://localhost:8000` if running frontend separately.

## API Endpoints

- `GET /api/health` — returns `{ "status": "ok" }`
- `GET /api/stations` — returns list of stations
- `GET /api/stations/{station_id}` — returns single station or 404

## MVP Features

- Interactive 3D globe using CesiumJS
- Clickable markers for stations
- Station info panel with details
- Loading/error states

## Future Improvements

- Add PostgreSQL/PostGIS for spatial queries
- Integrate real GIRO, Madrigal, and NOAA data sources
- Add foF2, hmF2, MUF graphs and historical measurements
- Add filters, search, and admin panel etc.
