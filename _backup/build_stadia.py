"""Build a working multi-page STADIA IP site from the saved Squarespace homepage.

Usage: python -I build_stadia.py <site_dir>
Reads <site_dir>/_backup/STADIA IP.original.html, writes index.html, the inner
pages, and turns "STADIA IP.html" into a redirect to index.html.
"""
import html
import os
import re
import sys

SITE = sys.argv[1]
SRC = os.path.join(SITE, "_backup", "STADIA IP.original.html")
SQ = "https://snail-tarpon-amw6.squarespace.com"
LINKEDIN = "https://www.linkedin.com/in/bowman-founder"
EMAIL = "Bill@StadiaIP.com"
TEL = "tel:+14053711564"
INVESTOR_MAILTO = "mailto:Bill@StadiaIP.com?subject=Investor%20Information%20Request"

HREF_MAP = {
    SQ + "/": "index.html",
    SQ + "/#page": "#page",
    SQ + "/#news": "solutions.html",
    SQ + "/#who-we-serve": "who-we-serve.html",
    SQ + "/#modular-facilities": "concepts.html",
    SQ + "/#about-2": "about.html",
    SQ + "/#social": "struxure.html",
    SQ + "/#get-in-touch": "contact.html",
    INVESTOR_MAILTO: "investors.html",
}
# Body buttons share placeholder hrefs, so they are matched by their label.
TEXT_MAP = [
    ("SCHEDULE A 30 MINUTE CALL", "contact.html"),
    ("LET'S DISCUSS YOUR VENUE", "contact.html"),
    ("SPEAK WITH BILL", "contact.html"),
    ("BILL ON LINKEDIN", LINKEDIN),
    ("REQUEST INVESTOR INFORMATION", "investors.html"),
    ("CALL 405-371-1564", TEL),
    ("EXPLORE SOLUTIONS", "#solutions"),
]
SECTION_IDS = {
    "6ae66061ed61a3612e575b8f": "playbook",
    "6ae6627238b2275fe7255842": "solutions",
    "6ae6691b6da4711e033e2418": "who-we-serve",
    "6ae66d7742c0e06d8f5ab399": "process",
    "6ae673f8df9ff834047198fa": "perspective",
    "6ae674afdf9ff8340471a8bd": "about",
    "6ae679a81dd0fa41af041792": "investors",
    "6ae67af637254162ede9a6b7": "faq",
    "6ae67c45d35cb84edfe9d939": "get-in-touch",
}


def link_text(inner):
    t = html.unescape(re.sub(r"<[^>]+>", " ", inner))
    t = t.replace("’", "'").replace("‘", "'")
    return " ".join(t.split()).upper()


def rewrite_link(m):
    tag, inner = m.group(1), m.group(2)
    href_m = re.search(r'href="([^"]*)"', tag)
    if not href_m:
        return m.group(0)
    old = html.unescape(href_m.group(1))
    text = link_text(inner)
    new = next((dest for label, dest in TEXT_MAP if text.startswith(label)), None)
    if new is None:
        new = HREF_MAP.get(old)
    if new is None:
        return m.group(0)
    tag = tag.replace(href_m.group(0), 'href="%s"' % html.escape(new, quote=True), 1)
    if new.startswith("https://"):
        if "target=" not in tag:
            tag = tag[:-1] + ' target="_blank" rel="noopener">'
    else:
        tag = re.sub(r'\s+target="_blank"', "", tag)
    return tag + inner + "</a>"


def remove_div_by_id(s, div_id):
    start = s.find('<div id="%s"' % div_id)
    if start < 0:
        return s
    depth, i = 0, start
    for m in re.finditer(r"<div\b|</div>", s[start:]):
        depth += 1 if m.group(0) == "<div" else -1
        if depth == 0:
            return s[:start] + s[start + m.end():]
    return s


def collapse_attr(m):
    return '%s="%s"' % (m.group(1), " ".join(m.group(2).split()))


