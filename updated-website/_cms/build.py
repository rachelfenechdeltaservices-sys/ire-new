# -*- coding: utf-8 -*-
"""Build the Top 10 Irish Casino website from the CMS content files.

    python updated-website/_cms/build.py            # writes the HTML pages into updated-website/

All text lives in updated-website/content/ and is edited in Sveltia CMS (/admin/).
Offers are shown in the order they appear in the CMS list (drag to reorder).
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.dirname(HERE)
CONTENT = os.path.join(SITE_DIR, "content")
sys.path.insert(0, HERE)

import templates as t  # noqa: E402
from templates import T, MI, A, btn, banner, page, section_title, offers_section, criteria_section, \
    accordion, rg_cta, disclaimer_strip, stat_cards, icon_boxes, document_body, paras, stars, fa, img_src, tel  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else SITE_DIR
written = []


def load(rel):
    with open(os.path.join(CONTENT, rel), encoding="utf-8") as f:
        return json.load(f)


def write(name, html):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(html)
    written.append(name)


SETTINGS = load("settings.json")
SPORT = load("offers-sportsbook.json")
CASINO = load("offers-casino.json")
FAQ = load("faq.json").get("items", [])

REVIEWS = []
for path in sorted(glob.glob(os.path.join(CONTENT, "reviews", "*.json"))):
    with open(path, encoding="utf-8") as f:
        r = json.load(f)
    if r.get("published", True) is False:
        continue
    r["_slug"] = os.path.splitext(os.path.basename(path))[0]
    REVIEWS.append(r)
REVIEWS.sort(key=lambda r: (r.get("menu_order") or 999, r.get("title", "")))

t.set_context({"settings": SETTINGS, "reviews": REVIEWS, "review_slugs": {r["_slug"] for r in REVIEWS}})


def pg(name):
    return load(f"pages/{name}.json")


# ------------------------------------------------------------------ home
def build_index():
    p = pg("home")
    body = banner(p["banner_title"], p["banner_text"], pill=f"Updated {SETTINGS['updated']}")
    body += offers_section("sportsbook-offers", SPORT, "sport")
    body += disclaimer_strip()
    tr = p["trust"]
    boxes = ""
    for b in tr.get("boxes", []):
        boxes += f"""                                        <div class="col-md-6">
                                            <div class="t10ic-iconic-box style-seven trust-box mb-30 pf_fadeup">
                                                <div class="icon"><i class="fal {fa(b.get('icon'))}"></i></div>
                                                <div class="content">
                                                    <h4>{T(b.get('title'))}</h4>
                                                    <p>{MI(b.get('text'))}</p>
                                                </div>
                                            </div>
                                        </div>
"""
    body += f"""                    <!--======  Licensed-only commitment  ======-->
                    <section class="agk-trust gray-dark pt-120 pb-90">
                        <div class="container">
                            <div class="row align-items-center">
                                <div class="col-lg-5">
{section_title(tr['subtitle'], tr['heading'], cls="mb-40")}                                    <div class="t10ic-content-box mb-40 pf_fadeup">
                                        <p>{MI(tr['text'])}</p>
                                    </div>
                                </div>
                                <div class="col-lg-7">
                                    <div class="row">
{boxes}                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>
"""
    g = p["guide"]
    body += f"""                    <!--======  Guide Section  ======-->
                    <section class="agk-about pt-130 pb-80">
                        <div class="container">
                            <div class="row">
                                <div class="col-xl-7">
                                    <div class="agk-content-box style-one mb-50 pf_fadeup">
                                        <div class="section-title mb-20">
                                            <span class="sub-title">{T(g['subtitle'])}</span>
                                            <h2>{T(g['heading'])}</h2>
                                        </div>
{paras(g['body'])}
                                        <div class="agk-button mb-30">
                                            {btn(T(g['button_label']), g['button_link'])}
                                        </div>
                                    </div>
                                </div>
                                <div class="col-xl-5">
                                    <div class="row stat-grid">
{stat_cards(g.get('stats'))}                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>
"""
    body += criteria_section(p["how_we_rate"])
    fq = p["faq"]
    body += f"""                    <!--======  FAQ Preview  ======-->
                    <section class="t10ic-faqs pt-130 pb-90">
                        <div class="container">
                            <div class="row">
                                <div class="col-lg-5">
{section_title(fq['subtitle'], fq['heading'], cls="mb-30")}                                    <div class="t10ic-content-box mb-40 pf_fadeup">
                                        <p>{MI(fq['text'])}</p>
                                        <div class="mt-30">{btn(T(fq['button_label']), "faq.html")}</div>
                                    </div>
                                </div>
                                <div class="col-lg-7">
{accordion(FAQ[:int(fq.get('count') or 3)], "homeFaq")}                                </div>
                            </div>
                        </div>
                    </section>
