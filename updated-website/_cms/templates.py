# -*- coding: utf-8 -*-
"""HTML building blocks for Top 10 Irish Casino.

Every piece of text comes from the content files in ../content (edited in Sveltia CMS).
`ctx` is the site context built in build.py: settings, reviews list and render helpers.
"""
import html
import re

import markdown as _md

# ---------------------------------------------------------------------------------------------
# Text rendering
# ---------------------------------------------------------------------------------------------

_ctx = {}


def set_context(ctx):
    _ctx.clear()
    _ctx.update(ctx)


def S():
    return _ctx["settings"]


def _tokens(s, mode, extra=None):
    """Replace {{site_name}}, {{domain}}, {{email}}, {{helpline}} (and extras) in text."""
    if s is None:
        return ""
    s = str(s)
    st = S()
    phone = st["helpline_number"]
    tel = "tel:" + re.sub(r"[^0-9+]", "", phone)
    values = {
        "site_name": st["site_name"],
        "domain": st["domain"],
        "email": st["email"],
        "year": st["year"],
        "updated": st["updated"],
        "helpline": f"[{phone}]({tel})" if mode == "md" else phone,
    }
    values.update(extra or {})
    return re.sub(r"\{\{\s*(\w+)\s*\}\}", lambda m: str(values.get(m.group(1), m.group(0))), s)


def T(s, **extra):
    """Plain text: tokens + HTML escaping."""
    return html.escape(_tokens(s, "plain", extra), quote=False)


def A(s, **extra):
    """Attribute-safe text."""
    return html.escape(_tokens(s, "plain", extra), quote=True)


def _post(h, list_class="check-list style-one legal-list"):
    # external links open in a new tab
    h = re.sub(r'<a href="(https?://[^"]+)">', r'<a href="\1" target="_blank" rel="noopener">', h)
    # bullet lists use the theme's check-list style
    h = h.replace("<ul>", f'<ul class="{list_class}">')
    h = h.replace("<li>", '<li><i class="flaticon-check"></i>')
    return h


def MD(s, list_class="check-list style-one legal-list", **extra):
    """Rich text (Markdown) -> HTML paragraphs and lists."""
    out = _md.markdown(_tokens(s, "md", extra), output_format="html")
    return _post(out, list_class)


def MI(s, **extra):
    """Inline rich text (Markdown) -> HTML without the surrounding <p>."""
    out = _md.markdown(_tokens(s, "md", extra), output_format="html").strip()
    if out.startswith("<p>") and out.endswith("</p>") and out.count("<p>") == 1:
        out = out[3:-4]
    return _post(out)


def paras(s, indent="                                        ", cls=""):
    """Markdown body rendered as indented paragraphs."""
    h = MD(s)
    if cls:
        h = h.replace("<p>", f'<p class="{cls}">')
    return "\n".join(indent + line for line in h.splitlines() if line.strip())


def img_src(path):
    return (path or "").lstrip("/")


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")


# ---------------------------------------------------------------------------------------------
# Head / header / banner / footer
# ---------------------------------------------------------------------------------------------

def btn(text, href, style="style-one", extra="", target_blank=False, offer=None):
    tgt = ' target="_blank" rel="nofollow noopener noreferrer sponsored"' if target_blank else ""
    if offer:
        tgt += f' data-offer="{html.escape(offer)}"'
    if style == "style-one":
        inner = f'<span class="text-flip"><span class="text">{text}</span><span class="text">{text}</span></span>'
    else:
        inner = f'<span class="text">{text}</span>'
    return f'<a href="{html.escape(href or "#", quote=True)}" class="theme-btn {style} {extra}"{tgt}>{inner}</a>'