def common_fixes(s):
    # Assets live next to the page, not in a nested *_files folder.
    s = s.replace("./STADIA IP_files/", "./")
    # Use the saved local copy of every Squarespace CDN image.
    s = re.sub(r"https://images\.squarespace-cdn\.com/content/v1/[^\"\s,&]*/([^/\"\s?,&]+)(\?[^\"\s,&]*)?",
               r"./\1", s)
    # crossorigin on local scripts blocks them when the page is opened as a file.
    s = re.sub(r'(<(?:script|link)\b[^>]*?)\s+crossorigin="anonymous"([^>]*(?:src|href)="\./)', r"\1\2", s)
    s = re.sub(r'(<(?:script|link)\b[^>]*(?:src|href)="\./[^"]*"[^>]*?)\s+crossorigin="anonymous"', r"\1", s)
    s = re.sub(r'<link rel="canonical"[^>]*>\s*', "", s)
    # <base href="."> makes "#anchor" links point at the folder instead of the page.
    s = re.sub(r'<base href="[^"]*">\s*', "", s)
    s = re.sub(r'(data-current-styles|data-language-picker)="([^"]*)"', collapse_attr, s)
    # The page was saved mid-scroll, which froze the header in its hidden state.
    s = s.replace('class="white header theme-col--primary shrink"', 'class="white header theme-col--primary"', 1)
    s = s.replace(" transform: translateY(-100%);\" data-controllers-bound=\"Header\"", "\" data-controllers-bound=\"Header\"", 1)
    # It was also saved at desktop width, so the mobile header items never got
    # their fade-in class and stay invisible on phones.
    h0, h1 = s.index("<header"), s.index("</header>")
    header = re.sub(r'class="([^"]*\bpreFade\b)(?![^"]*\bfadeIn\b)([^"]*)"', r'class="\1\2 fadeIn"', s[h0:h1])
    s = s[:h0] + header + s[h1:]
    s = remove_div_by_id(s, "floatingCart")
    s = re.sub(r"(<a\b[^>]*>)(.*?)</a>", rewrite_link, s, flags=re.S)
    s = s.replace("</head>", '<link rel="stylesheet" href="./stadia-pages.css">\n</head>', 1)
    return s


def add_section_ids(s):
    for sid, anchor in SECTION_IDS.items():
        s = re.sub(r'(<section\b)([^>]*data-section-id="%s")' % sid,
                   r'\1 id="%s"\2' % anchor, s, count=1)
    return s


def split_page(s):
    head_end = s.index("</head>")
    body_open_end = s.index(">", s.index("<body")) + 1
    main_start = s.index("<main")
    main_end = s.index("</main>") + len("</main>")
    return s[:head_end], s[head_end:body_open_end], s[body_open_end:main_start], s[main_end:]


# ---------- shared page fragments ----------

def hero(eyebrow, title, lead, buttons, variant="", img=None, note=None):
    cls = "sip-hero" + (" sip-hero--" + variant if variant else "")
    media = ""
    if img:
        media = '<img class="sip-hero__img" src="./%s" alt="" aria-hidden="true"><div class="sip-hero__shade"></div>' % img
    note_html = '<p class="sip-note" style="margin-top:20px">%s</p>' % note if note else ""
    return """
<section class="%s">%s
  <div class="sip-wrap">
    <p class="sip-eyebrow">%s</p>
    <h1 class="sip-h1">%s</h1>
    <p class="sip-lead">%s</p>
    <div class="sip-btns">%s</div>%s
  </div>
</section>""" % (cls, media, eyebrow, title, lead, buttons, note_html)


def btn(label, href, kind=""):
    cls = "sip-btn" + (" sip-btn--" + kind if kind else "")
    extra = ' target="_blank" rel="noopener"' if href.startswith("https://") else ""
    return '<a class="%s" href="%s"%s>%s</a>' % (cls, html.escape(href, quote=True), extra, label)


CTA = """
<section class="sip-band sip-band--deep">
  <div class="sip-wrap">
    <p class="sip-eyebrow">Let&rsquo;s build what&rsquo;s next</p>
    <h2 class="sip-h2">Your next revenue opportunity could be right in front of you.</h2>
    <p class="sip-lead">Have a stadium, athletic complex, municipal property or commercial venue in mind? Start with a conversation about what&rsquo;s possible.</p>
    <div class="sip-btns">%s%s</div>
  </div>
</section>""" % (btn("Schedule a 30 minute call &#8599;", "contact.html", "light"),
                 btn("Call 405-371-1564", TEL, "ghost"))

