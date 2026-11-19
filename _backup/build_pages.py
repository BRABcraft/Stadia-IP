"""Rebuild every STADIA IP page from the shared Squarespace header/footer shell.

Usage: python -I build_pages.py <site_dir>

Takes the <head>, header and footer from <site_dir>/solutions.html, sets the
nav to NAV below, and writes index.html plus each inner page with the content
defined here. The revenue estimator markup lives in engine-fragment.html.
Safe to run more than once.
"""
import html
import os
import re
import sys

SITE = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
CAL = "https://calendar.app.google/iaiNygTW1iEBeNHJ7"
LINKEDIN = "https://www.linkedin.com/in/bowman-founder"
TEL = "tel:+14053711564"
INVESTOR_MAILTO = "mailto:Bill@StadiaIP.com?subject=Investor%20information"

NAV = [
    ("solutions.html", "Solutions"),
    ("struxure.html", "StruXure"),
    ("who-we-serve.html", "Who We Serve"),
    ("concepts.html", "Concepts"),
    ("revenue.html", "Estimator"),
    ("about.html", "About"),
]


def btn(label, href, kind=""):
    cls = "sip-btn" + (" sip-btn--" + kind if kind else "")
    extra = ' target="_blank" rel="noopener"' if href.startswith("https://") else ""
    return '<a class="%s" href="%s"%s>%s</a>' % (cls, html.escape(href, quote=True), extra, label)


def hero(title, lead, buttons="", variant="", img=None):
    cls = "sip-hero" + (" sip-hero--" + variant if variant else "")
    media = ""
    if img:
        media = '<img class="sip-hero__img" src="./%s" alt="" aria-hidden="true"><div class="sip-hero__shade"></div>' % img
    btns = '<div class="sip-btns">%s</div>' % buttons if buttons else ""
    return """
<section class="%s">%s
  <div class="sip-wrap">
    <h1 class="sip-h1">%s</h1>
    <p class="sip-lead">%s</p>
    %s
  </div>
</section>""" % (cls, media, title, lead, btns)


def contact_strip(line='Book a 30 minute call, or call Bill at <span class="sip-nowrap">405-371-1564</span>.'):
    return """
<section class="sip-band sip-band--deep sip-band--short">
  <div class="sip-wrap sip-strip">
    <div>
      <h2 class="sip-h2">Get in touch</h2>
      <p>%s</p>
    </div>
    <div class="sip-btns">%s%s</div>
  </div>
</section>""" % (line, btn("Book a call", CAL, "light"), btn("Email Bill", "mailto:Bill@StadiaIP.com", "ghost"))


PAGES = {}

DESCRIPTIONS = {
    "index.html": "STADIA IP plans StruXure cabanas, container press boxes and premium seating for stadiums, schools and public venues.",
    "solutions.html": "Container buildings, StruXure shade and premium seating for athletic and public venues.",
    "who-we-serve.html": "STADIA IP works with colleges, high schools, cities and private venues.",
    "concepts.html": "Concept renderings of press boxes, sideline cabanas, covered decks and outdoor hospitality spaces.",
    "struxure.html": "StruXure motorized pergolas and Cabana X units planned into stadiums and outdoor venues.",
    "revenue.html": "Estimate yearly revenue from cabanas, lounge passes, events and sponsorship at your stadium.",
    "about.html": "STADIA IP was founded by Bill Bowman, a West Point graduate with decades in venue development.",
    "investors.html": "How investors and strategic partners can request information from STADIA IP.",
    "contact.html": "Book a 30 minute call with Bill Bowman, or email Bill@StadiaIP.com.",
}