def head(title, description):
    return f"""<!DOCTYPE html>
<html lang="en-IE">
    <head>
        <!--====== Required meta tags ======-->
        <meta charset="utf-8">
        <meta http-equiv="x-ua-compatible" content="ie=edge">
        <meta name="description" content="{A(description)}">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <!--====== Title ======-->
        <title>{T(title)}</title>
        <!--====== Favicon Icon ======-->
        <link rel="icon" href="favicon.ico" sizes="any">
        <link rel="icon" href="assets/images/favicon.png" type="image/png" sizes="64x64">
        <link rel="icon" href="assets/images/favicon-32x32.png" type="image/png" sizes="32x32">
        <link rel="apple-touch-icon" href="assets/images/apple-touch-icon.png">
        <meta name="theme-color" content="#0E0F11">
        <!--====== Google Fonts ======-->
        <link href="https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100..900;1,100..900&family=Source+Sans+3:ital,wght@0,200..900;1,200..900&display=swap" rel="stylesheet">
        <!--====== Flaticon css ======-->
        <link rel="stylesheet" href="assets/fonts/flaticon/flaticon_t10ic.css">
        <!--====== FontAwesome css ======-->
        <link rel="stylesheet" href="assets/fonts/fontawesome/css/all.min.css">
        <!--====== Bootstrap css ======-->
        <link rel="stylesheet" href="assets/css/plugins/bootstrap.min.css">
        <!--====== Slick-popup css ======-->
        <link rel="stylesheet" href="assets/css/plugins/slick.css">
        <!--====== Magnific-popup css ======-->
        <link rel="stylesheet" href="assets/css/plugins/magnific-popup.css">
        <!--====== Default css ======-->
        <link rel="stylesheet" href="assets/css/default.css">
        <!--====== Style css ======-->
        <link rel="stylesheet" href="assets/css/style.css">
        <!--====== Offers & site css ======-->
        <link rel="stylesheet" href="assets/css/offers.css">
    </head>
    <body>
        <!--====== Preloader ======-->
        <div class="preloader">
            <div class="loading-container">
                <div class="loading"></div>
                <div id="loading-icon"><img src="assets/images/loader.png" alt="{A('{{site_name}}')}" width="300" height="191"></div>
            </div>
        </div>
        <!--====== Start Overlay ======-->
        <div class="offcanvas__overlay"></div>
"""


def _logos():
    alt = A("{{site_name}}")
    header = (f'<picture class="site-logo">'
              f'<source media="(max-width: 991px)" srcset="assets/images/logo/logo-mobile.webp" type="image/webp">'
              f'<source media="(max-width: 991px)" srcset="assets/images/logo/logo-mobile.png">'
              f'<source srcset="assets/images/logo/logo-main.webp" type="image/webp">'
              f'<img src="assets/images/logo/logo-main.png" alt="{alt}" width="521" height="180"></picture>')
    mobile = (f'<picture class="site-logo site-logo-mobile">'
              f'<source srcset="assets/images/logo/logo-mobile.webp" type="image/webp">'
              f'<img src="assets/images/logo/logo-mobile.png" alt="{alt}" width="377" height="240"></picture>')
    main = (f'<picture class="site-logo site-logo-footer">'
            f'<source srcset="assets/images/logo/logo-main.webp" type="image/webp">'
            f'<img src="assets/images/logo/logo-main.png" alt="{alt}" width="521" height="180" loading="lazy"></picture>')
    return header, mobile, main


def _nav():
    reviews = [(f"{T(r['title'])}", f"{r['_slug']}.html") for r in _ctx["reviews"]]
    return [
        ("home", "Home", "index.html", None),
        ("sportsbook", "Sportsbook", "index.html#sportsbook-offers", None),
        ("casino", "Casino", "casino.html", None),
        ("reviews", "Reviews", "#", reviews),
        ("guides", "Guides", "#", [
            ("Irish Gambling Guide", "gambling-guide.html"),
            ("How We Rate", "index.html#how-we-rate"),
            ("Responsible Gambling", "responsible-gambling.html"),
            ("FAQ", "faq.html"),
        ]),
        ("about", "About", "about.html", None),
        ("contact", "Contact", "contact.html", None),
    ]


def tel():
    return "tel:" + re.sub(r"[^0-9+]", "", S()["helpline_number"])