PROCESS = """
<div class="sip-grid sip-grid--4 sip-steps">
  <div class="sip-step"><span class="sip-step__num">01</span><h3 class="sip-h3">Discover</h3><p>We learn about your property, challenges, goals and available spaces.</p></div>
  <div class="sip-step"><span class="sip-step__num">02</span><h3 class="sip-h3">Imagine</h3><p>We identify modular, architectural and revenue generating possibilities.</p></div>
  <div class="sip-step"><span class="sip-step__num">03</span><h3 class="sip-h3">Plan</h3><p>We coordinate relevant product partners and develop a tailored project scope.</p></div>
  <div class="sip-step"><span class="sip-step__num">04</span><h3 class="sip-h3">Activate</h3><p>We explore how the improvement can support events, partnerships and long term value.</p></div>
</div>"""


def ul(items):
    return '<ul class="sip-list">%s</ul>' % "".join("<li>%s</li>" % i for i in items)


# ---------- page content ----------

PAGES = {}

PAGES["solutions.html"] = ("Solutions", hero(
    "What we build",
    "One partner. Multiple ways to reimagine your venue.",
    "From fast, flexible athletic support spaces to premium outdoor hospitality, we help plan improvements around what your facility needs and what it could become.",
    btn("Schedule a 30 minute call &#8599;", "contact.html") + btn("See concepts", "concepts.html", "ghost"),
    img="Image+2.jpeg") + """
<section class="sip-band">
  <div class="sip-wrap">
    <div class="sip-row">
      <div class="sip-row__media"><img src="./image+%282%29.jpeg" alt="Shipping container press box behind home plate at a softball field" loading="lazy"></div>
      <div>
        <p class="sip-eyebrow">01 / Modular</p>
        <h2 class="sip-h2">Modular athletic infrastructure</h2>
        <p class="sip-lead">Shipping container based press boxes, observation decks, equipment facilities, support spaces and adaptable venue structures for schools and athletic programs.</p>
        """ + ul(["Press boxes and elevated viewing areas", "Observation decks", "Equipment storage and team support spaces",
                  "Covered training corridors", "Modular event infrastructure"]) + """
        <p class="sip-note">All concepts require site-specific design, engineering and approvals.</p>
      </div>
    </div>
    <div class="sip-row sip-row--flip">
      <div class="sip-row__media"><img src="./image+%284%29.png" alt="Louvered pergola covering an outdoor dining terrace on a campus lawn" loading="lazy"></div>
      <div>
        <p class="sip-eyebrow">02 / Outdoor</p>
        <h2 class="sip-h2">Premium outdoor environments</h2>
        <p class="sip-lead">Architectural shade, motorized pergolas, cabanas and gathering areas that extend the comfort and usability of outdoor spaces.</p>
        """ + ul(["Architectural shade", "Motorized pergolas", "Cabanas", "Covered gathering and dining areas"]) + """
        <a class="sip-textlink" href="struxure.html">About StruXure systems &rarr;</a>
      </div>
    </div>
    <div class="sip-row">
      <div class="sip-row__media"><img src="./Image.jpeg" alt="Covered premium viewing lounge overlooking a football stadium" loading="lazy"></div>
      <div>
        <p class="sip-eyebrow">03 / Revenue</p>
        <h2 class="sip-h2">Hospitality &amp; revenue spaces</h2>
        <p class="sip-lead">VIP viewing, sponsor entrances, alumni gathering spaces, event areas and opportunities for premium access and commercial activation.</p>
        """ + ul(["VIP and premium viewing", "Sponsor entrances and branded spaces", "Alumni and donor gathering spaces",
                  "Event areas", "Premium access and commercial activation"]) + """
      </div>
    </div>
  </div>
</section>
<section class="sip-band sip-band--ink">
  <div class="sip-wrap">
    <p class="sip-eyebrow">A smarter playbook</p>
    <h2 class="sip-h2">From a facilities arms race to a revenue arms race.</h2>
    <div class="sip-grid sip-grid--2">
      <p class="sip-lead">Facility upgrades should do more than look impressive. They should help institutions create value from spaces, audiences and relationships they already have.</p>
      <p class="sip-lead">STADIA IP brings together venue planning, modular building concepts, premium outdoor systems and commercial strategy to help turn unused potential into meaningful experiences and revenue opportunities.</p>
    </div>
  </div>
</section>""" + CTA)