# ---------------------------------------------------------------- Home
PAGES["index.html"] = ("STADIA IP", hero(
    "Premium seating and modular buildings for sports venues",
    "We plan cabanas, press boxes and covered seating for stadiums and public venues, and help you lease the space to fans and sponsors.",
    btn("Book a call", CAL) + btn("See solutions", "solutions.html", "ghost"),
    img="image+%281%29.png") + """
<section class="sip-band">
  <div class="sip-wrap">
    <h2 class="sip-h2">What we build</h2>
    <div class="sip-grid sip-grid--3">
      <a class="sip-card sip-card--link" href="solutions.html#modular">
        <img src="./image+%282%29.jpeg" alt="Shipping container press box behind home plate" loading="lazy">
        <h3 class="sip-h3">Container buildings</h3>
        <p>Press boxes, team rooms and storage built from shipping containers.</p>
      </a>
      <a class="sip-card sip-card--link" href="struxure.html">
        <img src="./image+%284%29.png" alt="Louvered pergola over an outdoor dining terrace" loading="lazy">
        <h3 class="sip-h3">StruXure shade</h3>
        <p>Motorized louvered roofs over cabanas and patios.</p>
      </a>
      <a class="sip-card sip-card--link" href="solutions.html#hospitality">
        <img src="./Image+2.jpeg" alt="Row of sponsor-branded sideline suites" loading="lazy">
        <h3 class="sip-h3">Premium seating</h3>
        <p>Sideline suites and lounges you can sell by the season.</p>
      </a>
    </div>
  </div>
</section>
<section class="sip-band sip-band--ink">
  <div class="sip-wrap sip-strip">
    <div>
      <h2 class="sip-h2">Revenue estimator</h2>
      <p class="sip-lead">Enter your stadium details and see a rough yearly figure for suites, lounge passes, events and sponsorship.</p>
    </div>
    <div class="sip-btns">""" + btn("Open the estimator", "revenue.html", "light") + """</div>
  </div>
</section>
<section class="sip-band">
  <div class="sip-wrap">
    <h2 class="sip-h2">Who we work with</h2>
    <ul class="sip-who">
      <li><a href="who-we-serve.html#colleges">Colleges and universities</a></li>
      <li><a href="who-we-serve.html#high-schools">High schools and districts</a></li>
      <li><a href="who-we-serve.html#cities">Cities and parks</a></li>
      <li><a href="who-we-serve.html#commercial">Restaurants, hotels and clubs</a></li>
    </ul>
  </div>
</section>
<section class="sip-band sip-band--paper">
  <div class="sip-wrap sip-founder sip-founder--short">
    <img src="./37-bill-bowman-founder-and-chief-deal-architect-of-stadia-ip.png" alt="Bill Bowman" loading="lazy">
    <div>
      <h2 class="sip-h2">Bill Bowman, founder</h2>
      <p class="sip-lead">Bill is a West Point graduate and former Army officer who has spent decades in venue development and concert production.</p>
      <a class="sip-textlink" href="about.html">More about Bill</a>
    </div>
  </div>
</section>""" + contact_strip())

# ---------------------------------------------------------------- Solutions
PAGES["solutions.html"] = ("Solutions", hero(
    "Solutions",
    "Most projects combine two of these. We size each one to the site and the budget.",
    img="Image+2.jpeg") + """
<section class="sip-band">
  <div class="sip-wrap">
    <div class="sip-row" id="modular">
      <div class="sip-row__media"><img src="./image+%282%29.jpeg" alt="Shipping container press box behind home plate at a softball field" loading="lazy"></div>
      <div>
        <h2 class="sip-h2">Container buildings</h2>
        <p class="sip-lead">Press boxes, camera decks, locker rooms and equipment storage made from shipping containers. Most of the work is done off site, then the units are set in place.</p>
      </div>
    </div>
    <div class="sip-row sip-row--flip" id="outdoor">
      <div class="sip-row__media"><img src="./image+%284%29.png" alt="Louvered pergola covering an outdoor dining terrace on a campus lawn" loading="lazy"></div>
      <div>
        <h2 class="sip-h2">Shade and outdoor rooms</h2>
        <p class="sip-lead">StruXure pergolas and cabanas with louvers that open for sun and close for rain.</p>
        <a class="sip-textlink" href="struxure.html">StruXure systems</a>
      </div>
    </div>
    <div class="sip-row" id="hospitality">
      <div class="sip-row__media"><img src="./Image.jpeg" alt="Covered premium viewing lounge overlooking a football stadium" loading="lazy"></div>
      <div>
        <h2 class="sip-h2">Premium seating and sponsor space</h2>
        <p class="sip-lead">Sideline suites, field-level lounges, donor areas and sponsor entrances. Each is planned so it can be leased by the season or rented by the event.</p>
        <a class="sip-textlink" href="revenue.html">Estimate the revenue</a>
      </div>
    </div>
    <p class="sip-note" style="margin-top:48px">Every project needs site-specific design, engineering and approvals.</p>
  </div>
</section>""" + contact_strip())