def header(active=""):
    h = S()["header"]
    logo_header, logo_mobile, _ = _logos()
    items = []
    for key, label, href, children in _nav():
        if children is not None and not children:
            continue
        cls = "menu-item" + (" has-children" if children else "") + (" active" if key == active else "")
        if children:
            sub = "\n".join(f'                                            <li><a href="{hh}">{l}</a></li>' for l, hh in children)
            items.append(f"""                                    <li class="{cls}"><a href="{href}">{label}</a>
                                        <ul class="sub-menu">
{sub}
                                        </ul>
                                    </li>""")
        else:
            items.append(f'                                    <li class="{cls}"><a href="{href}">{label}</a></li>')
    nav = "\n".join(items)
    button = btn(T(h["button_label"]), h["button_link"])
    return f"""        <!--=== Start  Header Area  ===-->
        <header class="header-area header-one transparent-header">
            <!--====  Compliance Top Bar  ===-->
            <div class="site-topbar">
                <div class="container">
                    <p><span class="age-badge">18+</span> <span class="topbar-full">{MI(h['topbar_full'])}</span><span class="topbar-short">{MI(h['topbar_short'])}</span> <a href="affiliate-disclosure.html">{T(h['topbar_link_label'])}</a></p>
                </div>
            </div>
            <!--====  Header Navigation  ===-->
            <div class="header-navigation">
                <div class="container">
                    <!--====  Primary Menu  ===-->
                    <div class="primary-menu">
                        <!--====  Site Branding  ===-->
                        <div class="site-branding">
                            <a href="index.html" class="brand-logo">{logo_header}</a>
                        </div>
                        <!--=== Main Menu===-->
                        <div class="pf-nav-menu">
                            <div class="site-branding d-block d-lg-none text-center">
                                <a href="index.html" class="brand-logo">{logo_mobile}</a>
                            </div>
                            <nav class="main-menu">
                                <ul>
{nav}
                                </ul>
                            </nav>
                            <!--=== PF Nav Button ===-->
                            <div class="pf-nav-button mt-20 d-block d-md-none">
                                {button}
                            </div>
                            <!--=== PF Menu Bottom ===-->
                            <div class="pf-menu-bottom mt-50 d-block d-lg-none">
                                <h5>{T(h['mobile_help_title'])}</h5>
                                <p class="mobile-help">{T(h['mobile_help_text'])} <a href="{tel()}">{T(S()['helpline_number'])}</a></p>
                            </div>
                        </div>
                        <!--=== Header Nav Right ===-->
                        <div class="nav-right-item">
                            <div class="nav-button d-none d-md-block">
                                {button}
                            </div>
                            <div class="navbar-toggler">
                                <span></span>
                                <span></span>
                                <span></span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </header><!--=== End  Header Area  ===-->
        <!--======  Smooth Wrapper  ======-->
        <div id="smooth-wrapper">
            <div id="smooth-content">
                <!--======  Main  ======-->
                <main>
"""


def banner(title, text, crumb=None, pill=None):
    right = ""
    if crumb:
        right = f"""<ul class="breadcrumb-link">
                                                    <li><a href="index.html">Home</a></li>
                                                    <li class="active">{T(crumb)}</li>
                                                </ul>"""
    elif pill:
        right = f"""<ul class="breadcrumb-link">
                                                    <li class="active"><i class="far fa-calendar-check"></i> {T(pill)}</li>
                                                </ul>"""
    return f"""                    <!--======  Page Banner  ======-->
                    <section class="t10ic-page-banner">
                        <div class="shape shape-circle1"><span></span></div>
                        <div class="shape shape-circle2"><span></span></div>
                        <div class="container">
                            <div class="row align-items-center">
                                <div class="col-lg-9">
                                    <div class="page-content">
                                        <h1 class="page-title">{T(title)}</h1>
                                        <div class="row">
                                            <div class="col-xl-8">
                                                <div class="text-box d-flex align-items-center">
                                                    <div class="icon">
                                                        <img class="rotate360" src="assets/images/pages/shape/star1.png" alt="">
                                                    </div>
                                                    <div class="text">
                                                        <p>{MI(text)}</p>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="col-xl-4">
                                                {right}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-lg-3">
                                    <div class="age-ring float-lg-end" aria-label="Adults only, 18+">
                                        <span class="ring"></span><span class="ring inner"></span>
                                        <strong>18+<small>Play safe</small></strong>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section><!--======  End Page Banner  ======-->
"""


