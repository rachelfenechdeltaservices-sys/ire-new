/*
 * Outbound offer link tracking.
 * Every operator button carries a data-offer="..." label (e.g. data-offer="netbet-sportsbook").
 * If the visitor arrived from a Google Ads click (?gclid=...), the gclid is passed through to
 * those links once they point at a real offer URL:
 *  - URLs ending in "?c=" or "?subid=" get the value appended directly.
 *  - Other URLs get "?gclid=" / "&gclid=" added.
 * Buttons still pointing at the homepage placeholder are left untouched.
 */
(function () {
    'use strict';
    var PLACEHOLDER = /^https?:\/\/(www\.)?top10irishcasino\.site\/?$/i;
    document.addEventListener('DOMContentLoaded', function () {
        var gclid = new URLSearchParams(window.location.search).get('gclid');
        if (!gclid) return;
        var value = encodeURIComponent(gclid);
        document.querySelectorAll('a[data-offer]').forEach(function (link) {
            var url = link.getAttribute('href');
            if (!url || url.indexOf('javascript:') === 0 || PLACEHOLDER.test(url)) return;
            if (/[?&](c|subid)=$/.test(url)) {
                link.setAttribute('href', url + value);
            } else {
                link.setAttribute('href', url + (url.indexOf('?') > -1 ? '&' : '?') + 'gclid=' + value);
            }
        });
    });
})();

/*
 * Mobile offer cards: "More info" toggle reveals the licence, extra
 * advantages, full terms and review link (desktop always shows them).
 */
(function () {
    'use strict';
    document.addEventListener('click', function (e) {
        var btn = e.target.closest ? e.target.closest('.offer-toggle') : null;
        if (!btn) return;
        var card = btn.closest('.offer-card');
        if (!card) return;
        var open = card.classList.toggle('is-open');
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
        // keep GSAP ScrollSmoother / ScrollTrigger in sync with the new height
        if (window.ScrollTrigger && typeof window.ScrollTrigger.refresh === 'function') {
            setTimeout(function () { window.ScrollTrigger.refresh(); }, 50);
        }
    });
})();
