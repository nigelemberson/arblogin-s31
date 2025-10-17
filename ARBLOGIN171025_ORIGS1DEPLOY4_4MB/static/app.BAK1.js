// app.js — dynamic accent from Calculate button + keep green pulse + settings safety
let demoMode=false;
let fetchEverySec=0;
let autoTimer=null;
let lastRows=[];
let lastBeepAt=0;
let lastMaxEdge=-1;

function qs(s){return document.querySelector(s)}

// ---------- PREFERENCES ----------
function getPref(k, def){
  try{
    const v = localStorage.getItem(k);
    if(v===null||v===undefined) return def;
    if(v==='true') return true;
    if(v==='false') return false;
    const n = Number(v);
    return Number.isFinite(n) ? n : v;
  }catch{ return def; }
}
function setPref(k, v){ try{ localStorage.setItem(k, String(v)); }catch{} }

function getEdgeThreshold(){ return getPref('edgeAlertThreshold', 0) }
function isBeepEnabled(){ return getPref('edgeBeepOn', true) }

// ---------- STYLE HELPERS ----------
function injectHeaderStyles(){
  if(document.getElementById('hdr-style')) return;
  const css = `
  .topbar{display:flex;gap:16px;align-items:center;justify-content:flex-start;background:#0b0b0b;border:1px solid #202020;border-radius:14px;padding:10px 12px;margin:10px 10px 0 10px;position:sticky;top:6px;z-index:50}
  .topbar .title{font-weight:900;color:#fff;margin-right:auto}
  .mini{padding:6px 10px;border-radius:10px;border:1px solid #444;background:#111;color:#ddd;cursor:pointer;font-weight:800}
  .seg{display:flex;align-items:center;gap:8px}
  .btn-pill{padding:6px 10px;border-radius:10px;border:1px solid #2c2c2c;background:#121212;color:#fff;cursor:pointer;font-weight:800}
  .btn-pill:hover{filter:brightness(1.1)}
  .num{min-width:38px;display:inline-flex;justify-content:center;align-items:center;font-weight:900;color:#23c26b}
  .select{padding:6px 10px;border-radius:10px;border:1px solid #2c2c2c;background:#121212;color:#fff}
  /* Default pulse (will get overridden by dynamic accent) */
  @keyframes edgePulse{ 0%,100%{ background:rgba(35,194,107,.10);} 50%{ background:rgba(35,194,107,.22);} }
  #t2body tr.edge-pos td{ animation: edgePulseCustom 1.0s ease-in-out infinite !important; }
  #t2body tr.edge-pos td:nth-child(6){ color:rgb(160,247,165) !important; font-weight:800; text-shadow:0 0 6px rgba(160,247,165,.65) !important; }
  #t2body tr.sel td{ outline:2px solid #23c26b; background:transparent !important; }
  #demoFlag{padding:6px 10px;border-radius:10px;border:1px solid #444;background:#111;color:#ddd;cursor:pointer;font-weight:800}
  #demoFlag.on{border-color:#0b803f;background:#00170b;color:#23c26b}
  @media (prefers-reduced-motion: reduce){ #t2body tr.edge-pos td{ animation: edgePulseCustom 1.0s ease-in-out infinite !important; } }
  `;
  const style=document.createElement('style'); style.id='hdr-style'; style.textContent=css; document.head.appendChild(style);
}
function ensureSettingsStyles(){
  if(document.getElementById('set-style')) return;
  const css = `
  .set-overlay{position:fixed;inset:0;background:rgba(0,0,0,.55);display:flex;align-items:center;justify-content:center;z-index:9999}
  .set-card{width:520px;max-width:92vw;background:#0b0b0b;border:1px solid #2a2a2a;border-radius:18px;box-shadow:0 18px 60px rgba(0,0,0,.6);color:#fff}
  .set-head{display:flex;justify-content:space-between;align-items:center;padding:14px 16px;border-bottom:1px solid #222}
  .set-title{font-weight:900;font-size:18px}
  .set-body{padding:16px;display:grid;gap:14px}
  .set-row{display:flex;align-items:center;justify-content:space-between;gap:12px}
  .set-row input[type="number"]{width:120px;padding:8px 10px;border-radius:10px;border:1px solid #3a3a3a;background:#111;color:#fff}
  .set-actions{display:flex;gap:10px;padding:12px 16px;border-top:1px solid #222;justify-content:flex-end}
  .set-btn{padding:10px 14px;border-radius:12px;border:2px solid #2a2a2a;background:#101010;color:#fff;cursor:pointer;font-weight:800}
  .set-btn.green{background:#23c26b;border-color:#0b803f;color:#00170b}`;
  const style=document.createElement('style'); style.id='set-style'; style.textContent=css; document.head.appendChild(style);
}