def footer():
    st = S()
    f = st["footer"]
    _, _, logo_main = _logos()
    email = html.escape(st["email"])
    reviews = "\n".join(f'                                                <li><a href="{r["_slug"]}.html">{T(r["brand"])}</a></li>'
                        for r in _ctx["reviews"])
    notices = "\n".join(f"                                <p>{MI(n)}</p>" for n in f.get("notices", []))
    return f"""                </main>
                <!--====== Start Footer Area ======-->
                <footer class="t10ic-footer gray-dark pt-130 primary-black-bg">
                    <div class="shape shape-one"><span><img class="rotate360" src="assets/images/marketing-agency/footer/element1.png" alt="Shape"></span></div>
                    <div class="shape shape-two"><span><img class="rotate360" src="assets/images/marketing-agency/footer/element2.png" alt="Shape"></span></div>
                    <div class="shape shape-blur_one"><span></span></div>
                    <div class="shape shape-blur_two"><span></span></div>
                    <!--=== Footer Widget Area ===-->
                    <div class="footer-widget-area pb-60">
                        <div class="container">
                            <div class="row">
                                <div class="col-lg-4 col-md-6 col-sm-12">
                                    <div class="footer-widget footer-about-widget mb-40 pf_fadeup">
                                        <div class="footer-content">
                                            <div class="footer-logo">
                                                <a href="index.html">{logo_main}</a>
                                            </div>
                                            <p>{MI(f['about'])}</p>
                                            <div class="footer-age-note"><span class="age-badge">18+</span> {T(f['age_note'])}</div>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-lg-2 col-md-6 col-6">
                                    <div class="footer-widget footer-nav-widget mb-40 pf_fadeup">
                                        <div class="footer-content">
                                            <h4 class="widget-title">Compare</h4>
                                            <ul class="footer-nav">
                                                <li><a href="index.html#sportsbook-offers">Sportsbook Offers</a></li>
                                                <li><a href="casino.html">Casino Offers</a></li>
                                                <li><a href="index.html#how-we-rate">How We Rate</a></li>
                                                <li><a href="gambling-guide.html">Gambling Guide</a></li>
                                                <li><a href="faq.html">FAQ</a></li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-lg-2 col-md-6 col-6">
                                    <div class="footer-widget footer-nav-widget mb-40 pf_fadeup">
                                        <div class="footer-content">
                                            <h4 class="widget-title">Reviews</h4>
                                            <ul class="footer-nav">
{reviews}
                                                <li><a href="about.html">About Us</a></li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-lg-4 col-md-6">
                                    <div class="footer-widget footer-contact-widget mb-40 pf_fadeup">
                                        <div class="footer-content">
                                            <h4 class="widget-title">{T(f['contact_title'])}</h4>
                                            <div class="t10ic-iconic-box style-three mb-30">
                                                <div class="icon"><i class="far fa-envelope"></i></div>
                                                <div class="content">
                                                    <h6>{T(f['email_label'])}</h6>
                                                    <p><a href="mailto:{email}">{email}</a></p>
                                                </div>
                                            </div>
                                            <div class="t10ic-iconic-box style-three">
                                                <div class="icon"><i class="far fa-phone-alt"></i></div>
                                                <div class="content">
                                                    <h6>{T(f['helpline_label'])}</h6>
                                                    <p><a href="{tel()}">{T(st['helpline_number'])}</a></p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <!--=== Responsible Gambling Block ===-->
                            <div class="footer-rg-block pf_fadeup">
                                <div class="rg-logos">
                                    <a href="https://gamblingcare.ie/" target="_blank" rel="noopener"><img src="assets/images/brands/logo-gamblingcare.png" alt="GamblingCare.ie"></a>
                                    <a href="https://www.problemgambling.ie/" target="_blank" rel="noopener"><img src="assets/images/brands/logo-extern.png" alt="Extern Problem Gambling"></a>
                                    <a href="https://www.gambleaware.org/" target="_blank" rel="noopener"><img src="assets/images/brands/logo-gambleaware.png" alt="GambleAware"></a>
                                    <a href="https://ibas-uk.com/" target="_blank" rel="noopener"><img src="assets/images/brands/logo-ibas.png" alt="IBAS"></a>
                                </div>
{notices}
                            </div>
                        </div>
                    </div>
                    <!--=== Footer Copyright ===-->
                    <div class="footer-copyright">
                        <div class="container">
                            <div class="row">
                                <div class="col-lg-5">
                                    <div class="copyright-text">
                                        <p>&copy; {T(st['year'])} <span>{T(st['site_name'])}</span> - {T(f['copyright'])}</p>
                                    </div>
                                </div>
                                <div class="col-lg-7">
                                    <div class="copyright-nav">
                                        <ul>
                                            <li><a href="terms-and-conditions.html">Terms &amp; Conditions</a></li>
                                            <li><a href="privacy-policy.html">Privacy Policy</a></li>
                                            <li><a href="cookie-policy.html">Cookies</a></li>
                                            <li><a href="affiliate-disclosure.html">Affiliate Disclosure</a></li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </footer><!--====== End Footer  ======-->
            </div>
        </div>
        <!--====== Jquery js ======-->
        <script src="assets/js/plugins/jquery-3.7.1.min.js"></script>
        <!--====== Bootstrap js ======-->
        <script src="assets/js/plugins/popper.min.js"></script>
        <script src="assets/js/plugins/bootstrap.min.js"></script>
        <!--====== Gsap Js ======-->
        <script src="assets/js/plugins/gsap/gsap.min.js"></script>
        <script src="assets/js/plugins/gsap/SplitText.min.js"></script>
        <script src="assets/js/plugins/gsap/ScrollSmoother.min.js"></script>
        <script src="assets/js/plugins/gsap/ScrollTrigger.min.js"></script>
        <!--====== Slick js ======-->
        <script src="assets/js/plugins/slick.min.js"></script>
        <!--====== Magnific js ======-->
        <script src="assets/js/plugins/jquery.magnific-popup.min.js"></script>
        <!--====== Waypoint js ======-->
        <script src="assets/js/plugins/jquery.waypoints.js"></script>
        <!--====== CounterUp js ======-->
        <script src="assets/js/plugins/jquery.counterup.min.js"></script>
        <!--====== Main js ======-->
        <script src="assets/js/theme.js"></script>
        <!--====== Outbound link tracking (gclid pass-through) ======-->
        <script src="assets/js/offers.js"></script>
    </body>
</html>
"""


