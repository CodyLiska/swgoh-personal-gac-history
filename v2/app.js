const $ = (s) => document.querySelector(s);
const state = {
  view: 'overview', data: {rounds:[],event_files:0,errors:[]}, units:{}, battles:[],
  status:{state:'idle',lines:[]}, page:1, expanded:null, selectedEnemy:'',
  filters:{query:'',mode:'all',type:'all',outcome:'all',season:'all'},
  counters:{query:'',mode:'all',match:'leader'}, lastStatus:'idle'
};
const fmt = new Intl.NumberFormat();
function esc(v){ return String(v == null ? '' : v).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function n(v){ return fmt.format(v || 0); }
function date(v){ if(!v) return 'Date unavailable'; const d = new Date(v); return Number.isNaN(+d) ? 'Date unavailable' : d.toLocaleDateString(undefined,{year:'numeric',month:'short',day:'numeric'}); }
function shortDate(v){ if(!v) return '—'; const d = new Date(v); return Number.isNaN(+d) ? '—' : d.toLocaleDateString(undefined,{month:'short',day:'numeric',year:'numeric'}); }
function pct(a,b){ return b ? Math.round(a/b*100) : 0; }
function modeOf(b){ const size=Math.max((b.defender_chars||[]).length,(b.attacker_chars||[]).length); return size<=3?'3v3':size===5?'5v5':size>=6?'Fleet':'Other'; }
function unit(id){ return state.units[id] || (id ? id.replace(/_/g,' ').replace(/([a-z])([A-Z])/g,'$1 $2') : 'Unknown'); }
function names(ids){ return (ids||[]).map(id => '<span class="chip">'+esc(unit(id))+'</span>').join('') || '<span class="muted">No units recorded</span>'; }
function rate(b){ const wins=b.filter(x=>x.outcome==='Win').length; return pct(wins,b.length); }
function labelType(b){ return b.battle_type==='your_attack'?'Your attack':'Opponent attack'; }
function titleRound(r){ return (r.season_number ? 'Season '+r.season_number+' · ' : '')+'Round '+(r.round_number||'?'); }
function roundDate(r){ return r.date || (r.battles||[]).map(b=>b.date).filter(Boolean).sort().at(-1) || null; }
function decorate(data){
  const rows=[];
  for(const r of data.rounds||[]) for(const b of r.battles||[]) rows.push(Object.assign({},b,{
    event_id:r.event_id,round_number:r.round_number,season_number:r.season_number,
    event_type:r.event_type,round_id:r._id,round_date:roundDate(r),matchup:r.matchup,
    mode:modeOf(b)
  }));
  rows.sort((a,b)=>(b.date||b.round_date||'').localeCompare(a.date||a.round_date||''));
  state.battles=rows;
}
function api(path,options){ return fetch(path,options).then(async r=>{const data=await r.json(); if(!r.ok) throw Error(data.error||('Request failed: '+r.status)); return data;}); }
async function loadData(){
  try{
    const [data,units]=await Promise.all([api('/api/history'),api('/api/units')]);
    state.data=data;state.units=units;decorate(data);
    $('#notice').hidden = !(data.errors||[]).length;
    if(data.errors.length) $('#notice').textContent='Some archive files could not be read: '+data.errors.join(' · ');
    updateChrome();render();
  }catch(e){ showNotice('Could not read local history: '+e.message); }
}
function showNotice(message){ $('#notice').hidden=false;$('#notice').textContent=message; }
function updateChrome(){
  $('#side-records').textContent=n(state.battles.length)+' battles';
  $('#side-updated').textContent=state.data.updated_at?'Updated '+date(state.data.updated_at):'No captured files yet';
  const busy=['running','stopping'].includes(state.status.state);
  $('#side-pulse').hidden=!busy;
  $('#global-status').innerHTML='<span class="status-dot '+(busy?'busy':state.status.state==='failed'?'fail':'')+'"></span>'+esc(busy?'Capture in progress':state.status.state==='failed'?'Capture needs attention':'Archive ready');
  $('#page-crumb').textContent=({overview:'OVERVIEW',history:'BATTLE HISTORY',counters:'COUNTER LAB',capture:'CAPTURE DATA'})[state.view];
  document.querySelectorAll('.nav-item').forEach(el=>el.classList.toggle('active',el.dataset.view===state.view));
}
function goto(view){ state.view=view; state.expanded=null; updateChrome(); render();window.scrollTo({top:0,behavior:'smooth'}); }
function render(){ const page=$('#page');page.innerHTML=({overview:renderOverview,history:renderHistory,counters:renderCounters,capture:renderCapture})[state.view](); }
function stat(label,value,hint,cls){ return '<div class="stat-card"><div class="label">'+esc(label)+'</div><div class="value '+(cls||'')+'">'+esc(value)+'</div><div class="hint">'+esc(hint)+'</div></div>'; }
function empty(text){ return '<div class="empty">'+esc(text)+'</div>'; }
function renderOverview(){
  const b=state.battles,off=b.filter(x=>x.battle_type==='your_attack'),def=b.filter(x=>x.battle_type==='opponent_attack');
  const wins=off.filter(x=>x.outcome==='Win').length;
  const rounds=[...state.data.rounds].sort((a,b)=>(roundDate(b)||'').localeCompare(roundDate(a)||'')).slice(0,6);
  const leaders=new Map();
  for(const x of off){const key=x.attacker||'Unknown';leaders.set(key,(leaders.get(key)||0)+1);}
  const top=[...leaders].sort((a,b)=>b[1]-a[1]).slice(0,5),max=top[0]?.[1]||1;
  const recent=rounds.map(r=>{
    const attacks=(r.battles||[]).filter(x=>x.battle_type==='your_attack'),w=attacks.filter(x=>x.outcome==='Win').length;
    return '<div class="round-row"><div><div class="round-name">'+esc(titleRound(r))+'</div><div class="round-meta">'+esc(shortDate(roundDate(r)))+(r.matchup?' · '+esc(r.matchup):'')+'</div></div><div class="round-right"><strong>'+n(w)+' / '+n(attacks.length)+'</strong><div class="round-meta">attack wins</div></div></div>';
  }).join('');
  const topRows=top.map(([name,count])=>'<div class="leader-row"><span class="leader-name">'+esc(name)+'</span><div class="bar-track"><span style="width:'+pct(count,max)+'%"></span></div><span class="leader-number">'+n(count)+'</span></div>').join('');
  return '<section class="hero"><div><div class="eyebrow">YOUR GRAND ARENA INTELLIGENCE</div><h1>Every battle tells a story.</h1><p>Explore your past GAC rounds, study the teams that worked, and capture new history from one place.</p></div><div class="hero-action"><div class="hero-stat"><strong>'+n(state.data.event_files)+'</strong> EVENTS ON FILE</div><button class="button button-primary" data-action="capture">◉ &nbsp; Capture latest history</button><small>Refresh your local archive from swgoh.gg</small></div></section>'+
  '<section class="stats">'+stat('Total battles',n(b.length),'Across '+n(state.data.rounds.length)+' rounds')+stat('Attack win rate',pct(wins,off.length)+'%',n(wins)+' wins in '+n(off.length)+' attacks','gold')+stat('Defenses faced',n(def.length),'Opponent attacks recorded')+stat('Events archived',n(state.data.event_files),'Canonical event files')+'</section>'+
  '<section class="two-col"><div class="panel"><div class="panel-head"><h2>Recent rounds</h2><button class="link-button" data-action="history">Explore battles →</button></div>'+(recent||empty('No rounds captured yet. Open Capture data to get started.'))+'</div><div class="panel"><div class="panel-head"><h2>Most used attack leaders</h2><span class="sub">BY BATTLE COUNT</span></div>'+(topRows||empty('Attack leaders will appear after a scrape.'))+'</div></section>';
}
function filteredBattles(){
  const f=state.filters,q=f.query.trim().toLowerCase();
  return state.battles.filter(b=>(f.mode==='all'||b.mode===f.mode)&&(f.type==='all'||b.battle_type===f.type)&&(f.outcome==='all'||b.outcome===f.outcome)&&(f.season==='all'||String(b.season_number)===f.season)&&(!q||[b.attacker,b.defender,b.matchup,b.event_id,...(b.attacker_chars||[]).map(unit),...(b.defender_chars||[]).map(unit)].join(' ').toLowerCase().includes(q)));
}
function options(values,selected){return values.map(([v,l])=>'<option value="'+esc(v)+'"'+(String(v)===String(selected)?' selected':'')+'>'+esc(l)+'</option>').join('');}
function renderHistory(){
  const rows=filteredBattles(),per=25,pages=Math.max(1,Math.ceil(rows.length/per));state.page=Math.min(state.page,pages);
  const subset=rows.slice((state.page-1)*per,state.page*per);
  const seasons=[...new Set(state.battles.map(x=>x.season_number).filter(Boolean))].sort((a,b)=>b-a);
  const trs=subset.map((b,i)=>{
    const index=(state.page-1)*per+i,id=b.event_id+'-'+b.round_number+'-'+state.battles.indexOf(b);
    const pill=b.outcome==='Win'?'win':b.outcome==='Loss'?'loss':'unknown';
    return '<tr><td><button class="row-link" data-action="battle" data-index="'+state.battles.indexOf(b)+'">'+esc(b.attacker||'Unknown')+'</button><div class="subline">'+esc(labelType(b))+'</div></td><td class="team-cell">'+esc(b.defender||'Unknown')+'<div class="subline">'+esc((b.defender_chars||[]).length)+' units</div></td><td><span class="pill">'+esc(b.mode)+'</span></td><td><span class="pill '+pill+'">'+esc(b.outcome||'Unknown')+'</span></td><td>'+esc(b.banners??'—')+'</td><td><span class="muted">'+esc(shortDate(b.date||b.round_date))+'</span></td></tr>';
  }).join('');
  return '<div class="page-heading"><div><div class="eyebrow">ARCHIVE / ALL ENGAGEMENTS</div><h1>Battle history</h1><p>Search every captured attack and defense in your local GAC archive.</p></div><span class="pill">'+n(rows.length)+' results</span></div>'+
  '<div class="panel"><div class="filters"><input id="history-search" class="input search" type="search" placeholder="Search teams, units, opponents…" value="'+esc(state.filters.query)+'" aria-label="Search battles"><select class="select" data-filter="mode" aria-label="Game mode">'+options([['all','All modes'],['3v3','3v3'],['5v5','5v5'],['Fleet','Fleet'],['Other','Other']],state.filters.mode)+'</select><select class="select" data-filter="type" aria-label="Attack type">'+options([['all','All battles'],['your_attack','Your attacks'],['opponent_attack','Opponent attacks']],state.filters.type)+'</select><select class="select" data-filter="outcome" aria-label="Outcome">'+options([['all','All outcomes'],['Win','Win'],['Loss','Loss'],['Retreat','Retreat'],['Draw','Draw']],state.filters.outcome)+'</select><select class="select" data-filter="season" aria-label="Season">'+options([['all','All seasons'],...seasons.map(s=>[s,'Season '+s])],state.filters.season)+'</select></div>'+
  (rows.length?'<div class="table-wrap"><table class="data-table"><thead><tr><th>ATTACKER</th><th>DEFENDER</th><th>MODE</th><th>RESULT</th><th>BANNERS</th><th>DATE</th></tr></thead><tbody>'+trs+'</tbody></table></div>':empty('No battles match these filters.'))+
  (state.expanded!==null ? renderDetail(state.battles[state.expanded]) : '')+
  '<div class="pagination"><span>Showing '+(rows.length?((state.page-1)*per+1):0)+'–'+Math.min(state.page*per,rows.length)+' of '+n(rows.length)+'</span><div class="controls"><button class="button button-small" data-action="prev" '+(state.page===1?'disabled':'')+'>← Previous</button><button class="button button-small" data-action="next" '+(state.page===pages?'disabled':'')+'>Next →</button></div></div></div>';
}
function renderDetail(b){
  if(!b) return '';
  return '<div class="detail"><div class="detail-head"><div><div class="eyebrow">BATTLE DETAIL</div><h2>'+esc(b.attacker||'Unknown')+' <span class="muted">vs</span> '+esc(b.defender||'Unknown')+'</h2></div><button class="icon-button" data-action="close-detail" aria-label="Close detail">×</button></div><div class="detail-grid"><div><div class="detail-label">ATTACKING TEAM</div><div class="chips">'+names(b.attacker_chars)+'</div></div><div><div class="detail-label">DEFENDING TEAM</div><div class="chips">'+names(b.defender_chars)+'</div></div></div><div class="detail-stats"><span>Outcome <b>'+esc(b.outcome||'—')+'</b></span><span>Banners <b>'+esc(b.banners??'—')+'</b></span><span>Attempt <b>'+esc(b.attempt??'—')+'</b></span><span>Duration <b>'+esc(b.duration||'—')+'</b></span><span>Event <b>'+esc(b.event_id||'—')+'</b></span><span>Round <b>'+esc(b.round_number||'—')+'</b></span></div></div>';
}
function counterPool(){ return state.battles.filter(b=>b.battle_type==='your_attack'&&(state.counters.mode==='all'||b.mode===state.counters.mode)); }
function enemyKey(b){return state.counters.match==='leader'?(b.defender||''):[...(b.defender_chars||[])].sort().join('|');}
function myKey(b){return state.counters.match==='leader'?(b.attacker||''):[...(b.attacker_chars||[])].sort().join('|');}
function counterOptions(){
  const map=new Map();for(const b of counterPool()){const key=enemyKey(b);if(!key)continue;const row=map.get(key)||{key,name:b.defender||'Unknown',members:b.defender_chars,count:0};row.count++;map.set(key,row);}
  return [...map.values()].filter(x=>[x.name,...(x.members||[]).map(unit)].join(' ').toLowerCase().includes(state.counters.query.toLowerCase())).sort((a,b)=>b.count-a.count);
}
function counterResults(key){
  const map=new Map();
  for(const b of counterPool().filter(x=>enemyKey(x)===key)){const k=myKey(b);if(!k)continue;const row=map.get(k)||{name:b.attacker||'Unknown',members:b.attacker_chars,battles:[]};row.battles.push(b);map.set(k,row);}
  return [...map.values()].sort((a,b)=>rate(b.battles)-rate(a.battles)||b.battles.length-a.battles.length);
}
function renderCounters(){
  const opts=counterOptions();
  if(!opts.some(x=>x.key===state.selectedEnemy))state.selectedEnemy=opts[0]?.key||'';
  const chosen=opts.find(x=>x.key===state.selectedEnemy),results=chosen?counterResults(chosen.key):[];
  const enemies=opts.map(x=>'<button class="enemy-button '+(x.key===state.selectedEnemy?'selected':'')+'" data-action="enemy" data-key="'+esc(x.key)+'"><span>'+esc(x.name)+'</span><small>'+n(x.count)+'</small></button>').join('');
  const cards=results.map(x=>{
    const bs=x.battles,w=bs.filter(b=>b.outcome==='Win').length,avg=Math.round(bs.reduce((a,b)=>a+(Number(b.banners)||0),0)/bs.length);
    const recent=bs.slice().sort((a,b)=>(b.date||'').localeCompare(a.date||'')).slice(0,5).map(b=>'<div><span>'+esc(b.outcome||'Unknown')+'</span> · '+esc(b.banners??'—')+' banners · '+esc(shortDate(b.date))+'</div>').join('');
    return '<div class="counter-result"><div class="counter-top"><strong>'+esc(x.name)+'</strong><span class="pill '+(rate(bs)>=70?'win':'')+'">'+n(bs.length)+' attempts</span></div><div class="counter-metrics"><span><b>'+pct(w,bs.length)+'%</b> win rate</span><span><b>'+avg+'</b> avg banners</span><span>'+n(w)+' wins</span></div><div class="chips">'+names(x.members)+'</div><div class="counter-battles">'+recent+'</div></div>';
  }).join('');
  return '<div class="page-heading"><div><div class="eyebrow">TACTICAL INTELLIGENCE</div><h1>Counter lab</h1><p>Choose an enemy team to see the attack teams you have used against it.</p></div></div>'+
  '<div class="filters"><div class="segment"><button data-action="match" data-value="leader" class="'+(state.counters.match==='leader'?'selected':'')+'">By leader</button><button data-action="match" data-value="team" class="'+(state.counters.match==='team'?'selected':'')+'">Exact team</button></div><select class="select" data-counter-filter="mode" aria-label="Game mode">'+options([['all','All modes'],['3v3','3v3'],['5v5','5v5'],['Fleet','Fleet']],state.counters.mode)+'</select></div>'+
  '<div class="counter-layout"><div class="panel"><div class="panel-head"><h2>Enemy teams</h2><span class="sub">'+n(opts.length)+' FOUND</span></div><input id="enemy-search" class="input" style="width:100%;margin-bottom:13px" type="search" placeholder="Search enemy teams…" value="'+esc(state.counters.query)+'" aria-label="Search enemy teams"><div class="enemy-list">'+(enemies||empty('No enemy teams match.'))+'</div></div><div class="panel"><div class="panel-head"><div><h2>'+esc(chosen?.name||'Select an enemy')+'</h2><div class="sub" style="margin-top:5px">'+(chosen?n(chosen.count)+' recorded encounters':'Choose a team from the left')+'</div></div><span class="pill">YOUR ATTACKS</span></div>'+(cards||empty('No recorded counters for this selection.'))+'</div></div>';
}
function renderCapture(){
  const s=state.status,busy=['running','stopping'].includes(s.state);
  const stateName={idle:'Ready to capture',running:'Capture in progress',stopping:'Stopping capture',complete:'Capture complete',failed:'Capture failed',stopped:'Capture stopped'}[s.state]||'Ready to capture';
  const desc={idle:'Your existing archive is ready. Start a scrape to update it.',running:'The scraper is working through your swgoh.gg history. Follow progress below.',stopping:'Waiting for the browser process to close.',complete:'Newly captured files are available in the archive.',failed:s.error||'Check the activity log for details.',stopped:'The scrape was stopped. Previously saved event files remain available.'}[s.state];
  const lines=(s.lines||[]).map(x=>'<span class="log-line">'+esc(x)+'</span>').join('');
  return '<div class="page-heading"><div><div class="eyebrow">SOURCE / SWGOH.GG</div><h1>Capture data</h1><p>Run the existing scraper here and review your local history when it finishes.</p></div></div>'+
  '<div class="capture-grid"><div class="panel"><div class="panel-head"><h2>Scrape settings</h2><span class="pill">LOCAL RUN</span></div><div class="field"><label for="profile-url">GAC history URL</label><input id="profile-url" class="input" type="url" spellcheck="false" value="'+esc(localStorage.getItem('gac-v2-url')||s.url||'https://swgoh.gg/p/887623583/gac-history/')+'" '+(busy?'disabled':'')+'><div class="help">The player profile whose history you want to capture.</div></div><label class="checkbox-row"><input id="headless" type="checkbox" '+(s.headless?'checked':'')+' '+(busy?'disabled':'')+'><span>Run Chrome headless <span class="muted">(visible Chrome is recommended for Cloudflare challenges)</span></span></label><div class="capture-actions"><button class="button button-primary" data-action="start" '+(busy?'disabled':'')+'>◉ &nbsp; Start capture</button><button class="button button-danger" data-action="stop" '+(!busy?'disabled':'')+'>Stop capture</button><button class="button" data-action="reload">↻ &nbsp; Reload archive</button></div><div class="help" style="margin-top:19px">The scraper uses this project’s local Chrome profile and cookies. If swgoh.gg asks for a challenge, complete it in the Chrome window.</div></div>'+
  '<div class="panel"><div class="panel-head"><h2>Capture status</h2><span class="eyebrow">'+esc(s.state.toUpperCase())+'</span></div><div class="state-box"><span class="state-orb">◉</span><div><strong>'+esc(stateName)+'</strong><small>'+esc(desc)+'</small></div></div><div class="steps"><div class="step"><span class="step-number">1</span><div><strong>Open your history</strong><p>Reuse the local signed-in Chrome session.</p></div></div><div class="step"><span class="step-number">2</span><div><strong>Capture each event</strong><p>'+(s.event_count!==null?esc(n(s.event_count))+' events found. ':'')+'Round data is saved to the canonical output files.</p></div></div><div class="step"><span class="step-number">3</span><div><strong>Explore the archive</strong><p>The dashboard reads those files directly after completion.</p></div></div></div></div></div>'+
  '<div class="panel section-gap"><div class="panel-head"><h2>Activity log</h2><span class="sub">'+(s.started_at?'STARTED '+esc(shortDate(s.started_at)):'WAITING FOR CAPTURE')+'</span></div><div class="log" role="log" aria-live="polite">'+(lines||'<span class="muted">Scrape activity will appear here.</span>')+'</div></div>'+
  '<div class="panel section-gap"><div class="panel-head"><h2>Local inventory</h2><span class="sub">READ FROM OUTPUT /</span></div><div class="inventory"><div><strong>'+n(state.data.event_files)+'</strong><small>EVENT FILES</small></div><div><strong>'+n(state.data.rounds.length)+'</strong><small>ROUNDS</small></div><div><strong>'+n(state.battles.length)+'</strong><small>BATTLES</small></div></div></div>';
}
async function updateStatus(){
  try{
    const next=await api('/api/status'),previous=state.status.state;
    const changed=JSON.stringify(next)!==JSON.stringify(state.status);
    state.status=next;updateChrome();
    if(['running','stopping'].includes(previous)&&['complete','failed','stopped'].includes(next.state)) await loadData();
    else if(state.view==='capture'&&changed) render();
  }catch(e){ if(state.view==='capture') showNotice('Could not read scrape status: '+e.message); }
}
async function start(){
  const url=$('#profile-url')?.value.trim(),headless=!!$('#headless')?.checked;
  localStorage.setItem('gac-v2-url',url);
  try{state.status=(await api('/api/scrape/start',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url,headless})})).status;updateChrome();render();}
  catch(e){showNotice(e.message);}
}
async function stop(){try{state.status=(await api('/api/scrape/stop',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'})).status;updateChrome();render();}catch(e){showNotice(e.message);}}
document.addEventListener('click',e=>{
  const nav=e.target.closest('[data-view]');if(nav){goto(nav.dataset.view);return;}
  const btn=e.target.closest('[data-action]');if(!btn)return;
  const action=btn.dataset.action;
  if(['capture','history','counters'].includes(action))goto(action);
  else if(action==='reload')loadData();
  else if(action==='start')start();
  else if(action==='stop')stop();
  else if(action==='battle'){state.expanded=Number(btn.dataset.index);render();}
  else if(action==='close-detail'){state.expanded=null;render();}
  else if(action==='prev'){state.page--;render();}
  else if(action==='next'){state.page++;render();}
  else if(action==='enemy'){state.selectedEnemy=btn.dataset.key;render();}
  else if(action==='match'){state.counters.match=btn.dataset.value;state.selectedEnemy='';render();}
});
document.addEventListener('change',e=>{
  if(e.target.dataset.filter){state.filters[e.target.dataset.filter]=e.target.value;state.page=1;state.expanded=null;render();}
  if(e.target.dataset.counterFilter){state.counters[e.target.dataset.counterFilter]=e.target.value;state.selectedEnemy='';render();}
});
document.addEventListener('input',e=>{
  const id=e.target.id;if(id!=='history-search'&&id!=='enemy-search')return;
  const value=e.target.value,pos=e.target.selectionStart;
  if(id==='history-search'){state.filters.query=value;state.page=1;state.expanded=null;}else{state.counters.query=value;state.selectedEnemy='';}
  render();const input=$('#'+id);input?.focus();input?.setSelectionRange(pos,pos);
});
$('#top-capture').addEventListener('click',()=>goto('capture'));
$('#refresh-btn').addEventListener('click',loadData);
Promise.all([loadData(),updateStatus()]).then(()=>{setInterval(updateStatus,2000);});

