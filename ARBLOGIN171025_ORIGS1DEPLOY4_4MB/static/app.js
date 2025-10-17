// === S13 additions (Table 2 colourizer + 1s pulse) ===
(function(){
  window.T2_VERSION="S13";
  const POS_EDGE_DEFAULT=0.01, WARN_EDGE_DEFAULT=0.001;
  const POS_EDGE=(window.T2_EDGE_POS??POS_EDGE_DEFAULT);
  const WARN_EDGE=(window.T2_EDGE_WARN??WARN_EDGE_DEFAULT);
  function findT2(){return document.querySelector('section[data-t2] table, table.t2-table, .t2-table')
    ||[...document.querySelectorAll('table')].find(tb=>{const r=tb.tHead?tb.tHead.rows[0]:tb.rows[0];if(!r)return false;
      return [...r.cells].some(c=>/^edge\s*%?$/i.test((c.textContent||'').trim()));})||null}
  function edgeIdx(t){const r=t.tHead?t.tHead.rows[0]:t.rows[0];if(!r)return -1;for(let i=0;i<r.cells.length;i++){
      if(/^edge\s*%?$/i.test((r.cells[i].textContent||'').trim()))return i;}const b=t.tBodies.length?t.tBodies[0].rows[0]:t.rows[1];
    if(!b)return -1;for(let i=0;i<b.cells.length;i++){if(/(-?\d+(?:\.\d+)?)\s*%/.test(b.cells[i].textContent||''))return i;}return -1}
  function parseEdge(txt,p){const s=String(txt||'').trim();const m=s.match(/(-?\d+(?:\.\d+)?)\s*%/);if(m)return parseFloat(m[1])/100;
    const n=parseFloat(s.replace(/[^0-9+\-.]/g,''));if(isNaN(n))return 0;return p?n/100:n}
  function paint(){const t=findT2();if(!t)return;const i=edgeIdx(t);if(i<0)return;const r=t.tHead?t.tHead.rows[0]:t.rows[0];
    const p=/%/.test((r.cells[i]?.textContent||''));const b=t.tBodies.length?t.tBodies[0]:t;[...b.rows].forEach(tr=>{
      tr.classList.remove('t2-pos','t2-warn','t2-neg','t2-pulse');tr.classList.add('t2-row');
      const e=parseEdge(tr.cells[i]?.textContent,p);if(e>=POS_EDGE)tr.classList.add('t2-pos','t2-pulse');
      else if(e>=WARN_EDGE)tr.classList.add('t2-warn','t2-pulse');else if(e<0)tr.classList.add('t2-neg','t2-pulse');});}
  const go=()=>{try{paint();}catch(e){}};document.readyState==='loading'?document.addEventListener('DOMContentLoaded',go):go();setInterval(go,2000);
  console.log("T2 colourizer loaded:",window.T2_VERSION,"POS",POS_EDGE,"WARN",WARN_EDGE);
})();
// === end S13 additions ===