def page(seo, active, body):
    return head(seo.get("title", ""), seo.get("description", "")) + header(active) + body + footer()


# ---------------------------------------------------------------------------------------------
# Reusable blocks
# ---------------------------------------------------------------------------------------------

def stars(rating):
    five = float(rating) / 2.0
    out = []
    for i in range(1, 6):
        if five >= i - 0.25:
            out.append('<i class="fas fa-star"></i>')
        elif five >= i - 0.75:
            out.append('<i class="fas fa-star-half-alt"></i>')
        else:
            out.append('<i class="far fa-star"></i>')
    return "".join(out)


def fa(icon):
    icon = (icon or "star").strip()
    return icon if icon.startswith("fa-") else "fa-" + icon


def offer_card(rank, o, kind):
    lab = S()["offers"]
    brand = o.get("brand", "")
    invert = ' class="logo-invert"' if o.get("invert_logo") else ""
    tag = f'<span class="offer-tag">{T(o["tag"])}</span>' if o.get("tag") else ""
    feats = "\n".join(f'                                                <li><i class="far fa-check"></i>{MI(f)}</li>' for f in o.get("features", []) if f)
    review = ""
    if o.get("review") and o["review"] in _ctx["review_slugs"]:
        rbrand = next((r.get("brand") for r in _ctx["reviews"] if r["_slug"] == o["review"]), brand)
        review = f'<a class="offer-review-link" href="{o["review"]}.html">{T(lab["review_link"], brand=rbrand)} <i class="far fa-arrow-right"></i></a>'
    kind_label = "Sportsbook" if kind == "sport" else "Casino"
    cta = T(lab["sport_button"] if kind == "sport" else lab["casino_button"])
    cid = f"offer-{'sb' if kind == 'sport' else 'cas'}-{rank}"
    tracking = o.get("tracking_id") or f"{slugify(brand)}-{'sportsbook' if kind == 'sport' else 'casino'}"
    rating = float(o.get("rating") or 0)
    ribbon = f'<span class="offer-ribbon"><i class="fas fa-crown"></i> {T(lab["top_pick_label"])}</span>' if rank == 1 else ''
    return f"""                            <!--=== Offer Card #{rank} : {T(brand)} ===-->
                            <div class="offer-card{' is-top' if rank == 1 else ''} mb-30 pf_fadeup" id="{cid}">
                                <span class="offer-rank">{rank}</span>
                                {ribbon}
                                <div class="offer-grid">
                                    <div class="offer-brand">
                                        <div class="offer-logo"><img{invert} src="{A(img_src(o.get('logo')))}" alt="{A(brand)} logo" loading="lazy"></div>
                                        <span class="offer-licence"><i class="far fa-shield-check"></i> {T(lab['licence_prefix'])} {T(o.get('licence', ''))}</span>
                                    </div>
                                    <div class="offer-info">
                                        <div class="offer-meta"><span class="offer-kind">{kind_label}</span>{tag}</div>
                                        <h3 class="offer-title">{T(o.get('headline', ''))} <span>{T(o.get('highlight', ''))}</span></h3>
                                        <ul class="offer-features">
{feats}
                                        </ul>
                                    </div>
                                    <div class="offer-rating">
                                        <span class="label">{T(lab['rating_label'])}</span>
                                        <div class="score">{rating:.1f}<small>/10</small></div>
                                        <div class="stars" aria-label="{rating:.1f} out of 10">{stars(rating)}</div>
                                    </div>
                                    <div class="offer-cta">
                                        {btn(cta, o.get('url') or '#', target_blank=True, extra="w-100", offer=tracking)}
                                        <div class="offer-cta-meta">
                                            <span class="offer-tc"><span class="age-badge sm">18+</span> {T(lab['tcs_label'])}</span>
                                            {review}
                                            <button type="button" class="offer-toggle" aria-expanded="false" aria-controls="{cid}-terms"><span class="more">{T(lab['more_info'])}</span><span class="less">{T(lab['less_info'])}</span> <i class="far fa-chevron-down"></i></button>
                                        </div>
                                    </div>
                                </div>
                                <div class="offer-terms" id="{cid}-terms">{T(o.get('terms', ''))}</div>
                            </div>
"""