# ---------------------------------------------------------------- Who we serve
PAGES["who-we-serve.html"] = ("Who We Serve", hero(
    "Who we serve",
    "We work with athletic departments, school districts, cities and private businesses.",
    variant="red") + """
<section class="sip-band">
  <div class="sip-wrap">
    <div class="sip-grid sip-grid--2">
      <article class="sip-card" id="colleges">
        <img src="./838F419E-4EC3-4777-9674-FF2F9F514906.png" alt="Row of sideline cabanas at a college football stadium" loading="lazy">
        <h2 class="sip-h3">Colleges and universities</h2>
        <p>Sideline cabanas, donor lounges and sponsor-branded space at football and baseball stadiums.</p>
      </article>
      <article class="sip-card" id="high-schools">
        <img src="./image+%281%29.jpeg" alt="Container locker room and equipment room around a covered hitting area" loading="lazy">
        <h2 class="sip-h3">High schools and districts</h2>
        <p>Press boxes, team rooms, equipment storage and covered seating for home crowds.</p>
      </article>
      <article class="sip-card" id="cities">
        <img src="./image+%282%29.png" alt="Louvered pergola shading outdoor public seating" loading="lazy">
        <h2 class="sip-h3">Cities and parks</h2>
        <p>Shade for plazas, park pavilions and event lawns.</p>
      </article>
      <article class="sip-card" id="commercial">
        <img src="./Struxure+outdoor+kitchen.png" alt="Pergola-covered outdoor kitchen and bar beside a brick building" loading="lazy">
        <h2 class="sip-h3">Restaurants, hotels and clubs</h2>
        <p>Covered patios, outdoor bars and kitchens that stay open in more kinds of weather.</p>
      </article>
    </div>
  </div>
</section>""" + contact_strip())

# ---------------------------------------------------------------- Concepts
GALLERY = [
    ("image+%282%29.jpeg", "Home plate press box", "Stacked containers with a rooftop camera platform."),
    ("image+%281%29.jpeg", "Team building", "Locker room, coaches&rsquo; office and equipment room around a covered hitting area."),
    ("Image+2.jpeg", "Sideline suites", "Covered suites with sponsor branding on each unit."),
    ("838F419E-4EC3-4777-9674-FF2F9F514906.png", "Field-level cabanas", "Team-branded cabanas along the track."),
    ("Image.jpeg", "Covered deck", "Lounge seating and bar tables under a louvered roof."),
    ("image+%281%29.png", "Viewing lounge", "Cabana seating under a pergola above the stands."),
    ("image+%283%29.png", "Hospitality box", "Raised, covered seating for donors and guests."),
    ("image+%284%29.png", "Campus terrace", "Outdoor dining on a campus green."),
    ("image+%282%29.png", "Public seating", "Shaded seating for a city plaza."),
    ("Struxure+outdoor+kitchen.png", "Outdoor kitchen and bar", "Next to an athletic building."),
]