"""
    body += rg_cta()
    write("index.html", page(p["seo"], "home", body))


# ------------------------------------------------------------------ casino
def build_casino():
    p = pg("casino")
    body = banner(p["banner_title"], p["banner_text"], pill=f"Updated {SETTINGS['updated']}")
    body += offers_section("casino-offers", CASINO, "casino")
    body += disclaimer_strip()
    g = p["guide"]
    checks = "\n".join(f'                                            <li><i class="flaticon-check"></i>{MI(x)}</li>' for x in g.get("checklist", []))
    body += f"""                    <!--======  Casino Guide  ======-->
                    <section class="agk-about pt-120 pb-60">
                        <div class="container">
                            <div class="row">
                                <div class="col-lg-6">
{section_title(g['subtitle'], g['heading'], cls="mb-30")}                                </div>
                                <div class="col-lg-6">
                                    <div class="t10ic-content-box mb-40 pf_fadeup">
{paras(g['body'])}
                                        <ul class="check-list style-one mt-20">
{checks}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>
"""
    body += criteria_section(p["how_we_rate"])
    body += rg_cta()
    write("casino.html", page(p["seo"], "casino", body))


# ------------------------------------------------------------------ about
def build_about():
    p = pg("about")
    i, e, pr = p["intro"], p["experts"], p["principles"]
    body = banner(p["banner_title"], p["banner_text"], crumb=p["banner_title"])
    body += f"""                    <section class="agk-about pt-130 pb-80">
                        <div class="container">
                            <div class="row">
                                <div class="col-xl-7">
                                    <div class="agk-content-box style-one mb-50 pf_fadeup">
                                        <div class="section-title mb-20">
                                            <span class="sub-title">{T(i['subtitle'])}</span>
                                            <h2>{T(i['heading'])}</h2>
                                        </div>
{paras(i['body'])}
                                    </div>
                                </div>
                                <div class="col-xl-5">
                                    <div class="row stat-grid">
{stat_cards(i.get('stats'))}                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>
                    <!--======  Experts & Players  ======-->
                    <section class="agk-experts gray-dark pt-120 pb-90">
                        <div class="container">
                            <div class="row align-items-center">
                                <div class="col-lg-5">
{section_title(e['subtitle'], e['heading'], cls="mb-40")}                                </div>
                                <div class="col-lg-7">
                                    <div class="t10ic-content-box mb-40 pf_fadeup">
{paras(e['body'])}
                                    </div>
                                </div>
                            </div>
                            <div class="row">
{icon_boxes(e.get('boxes'), cols="col-lg-4 col-md-6", cls="criteria-box")}                            </div>
                        </div>
                    </section>
                    <section class="agk-features pt-120 pb-90">
                        <div class="container">
                            <div class="row align-items-center">
                                <div class="col-lg-6">
{section_title(pr['subtitle'], pr['heading'], cls="mb-45")}                                </div>
                                <div class="col-lg-6">
                                    <div class="text-box mb-40 pf_fadeup"><p>{MI(pr['intro'])}</p></div>
                                </div>
                            </div>
                            <div class="row">
{icon_boxes(pr.get('boxes'), cols="col-lg-3 col-md-6", cls="criteria-box principle-box", mb="mb-40")}                            </div>
                        </div>
                    </section>
"""
    body += rg_cta()
    write("about.html", page(p["seo"], "about", body))


# ------------------------------------------------------------------ faq
def build_faq():
    p = pg("faq")
    email = A(SETTINGS["email"])
    side = ""
    for b in p.get("sidebar", []):
        if b.get("link_type") == "helpline":
            link = f'<a href="{tel()}" class="help-mail"><i class="far fa-phone-alt"></i>{T(SETTINGS["helpline_number"])}</a>'
        else:
            link = f'<a href="mailto:{email}" class="help-mail"><i class="far fa-envelope"></i>{email}</a>'
        side += f"""                                        <div class="sidebar-box pf_fadeup">
                                            <h4>{T(b.get('title'))}</h4>
                                            <p>{MI(b.get('text'))}</p>
                                            {link}
                                        </div>
