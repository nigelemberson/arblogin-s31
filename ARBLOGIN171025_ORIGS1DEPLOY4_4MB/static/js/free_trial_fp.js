// free_trial_fp.js — collects a browser fingerprint for anti-abuse (Option A MVP)
(function() {
  const setFP = (fp) => {
    var el = document.getElementById('ft_fp');
    if (el) el.value = fp || '';
  };

  // Wait for FingerprintJS global to load (defer scripts)
  window.addEventListener('load', function() {
    if (window.FingerprintJS && FingerprintJS.load) {
      FingerprintJS.load().then(fp => fp.get()).then(result => {
        setFP(result.visitorId || '');
      }).catch(() => setFP(''));
    } else {
      // If CDN blocked, leave blank (server can fall back to IP+UA hash)
      setFP('');
    }
  });
})();