PAGES["who-we-serve.html"] = ("Who We Serve", hero(
    "Who we serve",
    "Designed around the people who use the space.",
    "Every institution has different goals. We help translate those goals into functional environments with long term potential.",
    btn("Let&rsquo;s discuss your venue &#8599;", "contact.html", "light") + btn("Explore solutions", "solutions.html", "ghost"),
    variant="red") + """
<section class="sip-band">
  <div class="sip-wrap">
    <div class="sip-grid sip-grid--2">
      <article class="sip-card">
        <img src="./838F419E-4EC3-4777-9674-FF2F9F514906.png" alt="Row of sideline cabanas at a college football stadium" loading="lazy">
        <h2 class="sip-h3">Colleges &amp; universities</h2>
        <p>Stadiums, donor hospitality, premium seating, sponsorship spaces and alumni programs.</p>
        """ + ul(["Sideline cabanas and premium seating", "Donor and alumni hospitality areas", "Sponsor-branded spaces and entrances"]) + """
      </article>
      <article class="sip-card">
        <img src="./image+%281%29.jpeg" alt="Container locker room and equipment room around a covered hitting area" loading="lazy">
        <h2 class="sip-h3">High schools &amp; districts</h2>
        <p>Press boxes, training areas, spectator amenities and multipurpose athletic facilities.</p>
        """ + ul(["Press boxes and elevated viewing", "Equipment and training spaces", "Covered spectator and gathering areas"]) + """
      </article>
      <article class="sip-card">
        <img src="./image+%282%29.png" alt="Louvered pergola shading outdoor public seating" loading="lazy">
        <h2 class="sip-h3">Municipalities</h2>
        <p>Public gathering areas, parks, civic facilities and community event spaces.</p>
        """ + ul(["Shaded public gathering areas", "Park and civic facility improvements", "Community event spaces"]) + """
      </article>
      <article class="sip-card">
        <img src="./Struxure+outdoor+kitchen.png" alt="Pergola-covered outdoor kitchen and bar beside a brick building" loading="lazy">
        <h2 class="sip-h3">Commercial venues</h2>
        <p>Restaurants, hotels, clubs, entertainment properties and outdoor hospitality.</p>
        """ + ul(["Outdoor dining and bar areas", "Club and hotel hospitality spaces", "Entertainment and event venues"]) + """
      </article>
    </div>
  </div>
</section>
<section class="sip-band sip-band--paper">
  <div class="sip-wrap">
    <div class="sip-intro">
      <p class="sip-eyebrow">Our process</p>
      <h2 class="sip-h2">From first conversation to facility concept.</h2>
    </div>""" + PROCESS + """
  </div>
</section>""" + CTA)

GALLERY = [
    ("image+%282%29.jpeg", "Home plate press box", "Stacked shipping container press box with rooftop camera platform."),
    ("image+%281%29.jpeg", "Team support complex", "Container locker room, coaches&rsquo; office and equipment room around a covered hitting area."),
    ("Image+2.jpeg", "Sideline luxury suites", "A row of covered sideline suites with sponsor branding on every unit."),
    ("838F419E-4EC3-4777-9674-FF2F9F514906.png", "Field-level cabanas", "Program-branded cabanas lining the track at field level."),
    ("Image.jpeg", "Covered premium deck", "Lounge seating and bar tables under a louvered roof with a full view of the field."),
    ("image+%281%29.png", "Premium viewing lounge", "Cabana-style seating beneath a louvered pergola above the stands."),
    ("image+%283%29.png", "Elevated hospitality box", "Covered, elevated viewing for donors, sponsors and guests."),
    ("image+%284%29.png", "Campus terrace", "Louvered pergola over outdoor dining on a campus green."),
    ("image+%282%29.png", "Public gathering space", "Shaded seating for civic, municipal and community use."),
    ("Struxure+outdoor+kitchen.png", "Outdoor kitchen &amp; bar", "Pergola-covered outdoor kitchen beside an athletic facility."),
]