PAGES["concepts.html"] = ("Concepts", hero(
    "Concepts",
    "Concept renderings of the kinds of spaces we plan. Each one would be adjusted to the actual site.",
    variant="paper") + """
<section class="sip-band sip-band--tight">
  <div class="sip-wrap">
    <div class="sip-gallery">""" + "".join(
    '<figure><img src="./%s" alt="%s" loading="lazy"><figcaption><strong>%s</strong><span>%s</span></figcaption></figure>'
    % (src, re.sub(r"&\w+;", "", title), title, cap) for src, title, cap in GALLERY) + """
    </div>
    <p class="sip-note" style="margin-top:32px">Concept images only. Final designs need site-specific engineering and approvals.</p>
  </div>
</section>""" + contact_strip())

# ---------------------------------------------------------------- StruXure
PAGES["struxure.html"] = ("StruXure", hero(
    "StruXure outdoor systems",
    "StruXure makes motorized aluminum pergolas. The louvers rotate to let sun in or close against rain. "
    "We plan them into venues as cabanas, covered decks and patios.",
    img="Struxure+outdoor+kitchen.png") + """
<section class="sip-band">
  <div class="sip-wrap">
    <div class="sip-grid sip-grid--3">
      <article class="sip-card">
        <img src="./Image+2.jpeg" alt="Row of covered sideline suites at a football stadium" loading="lazy">
        <h2 class="sip-h3">Sideline cabanas</h2>
        <p>Cabana X units along the field, sold to groups or sponsors for the season.</p>
      </article>
      <article class="sip-card">
        <img src="./Image.jpeg" alt="Lounge under a louvered roof overlooking a stadium" loading="lazy">
        <h2 class="sip-h3">Covered decks</h2>
        <p>Shade over donor lounges and raised viewing areas.</p>
      </article>
      <article class="sip-card">
        <img src="./image+%284%29.png" alt="Louvered pergola over outdoor dining" loading="lazy">
        <h2 class="sip-h3">Patios and kitchens</h2>
        <p>Outdoor dining and bar space for campuses, clubs, hotels and restaurants.</p>
      </article>
    </div>
    <p class="sip-note" style="margin-top:40px">StruXure and Cabana X are trademarks of their respective owner.</p>
  </div>
</section>""" + contact_strip("Ask about product options, pricing and lead times for your area."))

# ---------------------------------------------------------------- Revenue estimator
ENGINE = open(os.path.join(HERE, "engine-fragment.html"), encoding="utf-8").read()
PAGES["revenue.html"] = ("Revenue Estimator", hero(
    "Revenue estimator",
    "Set your stadium details and choose what to add. The figures use average prices, so use them as a rough guide.",
    variant="paper") + "\n" + ENGINE + contact_strip("Bill can walk through these numbers with your actual site and schedule."))

# ---------------------------------------------------------------- About
PAGES["about.html"] = ("About", hero(
    "About STADIA IP",
    "STADIA IP plans cabanas, premium seating and modular buildings for sports and public venues. Bill Bowman founded the company.",
    variant="paper") + """
<section class="sip-band">
  <div class="sip-wrap sip-founder">
    <img src="./37-bill-bowman-founder-and-chief-deal-architect-of-stadia-ip.png" alt="William L. Bowman" loading="lazy">
    <div>
      <h2 class="sip-h2">William L. Bowman</h2>
      <p class="sip-role">Founder and Chief Deal Architect</p>
      <p>Bill grew up in a football family. His father, Dick Bowman, played both ways at Oklahoma under Bud Wilkinson and blocked for 1952 Heisman winner Billy Vessels. He went on to play for the New York Giants, coach, and later run professional and government sales for Rawlings.</p>
      <p>Bill graduated from West Point and served as an Army officer. Since then he has worked in venue development, concert production, commercial finance and enterprise sales.</p>
      <p>He started STADIA IP to help athletic directors and venue owners earn more from space they already have.</p>
      <div class="sip-btns">""" + btn("Talk to Bill", "contact.html") + btn("LinkedIn", LINKEDIN, "ghost") + """</div>
    </div>
  </div>
</section>
<section class="sip-band sip-band--paper sip-band--short">
  <div class="sip-wrap">
    <p style="margin:0">Investors and partners: <a class="sip-textlink" href="investors.html">investor information</a></p>
  </div>
</section>""")

