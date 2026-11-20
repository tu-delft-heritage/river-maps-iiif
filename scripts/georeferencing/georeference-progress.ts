import { createHash } from 'node:crypto';
import { mkdir, readFile, readdir, writeFile, copyFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { isDeepStrictEqual } from 'node:util';
import { html } from 'htm/preact';
import { render } from 'preact-render-to-string';
import { annotationForMap, type CanonicalMap } from './georeference-export.ts';
import { components, type ArchiveSnapshot } from '../nationaal-archief.ts';
import { shapeDiagnostics, shapeLimits } from './georeference-shape.ts';

const root = fileURLToPath(new URL('../../', import.meta.url));
const relativeData = 'data/georeferencing/nieuwe-stijl';
interface SourceMap { id: string; inventoryNumber: string; title: string; series: string; pilot: boolean; homepage: string; metadata: {label: string; value: string}[] }
interface Selection { sourceSha256: string; records: SourceMap[]; excluded: unknown[] }
interface ReviewGroup {id: string; title: string; description: string; mapIds: string[]; includeShapeFlags?: boolean}
interface ProcessingRecord {
  startedAt: string; completedAt: string | null; elapsedSeconds: number | null;
  commands: {command: string; elapsedSeconds: number; success: boolean}[];
}
export interface Acceptance {
  batchId: string; recordedOn: string; basis: string;
  maps: { id: string; geometrySha256: string }[];
}
export function geometrySnapshot(map: CanonicalMap) {
  return {resourceMask: map.mask.resourceMask, points: map.points.map(p => ({
    id: p.id, role: p.role, resourceCoords: p.resourceCoords, rdNew: p.rdNew,
    geo: p.geo, originalProjected: p.originalProjected
  }))};
}
export function geometryFingerprint(map: CanonicalMap): string {
  return createHash('sha256').update(JSON.stringify(geometrySnapshot(map))).digest('hex');
}
export function visualAcceptance(map: CanonicalMap, events: Acceptance[]) {
  const event = events.findLast(e => e.maps.some(m => m.id === map.id));
  if (!event) return {accepted: false, stale: false};
  const accepted = event.maps.find(m => m.id === map.id)!.geometrySha256 === geometryFingerprint(map);
  return {accepted, stale: !accepted, recordedOn: event.recordedOn};
}
const read = async <T>(path: string): Promise<T> => JSON.parse(await readFile(path, 'utf8'));
async function optional<T>(path: string): Promise<T | undefined> {
  try {return await read<T>(path);} catch(error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') return undefined;
    throw error;
  }
}
export async function progressModel(repo = root) {
  const data = resolve(repo, relativeData);
  const selection = await read<Selection>(resolve(data, 'selection.json'));
  const source = await readFile(resolve(repo, 'data/nationaal-archief/nieuwe-stijl.json'));
  if (createHash('sha256').update(source).digest('hex') !== selection.sourceSha256) throw new Error('Progress source snapshot is stale');
  const archive: ArchiveSnapshot = JSON.parse(source.toString());
  const labels = new Map([...components(archive.edition)].map(c => [c.code, c.title]));
  const events = (await optional<{events: Acceptance[]}>(resolve(data, 'human-reviews.json')))?.events ?? [];
  const known = new Map(selection.records.map(r => [r.id, r]));
  if (known.size !== selection.records.length || selection.records.some(r => r.series === 'D.01')) throw new Error('Duplicate maps or sheet indices in progress scope');
  let names: string[] = [];
  try {names = (await readdir(resolve(data, 'batches'))).filter(n => /^batch-\d{2}$/.test(n)).sort();}
  catch(error) {if ((error as NodeJS.ErrnoException).code !== 'ENOENT') throw error;}
  const definitions = [{id: 'pilot', folder: data, records: selection.records.filter(r => r.pilot)}];
  for (const id of names) {
    const selected = await read<Selection>(resolve(data, 'batches', id, 'selection.json'));
    if (selected.sourceSha256 !== selection.sourceSha256) throw new Error('Stale batch selection: '+id);
    definitions.push({id, folder: resolve(data, 'batches', id), records: selected.records});
  }
  const canonical = new Map<string, CanonicalMap>();
  const membership = new Map<string, string>();
  for (const batch of definitions) {
    const approved = (await optional<{maps: Record<string, unknown>}>(resolve(batch.folder, 'geometry-review.json')))?.maps ?? {};
    for (const record of batch.records) {
    if (!known.has(record.id) || membership.has(record.id)) throw new Error('Unknown or duplicate batch map: '+record.id);
    membership.set(record.id, batch.id);
    const map = await optional<CanonicalMap>(resolve(batch.folder, 'maps', record.id+'.json'));
    if (map) {
      if (map.id !== record.id || map.sourceSha256 !== selection.sourceSha256 || map.source.series !== record.series) throw new Error('Stale canonical map: '+record.id);
      if (map.mask.reviewStatus === 'ai-visually-reviewed' && !map.quality.reasons.includes('geometry-review-required') && isDeepStrictEqual(geometrySnapshot(map), approved[record.id])) canonical.set(record.id, map);
    }
  }
  }
  const maps = selection.records.map(r => {
    const map = canonical.get(r.id);
    const shape = map ? shapeDiagnostics(map.adjustment.linear) : undefined;
    const review = map ? visualAcceptance(map, events) : {accepted: false, stale: false};
    const batchId = membership.get(r.id);
    const checks = (map?.adjustment as (CanonicalMap['adjustment'] & {heldOutChecks?: {errorPixels: number}[]}) | undefined)?.heldOutChecks;
    const status = review.accepted ? 'accepted' : map ? 'prepared' : batchId ? 'queued' : 'unprocessed';
    return {id: r.id, inventory: r.inventoryNumber, title: r.title, series: r.series, batchId,
      date: r.metadata.find(m => m.label === 'Datering')?.value ?? '', homepage: r.homepage,
      status, reviewStale: review.stale, recordedOn: 'recordedOn' in review ? review.recordedOn : undefined,
      flags: [...new Set([...(map?.quality.reasons ?? []),...(shape?.flags ?? [])])], shape, rms: map?.adjustment.rmsPixels,
      check: checks?.length ? Math.max(...checks.map(p => p.errorPixels)) : undefined};
  });
  const counts = (rows: typeof maps) => ({total: rows.length,
    prepared: rows.filter(m => m.status === 'accepted' || m.status === 'prepared').length,
    accepted: rows.filter(m => m.status === 'accepted').length,
    pending: rows.filter(m => m.status === 'prepared').length,
    queued: rows.filter(m => m.status === 'queued').length,
    remaining: rows.filter(m => m.status === 'queued' || m.status === 'unprocessed').length,
    flagged: rows.filter(m => m.flags.length).length});
  const series = [...new Set(maps.map(m => m.series))].map(id => ({id, title: labels.get(id) ?? id,
    ...counts(maps.filter(m => m.series === id)),
    download: maps.some(m => m.series === id && canonical.has(m.id)) ? `annotations/series-${id}.json` : undefined}));
  const batches = await Promise.all(definitions.map(async b => {
    const timing = await optional<ProcessingRecord>(resolve(b.folder, 'processing.json'));
    return {id: b.id, ...counts(maps.filter(m => m.batchId === b.id)),
    processing: timing ? {startedAt: timing.startedAt, completedAt: timing.completedAt,
      elapsedSeconds: timing.elapsedSeconds, commandSeconds: timing.commands.reduce((sum,c) => sum+c.elapsedSeconds,0),
      commandRuns: timing.commands.length, failedCommands: timing.commands.filter(c=>!c.success).length} : null,
    series: [...new Set(b.records.map(r => r.series))].join(', '),
    download: canonical.size && b.records.some(r => canonical.has(r.id)) ? `annotations/${b.id}.json` : undefined};}));
  const next = series.find(s => s.remaining);
  const groups = (await optional<{groups: ReviewGroup[]}>(resolve(data,'review-groups.json')))?.groups ?? [];
  if(new Set(groups.map(g=>g.id)).size!==groups.length) throw new Error('Duplicate review group');
  const rechecks = groups.map(g => {
    if(!/^[a-z0-9-]+$/.test(g.id) || new Set(g.mapIds).size!==g.mapIds.length || g.mapIds.some(id=>!known.has(id)))
      throw new Error('Invalid review group: '+g.id);
    const selected=maps.filter(m=>g.mapIds.includes(m.id)||(g.includeShapeFlags&&m.shape?.flags.length));
    if(selected.some(m=>!canonical.has(m.id))) throw new Error('Review group contains unprepared geometry: '+g.id);
    return {...g,mapIds:selected.map(m=>m.id),...counts(selected),download:`annotations/recheck-${g.id}.json`};
  });
  return {model: {generatedAt: new Date().toISOString(), edition: 'Nieuwe Stijl', ...counts(maps),
    excludedIndices: selection.excluded.length, series, batches, maps, next, rechecks,
    shapeScreen: {tested:maps.filter(m=>m.shape).length,flagged:maps.filter(m=>m.shape?.flags.length).length,
      limits:shapeLimits,limitation:'Checks reflection and directional distortion in the saved RD-to-image fit. Uniform translation, rotation and uniform scale errors require separate label or geographic checks.'},
    policy: 'Process all remaining maps in one archival series per batch, in archival order. Keep numerical flags visible after visual acceptance.'}, canonical};
}
export type Progress = Awaited<ReturnType<typeof progressModel>>['model'];
const duration = (seconds: number | null | undefined) => seconds == null ? 'Not recorded' : seconds < 60 ? `${Math.round(seconds)} s` : seconds < 3600 ? `${(seconds/60).toFixed(1)} min` : `${(seconds/3600).toFixed(2)} h`;
const percent = (n: number, d: number) => (100*n/(d || 1)).toFixed(1);
function ProgressBar({accepted, pending, total}: {accepted: number; pending: number; total: number}) {
  return html`<div class="progress-track" role="img" aria-label=${`${accepted} accepted, ${pending} awaiting review, of ${total} maps`}>
    <span class="accepted" style=${`width:${percent(accepted,total)}%`}></span><span class="pending" style=${`width:${percent(pending,total)}%`}></span>
  </div>`;
}
// Allmaps parses JSON from the fragment; local files need no public URL or fetch.
export function allmapsViewerUrl(annotation: unknown): string {
  const url = new URL('https://viewer.allmaps.org/');
  url.hash = new URLSearchParams({data: JSON.stringify(annotation)}).toString();
  return url.href;
}
export function usableViewerUrl(annotation: unknown): string | undefined {
  const url = allmapsViewerUrl(annotation);
  // Keep embedded links below Chromium's 2 MiB URL limit. Series remain separate.
  return url.length < 2_000_000 ? url : undefined;
}
export function renderProgress(model: Progress, viewerLinks: ReadonlyMap<string, string> = new Map()): string {
  const data = JSON.stringify(model).replaceAll('<', '\\u003c').replaceAll('\u2028', '\\u2028').replaceAll('\u2029', '\\u2029');
  return '<!doctype html>\n'+render(html`<html lang="en"><head>
    <meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
    <title>Nieuwe Stijl · Georeferencing progress</title><link rel="stylesheet" href="assets/progress.css"/>
  </head><body><div class="shell">
    <header class="masthead"><a href="#" class="brand"><span class="brand-icon" aria-hidden="true">≋</span> River maps</a><span>Georeferencing workspace</span><span class="snapshot">Local snapshot · <time datetime=${model.generatedAt}>${model.generatedAt.slice(0,10)}</time></span></header>
    <main><header class="intro"><div><p class="eyebrow">Nationaal Archief · 2.16.5150</p><h1>Nieuwe Stijl progress</h1><p class="subtitle">Digitized river maps, one series at a time.</p></div><div class="intro-actions">${viewerLinks.has('annotations/all-prepared.json') ? html`<a class="button primary" href=${viewerLinks.get('annotations/all-prepared.json')} target="_blank" rel="noopener noreferrer" aria-label="Open all prepared maps in Allmaps Viewer">Open in Allmaps Viewer</a>` : null}<a class="button" href="annotations/all-prepared.json" download>Download prepared maps</a></div></header>
    <section class="overview" aria-label="Overall progress"><div class="overview-title"><div><h2>Collection coverage</h2><p>${model.prepared} of ${model.total} maps prepared · ${model.excludedIndices} sheet indices excluded</p></div><strong>${percent(model.prepared,model.total)}<span>%</span></strong></div>
      <${ProgressBar} accepted=${model.accepted} pending=${model.pending} total=${model.total}/>
      <div class="legend"><span><i class="accepted"></i>Visually accepted</span><span><i class="pending"></i>Awaiting your review</span><span><i class="remaining"></i>Remaining</span></div>
      <div class="metrics"><div><span>Visually accepted</span><strong>${model.accepted}</strong><small>Confirmed by you</small></div><div><span>Awaiting your review</span><strong>${model.pending}</strong><small>Prepared annotations</small></div><div><span>Still to process</span><strong>${model.remaining}</strong><small>${model.queued} selected for a batch</small></div><div><span>Numerical flags</span><strong>${model.flagged}</strong><small>Retained after visual review</small></div></div>
    </section>
    ${model.rechecks.map(g=>html`<section class="next-step" id=${`review-${g.id}`} aria-label=${g.title}><div class="next-label">${g.pending ? 'Follow-up review' : 'Review complete'}</div><div><strong>${g.title}</strong><p>${g.description}</p><p>${g.total} maps · ${g.pending ? `${g.pending} awaiting your review` : 'visually accepted'}</p><div class="batch-actions">${viewerLinks.has(g.download)?html`<a class="button primary" href=${viewerLinks.get(g.download)} target="_blank" rel="noopener noreferrer">${g.pending ? 'Review' : 'View'} ${g.total} maps in Allmaps</a>`:null}<a class="button" href=${g.download} download>Download combined annotation</a><a class="button" href="shape-audit.json" download>Collection shape audit</a></div></div></section>`)}
    <section class="next-step" aria-label="Suggested next series"><div class="next-label">${model.accepted===model.total ? 'Review complete' : 'Suggested next series'}</div><div><strong>${model.next ? `${model.next.id} · ${model.next.title}` : model.accepted===model.total ? 'All series visually accepted' : 'All series prepared'}</strong><p>${model.next ? `${model.next.remaining} maps left to prepare in this series. Each new batch contains all remaining maps in one series.` : model.accepted===model.total ? 'Every eligible map has been accepted in human review. Numerical flags remain available below.' : 'Every eligible map has a prepared annotation. Review any pending batches below.'}</p></div><span class="pill">Series by series</span></section>
    <section aria-labelledby="series-heading"><div class="section-heading"><div><h2 id="series-heading">Series coverage</h2><p>${model.series.length} series · choose a series to inspect its maps</p></div></div>
      <div class="table-wrap"><table class="series-table"><thead><tr><th scope="col">Series</th><th scope="col">Progress</th><th scope="col">Accepted</th><th scope="col">To review</th><th scope="col">Remaining</th><th scope="col">QA flags</th></tr></thead><tbody>
      ${model.series.map(s => html`<tr><td><button class="series-link" data-series=${s.id}><span class="code">${s.id}</span>${s.title}</button>${s.download ? html`<div class="series-actions">${viewerLinks.has(s.download) ? html`<a href=${viewerLinks.get(s.download)} target="_blank" rel="noopener noreferrer" aria-label=${`Open series ${s.id} in Allmaps Viewer`}>View ${s.prepared} maps</a>` : null}<a href=${s.download} download>JSON</a></div>` : null}</td><td><${ProgressBar} accepted=${s.accepted} pending=${s.pending} total=${s.total}/><span class="table-meta">${s.prepared} / ${s.total} prepared</span></td><td>${s.accepted}</td><td>${s.pending || '—'}</td><td>${s.remaining || '—'}</td><td>${s.flagged || '—'}</td></tr>`)}</tbody></table></div>
    </section>
    <section aria-labelledby="batch-heading"><div class="section-heading"><div><h2 id="batch-heading">Review batches</h2><p>Visual acceptance and the numerical screen are tracked separately.</p></div></div><div class="batch-grid">
    ${model.batches.map(b => html`<article class="batch-card"><div class="batch-top"><h3>${b.id === 'pilot' ? '24-scan pilot' : b.id.replace('batch-', 'Batch ')}</h3><span class=${`pill ${b.accepted===b.total ? 'green' : b.prepared===b.total ? 'purple' : ''}`}>${b.accepted===b.total ? 'Visually accepted' : b.prepared===b.total ? 'Ready for review' : 'In preparation'}</span></div><strong class="batch-number">${b.prepared}<small> / ${b.total} maps</small></strong><p>${b.flagged} with numerical flags · ${b.accepted} accepted</p><p class="batch-series">${b.series}</p>${b.download ? html`<div class="batch-actions">${viewerLinks.has(b.download) ? html`<a class="button primary" href=${viewerLinks.get(b.download)} target="_blank" rel="noopener noreferrer" aria-label=${`Open ${b.id} in Allmaps Viewer`}>Open in Allmaps Viewer</a>` : null}<a class="button" href=${b.download} download>Download annotation</a></div>` : html`<span class="muted">Annotation not yet prepared</span>`}</article>`)}</div></section>
    <section aria-labelledby="statistics-heading"><div class="section-heading"><div><h2 id="statistics-heading">Processing statistics</h2><p>Recorded measurements only. Timing starts with Batch 03; earlier runs were not timed.</p></div></div>
      <div class="table-wrap"><table><thead><tr><th>Batch</th><th>Elapsed incl. review</th><th>Measured command time</th></tr></thead><tbody>
      ${model.batches.map(b=>html`<tr><td>${b.id}</td><td>${b.processing && !b.processing.completedAt ? 'Recording…' : duration(b.processing?.elapsedSeconds)}</td><td>${duration(b.processing?.commandSeconds)}${b.processing ? html`<div class="table-meta">${b.processing.commandRuns} runs${b.processing.failedCommands ? ` · ${b.processing.failedCommands} failed` : ''}</div>` : null}</td></tr>`)}</tbody></table></div>
      <p class="statistics-note">Elapsed time runs from batch setup to the first completed export, including preparation, visual review and waits. Command time is the cumulative duration of recorded processing commands, including retries and later replays.</p>
    </section>
    <section id="maps" aria-labelledby="maps-heading"><div class="section-heading"><div><h2 id="maps-heading">Map register</h2><p>Find individual sheets, review state, and adjustment results.</p></div><span id="result-count" class="muted" aria-live="polite"></span></div>
      <div class="filters"><label>Search maps<input id="search" type="search" placeholder="Inventory, sheet, or place…"/></label><label>Series<select id="series-filter"><option value="">All series</option>${model.series.map(s=>html`<option value=${s.id}>${s.id} · ${s.title}</option>`)}</select></label><label>Review state<select id="status-filter"><option value="">All states</option><option value="accepted">Visually accepted</option><option value="prepared">Awaiting review</option><option value="queued">Selected for processing</option><option value="unprocessed">Not started</option></select></label><label class="check-label"><input type="checkbox" id="flagged-only"/>With QA flags</label></div>
      <div class="table-wrap"><table class="map-table"><thead><tr><th>Inventory / map</th><th>Series</th><th>Review state</th><th>Fit RMS</th><th>Check error</th><th>Numerical screen</th></tr></thead><tbody id="map-rows"></tbody></table></div><p id="empty" hidden>No maps match these filters.</p><div class="pagination"><button id="previous" class="button">Previous</button><span id="page-number" aria-live="polite"></span><button id="next" class="button">Next</button></div>
      <noscript><p>Enable JavaScript to filter the map register. Collection and series totals above remain available.</p></noscript>
    </section>
    <footer><p>Visual acceptance records your review of the map placement and mask. Numerical flags remain visible; acceptance does not change the fit or its uncertainty.</p><p>This dashboard uses saved repository data and makes no image-server requests. Rebuild with <code>pnpm georeference:dashboard</code>; processing runs refresh it after export.</p></footer>
    </main></div><script id="progress-data" type="application/json" dangerouslySetInnerHTML=${{__html:data}}></script><script src="assets/progress.js" defer></script></body></html>`)+'\n';
}
export async function buildProgress(repo = root) {
  const {model, canonical} = await progressModel(repo);
  const output = resolve(repo, 'dashboard');
  await mkdir(resolve(output, 'assets'), {recursive: true});
  await mkdir(resolve(output, 'annotations'), {recursive: true});
  const bundle = (id: string, maps: CanonicalMap[]) => ({'@context':'http://www.w3.org/ns/anno.jsonld',
    id:`urn:river-maps:nieuwe-stijl:progress:${id}`,type:'AnnotationPage',label:{en:[`Nieuwe Stijl: ${id} (${maps.length} maps)`]},
    items:maps.map(m => ({...annotationForMap(m), metadata:m.source.metadata,
      seeAlso:[{id:m.batchId ? `../../${relativeData}/batches/${m.batchId}/maps/${m.id}.json` : `../../${relativeData}/maps/${m.id}.json`,type:'Dataset',format:'application/json'}]}))});
  const files = new Map<string, unknown>([['progress.json',model],['annotations/all-prepared.json',bundle('all-prepared',[...canonical.values()])]]);
  files.set('shape-audit.json',{generatedAt:model.generatedAt,...model.shapeScreen,
    maps:model.maps.filter(m=>m.shape).map(m=>({id:m.id,inventory:m.inventory,series:m.series,
      geometrySha256:geometryFingerprint(canonical.get(m.id)!),...m.shape}))});
  for(const group of model.rechecks) files.set(group.download,bundle(group.id,group.mapIds.map(id=>canonical.get(id)!)));
  for(const batch of model.batches) if(batch.download) {
    const maps = model.maps.filter(m=>m.batchId===batch.id).flatMap(m=>canonical.has(m.id)?[canonical.get(m.id)!]:[]);
    files.set(batch.download,bundle(batch.id,maps));
  }
  for(const series of model.series) if(series.download) {
    const maps = model.maps.filter(m=>m.series===series.id).flatMap(m=>canonical.has(m.id)?[canonical.get(m.id)!]:[]);
    files.set(series.download,bundle(series.id,maps));
  }
  for(const [path,value] of files) {await mkdir(dirname(resolve(output,path)),{recursive:true});await writeFile(resolve(output,path),JSON.stringify(value,null,2)+'\n');}
  for(const file of ['progress.css','progress.js']) await copyFile(resolve(repo,'site',file),resolve(output,'assets',file));
  const viewerLinks = new Map<string,string>();
  for(const [path,annotation] of files) if(path.startsWith('annotations/')) {
    const url=usableViewerUrl(annotation);
    if(url)viewerLinks.set(path,url);
  }
  await writeFile(resolve(output,'index.html'),renderProgress(model, viewerLinks));
  console.log(`Dashboard: ${model.prepared}/${model.total} prepared; ${model.accepted} visually accepted; ${model.pending} awaiting review.`);
  return model;
}
if(process.argv[1] && resolve(process.argv[1])===fileURLToPath(import.meta.url)) await buildProgress();