PAGES["concepts.html"] = ("Concepts", hero(
    "Concepts",
    "Modular facilities, premium spaces, real possibilities.",
    "A look at the kinds of spaces STADIA IP helps plan: container-based athletic structures, covered premium seating and outdoor hospitality that can host events, sponsors and fans.",
    btn("Schedule a 30 minute call &#8599;", "contact.html") + btn("Explore solutions", "solutions.html", "ghost"),
    img="image+%281%29.png",
    note="Concept imagery shown for planning and discussion purposes.") + """
<section class="sip-band">
  <div class="sip-wrap">
    <div class="sip-intro">
      <p class="sip-eyebrow">Concept gallery</p>
      <h2 class="sip-h2">What your venue could become.</h2>
      <p class="sip-lead">Shipping container structures can serve as press boxes, elevated viewing areas, equipment storage, team support spaces, covered training corridors and modular event infrastructure. Premium outdoor systems add shade, comfort and hospitality.</p>
    </div>
    <div class="sip-gallery">""" + "".join(
    '<figure><img src="./%s" alt="%s concept" loading="lazy"><figcaption><strong>%s</strong><span>%s</span></figcaption></figure>'
    % (src, re.sub("&amp;", "and", title), title, cap) for src, title, cap in GALLERY) + """
    </div>
    <p class="sip-note" style="margin-top:32px">Concept imagery shown for planning and discussion purposes. All concepts require site-specific design, engineering and approvals.</p>
  </div>
</section>
<section class="sip-band sip-band--ink">
  <div class="sip-wrap">
    <div class="sip-intro">
      <p class="sip-eyebrow">Our process</p>
      <h2 class="sip-h2">From first conversation to facility concept.</h2>
    </div>""" + PROCESS + """
  </div>
</section>""" + CTA)

FAQ = [
    ("What does STADIA IP do?", "STADIA IP develops venue improvement concepts and complementary revenue programs for university athletic departments, high schools, municipal facilities and commercial properties. Solutions may involve modular structures, premium outdoor architecture and hospitality spaces."),
    ("Can STADIA IP help with high school athletic facilities?", "Yes. We can explore press boxes, spectator amenities, equipment and training spaces, covered gathering areas and other facility improvements for schools and districts."),
    ("What can shipping container structures be used for?", "Potential applications include press boxes, elevated viewing areas, equipment storage, team support spaces, covered training corridors and modular event infrastructure. All concepts require site-specific design, engineering and approvals."),
    ("Do you offer StruXure products?", "STADIA IP&rsquo;s business model includes StruXure premium outdoor systems. Contact Bill to discuss product options, territory and project availability."),
    ("How do we start a project?", "Email Bill to request a 30 minute discovery conversation. Share your facility type, location, goals and desired timing so the team can discuss possible next steps."),
]
FAQ_HTML = '<div class="sip-faq">%s</div>' % "".join(
    "<details><summary>%s</summary><p>%s</p></details>" % (q, a) for q, a in FAQ)

