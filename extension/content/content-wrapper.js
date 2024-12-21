(function () {
  'use strict';

  // Ensure jQuery is loaded
  const ensureJQuery = async () => {
    if (typeof window.jQuery === 'undefined') {
      // Dynamically load jQuery from your extension's local directory
      const script = document.createElement('script');
      script.src = chrome.runtime.getURL('scripts/jquery.min.js'); // Adjust path if necessary
      document.head.appendChild(script);
      await new Promise(resolve => (script.onload = resolve));
      console.log('jQuery loaded successfully.');
    } else {
      console.log('jQuery is already available.');
    }
  };

  const injectTime = performance.now();
  (async () => {
    // Ensure jQuery is available before running content.js
    await ensureJQuery();
    const { onExecute } = await import(
      /* @vite-ignore */
      chrome.runtime.getURL("content/content.js")
    );
    onExecute?.({ perf: { injectTime, loadTime: performance.now() - injectTime } });
  })().catch(console.error);

})();