"""
    body = banner(p["banner_title"], p["banner_text"], crumb="FAQ")
    body += f"""                    <section class="t10ic-faqs pt-130 pb-90">
                        <div class="container">
                            <div class="row">
                                <div class="col-lg-8">
{section_title(p['subtitle'], p['heading'], cls="mb-40", p=p.get('intro'))}{accordion(FAQ, "faqPage")}                                </div>
                                <div class="col-lg-4">
                                    <aside class="legal-sidebar">
{side}                                    </aside>
                                </div>
                            </div>
                        </div>
                    </section>
"""
    body += rg_cta()
    write("faq.html", page(p["seo"], "guides", body))


# ------------------------------------------------------------------ contact
def build_contact():
    p = pg("contact")
    email = A(SETTINGS["email"])
    body = banner(p["banner_title"], p["banner_text"], crumb="Contact")
    body += f"""                    <section class="t10ic-service-details pt-130 pb-90">
                        <div class="container">
                            <div class="row">
                                <div class="col-lg-6">
{section_title(p['subtitle'], p['heading'], cls="mb-30")}                                    <div class="t10ic-content-box mb-40 pf_fadeup">
{paras(p['body'])}
                                    </div>
                                </div>
                                <div class="col-lg-6">
                                    <div class="contact-cards">
                                        <div class="t10ic-iconic-box style-seven contact-card mb-30 pf_fadeup">
                                            <div class="icon"><i class="fal fa-envelope-open-text"></i></div>
                                            <div class="content">
                                                <h4>{T(p['email_title'])}</h4>
                                                <p><a href="mailto:{email}">{email}</a></p>
                                            </div>
                                        </div>
                                        <div class="t10ic-iconic-box style-seven contact-card mb-30 pf_fadeup">
                                            <div class="icon"><i class="fal fa-hands-helping"></i></div>
                                            <div class="content">
                                                <h4>{T(p['support_title'])}</h4>
                                                <p>{T(p['support_text'])}<br><a href="{tel()}">{T(SETTINGS['helpline_number'])}</a></p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>
"""
    write("contact.html", page(p["seo"], "contact", body))


# ------------------------------------------------------------------ document pages
DOC_PAGES = [
    ("gambling-guide", "guides", "Gambling Guide", True),
    ("responsible-gambling", "guides", None, False),
    ("terms-and-conditions", "", None, False),
    ("privacy-policy", "", None, False),
    ("cookie-policy", "", None, False),
    ("affiliate-disclosure", "", None, True),
]


def build_document(name, active, crumb, _unused):
    p = pg(name)
    body = banner(p["banner_title"], p["banner_text"], crumb=crumb or p["banner_title"])
    body += document_body(p, SETTINGS["updated"] if p.get("show_updated") else None)
    if name in ("gambling-guide",):
        body += rg_cta()
    write(f"{name}.html", page(p["seo"], active, body))


# ------------------------------------------------------------------ reviews
def chips(items):
    return "".join(f'<span class="chip">{T(x)}</span>' for x in items or [])


def find_offer(data, slug):
    for o in data.get("offers", []):
        if o.get("enabled", True) and o.get("review") == slug:
            return o
    return None


def build_review(r):
    slug = r["_slug"]
    name = r.get("brand", "")
    sport = find_offer(SPORT, slug)
    casino = find_offer(CASINO, slug)
    visit_url = (sport or casino or {}).get("url") or r.get("visit_url") or ""
    track = f"{slug.replace('-review', '')}-sportsbook-review"
    invert = ' class="logo-invert"' if r.get("invert_logo") else ""
    lab = SETTINGS["offers"]

    def visit_btn(**kw):
        return btn(f"Visit {T(name)}", visit_url, target_blank=True, offer=track, **kw) if visit_url else ""

    score = float(r.get("score") or 0)
    score_rows = "".join(f'<li><span>{T(s.get("label"))}</span><span class="bar"><span style="width:{float(s.get("score") or 0)*10:.0f}%"></span></span><strong>{float(s.get("score") or 0):.1f}</strong></li>' for s in r.get("scores", []))
    glance = "".join(f"""
                                        <div class="col-md-6">
                                            <div class="glance-item mb-30 pf_fadeup">
                                                <div class="icon"><i class="fal {fa(g.get('icon'))}"></i></div>
                                                <div class="content"><h5>{T(g.get('title'))}</h5><p>{MI(g.get('text'))}</p></div>
                                            </div>
                                        </div>""" for g in r.get("glance", []))
    pros = "".join(f'<li><i class="far fa-check"></i>{MI(x)}</li>' for x in r.get("pros", []))
    cons = "".join(f'<li><i class="far fa-times"></i>{MI(x)}</li>' for x in r.get("cons", []))
    casino_btn = ""
    if casino and casino.get("url"):
        casino_btn = btn(f"Visit {T(name)} Casino", casino["url"], style="style-two", target_blank=True,
                         offer=f"{slug.replace('-review', '')}-casino-review")
    promos = "".join(f'<li><i class="fal {fa(x.get("icon"))}"></i><div><h5>{T(x.get("title"))}</h5><p>{MI(x.get("text"))}</p></div></li>' for x in r.get("promotions", []))

    welcome = ""
    if sport:
        welcome = f"""                    <!--======  Welcome offer  ======-->
                    <section class="review-offer pt-120 pb-60">
                        <div class="container">
                            <div class="welcome-box pf_fadeup">
                                <div class="row align-items-center">
                                    <div class="col-lg-8">
                                        <span class="sub-title">Welcome Offer</span>
                                        <h2>{T(sport.get('headline'))} <span>{T(sport.get('highlight'))}</span></h2>
                                        <p>{MI(r.get('offer_body'))}</p>
                                    </div>
                                    <div class="col-lg-4 text-lg-end">
                                        {btn("Claim the offer", sport.get('url') or '#', target_blank=True, offer=track)}
                                    </div>
                                </div>
                                <div class="offer-terms">{T(sport.get('terms'))}</div>
                            </div>
                        </div>
                    </section>
