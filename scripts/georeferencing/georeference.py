#!/usr/bin/env python3
import argparse
from georeference.catalog import CACHE, DATA, pilot_records, read, save, select
from georeference.acquire import ImageCache, overview_request


def main():
    parser = argparse.ArgumentParser(description='RD-grid georeferencing pilot')
    parser.add_argument('command', choices=['select', 'overviews', 'prepare', 'pilot', 'hydrate', 'ties', 'ocr'])
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--inventory', nargs='+')
    parser.add_argument('--fetch', action='store_true', help='Allow hydrate to retrieve missing evidence; default is offline')
    args = parser.parse_args()
    if args.command == 'select':
        selection = select()
        print(f"Selected {len(selection['records'])} maps; {len(selection['pilotInventoryNumbers'])} pilot scans")
        return
    if args.command == 'hydrate':
        from georeference.evidence import hydrate
        hydrate(offline=not args.fetch)
        return
    if args.command == 'prepare':
        from georeference.prepare import prepare
        prepare(args.offline,args.inventory)
        return
    if args.command == 'ties':
        from georeference.ties import prepare_ties
        prepare_ties(args.offline)
        return
    if args.command == 'ocr':
        from georeference.ocr import propose_ocr
        propose_ocr()
        return
    if args.command == 'pilot':
        from georeference.evidence import hydrate
        from georeference.pilot import run_pilot
        hydrate(offline=True)
        run_pilot()
        return
    cache = ImageCache(offline=args.offline)
    records = pilot_records()
    if args.inventory:
        records = [r for r in records if r['inventoryNumber'] in args.inventory]
    for record in records:
        url, region = overview_request(record)
        evidence, path = cache.get(record, url, region, 'overview')
        save(CACHE / 'work' / record['inventoryNumber'] / 'overview.json', evidence)
        print(record['inventoryNumber'], path, flush=True)
    print(f'Network requests: {cache.network_requests}; cache hits: {cache.cache_hits}')


if __name__ == '__main__':
    main()