PAGES["about.html"] = ("About", hero(
    "The STADIA IP perspective",
    "Don&rsquo;t just build a better venue. Build a better business around it.",
    '<span class="sip-tagline">Design &middot; Infrastructure &middot; Experience &middot; Revenue</span>',
    btn("Speak with Bill &#8599;", "contact.html") + btn("Explore solutions", "solutions.html", "ghost"),
    img="Image.jpeg") + """
<section class="sip-band">
  <div class="sip-wrap">
    <div class="sip-row">
      <div>
        <p class="sip-eyebrow">A smarter playbook</p>
        <h2 class="sip-h2">From a facilities arms race to a revenue arms race.</h2>
        <p class="sip-lead">Facility upgrades should do more than look impressive. They should help institutions create value from spaces, audiences and relationships they already have.</p>
        <p class="sip-lead">STADIA IP brings together venue planning, modular building concepts, premium outdoor systems and commercial strategy to help turn unused potential into meaningful experiences and revenue opportunities.</p>
      </div>
      <div class="sip-row__media"><img src="./image+%283%29.png" alt="Guests in a covered hospitality box overlooking a football game" loading="lazy"></div>
    </div>
  </div>
</section>
<section class="sip-band sip-band--paper" id="founder">
  <div class="sip-wrap sip-founder">
    <img src="./37-bill-bowman-founder-and-chief-deal-architect-of-stadia-ip.png" alt="William L. Bowman, Founder and Chief Deal Architect of STADIA IP" loading="lazy">
    <div>
      <p class="sip-eyebrow">Meet the founder</p>
      <h2 class="sip-h2">William L. Bowman</h2>
      <p class="sip-eyebrow" style="color:var(--sip-ink)">Founder &amp; Chief Deal Architect</p>
      <p>Bill Bowman&rsquo;s connection to athletics is more than a career&mdash;it&rsquo;s a lifelong legacy rooted in one of college football&rsquo;s most celebrated traditions.</p>
      <p>Raised in a football coaching family, Bill is the son of Dick Bowman, a two-way player for the University of Oklahoma under legendary coach Bud Wilkinson. Dick blocked for 1952 Heisman Trophy winner Billy Vessels and helped lay the foundation for Oklahoma&rsquo;s historic 47-game winning streak. Drafted by the New York Giants, he played under NFL icons Tom Landry and Vince Lombardi before pursuing a distinguished coaching career and eventually leading professional and government sales for Rawlings Sporting Goods.</p>
      <p>Growing up immersed in athletics and the facilities that support them, Bill developed an early understanding of the people, operations, and infrastructure behind successful sports programs. He carried that foundation to West Point, graduating from the United States Military Academy and serving as a U.S. Army officer.</p>
      <p>Over the following decades, Bill built a diverse career spanning venue development, concert production, commercial financing, executive leadership, and complex enterprise sales. His experience combines hands-on operational knowledge with the ability to develop strategic partnerships and navigate sophisticated business opportunities.</p>
      <p>Today, as Founder and Chief Deal Architect of STADIA IP, Bill brings together his athletic heritage, military leadership, extensive industry relationships, and decades of business experience to help athletic directors, university leaders, and commercial partners transform underutilized spaces into valuable, revenue-generating assets.</p>
      <div class="sip-btns">""" + btn("Speak with Bill &#8599;", "contact.html") + btn("Bill on LinkedIn &#8599;", LINKEDIN, "ghost") + """</div>
    </div>
  </div>
</section>
<section class="sip-band" id="faq">
  <div class="sip-wrap">
    <div class="sip-intro">
      <p class="sip-eyebrow">STADIA IP details</p>
      <h2 class="sip-h2">Questions before we start?</h2>
    </div>""" + FAQ_HTML + """
  </div>
</section>""" + CTA)

PAGES["struxure.html"] = ("StruXure", hero(
    "Premium outdoor systems",
    "StruXure, built into the venue plan.",
    "STADIA IP&rsquo;s business model includes StruXure premium outdoor systems: architectural shade, motorized pergolas and cabanas that extend the comfort and usability of outdoor spaces.",
    btn("Ask about StruXure &#8599;", "contact.html") + btn("See concepts", "concepts.html", "ghost"),
    img="Struxure+outdoor+kitchen.png") + """
<section class="sip-band">
  <div class="sip-wrap">
    <div class="sip-intro">
      <p class="sip-eyebrow">Where it fits</p>
      <h2 class="sip-h2">Comfort that creates new reasons to gather.</h2>
      <p class="sip-lead">Covered, comfortable outdoor space can become premium seating, sponsor inventory, donor hospitality or an everyday amenity. We plan StruXure systems as part of the venue experience, not as an add-on.</p>
    </div>
    <div class="sip-grid sip-grid--3">
      <article class="sip-card">
        <img src="./Image+2.jpeg" alt="Row of covered sideline suites at a football stadium" loading="lazy">
        <h3 class="sip-h3">Sideline cabanas &amp; suites</h3>
        <p>Premium, sponsor-ready seating along the field that turns game day into a hospitality experience.</p>
      </article>
      <article class="sip-card">
        <img src="./Image.jpeg" alt="Lounge under a louvered roof overlooking a stadium" loading="lazy">
        <h3 class="sip-h3">Covered viewing decks</h3>
        <p>Shade and weather comfort for elevated viewing, donor lounges and VIP areas.</p>
      </article>
      <article class="sip-card">
        <img src="./image+%284%29.png" alt="Louvered pergola over outdoor dining" loading="lazy">
        <h3 class="sip-h3">Outdoor hospitality</h3>
        <p>Dining terraces, outdoor kitchens and gathering areas for campuses, clubs, hotels and restaurants.</p>
      </article>
    </div>
  </div>
</section>
<section class="sip-band sip-band--paper">
  <div class="sip-wrap sip-row">
    <div>
      <p class="sip-eyebrow">Product options</p>
      <h2 class="sip-h2">Let&rsquo;s talk products, territory and timing.</h2>
      <p class="sip-lead">Contact Bill to discuss StruXure product options, territory and project availability for your venue.</p>
      <div class="sip-btns">""" + btn("Talk to Bill &#8599;", "contact.html") + btn("Email Bill", "mailto:Bill@StadiaIP.com?subject=StruXure%20Inquiry", "ghost") + """</div>
    </div>
    <div class="sip-row__media"><img src="./image+%281%29.png" alt="Fans in cabana seating beneath a louvered pergola" loading="lazy"></div>
  </div>
  <div class="sip-wrap"><p class="sip-note" style="margin-top:40px">StruXure is a trademark of its respective owner. Concept imagery shown for planning and discussion purposes.</p></div>
</section>""" + CTA)

