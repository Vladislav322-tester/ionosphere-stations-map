import React from 'react'
import { Station } from '../types/station'

type Props = {
  station: Station | null
  onClose: () => void
}

export default function StationInfoPanel({ station, onClose }: Props) {
  if (!station) {
    return (
      <div className="panel empty info-panel">
        <h2>Информация о станции</h2>
        <p>Станция не выбрана. Нажмите на маркер на глобусе.</p>
      </div>
    )
  }

  const empty = (v: any) => (v === undefined || v === null || String(v).trim() === '' ? 'нет данных' : v)

  const status = String((station as any).status || '').trim()
  const statusKey = status === 'Активна' ? 'status-active' : status === 'Закрыта' ? 'status-closed' : 'status-unknown'

  return (
    <div className="panel info-panel">
      <div className="panel-header">
        <div>
          <div className="station-title">{empty(station.name)}</div>
          <div className={`status-badge ${statusKey}`}>{status || 'нет данных'}</div>
        </div>
        <button className="close-button" onClick={onClose} aria-label="Закрыть">✕</button>
      </div>

      <div className="station-fields">
        <div className="station-field">
          <div className="station-label">Название (URSI)</div>
          <div className={`station-value ${empty(station.name) === 'нет данных' ? 'station-value empty' : ''}`}>{empty(station.name)}</div>
        </div>

        <div className="station-field">
          <div className="station-label">Код URSI</div>
          <div className={`station-value ${empty((station as any).code || station.id) === 'нет данных' ? 'station-value empty' : ''}`}>{empty((station as any).code || station.id)}</div>
        </div>

        <div className="station-field">
          <div className="station-label">Широта (градусы)</div>
          <div className={`station-value`}>{empty(station.latitude)}</div>
        </div>

        <div className="station-field">
          <div className="station-label">Долгота (градусы)</div>
          <div className={`station-value`}>{empty(station.longitude)}</div>
        </div>

        <div className="station-field">
          <div className="station-label">Интервал работы</div>
          <div className={`station-value ${empty((station as any).period) === 'нет данных' ? 'station-value empty' : ''}`}>{empty((station as any).period)}</div>
        </div>

        <div className="station-field">
          <div className="station-label">Метод зондирования</div>
          <div className={`station-value ${empty((station as any).method || station.type) === 'нет данных' ? 'station-value empty' : ''}`}>{empty((station as any).method || station.type)}</div>
        </div>

        <div className="station-field">
          <div className="station-label">Текущий статус</div>
          <div className={`station-value ${empty((station as any).status) === 'нет данных' ? 'station-value empty' : ''}`}>{empty((station as any).status)}</div>
        </div>

        <div className="station-field">
          <div className="station-label">Дата основания</div>
          <div className={`station-value ${empty((station as any).start_year) === 'нет данных' ? 'station-value empty' : ''}`}>{empty((station as any).start_year)}</div>
        </div>

        <div className="station-field">
          <div className="station-label">Организация / Основатель</div>
          <div className={`station-value ${empty((station as any).organization || station.source) === 'нет данных' ? 'station-value empty' : ''}`}>{empty((station as any).organization || station.source)}</div>
        </div>

        <div className="station-field long">
          <div className="station-label">История аппаратурных комплексов</div>
          <div className={`station-value ${empty((station as any).history) === 'нет данных' ? 'station-value empty' : ''}`}>{empty((station as any).history)}</div>
        </div>

        <div className="station-field long">
          <div className="station-label">Действующий комплекс</div>
          <div className={`station-value ${empty((station as any).equipment) === 'нет данных' ? 'station-value empty' : ''}`}>{empty((station as any).equipment)}</div>
        </div>
      </div>
    </div>
  )
}
