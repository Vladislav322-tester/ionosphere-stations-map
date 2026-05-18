import React, { useEffect, useState } from 'react'
import { Station } from './types/station'
import { fetchStations } from './services/stationsApi'
import Globe from './components/Globe'
import StationInfoPanel from './components/StationInfoPanel'

export default function App() {
  const [stations, setStations] = useState<Station[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selected, setSelected] = useState<Station | null>(null)

  useEffect(() => {
    setLoading(true)
    fetchStations()
      .then((data) => setStations(data))
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="app">
      <header className="header">
        <h1>Интерактивная карта ионосферных станций</h1>
        <p className="subtitle">Визуализация мировой сети станций наблюдения за ионосферой</p>
      </header>

      <main className="main">
        <section className="globe-area">
          {loading && <div className="status">Загрузка станций...</div>}
          {error && <div className="status error">Ошибка: {error}</div>}
          {!loading && !error && (
            <Globe
              stations={stations}
              selectedStationId={selected?.id ?? null}
              onSelect={(id) => {
                const s = stations.find(st => st.id === id) || null
                setSelected(s)
              }}
            />
          )}
        </section>

        <aside className="panel-area">
          <StationInfoPanel station={selected} onClose={() => setSelected(null)} />
        </aside>
      </main>

      <footer className="footer">
        <small>Прототип MVP для визуализации ионосферных станций по всему миру</small>
      </footer>
    </div>
  )
}
