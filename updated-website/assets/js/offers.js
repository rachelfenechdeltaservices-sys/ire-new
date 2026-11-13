/*
 * Outbound offer link tracking.
 * If the visitor arrived from a Google Ads click (?gclid=...), pass the gclid
 * through to every operator link that goes via the /visit/ redirect.
 *  - Links ending in "?c=" or "?subid=" expect the value appended directly.
 *  - Other links get "?gclid=" / "&gclid=" added.
 */
(function () {
    'use strict';
    document.addEventListener('DOMContentLoaded', function () {
        var params = new URLSearchParams(window.location.search);
        var gclid = params.get('gclid');
        if (!gclid) return;
        var value = encodeURIComponent(gclid);

        document.querySelectorAll('a[href*="topinireland.online/visit/"]').forEach(function (link) {
            var url = link.getAttribute('href');
            if (!url || url.indexOf('javascript:') === 0) return;
            if (/[?&](c|subid)=$/.test(url)) {
                link.setAttribute('href', url + value);
            } else {
                link.setAttribute('href', url + (url.indexOf('?') > -1 ? '&' : '?') + 'gclid=' + value);
            }
        });
    });
})();
