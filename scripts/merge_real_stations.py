#!/usr/bin/env python3
"""
Merge multiple station lists into a single cleaned JSON file.

Usage examples:
  python scripts/merge_real_stations.py \
    --giro path/to/giro.csv \
    --didbase https://example.com/didbase.csv \
    --manual path/to/manual.json

By default writes to `backend/app/data/stations.json` (backup is created).
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
import unicodedata
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.request import urlopen

OUT_PATH = os.path.join('backend', 'app', 'data', 'stations.json')


def read_text(path_or_url: str) -> str:
    if re.match(r'^https?://', path_or_url):
        with urlopen(path_or_url) as r:
            return r.read().decode('utf-8')
    else:
        with open(path_or_url, 'r', encoding='utf-8') as f:
            return f.read()


def load_json(content: str) -> List[Dict[str, Any]]:
    data = json.loads(content)
    if isinstance(data, list):
        return data
    # try find array under a key
    if isinstance(data, dict):
        for v in data.values():
            if isinstance(v, list):
                return v
    raise ValueError('JSON does not contain an array of stations')


def sniff_csv(content: str) -> List[Dict[str, str]]:
    # Try to parse CSV with header
    reader = csv.DictReader(content.splitlines())
    return list(reader)


def parse_any(path_or_url: str) -> List[Dict[str, Any]]:
    text = read_text(path_or_url)
    text_strip = text.lstrip()
    if text_strip.startswith('[') or text_strip.startswith('{'):
        try:
            return load_json(text)
        except Exception:
            pass
    # Fallback to CSV
    try:
        rows = sniff_csv(text)
        return [dict(r) for r in rows]
    except Exception:
        raise


def safe_float(v: Any) -> Optional[float]:
    try:
        if v is None or v == '':
            return None
        return float(v)
    except Exception:
        return None


def slugify(s: str) -> str:
    s = s.lower()
    s = unicodedata.normalize('NFKD', s)
    s = s.encode('ascii', 'ignore').decode('ascii')
    s = re.sub(r'[^a-z0-9]+', '_', s).strip('_')
    return s or 'station'


COUNTRY_MAP = {
    'usa': 'США',
    'us': 'США',
    'united states': 'США',
    'russia': 'Россия',
    'russian federation': 'Россия',
    'uk': 'Великобритания',
    'united kingdom': 'Великобритания',
    'england': 'Великобритания',
    'germany': 'Германия',
    'france': 'Франция',
    'china': 'Китай',
    'japan': 'Япония',
    'south korea': 'Южная Корея',
    'korea': 'Южная Корея',
    'australia': 'Австралия',
    'new zealand': 'Новая Зеландия',
    'italy': 'Италия',
    'spain': 'Испания',
    'brazil': 'Бразилия',
    'canada': 'Канада',
    'peru': 'Перу',
    'argentina': 'Аргентина',
    'mexico': 'Мексика',
    'india': 'Индия',
    'kazakhstan': 'Казахстан',
    'sweden': 'Швеция',
    'finland': 'Финляндия',
    'norway': 'Норвегия',
    'iceland': 'Исландия',
    'south africa': 'ЮАР',
    'united arab emirates': 'ОАЭ',
    'uae': 'ОАЭ',
}

TYPE_MAP = {
    'ionosonde': 'Ионозонд',
    'ionospheric sounder': 'Ионозонд',
    'radar': 'Радар',
    'incoherent scatter radar': 'Радар нелинейного рассеяния',
    'gnss': 'GNSS',
    'gps': 'GNSS',
}


def normalize_country(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    n = name.strip()
    # if already in Cyrillic, return as-is
    if re.search(r'[\u0400-\u04FF]', n):
        return n
    key = n.lower()
    key = re.sub(r"\s+\(.+\)", '', key).strip()
    key = key.replace('.', '').strip()
    return COUNTRY_MAP.get(key, n)


def normalize_type(tp: Optional[str]) -> Optional[str]:
    if not tp:
        return None
    t = tp.strip()
    if re.search(r'[\u0400-\u04FF]', t):
        return t
    key = t.lower()
    key = key.replace('-', ' ').strip()
    return TYPE_MAP.get(key, t)


def extract_fields(raw: Dict[str, Any]) -> Dict[str, Any]:
    # Common field names we accept
    candidates = {k.lower(): v for k, v in raw.items()}
    def pick(*names):
        for n in names:
            if n in candidates and candidates[n] not in (None, ''):
                return candidates[n]
        return None

    name = pick('name', 'station', 'station_name')
    country = pick('country', 'country_name')
    lat = safe_float(pick('lat', 'latitude', 'φ', 'y'))
    lon = safe_float(pick('lon', 'longitude', 'λ', 'x'))
    stype = pick('type', 'station_type')
    source = pick('source', 'data_source', 'origin') or ''
    desc = pick('description', 'info', 'note') or ''
    sid = pick('id', 'station_id')

    if sid is None and name:
        sid = slugify(str(name))

    return {
        'id': str(sid) if sid is not None else slugify(name or 'station'),
        'name': name or '',
        'country': normalize_country(country) or '',
        'latitude': lat,
        'longitude': lon,
        'type': normalize_type(stype) or '',
        'source': source,
        'description': desc,
        'status': raw.get('status') or 'active',
    }


def same_coord(a: Optional[float], b: Optional[float], tol: float = 1e-3) -> bool:
    if a is None or b is None:
        return False
    return abs(a - b) <= tol


def merge_records(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    # Prefer filled values, keep lat/lon from existing if present
    out = a.copy()
    for k in ['name', 'country', 'type', 'source', 'description', 'status']:
        if (not out.get(k)) and b.get(k):
            out[k] = b[k]
    # merge coordinates (prefer non-null)
    if out.get('latitude') is None and b.get('latitude') is not None:
        out['latitude'] = b['latitude']
    if out.get('longitude') is None and b.get('longitude') is not None:
        out['longitude'] = b['longitude']
    # keep id as the first one's id
    return out


def dedupe_and_merge(records: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen_names: Dict[str, int] = {}

    for r in records:
        rec = extract_fields(r)
        # ignore records without coords
        if rec['latitude'] is None or rec['longitude'] is None:
            # still keep if have name and other fields
            pass

        # check duplicates by name
        name_key = rec['name'].strip().lower() if rec['name'] else ''
        found_idx: Optional[int] = None

        if name_key:
            if name_key in seen_names:
                found_idx = seen_names[name_key]

        # check by coordinates if not found by name
        if found_idx is None and rec['latitude'] is not None and rec['longitude'] is not None:
            for i, existing in enumerate(out):
                if same_coord(rec['latitude'], existing.get('latitude')) and same_coord(rec['longitude'], existing.get('longitude')):
                    found_idx = i
                    break

        if found_idx is not None:
            merged = merge_records(out[found_idx], rec)
            out[found_idx] = merged
            if name_key:
                seen_names[name_key] = found_idx
        else:
            seen_names[name_key] = len(out)
            out.append(rec)

    return out


def load_inputs(paths: List[str]) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for p in paths:
        try:
            recs = parse_any(p)
            records.extend(recs)
            print(f'Loaded {len(recs)} records from {p}')
        except Exception as e:
            print(f'Warning: failed to parse {p}: {e}', file=sys.stderr)
    return records


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', help='Existing stations.json', default=OUT_PATH)
    ap.add_argument('--giro', nargs='*', help='GIRO file(s) or URL(s)')
    ap.add_argument('--didbase', nargs='*', help='DIDBase file(s) or URL(s)')
    ap.add_argument('--manual', nargs='*', help='Manual file(s)')
    ap.add_argument('--extra', nargs='*', help='Any additional files or URLs')
    ap.add_argument('--out', help='Output path', default=OUT_PATH)
    ap.add_argument('--backup', action='store_true', help='Backup existing output')
    args = ap.parse_args(argv)

    inputs: List[str] = []
    # base is also included as first source
    if args.base and os.path.exists(args.base):
        inputs.append(args.base)

    for k in ('giro', 'didbase', 'manual', 'extra'):
        seq = getattr(args, k)
        if seq:
            inputs.extend(seq)

    if not inputs:
        print('No input files provided. At least a base file or other sources required.', file=sys.stderr)
        return 2

    records = load_inputs(inputs)

    merged = dedupe_and_merge(records)

    print(f'Merged -> {len(merged)} unique stations')

    out_path = args.out
    if args.backup and os.path.exists(out_path):
        bak = out_path + '.bak'
        os.replace(out_path, bak)
        print(f'Backed up existing {out_path} -> {bak}')

    # ensure all records have the required schema and types
    final: List[Dict[str, Any]] = []
    for r in merged:
        final.append({
            'id': str(r.get('id') or slugify(r.get('name') or 'station')),
            'name': r.get('name') or '',
            'country': r.get('country') or '',
            'latitude': None if r.get('latitude') is None else float(r.get('latitude')),
            'longitude': None if r.get('longitude') is None else float(r.get('longitude')),
            'type': r.get('type') or '',
            'source': r.get('source') or '',
            'description': r.get('description') or '',
            'status': r.get('status') or 'active',
        })

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    print(f'Wrote merged stations to {out_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