// Parse rgb/rgba("r, g, b") → [r,g,b]
function parseRGB(str){
  if(!str) return null;
  const m = String(str).match(/rgba?\s*\(\s*(\d+)[,\s]+(\d+)[,\s]+(\d+)/i);
  if(!m) return null;
  return [parseInt(m[1],10), parseInt(m[2],10), parseInt(m[3],10)];
}
// Apply dynamic accent using Calculate button's background
function applyDynamicAccent(){
  const r=160, g=247, b=165;
  const accent = `rgb(${r}, ${g}, ${b})`;
  const a10 = `rgba(${r}, ${g}, ${b}, .10)`;
  const a22 = `rgba(${r}, ${g}, ${b}, .22)`;
  const a60 = `rgba(${r}, ${g}, ${b}, .60)`;

  // Remove existing dynamic block if any
  const old = document.getElementById('accent-style');
  if(old) old.remove();

  const css = `
  @keyframes edgePulseCustom{0%,100%{background:rgba(160,247,165,.18);}50%{background:rgba(160,247,165,.40);}};}50%{background:${a22};}}
  #t2body tr.edge-pos td{ animation: edgePulseCustom 1.0s ease-in-out infinite !important; }
  #t2body tr.edge-pos td:nth-child(6){ color:rgb(160,247,165) !important; font-weight:800; text-shadow:0 0 6px rgba(160,247,165,.65) !important; } !important; text-shadow:0 0 6px ${a60} !important; }
  #t2body tr.sel td{ outline:2px solid ${accent} !important; }
  .num{ color:${accent} !important; }`;

  const style=document.createElement('style'); style.id='accent-style'; style.textContent=css; document.head.appendChild(style);
}

// ---------- HEADER INJECTION ----------
function injectHeader(){
  injectHeaderStyles();
  if(document.querySelector('.topbar')) return;
  const bar = document.createElement('div');
  bar.className = 'topbar';
  bar.innerHTML = `
    <div class="title">Sports Arbitrage Bot — Web</div>
    <div class="seg">
      <span class="mini">Fetch every</span>
      <button class="btn-pill" id="decFetch">−</button>
      <span class="num" id="fetchVal">0</span>
      <button class="btn-pill" id="incFetch">+</button>
      <span class="mini">sec</span>
    </div>
    <div class="seg">
      <span class="mini">League</span>
      <select id="leagueSelect" class="select">
        <option>EPL</option>
        <option>LaLiga</option>
        <option>Serie A</option>
        <option>NBA</option>
      </select>
    </div>
    <button class="btn-pill" id="demoFlag">Demo: OFF</button>
    <button class="btn-pill" id="btnSettingsTop">Settings</button>
  `;
  const app = document.querySelector('main, .container, body');
  (app||document.body).insertBefore(bar, app?.firstChild||document.body.firstChild);
}

// ---------- SETTINGS MODAL ----------
function showSettings(){
  ensureSettingsStyles();
  const th = getEdgeThreshold();
  const on = isBeepEnabled();
  const disp = fetchEverySec>0 ? `${fetchEverySec}s` : '15s';
  const overlay = document.createElement('div'); overlay.className='set-overlay';
  const card = document.createElement('div'); card.className='set-card'; overlay.appendChild(card);
  card.innerHTML = `
    <div class="set-head">
      <div class="set-title">Settings</div>
      <button class="set-btn" id="set-close">Close</button>
    </div>
    <div class="set-body">
      <div class="set-row">
        <label>Edge alert threshold (%)</label>
        <input id="set-threshold" type="number" step="0.1" min="-100" max="100" value="${th}">
      </div>
      <div class="set-row">
        <label>Enable beep on opportunities</label>
        <input id="set-beep" type="checkbox" ${on?'checked':''}>
      </div>
      <div class="set-row">
        <label>Auto refresh every (seconds)</label>
        <div>Use the +/- in header. Current: <strong id="set-cur">${disp}</strong></div>
      </div>
    </div>
    <div class="set-actions">
      <button class="set-btn" id="set-save">Save</button>
      <button class="set-btn green" id="set-done">Done</button>
    </div>`;
  document.body.appendChild(overlay);
  const close = ()=> overlay.remove();
  overlay.addEventListener('click', (e)=>{ if(e.target===overlay) close(); });
  card.querySelector('#set-close').addEventListener('click', close);
  card.querySelector('#set-done').addEventListener('click', close);
  card.querySelector('#set-save').addEventListener('click', ()=>{
    const v = parseFloat(card.querySelector('#set-threshold').value||'0')||0;
    const b = !!card.querySelector('#set-beep').checked;
    setPref('edgeAlertThreshold', v);
    setPref('edgeBeepOn', b);
    alert('Saved.');
  });
}

// ---------- RENDER / DATA ----------
function renderRows(tbody, rows){
  if(!tbody) return;
  let html='';
  for(const r of rows){ html += '<tr>' + r.map(c=>`<td>${(c??'')}</td>`).join('') + '</tr>'; }
  tbody.innerHTML = html;
  highlightRows();
}
function highlightRows(){
  const threshold = getEdgeThreshold();
  const trs = qs('#t2body')?.querySelectorAll('tr') || [];
  trs.forEach(tr=>{
    const tds = tr.querySelectorAll('td');
    if(tds.length<6) return;
    const raw = tds[5].innerText;
    const edge = parseFloat(String(raw).replace(/[^0-9.\-]/g,''));
    tr.classList.remove('edge-pos');
    if(Number.isFinite(edge) && edge >= threshold && edge > 0){
      tr.classList.add('edge-pos');
    }
  });
}
async function refreshTable2(){
  const btn = qs('#btnRefresh'); if(btn) btn.disabled = true;
  try{
    const url = demoMode ? '/api/demo_table2' : '/api/latest_table2';
    const res = await fetch(url, {cache:'no-store'});
    const data = await res.json();
    lastRows = data.rows || [];
    renderRows(qs('#t2body'), lastRows);
    const src = qs('#t2src'); if(src) src.textContent = data.csv_path || 'None';
    const ts = new Date().toLocaleTimeString(); const lu = qs('#lastUpdate'); if(lu) lu.textContent = ts;
    checkEdgesAndBeep(lastRows);
  }catch(e){ alert('Refresh failed: '+e); }
  finally{ if(btn) btn.disabled = false; }
}

// ---------- AUTO REFRESH (seconds) ----------
function msForInterval(){ return (fetchEverySec && fetchEverySec>0 ? fetchEverySec*1000 : 13000) }
function toggleAuto(){
  const label = qs('#autoState');
  if(autoTimer){
    clearInterval(autoTimer); autoTimer=null;
    if(label) label.textContent='Off';
  }else{
    autoTimer=setInterval(refreshTable2, msForInterval());
    const disp = fetchEverySec>0 ? `${fetchEverySec}s` : '15s';
    if(label) label.textContent = `On (${disp})`;
    refreshTable2();
  }
}
function saveFetchEvery(v){ setPref('fetchEverySec', v); }
function loadFetchEvery(){
  const s = getPref('fetchEverySec', null);
  if(s!==null && s!==undefined) return s;
  const oldMin = getPref('fetchEveryMin', null);
  if(oldMin!==null && oldMin!==undefined){
    const converted = Math.min(999, Math.max(0, Number(oldMin)*60|0));
    setPref('fetchEverySec', converted);
    return converted;
  }
  return 0;
}
function updFetch(){
  fetchEverySec = Math.max(0, Math.min(999, Number(fetchEverySec)||0));
  const fv=qs('#fetchVal'); if(fv) fv.textContent = String(fetchEverySec);
  setPref('fetchEverySec', fetchEverySec);
  if(autoTimer){
    clearInterval(autoTimer);
    autoTimer = setInterval(refreshTable2, msForInterval());
    const label = qs('#autoState');
    const disp = fetchEverySec>0 ? `${fetchEverySec}s` : '15s';
    if(label) label.textContent = `On (${disp})`;
  }
}

// ---------- DEMO ----------
function setDemo(on){
  demoMode = !!on;
  setPref('demoModeOn', demoMode);
  const flag = qs('#demoFlag');
  if(flag){ flag.textContent = 'Demo: ' + (demoMode?'ON':'OFF'); flag.classList.toggle('on', demoMode); }
  refreshTable2();
}

// ---------- CALC & UTILS ----------
function getVal(id){ return parseFloat(qs('#'+id)?.value||'')||0 }
function setVal(id,val){ const el=qs('#'+id); if(el) el.value = (val??''); }
function calcArb(){
  const stake=getVal('stake'), a=getVal('oddsA'), b=getVal('oddsB'), comm=(getVal('comm')||0)/100, fee=getVal('fee')||0;
  if(a<=1||b<=1||stake<=0){ alert('Enter valid stake and odds'); return; }
  const k=a/(a+b), stakeA=stake*k, stakeB=stake-stakeA;
  const retA=stakeA*a*(1-comm)-fee, retB=stakeB*b*(1-comm)-fee;
  const profitA=retA-stake, profitB=retB-stake, minProfit=Math.min(profitA,profitB);
  const edge = stake? (minProfit/stake*100) : 0;
  setVal('stakeA', stakeA.toFixed(2));
  setVal('stakeB', stakeB.toFixed(2));
  setVal('edge', edge.toFixed(2)+' %');
  setVal('profitA', profitA.toFixed(2));
  setVal('profitB', profitB.toFixed(2));
  setVal('minProfit', minProfit.toFixed(2));
}
function clearCalc(){
  setVal('stake', '100.00');
  setVal('oddsA', '2.10');
  setVal('oddsB', '3.60');
  setVal('comm', '0.00');
  setVal('fee', '0.00');
  ['stakeA','stakeB','edge','profitA','profitB','minProfit'].forEach(id=>setVal(id,''));
}

// ---------- TABLE 2 SELECTION ----------
let selectedRow=null;
function onRowClick(e){
  let tr = e.target.closest('tr'); if(!tr) return;
  if(selectedRow) selectedRow.classList.remove('sel');
  selectedRow = tr; selectedRow.classList.add('sel');
}
function useSelection(){
  if(!selectedRow){ alert('Click a row in Table 2 first.'); return; }
  const tds = Array.from(selectedRow.querySelectorAll('td'));
  if(!tds.length){ alert('Cannot read the selected row.'); return; }

  const clean = td => parseFloat(td.innerText.trim().replace(/[^0-9.\-]/g,''));
  let a=NaN, b=NaN;
  if(tds.length >= 5){
    const tryA = clean(tds[2]);
    const tryB = clean(tds[4]);
    if(tryA>1 && tryB>1){ a=tryA; b=tryB; }
  }
  if(!(a>1 && b>1)){
    const nums = [];
    tds.forEach(td=>{
      const v = clean(td);
      if(!Number.isNaN(v) && v>1) nums.push(v);
    });
    if(nums.length>=2){ a=nums[0]; b=nums[1]; }
  }
  if(!(a>1 && b>1)){ alert('Selected row has no usable odds.'); return; }
  setVal('oddsA', a.toFixed(2));
  setVal('oddsB', b.toFixed(2));
}

// ---------- COPY / BET CARD / EXPORT ----------
async function autoCopy(){
  const stake = getVal('stake');
  const oddsA = getVal('oddsA');
  const oddsB = getVal('oddsB');
  if(!(stake>0 && oddsA>1 && oddsB>1)){
    alert('Fill Stake, Odds A and Odds B first (Use Selection helps).');
    return;
  }
  if(!qs('#stakeA')?.value){ calcArb(); }
  const slip = buildSlipText();
  try{
    if(navigator.clipboard?.writeText){
      await navigator.clipboard.writeText(slip);
      alert('Copied to clipboard.');
    }else{
      const ta = document.createElement('textarea');
      ta.value = slip; document.body.appendChild(ta); ta.select();
      document.execCommand('copy'); document.body.removeChild(ta);
      alert('Copied to clipboard.');
    }
  }catch(e){
    alert('Copy failed: '+e);
  }
}
function injectBCStyles(){
  if(document.getElementById('bc-style')) return;
  const css = `.bc-overlay{position:fixed;inset:0;background:rgba(0,0,0,.55);display:flex;align-items:center;justify-content:center;z-index:9999}
  .bc-card{width:560px;max-width:92vw;background:#0b0b0b;border:1px solid #2a2a2a;border-radius:18px;box-shadow:0 18px 60px rgba(0,0,0,.6);color:#fff}
  .bc-head{display:flex;justify-content:space-between;align-items:center;padding:14px 16px;border-bottom:1px solid #222}
  .bc-title{font-weight:900;font-size:18px}
  .bc-body{padding:16px;display:grid;grid-template-columns:1fr 1fr;gap:10px}
  .bc-row{display:flex;justify-content:space-between;gap:10px;padding:8px 10px;background:#0f0f0f;border:1px solid #202020;border-radius:10px}
  .bc-key{color:#a3a3a3}
  .bc-actions{display:flex;gap:10px;padding:12px 16px;border-top:1px solid #222;justify-content:flex-end}
  .bc-btn{padding:10px 14px;border-radius:12px;border:2px solid #2a2a2a;background:#101010;color:#fff;cursor:pointer;font-weight:800}
  .bc-btn.green{background:#23c26b;border-color:#0b803f;color:#00170b}
  .bc-btn.orange{background:#ff7a00;border-color:#a54a00;color:#1a0d00}
  @media print{body *:not(.bc-card):not(.bc-card *){visibility:hidden !important}.bc-card{position:fixed;inset:auto;left:0;top:0;transform:none;box-shadow:none;border:0;width:auto;max-width:none}}`;
  const style=document.createElement('style'); style.id='bc-style'; style.textContent=css; document.head.appendChild(style);
}
function buildSlipData(){
  const ctx = { mode: demoMode ? 'DEMO':'LIVE' };
  const get = id => (qs('#'+id)?.value||'').trim();
  if(!get('stakeA')) calcArb();

  ctx.match = (selectedRow ? selectedRow.querySelector('td')?.innerText.trim() : '') || '—';
  if(selectedRow){
    const t = Array.from(selectedRow.querySelectorAll('td')).map(td=>td.innerText.trim());
    ctx.bookA = t[1]||'—'; ctx.oddsA = t[2]||get('oddsA'); ctx.bookB = t[3]||'—'; ctx.oddsB = t[4]||get('oddsB');
  }else{
    ctx.bookA='—'; ctx.bookB='—'; ctx.oddsA=get('oddsA'); ctx.oddsB=get('oddsB');
  }
  ctx.stake = get('stake');
  ctx.stakeA = get('stakeA'); ctx.stakeB = get('stakeB');
  ctx.comm = get('comm'); ctx.fee = get('fee');
  ctx.edge = get('edge'); ctx.minProfit = get('minProfit');
  return ctx;
}
function buildSlipText(){
  const d = buildSlipData();
  return [
    'Big Cheese — Bet Card',
    `Mode: ${d.mode}`,
    `Match: ${d.match}`,
    `Book A: ${d.bookA} | Odds A: ${d.oddsA}`,
    `Book B: ${d.bookB} | Odds B: ${d.oddsB}`,
    `Stake: ${d.stake} | Stake A: ${d.stakeA} | Stake B: ${d.stakeB}`,
    `Commission: ${d.comm}% | Fixed Fee: ${d.fee}`,
    `Edge: ${d.edge} | Min Profit: ${d.minProfit}`
  ].join('\n');
}
function showBetCard(){
  injectBCStyles();
  const d = buildSlipData();
  const overlay = document.createElement('div'); overlay.className='bc-overlay';
  const card = document.createElement('div'); card.className='bc-card'; overlay.appendChild(card);
  card.innerHTML = `
    <div class="bc-head">
      <div class="bc-title">Bet Card <span class="bc-key">(${d.mode})</span></div>
      <button class="bc-btn" id="bc-close">Close</button>
    </div>
    <div class="bc-body">
      <div class="bc-row"><span class="bc-key">Match</span><span>${d.match}</span></div>
      <div class="bc-row"><span class="bc-key">Stake</span><span>${d.stake}</span></div>
      <div class="bc-row"><span class="bc-key">Book A</span><span>${d.bookA}</span></div>
      <div class="bc-row"><span class="bc-key">Odds A</span><span>${d.oddsA}</span></div>
      <div class="bc-row"><span class="bc-key">Book B</span><span>${d.bookB}</span></div>
      <div class="bc-row"><span class="bc-key">Odds B</span><span>${d.oddsB}</span></div>
      <div class="bc-row"><span class="bc-key">Stake A</span><span>${d.stakeA}</span></div>
      <div class="bc-row"><span class="bc-key">Stake B</span><span>${d.stakeB}</span></div>
      <div class="bc-row"><span class="bc-key">Commission</span><span>${d.comm}%</span></div>
      <div class="bc-row"><span class="bc-key">Fixed Fee</span><span>${d.fee}</span></div>
      <div class="bc-row"><span class="bc-key">Edge</span><span>${d.edge}</span></div>
      <div class="bc-row"><span class="bc-key">Min Profit</span><span>${d.minProfit}</span></div>
    </div>
    <div class="bc-actions">
      <button class="bc-btn" id="bc-copy">Copy</button>
      <button class="bc-btn orange" id="bc-print">Print</button>
      <button class="bc-btn green" id="bc-done">Done</button>
    </div>`;
  document.body.appendChild(overlay);
  const close = ()=> overlay.remove();
  overlay.addEventListener('click', (e)=>{ if(e.target===overlay) close(); });
  card.querySelector('#bc-close').addEventListener('click', close);
  card.querySelector('#bc-done').addEventListener('click', close);
  card.querySelector('#bc-copy').addEventListener('click', async ()=>{
    try{ await navigator.clipboard.writeText(buildSlipText()); alert('Bet Card copied.'); }catch(e){ alert('Copy failed: '+e); }
  });
  card.querySelector('#bc-print').addEventListener('click', ()=>{ window.print(); });
}
function exportCSV(){
  if(!lastRows || !lastRows.length){ alert('No data to export.'); return; }
  const header = ['Match','Book A','Odds A','Book B','Odds B','Edge %','Time'];
  const lines = [header.join(',')];
  lastRows.forEach(r=>{
    const row = (r||[]).map(c=>{
      const s = (c??'').toString().replace(/"/g,'""');
      return /[",\n]/.test(s) ? `"${s}"` : s;
    }).join(',');
    lines.push(row);
  });
  const csv = lines.join('\r\n');
  const blob = new Blob([csv], {type:'text/csv;charset=utf-8;'});
  const a = document.createElement('a');
  const stamp = new Date().toISOString().replace(/[:.]/g,'-');
  a.href = URL.createObjectURL(blob);
  a.download = `table2_${demoMode?'demo_':''}${stamp}.csv`;
  document.body.appendChild(a); a.click(); document.body.removeChild(a);
}

// ---------- POSITIVE EDGE ALERT ----------
function getEdgeFromRow(row){
  if(!row || row.length<6) return null;
  const raw = row[5] ?? '';
  const num = parseFloat(String(raw).replace(/[^0-9.\-]/g,''));
  return Number.isFinite(num) ? num : null;
}
function beep(){
  const now = Date.now();
  if(now - lastBeepAt < 7000) return;
  lastBeepAt = now;
  try{
    const ctx = new (window.AudioContext||window.webkitAudioContext)();
    const o = ctx.createOscillator(); const g = ctx.createGain();
    o.type='sine'; o.frequency.value = 880; o.connect(g); g.connect(ctx.destination);
    g.gain.setValueAtTime(0.001, ctx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.2, ctx.currentTime+0.02);
    o.start();
    setTimeout(()=>{ g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime+0.18); o.stop(ctx.currentTime+0.2); }, 50);
  }catch{}
}
function checkEdgesAndBeep(rows){
  let maxEdge=-1;
  for(const r of rows){
    const e = getEdgeFromRow(r);
    if(e!==null && e>maxEdge) maxEdge = e;
  }
  const threshold = getEdgeThreshold();
  const enabled = isBeepEnabled();
  if(enabled && maxEdge>=threshold && maxEdge>lastMaxEdge){ beep(); }
  lastMaxEdge = Math.max(lastMaxEdge, maxEdge);
}

// ---------- UI WIRING ----------
window.addEventListener('DOMContentLoaded',()=>{
  injectHeader();
  // Apply accent after DOM paints so #btnCalc exists
  requestAnimationFrame(applyDynamicAccent);

  // Restore preferences
  demoMode = !!getPref('demoModeOn', false);
  const flag = qs('#demoFlag');
  if(flag){ flag.textContent = 'Demo: ' + (demoMode?'ON':'OFF'); flag.classList.toggle('on', demoMode); }

  fetchEverySec = loadFetchEvery();
  const fv=qs('#fetchVal'); if(fv) fv.textContent = String(fetchEverySec);

  qs('#btnRefresh')?.addEventListener('click',refreshTable2);
  qs('#btnAuto')?.addEventListener('click',toggleAuto);
  qs('#btnCalc')?.addEventListener('click',calcArb);
  qs('#btnClear')?.addEventListener('click',clearCalc);
  qs('#t2body')?.addEventListener('click',onRowClick);
  qs('#btnUseSel')?.addEventListener('click',useSelection);
  qs('#btnAutoCopy')?.addEventListener('click',autoCopy);
  qs('#btnBetCard')?.addEventListener('click',showBetCard);
  qs('#btnExport')?.addEventListener('click',exportCSV);
  qs('#btnSettings')?.addEventListener('click',showSettings);
  qs('#btnSettingsTop')?.addEventListener('click',showSettings);

  qs('#btnOneApi')?.addEventListener('click',()=>alert('Fetch One API not yet wired.'));
  qs('#btnAutoApi')?.addEventListener('click',()=>alert('Fetch Auto API not yet wired.'));
  qs('#btnAudio')?.addEventListener('click',()=>alert('Audio panel not yet wired.'));
  qs('#btnAudit')?.addEventListener('click',()=>alert('Audit Log not yet wired.'));
  qs('#btnExit')?.addEventListener('click',()=>window.location.href='/logout');
  qs('#btnKey')?.addEventListener('click',()=>alert('Key panel not yet wired.'));

  const df=qs('#demoFlag'); df?.addEventListener('click',()=>{ setDemo(!demoMode); });

  qs('#incFetch')?.addEventListener('click',()=>{fetchEverySec=Math.min(999, (Number(fetchEverySec)||0)+1); setPref('fetchEverySec', fetchEverySec); updFetch(); const fv=qs('#fetchVal'); if(fv) fv.textContent = String(fetchEverySec); });
  qs('#decFetch')?.addEventListener('click',()=>{fetchEverySec=Math.max(0, (Number(fetchEverySec)||0)-1); setPref('fetchEverySec', fetchEverySec); updFetch(); const fv=qs('#fetchVal'); if(fv) fv.textContent = String(fetchEverySec); });

  updFetch();
  refreshTable2();
});
