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
    'Широта',
    'Долгота',
    'Интервал работы',
    'Метод зондирования',
    'Текущий статус',
    'Дата основания',
    'Организация / Основатель',
    'История аппаратурных комплексов',
    'Действующий комплекс',
]


def normalize_code(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text.upper()


def parse_line(fields: List[str]) -> Optional[Dict[str, Any]]:
    if not fields:
        return None

    # Remove BOM or whitespace around fields
    fields = [f.strip() for f in fields]
    fields = [f for f in fields if f != ''] if len(fields) == 1 and fields[0] == '' else fields
    if len(fields) < 5:
        return None

    # Expected data rows are either [№, name, code, lat, lon, status]
    # or may lack the row number: [name, code, lat, lon, status]
    if len(fields) == 6:
        _, name, code, lat, lon, status = fields
    elif len(fields) == 5:
        name, code, lat, lon, status = fields
    else:
        # Handle malformed row with empty first cell
        if fields[0] == '' and len(fields) >= 6:
            _, name, code, lat, lon, status = fields[:6]
        else:
            # Try to recover from extra separators by taking the last 4 columns as lat/lon/status/code
            name = fields[1] if fields[0].isdigit() else fields[0]
            code = fields[2] if fields[0].isdigit() else fields[1]
            lat = fields[-3]
            lon = fields[-2]
            status = fields[-1]

    code = normalize_code(code)
    if not code:
        return None

    try:
        latitude = float(lat)
        longitude = float(lon)
    except ValueError:
        return None

    if not name:
        return None

    return {
        'id': code.lower(),
        'name': name,
        'country': 'нет данных',
        'latitude': latitude,
        'longitude': longitude,
        'type': 'нет данных',
        'source': 'stations_raw.txt',
        'description': 'нет данных',
        'code': code,
        'period': 'нет данных',
        'method': 'ВЗ',
        'status': status if status else 'нет данных',
        'start_year': 'нет данных',
        'organization': 'нет данных',
        'history': 'нет данных',
        'equipment': 'нет данных',
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
                'Широта': s.get('latitude', 'нет данных'),
                'Долгота': s.get('longitude', 'нет данных'),
                'Интервал работы': s.get('period', 'нет данных'),
                'Метод зондирования': s.get('method', 'нет данных'),
                'Текущий статус': s.get('status', 'нет данных'),
                'Дата основания': s.get('start_year', 'нет данных'),
                'Организация / Основатель': s.get('organization', 'нет данных'),
                'История аппаратурных комплексов': s.get('history', 'нет данных'),
                'Действующий комплекс': s.get('equipment', 'нет данных'),
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
    rows = build_rows(stations)
    write_json(stations, JSON_PATH)
    write_excel(rows, stations, OUT_FILE)


if __name__ == '__main__':
    main()
