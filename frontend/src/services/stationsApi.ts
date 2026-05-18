import { Station } from '../types/station'

const API_BASE =
  (import.meta.env.VITE_API_BASE_URL as string) ||
  "https://ionosphere-stations-map.onrender.com"

export async function fetchStations(): Promise<Station[]> {
  const res = await fetch(`${API_BASE}/api/stations`)

  if (!res.ok) {
    throw new Error(`Failed to fetch stations: ${res.status}`)
  }

  return res.json()
}

export async function fetchStation(id: string): Promise<Station> {
  const res = await fetch(`${API_BASE}/api/stations/${id}`)

  if (!res.ok) {
    throw new Error(`Station not found: ${res.status}`)
  }

  return res.json()
}