PAGES["investors.html"] = ("Investors", hero(
    "For strategic partners &amp; investors",
    "Interested in the bigger picture?",
    "STADIA IP is developing a scalable approach that combines venue projects, product partnerships and institutional revenue programs. Qualified investors and strategic partners can request information for private review.",
    btn("Request investor information &#8599;", INVESTOR_MAILTO) + btn("Meet the founder", "about.html#founder", "ghost"),
    variant="paper") + """
<section class="sip-band sip-band--ink">
  <div class="sip-wrap">
    <div class="sip-intro">
      <p class="sip-eyebrow">The approach</p>
      <h2 class="sip-h2">Three parts, one platform.</h2>
    </div>
    <div class="sip-grid sip-grid--3">
      <div class="sip-step"><span class="sip-step__num">01</span><h3 class="sip-h3">Venue projects</h3><p>Modular, architectural and hospitality improvements for athletic, municipal and commercial venues.</p></div>
      <div class="sip-step"><span class="sip-step__num">02</span><h3 class="sip-h3">Product partnerships</h3><p>Premium systems, such as StruXure outdoor structures, coordinated into each project scope.</p></div>
      <div class="sip-step"><span class="sip-step__num">03</span><h3 class="sip-h3">Institutional revenue programs</h3><p>Premium access, sponsorship and event activation built around the improved space.</p></div>
    </div>
  </div>
</section>
<section class="sip-band">
  <div class="sip-wrap sip-row">
    <div>
      <p class="sip-eyebrow">How to request information</p>
      <h2 class="sip-h2">Private review, by request.</h2>
      <ol class="sip-numbered">
        <li>Email Bill with your name, firm or organization, and the nature of your interest.</li>
        <li>Your inquiry is reviewed.</li>
        <li>Investor materials are shared separately for private review.</li>
      </ol>
      <div class="sip-btns">""" + btn("Request investor information &#8599;", INVESTOR_MAILTO) + btn("Call 405-371-1564", TEL, "ghost") + """</div>
      <p class="sip-note" style="margin-top:24px">Investor materials are shared separately after inquiry review. Nothing on this website is an offer to sell, or a solicitation of an offer to buy, any security.</p>
    </div>
    <div class="sip-row__media"><img src="./Image+2.jpeg" alt="Sponsor-branded sideline suites at a stadium" loading="lazy"></div>
  </div>
</section>""")

