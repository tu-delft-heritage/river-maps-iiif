(() => {
  'use strict';
  const data = JSON.parse(document.getElementById('progress-data').textContent);
  const byId = id => document.getElementById(id);
  const labels = {accepted:'Visually accepted', prepared:'Awaiting review', queued:'Selected for processing', unprocessed:'Not started'};
  const flagLabels = {'rms-above-2px':'RMS above 2 px','check-above-5px':'Check above 5 px','poor-control-coverage':'Control coverage','ill-conditioned-controls':'Control geometry'};
  let page = 0;
  const size = 25;
  function element(tag, text, className) {
    const node = document.createElement(tag);
    if (text != null) node.textContent = text;
    if (className) node.className = className;
    return node;
  }
  function update() {
    const query = byId('search').value.trim().toLocaleLowerCase();
    const series = byId('series-filter').value, status = byId('status-filter').value;
    const rows = data.maps.filter(m => (!series || m.series === series) && (!status || m.status === status)
      && (!byId('flagged-only').checked || m.flags.length)
      && (!query || `${m.inventory} ${m.title} ${m.date} ${m.series}`.toLocaleLowerCase().includes(query)));
    const pages = Math.max(1,Math.ceil(rows.length/size));
    page = Math.min(page,pages-1);
    const fragment = document.createDocumentFragment();
    for (const m of rows.slice(page*size,(page+1)*size)) {
      const row = element('tr'), title = element('td');
      const link = element('a',m.inventory,'inventory-link');
      if (/^https?:\/\//.test(m.homepage ?? '')) {link.href=m.homepage;link.target='_blank';link.rel='noopener noreferrer';}
      title.append(link,element('div',m.title,'map-title'));
      if (m.date) title.append(element('div',m.date,'table-meta'));
      const state = element('td');
      state.append(element('span',labels[m.status],`pill ${m.status==='accepted'?'green':m.status==='prepared'?'purple':''}`));
      if (m.reviewStale) state.append(element('small','Geometry changed; review again','review-stale'));
      const qa = element('td');
      if (m.flags.length) for (const flag of m.flags) qa.append(element('div',flagLabels[flag]??flag,'flag-text'));
      else qa.append(element('span',m.rms==null?'—':'Pass',m.rms==null?'muted':'pass-text'));
      row.append(title,element('td',m.series),state,element('td',m.rms==null?'—':m.rms.toFixed(2)+' px','number'),element('td',m.check==null?'—':m.check.toFixed(2)+' px','number'),qa);
      fragment.append(row);
    }
    byId('map-rows').replaceChildren(fragment);
    byId('result-count').textContent=`${rows.length} ${rows.length===1?'map':'maps'}`;
    byId('page-number').textContent=rows.length?`${page*size+1}–${Math.min((page+1)*size,rows.length)} of ${rows.length}`:'0 maps';
    byId('empty').hidden=rows.length!==0;
    byId('previous').disabled=page===0;byId('next').disabled=page>=pages-1;
  }
  for (const id of ['search','series-filter','status-filter','flagged-only']) byId(id).addEventListener('input',()=>{page=0;update();});
  byId('previous').addEventListener('click',()=>{page--;update();});
  byId('next').addEventListener('click',()=>{page++;update();});
  for (const button of document.querySelectorAll('[data-series]')) button.addEventListener('click',()=>{
    byId('series-filter').value=button.dataset.series;byId('search').value='';byId('status-filter').value='';byId('flagged-only').checked=false;page=0;update();
    byId('maps').scrollIntoView({behavior:'smooth'});byId('series-filter').focus({preventScroll:true});
  });
  update();
})();