"""

    body = banner(r["title"], r.get("tagline", ""), crumb=r["title"])
    body += f"""                    <!--======  Review Hero (service-details layout)  ======-->
                    <section class="t10ic-service-details review-page pt-130 pb-60">
                        <div class="container">
                            <div class="row">
                                <div class="col-lg-7">
                                    <div class="t10ic-content-box mb-50 pf_fadeup">
                                        <div class="section-title mb-25">
                                            <span class="sub-title"><i class="fas fa-star"></i> Operator Review · {T(r.get('month'))}</span>
                                            <h2>{T(name)} — Sportsbook &amp; Casino</h2>
                                        </div>
                                        <p class="lead-text">{MI(r.get('lead'))}</p>
                                        <div class="review-actions mt-30">
                                            {visit_btn()}
                                            <span class="offer-tc"><span class="age-badge sm">18+</span> {T(lab['tcs_label'])}</span>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-lg-5">
                                    <div class="score-panel mb-50 pf_fadeup">
                                        <div class="score-head">
                                            <div class="offer-logo"><img{invert} src="{A(img_src(r.get('logo')))}" alt="{A(name)} logo"></div>
                                            <div class="score-total">
                                                <span class="label">Editor score</span>
                                                <div class="score">{score:.1f}<small>/10</small></div>
                                                <div class="stars">{stars(score)}</div>
                                            </div>
                                        </div>
                                        <ul class="score-bars">{score_rows}</ul>
                                        <span class="offer-licence"><i class="far fa-shield-check"></i> {T(lab['licence_prefix'])} {T(r.get('licence'))}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>
                    <!--======  At a glance  ======-->
                    <section class="review-glance gray-dark pt-120 pb-90">
                        <div class="container">
                            <div class="row">
                                <div class="col-lg-5">
{section_title("At a Glance", f"The key facts about {name}", cls="mb-30", p=r.get('glance_intro'))}                                </div>
                                <div class="col-lg-7">
                                    <div class="row">{glance}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>
{welcome}                    <!--======  Why it stands out  ======-->
                    <section class="agk-features pt-60 pb-60">
                        <div class="container">
                            <div class="row align-items-center">
                                <div class="col-lg-6">
{section_title(f"What makes {name} unique", f"Why {name} stands out in Ireland", cls="mb-40")}                                </div>
                                <div class="col-lg-6"><div class="text-box mb-40 pf_fadeup"><p>{MI(r.get('unique_intro'))}</p></div></div>
                            </div>
                            <div class="row">
{icon_boxes(r.get('unique'), cls="review-feature")}                            </div>
                            <div class="why-box mt-20 pf_fadeup">
                                <h4><i class="far fa-thumbs-up"></i> Why Irish players should pick {T(name)}</h4>
                                <p>{MI(r.get('why'))}</p>
                            </div>
                        </div>
                    </section>
                    <!--======  Pros & Cons  ======-->
                    <section class="review-proscons gray-dark pt-120 pb-90">
                        <div class="container">
                            <div class="row">
                                <div class="col-lg-12">
{section_title("Quick Verdict", "Pros & cons at a glance", center=True, cls="mb-50")}                                </div>
                                <div class="col-lg-6"><div class="pc-box pros mb-30 pf_fadeup"><h4>Pros</h4><ul>{pros}</ul></div></div>
                                <div class="col-lg-6"><div class="pc-box cons mb-30 pf_fadeup"><h4>Cons</h4><ul>{cons}</ul></div></div>
                            </div>
                        </div>
                    </section>
                    <!--======  Sportsbook  ======-->
                    <section class="agk-features pt-120 pb-60">
                        <div class="container">
                            <div class="row align-items-center">
                                <div class="col-lg-6">
{section_title("Sportsbook", r.get('sportsbook_title'), cls="mb-40")}                                </div>
                                <div class="col-lg-6"><div class="text-box mb-40 pf_fadeup"><p>{MI(r.get('sportsbook_intro'))}</p></div></div>
                            </div>
                            <div class="row">
{icon_boxes(r.get('sportsbook_features'), cls="review-feature")}                            </div>
                            <div class="chip-box pf_fadeup">
                                <h5>Sports you'll find on {T(name)}</h5>
                                <div class="chips">{chips(r.get('sports'))}</div>
                            </div>
                        </div>
                    </section>
                    <!--======  Casino  ======-->
                    <section class="agk-features gray-dark pt-120 pb-90">
                        <div class="container">
                            <div class="row align-items-center">
                                <div class="col-lg-6">
{section_title("Other Products", r.get('casino_title'), cls="mb-40")}                                </div>
                                <div class="col-lg-6"><div class="text-box mb-40 pf_fadeup"><p>{MI(r.get('casino_intro'))}</p></div></div>
                            </div>
                            <div class="row">
{icon_boxes(r.get('casino_features'), cols="col-lg-3 col-md-6", cls="review-feature")}                            </div>
                        </div>
                    </section>
                    <!--======  Banking & Promotions  ======-->
                    <section class="t10ic-service-details pt-120 pb-60">
                        <div class="container">
                            <div class="row">
                                <div class="col-lg-6">
                                    <div class="t10ic-content-box mb-50 pf_fadeup">
                                        <div class="section-title mb-25"><span class="sub-title">Banking</span><h2>Deposits, withdrawals &amp; payout times</h2></div>
                                        <p>{MI(r.get('banking_intro'))}</p>
                                        <div class="chips mt-20 mb-20">{chips(r.get('payments'))}</div>
                                        <p class="small-note">{MI(r.get('banking_note'))}</p>
                                    </div>
                                </div>
                                <div class="col-lg-6">
                                    <div class="t10ic-content-box mb-50 pf_fadeup">
                                        <div class="section-title mb-25"><span class="sub-title">Loyalty</span><h2>Ongoing promotions &amp; rewards</h2></div>
                                        <p>{MI(r.get('promotions_intro'))}</p>
                                        <ul class="promo-list mt-20">
                                            {promos}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>
                    <!--======  Safety  ======-->
                    <section class="agk-features gray-dark pt-120 pb-90">
                        <div class="container">
                            <div class="row align-items-center">
                                <div class="col-lg-6">
{section_title("Safety & Responsible Play", "Licensing, security and player protection", cls="mb-40")}                                </div>
                                <div class="col-lg-6"><div class="text-box mb-40 pf_fadeup"><p>{MI(r.get('safety'))}</p></div></div>
                            </div>
                            <div class="row">
{icon_boxes(r.get('safety_features'), cls="review-feature")}                            </div>
                        </div>
                    </section>
                    <!--======  Verdict  ======-->
                    <section class="review-verdict pt-120 pb-60">
                        <div class="container">
                            <div class="verdict-box pf_fadeup">
                                <div class="row">
                                    <div class="col-lg-8">
                                        <span class="sub-title">Our Verdict</span>
                                        <h2>{T(r.get('verdict_title'))}</h2>
                                        {t.MD(r.get('verdict', '')).replace(chr(10), '')}
                                    </div>
                                    <div class="col-lg-4">
                                        <div class="verdict-score">
                                            <div class="score">{score:.1f}<small>/10</small></div>
                                            <div class="stars">{stars(score)}</div>
                                            <div class="verdict-buttons">
                                                {visit_btn(extra="w-100")}
                                                {casino_btn}
                                            </div>
                                            <span class="offer-tc"><span class="age-badge sm">18+</span> {T(lab['tcs_label'])}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>
                    <!--======  FAQ  ======-->
                    <section class="t10ic-faqs pt-60 pb-90">
                        <div class="container">
                            <div class="row">
                                <div class="col-lg-4">
{section_title("FAQ", f"{name} — common questions", cls="mb-40")}                                </div>
                                <div class="col-lg-8">
{accordion(r.get('faqs', []), f"faq-{slug.replace('-review', '')}")}                                </div>
                            </div>
                        </div>
                    </section>