PAGES["contact.html"] = ("Talk to Bill", hero(
    "Let&rsquo;s build what&rsquo;s next",
    "Schedule a 30 minute call.",
    "Have a stadium, athletic complex, municipal property or commercial venue in mind? Start with a conversation about what&rsquo;s possible.",
    btn("Email Bill &#8599;", "mailto:Bill@StadiaIP.com?subject=30%20Minute%20Call%20Request", "light") + btn("Call 405-371-1564", TEL, "ghost"),
    variant="red") + """
<section class="sip-band">
  <div class="sip-wrap sip-contact">
    <div>
      <p class="sip-eyebrow">Talk to Bill</p>
      <h2 class="sip-h2">William L. Bowman</h2>
      <p>Founder &amp; Chief Deal Architect</p>
      <ul class="sip-methods">
        <li><span>Email</span><a href="mailto:Bill@StadiaIP.com">Bill@StadiaIP.com</a></li>
        <li><span>Phone</span><a href="tel:+14053711564">405-371-1564</a></li>
        <li><span>LinkedIn</span><a href=\"""" + LINKEDIN + """\" target="_blank" rel="noopener">Bill on LinkedIn &#8599;</a></li>
      </ul>
      <h3 class="sip-h3">What to share</h3>
      <p>To make the first conversation count, tell us:</p>
      """ + ul(["Your facility type", "Location", "Goals for the space", "Desired timing"]) + """
    </div>
    <form class="sip-form" id="sip-contact-form" novalidate>
      <h3 class="sip-h3">Request a discovery call</h3>
      <p class="sip-note" style="margin-bottom:24px">Sending opens your email app with these details filled in, addressed to Bill.</p>
      <div class="sip-form__grid">
        <div><label for="f-name">Name</label><input id="f-name" name="name" autocomplete="name" required></div>
        <div><label for="f-org">Organization</label><input id="f-org" name="organization" autocomplete="organization"></div>
        <div><label for="f-email">Email</label><input id="f-email" name="email" type="email" autocomplete="email" required></div>
        <div><label for="f-phone">Phone</label><input id="f-phone" name="phone" type="tel" autocomplete="tel"></div>
        <div><label for="f-facility">Facility type</label>
          <select id="f-facility" name="facility">
            <option>College or university</option>
            <option>High school or district</option>
            <option>Municipality</option>
            <option>Commercial venue</option>
            <option>Other</option>
          </select></div>
        <div><label for="f-location">Location</label><input id="f-location" name="location" placeholder="City, State"></div>
        <div class="sip-form__full"><label for="f-timing">Desired timing</label>
          <select id="f-timing" name="timing">
            <option>Exploring options</option>
            <option>Within 6 months</option>
            <option>6 to 12 months</option>
            <option>12 months or more</option>
          </select></div>
        <div class="sip-form__full"><label for="f-goals">Goals for the space</label><textarea id="f-goals" name="goals" placeholder="What would you like this space to do for your program, fans or partners?"></textarea></div>
      </div>
      <button class="sip-btn" type="submit">Send to Bill &#8599;</button>
      <p class="sip-form__status" id="sip-form-status" role="status" aria-live="polite"></p>
    </form>
  </div>
</section>
<section class="sip-band sip-band--paper">
  <div class="sip-wrap">
    <div class="sip-intro">
      <p class="sip-eyebrow">What happens next</p>
      <h2 class="sip-h2">From first conversation to facility concept.</h2>
    </div>""" + PROCESS + """
  </div>
</section>""")


def build():
    src = open(SRC, encoding="utf-8").read()
    s = common_fixes(src)

    home = add_section_ids(s)
    write("index.html", home)

    head, body_open, header, footer = split_page(s)
    body_open = body_open.replace(" homepage ", " ")
    for filename, (title, content) in PAGES.items():
        page_head = re.sub(r"<title>.*?</title>", "<title>%s | STADIA IP</title>" % title, head, count=1, flags=re.S)
        page_header = re.sub(
            r'(<div class="header-nav-item header-nav-item--external)("[^>]*>\s*<a href="%s")' % re.escape(filename),
            r"\1 header-nav-item--active\2", header)
        main = '<main id="page" class="sip" role="main">%s\n</main>' % content
        footer_with_js = footer.replace("</body>", '<script src="./stadia-pages.js"></script>\n</body>', 1)
        write(filename, page_head + body_open + page_header + main + footer_with_js)

    write("STADIA IP.html", """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>STADIA IP</title><meta http-equiv="refresh" content="0; url=index.html">
<script>location.replace('index.html' + location.hash);</script></head>
<body style="font-family:sans-serif;padding:24px"><a href="index.html">Continue to the STADIA IP homepage</a></body></html>
""")


def write(name, text):
    with open(os.path.join(SITE, name), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print("wrote", name, len(text))


build()