def section_title(sub, h2, center=False, p=None, cls="mb-50"):
    pp = f"\n                                        <p>{MI(p)}</p>" if p else ""
    return f"""                                    <div class="section-title {'text-center ' if center else ''}{cls} pf_fadeup">
                                        <span class="sub-title">{T(sub)}</span>
                                        <h2>{T(h2)}</h2>{pp}
                                    </div>
"""


def offers_section(sec_id, data, kind, gray=False, extra_bottom=""):
    offers = [o for o in data.get("offers", []) if o.get("enabled", True)]
    cards = "".join(offer_card(i + 1, o, kind) for i, o in enumerate(offers))
    sub = data.get("subtitle", "")
    return f"""                    <!--======  {T(sub)} Section  ======-->
                    <section class="agk-offers {'gray-dark ' if gray else ''}pt-120 pb-90" id="{sec_id}">
                        <div class="container">
                            <div class="row align-items-end">
                                <div class="col-lg-7">
{section_title(sub, data.get('heading', ''), cls="mb-30")}                                </div>
                                <div class="col-lg-5">
                                    <div class="offers-intro mb-40 pf_fadeup"><p>{MI(data.get('intro', ''))}</p></div>
                                </div>
                            </div>
{cards}{extra_bottom}                        </div>
                    </section><!--======  End {T(sub)} Section  ======-->
"""


