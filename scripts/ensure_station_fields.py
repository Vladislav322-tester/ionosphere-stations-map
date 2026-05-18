#!/usr/bin/env python3
"""Ensure every station in backend/app/data/stations.json has the required fields.

Adds missing keys with "нет данных" or preserves existing values.
"""
import json
import os
from typing import Any, Dict

PATH = os.path.join('backend', 'app', 'data', 'stations.json')

REQUIRED = ['code', 'period', 'method', 'status', 'start_year', 'organization', 'history', 'equipment']


def ensure(obj: Dict[str, Any]) -> Dict[str, Any]:
    for k in REQUIRED:
        if k not in obj or obj.get(k) is None or (isinstance(obj.get(k), str) and obj.get(k).strip() == ''):
            obj[k] = 'нет данных'
    return obj


def main():
    if not os.path.exists(PATH):
        print('stations.json not found at', PATH)
        return 2
    with open(PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    changed = False
    for i, s in enumerate(data):
        before = dict(s)
        data[i] = ensure(s)
        if data[i] != before:
            changed = True

    if changed:
        with open(PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print('Updated', PATH)
    else:
        print('No changes needed')


if __name__ == '__main__':
    raise SystemExit(main())
