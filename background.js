const proxyBase = "https://proxy-flask-vercel.vercel.app/?url=";

chrome.webRequest.onBeforeRequest.addListener(
  function(details) {
    const url = details.url;
    if (url.startsWith(proxyBase)) {
      return {};
    }
    const redirectUrl = proxyBase + encodeURIComponent(url);
    return { redirectUrl: redirectUrl };
  },
  { urls: ["*://steamunlocked.net/*"] },
  ["blocking"]
);
