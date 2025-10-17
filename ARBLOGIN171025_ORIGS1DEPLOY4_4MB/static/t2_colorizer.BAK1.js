/* t2_colorizer.js — S12: force inline colours, no pulse */
(function(){
  window.T2_VERSION = "S12";
  (function ensureInline(){
    const id="t2-inline-S12";
    if(!document.getElementById(id)){
      const st=document.createElement('style'); st.id=id;
      st.textContent=[
        '.t2-pos{background-color:#2EE66B !important;}',
        '.t2-warn{background-color:#F5C542 !important;}',
        '.t2-neg{background-color:#DE3E4B !important;}',
        '.t2-pulse{animation:none !important;}',
        '.t2-selected{outline:2px solid #1a7a3b;outline-offset:-2px;}'
      ].join('\n');
      document.head.appendChild(st);
    }
  })();
  const POS_EDGE=0.01, WARN_EDGE=0.001;
  function findT2(){return document.querySelector('section[data-t2] table, table.t2-table, .t2-table')
    || [...document.querySelectorAll('table')].find(tb=>{const r=tb.tHead?tb.tHead.rows[0]:tb.rows[0];if(!r)return false;
      return [...r.cells].some(c=>/^edge\s*%?$/i.test((c.textContent||'').trim()));})||null;}
  function edgeIdx(t){const r=t.tHead?t.tHead.rows[0]:t.rows[0];if(!r)return -1;for(let i=0;i<r.cells.length;i++){
      if(/^edge\s*%?$/i.test((r.cells[i].textContent||'').trim())) return i;}
    const b=t.tBodies.length?t.tBodies[0].rows[0]:t.rows[1];if(!b)return -1;for(let i=0;i<b.cells.length;i++){
      if(/(-?\d+(?:\.\d+)?)\s*%/.test(b.cells[i].textContent||'')) return i;}return -1;}
  function parse(txt,ph){const s=String(txt||'').trim();const m=s.match(/(-?\d+(?:\.\d+)?)\s*%/);if(m)return parseFloat(m[1])/100;
    const n=parseFloat(s.replace(/[^0-9+\-.]/g,''));if(isNaN(n))return 0;return ph?n/100:n;}
  function paint(){const t=findT2();if(!t)return;const i=edgeIdx(t);if(i<0)return;const ph=/%/.test((t.tHead?t.tHead.rows[0]:t.rows[0]).cells[i].textContent||'');
    const b=t.tBodies.length?t.tBodies[0]:t;[...b.rows].forEach(tr=>{tr.classList.remove('t2-pos','t2-warn','t2-neg','t2-pulse');
      const e=parse(tr.cells[i]?.textContent,ph);if(e>=POS_EDGE)tr.classList.add('t2-pos');else if(e>=WARN_EDGE)tr.classList.add('t2-warn');else if(e<0)tr.classList.add('t2-neg');});}
  const POS_EDGE=0.01, WARN_EDGE=0.001;
  const go=()=>{try{paint();}catch(e){}};document.readyState==='loading'?document.addEventListener('DOMContentLoaded',go):go();setInterval(go,2000);
  console.log("T2 colourizer loaded:", window.T2_VERSION);
})();
