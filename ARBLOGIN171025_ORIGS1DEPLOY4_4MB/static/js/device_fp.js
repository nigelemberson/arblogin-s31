// static/js/device_fp.js — local lightweight fingerprint
(function(){
  function toHex(bytes){return Array.from(bytes).map(b=>b.toString(16).padStart(2,'0')).join('');}
  async function sha256(s){const enc=new TextEncoder();const buf=await crypto.subtle.digest('SHA-256',enc.encode(s));return toHex(new Uint8Array(buf));}
  function getData(){
    try {
      const nav = window.navigator||{};
      const scr = window.screen||{};
      return [
        nav.userAgent||'',
        nav.language||'',
        nav.platform||'',
        scr.width||0, scr.height||0, scr.colorDepth||0,
        Intl.DateTimeFormat().resolvedOptions().timeZone||'',
      ].join('|');
    } catch(e){ return String(Math.random()); }
  }
  window.addEventListener('load', async function(){
    const val = await sha256(getData());
    const el = document.getElementById('ft_fp');
    if (el) el.value = val;
  });
})();
