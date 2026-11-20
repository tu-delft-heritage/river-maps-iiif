"""Measured CLI durations; model token accounting is deliberately unavailable."""
from contextlib import contextmanager
from datetime import datetime,timezone
from time import perf_counter
from .batch import batch_dir
from .catalog import read,save

@contextmanager
def record_command(batch,command):
    start=datetime.now(timezone.utc).isoformat();clock=perf_counter();success=False
    try:
        yield
        success=True
    finally:
        path=batch_dir(batch)/'processing.json'
        value=read(path) if path.exists() else {'schemaVersion':1,'batchId':batch,'startedAt':start,'completedAt':None,'elapsedSeconds':None,'timingBasis':'Recorded wall-clock interval including preparation, review and waits; not CPU or model latency.','commands':[]}
        value['commands'].append({'command':command,'startedAt':start,'completedAt':datetime.now(timezone.utc).isoformat(),'elapsedSeconds':perf_counter()-clock,'success':success})
        save(path,value)