def criteria_section(data, sec_id="how-we-rate", gray=True):
    boxes = ""
    for c in data.get("criteria", []):
        boxes += f"""                                <div class="col-lg-4 col-md-6 col-sm-12">
                                    <div class="t10ic-iconic-box style-seven criteria-box mb-30 pf_fadeup">
                                        <div class="icon"><i class="fal {fa(c.get('icon'))}"></i></div>
                                        <div class="content">
                                            <h4>{T(c.get('title'))}</h4>
                                            <p>{MI(c.get('text'))}</p>
                                        </div>
                                    </div>
                                </div>
"""
    return f"""                    <!--======  How We Rate Section  ======-->
                    <section class="agk-features {'gray-dark ' if gray else ''}pt-120 pb-90" id="{sec_id}">
                        <div class="container">
                            <div class="row align-items-center">
                                <div class="col-lg-6">
{section_title(data.get('subtitle'), data.get('heading'), cls="mb-45")}                                </div>
                                <div class="col-lg-6">
                                    <div class="text-box mb-40 pf_fadeup">
                                        <p>{MI(data.get('intro'))}</p>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
{boxes}                            </div>
                        </div>
                    </section><!--======  End How We Rate Section  ======-->
"""


def accordion(items, acc_id="accordionOne", first_open=True):
    """items: list of dicts with question, answer and optional note."""
    out = ""
    for i, it in enumerate(items):
        n = i + 1
        show = first_open and i == 0
        note = it.get("note")
        note_html = f'<p class="faq-note"><i class="far fa-lightbulb-on"></i> {T(note)}</p>' if note else ""
        out += f"""                                        <div class="t10ic-accordion-item mb-20">
                                            <div class="accordion-header">
                                                <h6 class="accordion-title" data-bs-toggle="collapse" data-bs-target="#{acc_id}-c{n}" aria-expanded="{'true' if show else 'false'}">
                                                    {T(it.get('question'))}
                                                </h6>
                                            </div>
                                            <div id="{acc_id}-c{n}" class="accordion-collapse collapse{' show' if show else ''}" data-bs-parent="#{acc_id}">
                                                <div class="accordion-content">
                                                    <p>{MI(it.get('answer'))}</p>
                                                    {note_html}
                                                </div>
                                            </div>
                                        </div>
"""
    return f"""                                    <div class="t10ic-accordion mb-30 pf_fadeup" id="{acc_id}">
{out}                                    </div>
"""


def rg_cta():
    c = S()["rg_cta"]
    return f"""                    <!--=== Responsible Gambling CTA ===-->
                    <section class="agk-cta rg-cta">
                        <div class="t10ic-cta-wrappper gray-dark pt-40 pb-20">
                            <div class="shape shape_one"><span></span></div>
                            <div class="shape shape_two"><span></span></div>
                            <div class="container">
                                <div class="row align-items-center">
                                    <div class="col-lg-7">
                                        <div class="section-title mb-30 pf_fadeup">
                                            <span class="sub-title">{T(c['subtitle'])}</span>
                                            <h2>{T(c['heading'])}</h2>
                                        </div>
                                    </div>
                                    <div class="col-lg-5">
                                        <div class="t10ic-button rg-cta-buttons float-lg-end mb-40 pf_fadeup">
                                            {btn(T(c['button_label']), c['button_link'])}
                                            {btn(T(c['call_label']), tel(), style="style-two")}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section><!--=== End CTA Section ===-->
"""


def disclaimer_strip():
    return f"""                    <div class="container">
                        <div class="offers-disclaimer pf_fadeup">
                            <span class="age-badge">18+</span>
                            <p>{MI(S()['offers']['disclaimer'])}</p>
                        </div>
                    </div>
"""


def stat_value(v):
    """'40+' -> animated counter <span class="count">40</span>+ ; '0%' / '18+' stay static."""
    v = str(v or "")
    m = re.match(r"^(\d+)(.*)$", v)
    if m and int(m.group(1)) > 0 and v != "18+":
        return f'<span class="count">{m.group(1)}</span>{T(m.group(2))}'
    return T(v)


