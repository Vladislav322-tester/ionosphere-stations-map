#!/usr/bin/env python3
"""Convert stations_raw.txt into backend JSON and Excel output."""
from __future__ import annotations

import csv
import json
import os
import sys
from collections import Counter
from typing import Any, Dict, List, Optional

RAW_PATH = 'stations_raw.txt'
JSON_PATH = os.path.join('backend', 'app', 'data', 'stations.json')
OUT_DIR = os.path.join('output')
OUT_FILE = os.path.join(OUT_DIR, 'ionospheric_stations_world.xlsx')

HEADERS = [
    'Название (URSI)',
    'Код URSI',
    'Широта (градусы)',
    'Долгота (градусы)',
    'Интервал данных',
    'Метод зондирования',
    'Текущий статус',
    'Дата основания',
    'Организация / Основатель',
    'История аппаратурных комплексов',
    'Действующий комплекс',
    'Диапазон рабочих частот',
]


def normalize_code(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text.upper()


def make_id(name: str, code: str) -> str:
    import re
    base = f"{name}_{code}"
    base = base.lower()
    # replace non-alphanumeric with underscore
    base = re.sub(r"[^a-z0-9]+", "_", base)
    base = base.strip("_")
    return base


def parse_line(fields: List[str]) -> Optional[Dict[str, Any]]:
    if not fields:
        return None

    # Remove BOM or whitespace around fields
    fields = [f.strip() for f in fields]
    # Expected columns (13): №;Название;Код;Широта;Долгота;Интервал данных;Метод;Статус;Дата основания;организация;история;комплекс;частоты
    if len(fields) < 13:
        return None

    # Map by position
    # allow first column to be index
    _, name, code, lat, lon, data_interval, method, status_raw, start_year, organization, history, equipment, frequency_range = fields[:13]

    code = normalize_code(code)
    if not code:
        return None

    # parse coords
    try:
        latitude = float(lat)
        longitude = float(lon)
    except ValueError:
        return None

    if not name:
        return None

    # normalize status
    st = status_raw or ''
    st_low = st.lower()
    if 'действ' in st_low:
        status = 'Активна'
    elif 'закрыт' in st_low:
        status = 'Закрыта'
    else:
        status = st if st.strip() != '' else 'нет данных'

    station_id = make_id(name, code)

    return {
        'id': station_id,
        'name': name,
        'code': code,
        'latitude': latitude,
        'longitude': longitude,
        'data_interval': data_interval or 'нет данных',
        'method': method or 'нет данных',
        'status': status,
        'start_year': start_year or 'нет данных',
        'organization': organization or 'нет данных',
        'history': history or 'нет данных',
        'equipment': equipment or 'нет данных',
        'frequency_range': frequency_range or 'нет данных',
        'type': 'нет данных',
        'source': 'stations_raw.txt',
        'description': 'нет данных',
    }


def load_raw(path: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not os.path.exists(path):
        raise FileNotFoundError(f'Raw source not found: {path}')

    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(';')
            if parts[0].startswith('№') or parts[0].lower().startswith('no'):
                continue
            parsed = parse_line(parts)
            if parsed is not None:
                rows.append(parsed)
    return rows


def build_rows(stations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    rows: List[Dict[str, Any]] = []
    for s in stations:
        ursi = s.get('code') or s.get('id') or ''
        key = ursi.strip().upper()
        if not key or key in seen:
            continue
        seen.add(key)
        rows.append(
            {
                'Название (URSI)': s.get('name', 'нет данных'),
                'Код URSI': s.get('code', 'нет данных'),
                'Широта (градусы)': s.get('latitude', 'нет данных'),
                'Долгота (градусы)': s.get('longitude', 'нет данных'),
                'Интервал данных': s.get('data_interval') or s.get('period') or 'нет данных',
                'Метод зондирования': s.get('method', 'нет данных'),
                'Текущий статус': s.get('status', 'нет данных'),
                'Дата основания': s.get('start_year', 'нет данных'),
                'Организация / Основатель': s.get('organization', 'нет данных'),
                'История аппаратурных комплексов': s.get('history', 'нет данных'),
                'Действующий комплекс': s.get('equipment', 'нет данных'),
                'Диапазон рабочих частот': s.get('frequency_range', 'нет данных'),
            }
        )
    return rows


def write_json(stations: List[Dict[str, Any]], path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(stations, f, ensure_ascii=False, indent=2)
    print(f'Wrote JSON to {path}')


def write_excel(rows: List[Dict[str, Any]], stations: List[Dict[str, Any]], path: str):
    try:
        from openpyxl import Workbook
    except ImportError:
        print('openpyxl not installed. Install with: pip install openpyxl', file=sys.stderr)
        raise

    wb = Workbook()
    ws = wb.active
    ws.title = 'Станции'
    ws.append(HEADERS)
    for row in rows:
        ws.append([row[h] for h in HEADERS])

    ws2 = wb.create_sheet('Источники')
    sources = [s.get('source') or 'нет данных' for s in stations]
    counts = Counter(sources)
    ws2.append(['Источник', 'Количество записей', 'Примечание'])
    for source, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        note = '' if source and source != 'нет данных' else 'нет данных'
        ws2.append([source, count, note])

    os.makedirs(os.path.dirname(path), exist_ok=True)
    wb.save(path)
    print(f'Wrote Excel to {path}')


def main():
    stations = load_raw(RAW_PATH)

    # Deduplicate by URSI code (keep first occurrence)
    seen = set()
    unique = []
    for s in stations:
        code = (s.get('code') or '').strip().upper()
        if not code:
            continue
        if code in seen:
            continue
        seen.add(code)
        # Ensure required keys exist
        for k in ['name','code','latitude','longitude','data_interval','method','status','start_year','organization','history','equipment','frequency_range','type','source','description','id']:
            if k not in s:
                s[k] = 'нет данных'
        unique.append(s)

    rows = build_rows(unique)
    write_json(unique, JSON_PATH)
    write_excel(rows, unique, OUT_FILE)


if __name__ == '__main__':
    main()