"""
    body += rg_cta()
    write(f"{slug}.html", page(r.get("seo", {}), "reviews", body))


def write_cms_config():
    """admin/config.yml is generated from _cms/cms-config.source.yml (shared field definitions
    under `x-` keys are expanded, because Sveltia CMS does not allow extra top-level keys)."""
    import yaml

    class NoAliasDumper(yaml.SafeDumper):
        def ignore_aliases(self, data):
            return True

    with open(os.path.join(HERE, "cms-config.source.yml"), encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    for key in [k for k in cfg if k.startswith("x-")]:
        del cfg[key]
    header = ("# GENERATED FILE - do not edit by hand.\n"
              "# Edit _cms/cms-config.source.yml and run: python _cms/build.py\n"
              "# The backend part (GitHub repository, branch, login URL) is added at runtime by backend.php\n"
              "# from your private cms-config.php file.\n\n")
    os.makedirs(os.path.join(SITE_DIR, "admin"), exist_ok=True)
    with open(os.path.join(SITE_DIR, "admin", "config.yml"), "w", encoding="utf-8") as f:
        f.write(header)
        yaml.dump(cfg, f, Dumper=NoAliasDumper, sort_keys=False, allow_unicode=True, width=100)


MANIFEST = os.path.join(HERE, "generated-pages.json")


def remove_stale_pages():
    """Delete pages this build generated before but no longer does (e.g. a review deleted in the CMS)."""
    try:
        with open(MANIFEST, encoding="utf-8") as f:
            previous = set(json.load(f))
    except (OSError, ValueError):
        previous = set()
    for name in sorted(previous - set(written)):
        path = os.path.join(SITE_DIR, name)
        if name.endswith(".html") and os.path.dirname(name) == "" and os.path.isfile(path):
            os.remove(path)
            print("removed", name)
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(sorted(written), f, indent=2)
        f.write("\n")


HTACCESS = os.path.join(SITE_DIR, ".htaccess")
BLOCK_START = "# BEGIN CMS offer links"
BLOCK_END = "# END CMS offer links"


def _apache_target(url):
    # In a RewriteRule substitution, % and $ start back-references; escape literal ones.
    return url.replace("\\", "\\\\").replace("%", "\\%").replace("$", "\\$")


def offer_redirect_rules():
    """Rules for offers whose short link (e.g. /link1) has an affiliate destination filled in."""
    seen = {}
    lines = []
    for label, data in (("Sportsbook", SPORT), ("Casino", CASINO)):
        for o in data.get("offers", []):
            short = (o.get("url") or "").strip()
            dest = (o.get("redirect_to") or "").strip()
            if not short.startswith("/") or not dest:
                continue
            if not re.match(r"^https?://\S+$", dest):
                print(f"WARNING: {o.get('brand')}: affiliate destination is not a valid http(s) URL, skipped")
                continue
            path = short.strip("/")
            if not re.match(r"^[A-Za-z0-9._~/-]+$", path):
                print(f"WARNING: {o.get('brand')}: short link {short} has unsupported characters, skipped")
                continue
            if path in seen:
                if seen[path] != dest:
                    print(f"WARNING: {short} is used by more than one offer with different destinations; "
                          f"keeping the first ({seen[path]})")
                continue
            seen[path] = dest
            pattern = "^" + re.sub(r"([.])", r"\\\1", path) + "/?$"
            lines.append(f"# {short} -> {o.get('brand')} ({label})")
            if "{gclid}" in dest:
                with_id = _apache_target(dest).replace("{gclid}", "%1")
                without = _apache_target(dest.replace("{gclid}", ""))
                lines.append("RewriteCond %{QUERY_STRING} (?:^|&)gclid=([^&]*)")
                lines.append(f"RewriteRule {pattern} {with_id} [R=302,L,NE]")
                lines.append(f"RewriteRule {pattern} {without} [R=302,L,NE]")
            else:
                flags = "R=302,L,NE,QSA" if "?" in dest else "R=302,L,NE"
                lines.append(f"RewriteRule {pattern} {_apache_target(dest)} [{flags}]")
    return lines


def write_htaccess():
    """Keep the generated offer-link block in updated-website/.htaccess up to date.
    Anything outside the BEGIN/END markers (e.g. redirects you add by hand) is left untouched."""
    rules = offer_redirect_rules()
    block = [BLOCK_START,
             "# Generated by _cms/build.py from the offers' \"Affiliate destination\" field in the CMS.",
             "# Do not edit inside this block - change the offer in /admin/ instead.",
             "# Add your own redirects outside this block (above or below), e.g.:",
             "#   RewriteRule ^link1/?$ https://partner.example/?c=123 [R=302,L,NE,QSA]"]
    if rules:
        block += ["<IfModule mod_rewrite.c>", "RewriteEngine On"] + rules + ["</IfModule>"]
    else:
        block += ["# (no affiliate destinations filled in yet)"]
    block.append(BLOCK_END)
    block_text = "\n".join(block) + "\n"
    try:
        with open(HTACCESS, encoding="utf-8") as f:
            current = f.read()
    except OSError:
        current = ("# Top 10 Irish Casino - Apache settings\n"
                   "Options -Indexes\n"
                   "ErrorDocument 404 /404.html\n\n"
                   "# Private CMS settings must never be downloadable, wherever they are placed\n"
                   "<FilesMatch \"^(cms-config\\.php|cms-config\\.example\\.php|\\.cms-login-attempts\\.json)$\">\n"
                   "    <IfModule mod_authz_core.c>\n        Require all denied\n    </IfModule>\n"
                   "    <IfModule !mod_authz_core.c>\n        Order allow,deny\n        Deny from all\n    </IfModule>\n"
                   "</FilesMatch>\n\n"
                   "# Offer short links (/link1, /link2, ...). Add hand-written redirects here, outside the CMS block.\n"
                   "<IfModule mod_rewrite.c>\n"
                   "RewriteEngine On\n"
                   "</IfModule>\n\n")
    if BLOCK_START in current and BLOCK_END in current:
        before = current.split(BLOCK_START)[0]
        after = current.split(BLOCK_END, 1)[1].lstrip("\n")
        new = before + block_text + ("\n" + after if after else "")
    else:
        new = current.rstrip("\n") + "\n\n" + block_text
    with open(HTACCESS, "w", encoding="utf-8") as f:
        f.write(new)


def build_404():
    p = pg("404")
    body = f"""                    <section class="t10ic-page-banner page-404">
                        <div class="shape shape-circle1"><span></span></div>
                        <div class="shape shape-circle2"><span></span></div>
                        <div class="container text-center">
                            <h1 class="page-title big-404">404</h1>
                            <h3 class="mb-20">{T(p['heading'])}</h3>
                            <p class="mb-40">{MI(p['text'])}</p>
                            {btn(T(p['button_label']), "index.html")}
                        </div>
                    </section>
"""
    write("404.html", page(p["seo"], "", body))


if __name__ == "__main__":
    build_index()
    build_casino()
    build_about()
    build_faq()
    for args in DOC_PAGES:
        build_document(*args)
    build_contact()
    for r in REVIEWS:
        build_review(r)
    build_404()
    if OUT == SITE_DIR:
        write_cms_config()
        remove_stale_pages()
        write_htaccess()
    print(f"Built {len(written)} pages into {os.path.relpath(OUT)}: " + ", ".join(written))