# ---------------------------------------------------------------- Investors
PAGES["investors.html"] = ("Investors", hero(
    "Investors",
    "STADIA IP earns from venue projects, from product partnerships such as StruXure, and from the premium seating and sponsorship programs run in the finished space.",
    variant="paper") + """
<section class="sip-band">
  <div class="sip-wrap sip-row">
    <div>
      <h2 class="sip-h2">Request materials</h2>
      <p class="sip-lead">Email Bill with your name, your firm and what you are interested in. After a short review, he will send investor materials for private review.</p>
      <div class="sip-btns">""" + btn("Email Bill", INVESTOR_MAILTO) + btn("405-371-1564", TEL, "ghost") + """</div>
      <p class="sip-note" style="margin-top:24px">Nothing on this website is an offer to sell, or a solicitation of an offer to buy, any security.</p>
    </div>
    <div class="sip-row__media"><img src="./Image+2.jpeg" alt="Sponsor-branded sideline suites at a stadium" loading="lazy"></div>
  </div>
</section>""")

# ---------------------------------------------------------------- Contact
PAGES["contact.html"] = ("Contact", hero(
    "Talk to Bill",
    "Book a 30 minute call, or send a few details below and Bill will get back to you.",
    btn("Book a call", CAL, "light") + btn("405-371-1564", TEL, "ghost"),
    variant="red") + """
<section class="sip-band">
  <div class="sip-wrap sip-contact">
    <div>
      <ul class="sip-methods">
        <li><span>Email</span><a href="mailto:Bill@StadiaIP.com">Bill@StadiaIP.com</a></li>
        <li><span>Phone</span><a href="tel:+14053711564">405-371-1564</a></li>
        <li><span>LinkedIn</span><a href=\"""" + LINKEDIN + """\" target="_blank" rel="noopener">William L. Bowman</a></li>
      </ul>
      <h2 class="sip-h3">What happens next</h2>
      <p>The first call covers your site and what you want from it. If it looks like a fit, Bill visits and writes up a project scope with the right product partners.</p>
    </div>
    <form class="sip-form" id="sip-contact-form" novalidate>
      <h2 class="sip-h3">Send your details</h2>
      <p class="sip-note" style="margin-bottom:24px">This opens your email app with the message filled in.</p>
      <div class="sip-form__grid">
        <div><label for="f-name">Name</label><input id="f-name" name="name" autocomplete="name" required></div>
        <div><label for="f-org">Organization</label><input id="f-org" name="organization" autocomplete="organization"></div>
        <div><label for="f-email">Email</label><input id="f-email" name="email" type="email" autocomplete="email" required></div>
        <div><label for="f-phone">Phone</label><input id="f-phone" name="phone" type="tel" autocomplete="tel"></div>
        <div><label for="f-facility">Facility type</label>
          <select id="f-facility" name="facility">
            <option>College or university</option>
            <option>High school or district</option>
            <option>City or park</option>
            <option>Restaurant, hotel or club</option>
            <option>Other</option>
          </select></div>
        <div><label for="f-location">Location</label><input id="f-location" name="location" placeholder="City, State"></div>
        <div class="sip-form__full"><label for="f-timing">Timing</label>
          <select id="f-timing" name="timing">
            <option>Just looking</option>
            <option>Within 6 months</option>
            <option>6 to 12 months</option>
            <option>More than a year out</option>
          </select></div>
        <div class="sip-form__full"><label for="f-goals">About the project</label><textarea id="f-goals" name="goals"></textarea></div>
      </div>
      <button class="sip-btn" type="submit">Send</button>
      <p class="sip-form__status" id="sip-form-status" role="status" aria-live="polite"></p>
    </form>
  </div>
</section>""")


# ---------------------------------------------------------------- shell

