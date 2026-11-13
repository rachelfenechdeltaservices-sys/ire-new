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