def stat_cards(stats):
    out = ""
    for s in stats or []:
        out += (f'                                        <div class="col-6"><div class="t10ic-counter-box style-two stat-card text-center mb-30 pf_fadeup">'
                f'<div class="content"><h2>{stat_value(s.get("value"))}</h2><p>{T(s.get("label"))}</p></div></div></div>\n')
    return out


def icon_boxes(items, cols="col-lg-4 col-md-6", cls="", mb="mb-30"):
    out = ""
    for b in items or []:
        out += f"""                                <div class="{cols}">
                                    <div class="t10ic-iconic-box style-seven {cls} {mb} pf_fadeup">
                                        <div class="icon"><i class="fal {fa(b.get('icon'))}"></i></div>
                                        <div class="content">
                                            <h4>{T(b.get('title'))}</h4>
                                            <p>{MI(b.get('text'))}</p>
                                        </div>
                                    </div>
                                </div>
"""
    return out


def document_body(doc, show_updated_value=None):
    """Legal / guide layout (service-details style): table of contents + sections."""
    sections = doc.get("sections", [])
    toc = "\n".join(f'                                                <li><a href="#{A(s.get("anchor") or slugify(s.get("heading")))}"><i class="far fa-angle-right"></i>{T(s.get("heading"))}</a></li>' for s in sections)
    blocks = ""
    for s in sections:
        sid = s.get("anchor") or slugify(s.get("heading"))
        inner = paras(s.get("body", ""))
        if s.get("note"):
            inner += f'\n                                        <p class="guide-note"><i class="far fa-info-circle"></i> {T(s["note"])}</p>'
        if s.get("link_label") and s.get("link_url"):
            inner += f'\n                                        <p><a href="{A(s["link_url"])}" class="inline-link">{T(s["link_label"])} <i class="far fa-arrow-right"></i></a></p>'
        if s.get("stats"):
            cards = "\n".join(f'                                            <div class="col-4"><div class="stat-card text-center"><h2>{T(x.get("value"))}</h2><p>{T(x.get("label"))}</p></div></div>' for x in s["stats"])
            inner += f"""
                                        <div class="row guide-stats mt-30">
{cards}
                                        </div>"""
        blocks += f"""                                    <div class="t10ic-content-box legal-block mb-50 pf_fadeup" id="{A(sid)}">
                                        <h3>{T(s.get('heading'))}</h3>
{inner}
                                    </div>
"""
    intro_html = ""
    if doc.get("intro") or show_updated_value:
        upd = f'<span class="sub-title">Last updated: {T(show_updated_value)}</span>' if show_updated_value else ""
        intro_html = f"""                                    <div class="t10ic-content-box legal-intro mb-50 pf_fadeup">
                                        {upd}
                                        <p class="lead-text">{MI(doc.get('intro', ''))}</p>
                                    </div>
"""
    email = html.escape(S()["email"])
    return f"""                    <!--======  Start Details Section (service-details layout)  ======-->
                    <section class="t10ic-service-details legal-page pt-130 pb-80">
                        <div class="container">
                            <div class="service-details-wrapper">
                                <div class="row">
                                    <div class="col-lg-4">
                                        <aside class="legal-sidebar mb-50">
                                            <div class="sidebar-box pf_fadeup">
                                                <h4>{T(doc.get('sidebar_title') or 'On this page')}</h4>
                                                <ul class="legal-toc">
{toc}
                                                </ul>
                                            </div>
                                            <div class="sidebar-box sidebar-help pf_fadeup">
                                                <h4>Questions?</h4>
                                                <p>Our team is happy to help with anything on this page.</p>
                                                <a href="mailto:{email}" class="help-mail"><i class="far fa-envelope"></i>{email}</a>
                                            </div>
                                        </aside>
                                    </div>
                                    <div class="col-lg-8">
{intro_html}{blocks}                                    </div>
                                </div>
                            </div>
                        </div>
                    </section><!--======  End Details Section ======-->
"""