def nav_desktop(current, style_delay):
    out = []
    for href, label in NAV:
        active = " header-nav-item--active" if href == current else ""
        out.append('\n    <div class="header-nav-item header-nav-item--external%s">\n'
                   '      <a href="%s" data-animation-role="header-element" class="preFade fadeIn" '
                   'style="transition-timing-function: ease; transition-duration: 0.65s; transition-delay: %s;">%s</a>\n'
                   '    </div>\n' % (active, href, style_delay, label))
    return "".join(out)


def nav_mobile():
    return "".join('\n          <div class="container header-menu-nav-item header-menu-nav-item--external">\n'
                   '            <a href="%s">%s</a>\n          </div>\n' % (href, label) for href, label in NAV)


def set_nav(header, current):
    # Desktop nav lists (there are two: one per header layout)
    def repl_desktop(m):
        delay = re.search(r"transition-delay: ([^;]+);", m.group(2))
        return m.group(1) + nav_desktop(current, delay.group(1) if delay else "0s") + m.group(3)
    header = re.sub(r'(<nav class="header-nav-list">)(.*?)(\s*</nav>)', repl_desktop, header, flags=re.S)
    # Mobile menu
    header = re.sub(r'(<div class="header-menu-nav-wrapper">)((?:\s*<div class="container header-menu-nav-item[^"]*">\s*<a href="[^"]*">[^<]*</a>\s*</div>)+)',
                    lambda m: m.group(1) + nav_mobile(), header, flags=re.S)
    header = header.replace("Talk to Bill ↗", "Talk to Bill")
    return header


def set_footer(footer):
    tagline = "Sports · Entertainment · Education · Municipal · Commercial"
    links = ('<a href="contact.html">Contact</a>&nbsp;&nbsp;&nbsp;<a href="investors.html">Investors</a>'
             '&nbsp;&nbsp;&nbsp;<a href="concepts.html">Concepts</a>')
    footer = footer.replace(tagline, links)
    footer = footer.replace("Preliminary website concept. Images are illustrative mockups.",
                            "Images are concept renderings.")
    return footer


def split_page(s):
    head_end = s.index("</head>")
    body_open_end = s.index(">", s.index("<body")) + 1
    main_start = s.index("<main")
    main_end = s.index("</main>") + len("</main>")
    return s[:head_end], s[head_end:body_open_end], s[body_open_end:main_start], s[main_end:]


def build():
    shell = open(os.path.join(SITE, "solutions.html"), encoding="utf-8").read()
    head, body_open, header, footer = split_page(shell)
    footer = set_footer(footer)
    if "stadia-pages.js" not in footer:
        footer = footer.replace("</body>", '<script src="./stadia-pages.js"></script>\n</body>', 1)
    footer = footer.replace('<script src="./stadia-engine.js"></script>\n', "")
    head = head.replace('<link rel="stylesheet" href="./stadia-engine.css">\n', "")
    for filename, (title, content) in PAGES.items():
        full_title = title if filename == "index.html" else "%s | STADIA IP" % title
        page_head = re.sub(r"<title>.*?</title>", "<title>%s</title>" % full_title, head, count=1, flags=re.S)
        page_head = re.sub(r'<meta name="description" content="[^"]*">',
                           '<meta name="description" content="%s">' % html.escape(DESCRIPTIONS[filename], quote=True), page_head, count=1)
        url = "https://www.stadiaip.com/" + ("" if filename == "index.html" else filename)
        page_head = re.sub(r'(<meta (?:name="twitter:url"|property="og:url") content=")[^"]*', r"\g<1>" + url, page_head)
        page_foot = footer
        if filename == "revenue.html":
            page_head += '<link rel="stylesheet" href="./stadia-engine.css">\n'
            page_foot = footer.replace("</body>", '<script src="./stadia-engine.js"></script>\n</body>', 1)
        main = '<main id="page" class="sip" role="main">%s\n</main>' % content
        write(filename, page_head + body_open + set_nav(header, filename) + main + page_foot)


def write(name, text):
    with open(os.path.join(SITE, name), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print("wrote", name, len(text))


build()
