#!/usr/bin/env python3
"""Resumable follow-on batches. Keeps pilot records and release decisions unchanged."""
import argparse
from georeference.batch import select_batch, acquire_batch, hydrate_batch

parser=argparse.ArgumentParser()
parser.add_argument('command',choices=['select','acquire','hydrate','propose','packs','measure'])
parser.add_argument('--batch',default='batch-01')
parser.add_argument('--offline',action='store_true')
parser.add_argument('--inventory',nargs='+')
parser.add_argument('--series',help='Limit a new selection to one archival series, e.g. D.02')
parser.add_argument('--limit',type=int,help='Optional legacy size limit (1–50); default processes the complete remaining series')
args=parser.parse_args()
from georeference.timing import record_command
with record_command(args.batch,args.command):
    if args.command=='select':select_batch(args.batch,args.series,args.limit)
    elif args.command=='acquire':acquire_batch(args.batch,args.offline,args.inventory)
    elif args.command=='hydrate':hydrate_batch(args.batch,args.offline)
    elif args.command=='propose':
        from georeference.registration import propose
        propose(args.batch)
    elif args.command=='packs':
        from georeference.batch_review import packs
        packs(args.batch)
    else:
        from georeference.batch_measure import measure_batch
        measure_batch(args.batch)
