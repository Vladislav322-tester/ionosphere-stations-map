#!/usr/bin/env python3
"""
Build an Excel file `output/ionospheric_stations_world.xlsx` from
`backend/app/data/stations.json` and other optional inputs.

Behavior:
- Reads `backend/app/data/stations.json` by default.
- Produces an .xlsx file with a sheet containing the requested columns
  (Russian headers) and a second sheet `Источники` listing unique sources.
- Removes duplicates by URSI code (uses `id` field as URSI code).
- Does NOT invent data; missing fields are written as "нет данных".

Usage:
  python scripts/build_ionospheric_stations_excel.py

If `openpyxl` is missing the script prints an install hint and exits.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter
from typing import Any, Dict, List


OUT_DIR = os.path.join('output')
OUT_FILE = os.path.join(OUT_DIR, 'ionospheric_stations_world.xlsx')
SRC_JSON = os.path.join('backend', 'app', 'data', 'stations.json')


def load_stations(path: str) -> List[Dict[str, Any]]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def safe(v: Any) -> str:
    if v is None:
        return 'нет данных'
    if isinstance(v, str) and v.strip() == '':
        return 'нет данных'
    return v


def build_rows(stations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Deduplicate by URSI code (id). Keep first occurrence.
    seen = {}
    rows = []
    for s in stations:
        ursi = s.get('id') or ''
        key = ursi.strip()
        if key:
            if key in seen:
                continue
            seen[key] = True

        row = {
            'Название (URSI)': safe(s.get('name')) if s.get('name') else 'нет данных',
            'Код URSI': safe(ursi) if ursi else 'нет данных',
            'Широта (градусы)': s.get('latitude') if s.get('latitude') is not None else 'нет данных',
            'Долгота (градусы)': s.get('longitude') if s.get('longitude') is not None else 'нет данных',
            'Интервал работы': s.get('period') or s.get('work_interval') or s.get('interval') or 'нет данных',
            'Метод зондирования': s.get('method') or s.get('type') or 'нет данных',
            'Текущий статус': s.get('status') or 'нет данных',
            'Дата основания': s.get('start_year') or s.get('founded') or s.get('established') or 'нет данных',
            'Организация / Основатель': s.get('organization') or s.get('source') or 'нет данных',
            'История аппаратурных комплексов': s.get('history') or 'нет данных',
            'Действующий комплекс': s.get('equipment') or s.get('current_equipment') or 'нет данных',
        }
        rows.append(row)
    return rows


def write_excel(rows: List[Dict[str, Any]], stations: List[Dict[str, Any]]):
    try:
        from openpyxl import Workbook
    except Exception:
        print('openpyxl not installed. Install with: pip install openpyxl', file=sys.stderr)
        sys.exit(1)

    wb = Workbook()
    ws = wb.active
    ws.title = 'Станции'

    headers = [
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

    ws.append(headers)
    for r in rows:
        row = [r[h] for h in headers]
        ws.append(row)

    # Second sheet: Источники
    ws2 = wb.create_sheet('Источники')
    sources = [s.get('source') or 'нет данных' for s in stations]
    cnt = Counter(sources)
    ws2.append(['Источник', 'Количество записей', 'Примечание'])
    for src, c in sorted(cnt.items(), key=lambda x: (-x[1], x[0])):
        note = '' if src and src != 'нет данных' else 'нет данных'
        ws2.append([src, c, note])

    os.makedirs(OUT_DIR, exist_ok=True)
    wb.save(OUT_FILE)
    print(f'Wrote Excel to {OUT_FILE}')


def main(argv=None):
    if not os.path.exists(SRC_JSON):
        print(f'Source JSON not found: {SRC_JSON}', file=sys.stderr)
        sys.exit(2)

    stations = load_stations(SRC_JSON)
    rows = build_rows(stations)
    write_excel(rows, stations)


if __name__ == '__main__':
    main()
