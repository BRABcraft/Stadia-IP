// Revenue Benchmark & Opportunity Engine (homepage).
// Calculation model carried over from the Gemini prototype; the Chart.js
// charts are replaced with CSS bars so the page needs no extra libraries.
(function () {
  var root = document.getElementById('revenue-engine');
  if (!root) return;

  var $ = function (id) { return document.getElementById(id); };
  var money = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
  var fmt = function (n) { return money.format(n); };
  var TIER_MULT = { p4: 1.35, g5: 1.0, fcs: 0.75, div2: 0.55 };
  var DEFAULTS = { sieCabanas: 12, sieVip: 250, sieEvents: 18, sieSponsor: 600000 };
  var SEGMENTS = [
    { key: 'cabana', label: 'Cabana suites', color: '#86151d' },
    { key: 'vip', label: 'Field-level VIP lounge', color: '#430d12' },
    { key: 'events', label: 'Year-round events', color: '#e2525c' },
    { key: 'sponsor', label: 'Naming & sponsorship', color: '#8f898c' }
  ];
  var last = null;

  function num(id, fallback) {
    var v = parseFloat($(id).value);
    return isFinite(v) && v > 0 ? v : fallback;
  }
  function setText(id, text) { var el = $(id); if (el) el.textContent = text; }
  function paintRange(input) {
    var pct = (input.value - input.min) / (input.max - input.min) * 100;
    input.style.setProperty('--fill', pct + '%');
  }

  function calculate() {
    var tier = $('sieTier').value;
    var m = TIER_MULT[tier] || 1;
    var d = {
      name: $('sieName').value.trim() || 'State University Athletics',
      tierText: $('sieTier').options[$('sieTier').selectedIndex].text,
      budget: num('sieBudget', 80),
      capacity: num('sieCapacity', 50000),
      sqFt: num('sieSqFt', 15000),
      currentVip: num('sieCurrentVip', 4),
      cabanas: parseInt($('sieCabanas').value, 10),
      vipPasses: parseInt($('sieVip').value, 10),
      events: parseInt($('sieEvents').value, 10),
      sponsor: parseFloat($('sieSponsor').value),
      nil: $('sieNil').checked
    };

    d.cabanaRev = d.cabanas * 75000 * m;
    d.vipRev = d.vipPasses * 2500 * m;
    d.eventsRev = d.events * 22000 * m;
    d.sponsorRev = d.sponsor;
    d.gross = d.cabanaRev + d.vipRev + d.eventsRev + d.sponsorRev;
    d.nilYield = d.nil ? (d.cabanaRev + d.vipRev) * 0.25 : 0;
    d.capex = d.cabanas * 48000 + d.sqFt * 18;
    d.net = d.gross - d.capex;
    d.payback = Math.max(1.5, Math.min(24, d.capex / (d.gross / 12)));
    d.yieldPerSqFt = d.gross / d.sqFt;
    d.growthPct = d.gross / (d.budget * 1000000) * 100;
    d.footprintGap = d.sqFt * 85 * m;

    var score = Math.round(
      Math.min(d.cabanas / 24, 1) * 30 +
      Math.min(d.gross / 3500000, 1) * 40 +
      Math.min(d.events / 30, 1) * 20 +
      (d.nil ? 10 : 0)
    );
    d.score = Math.min(Math.max(score, 15), 99);
    d.tierLabel = d.score >= 80 ? 'Pacesetter / dominant tier'
      : d.score >= 60 ? 'Competitive innovator'
      : d.score >= 40 ? 'Standard market rate'
      : 'Emerging program';

    d.legacySuites = d.currentVip * 50000 * m;
    d.legacySponsor = 150000 * m;
    d.legacyEvents = 80000 * m;
    d.legacyTotal = d.legacySuites + d.legacySponsor + d.legacyEvents;
    return d;
  }

  function render() {
    ['sieCabanas', 'sieVip', 'sieEvents', 'sieSponsor'].forEach(function (id) { paintRange($(id)); });
    var d = last = calculate();

    setText('sieCabanasVal', d.cabanas + ' units');
    setText('sieVipVal', d.vipPasses.toLocaleString() + ' passes');
    setText('sieEventsVal', d.events + ' / year');
    setText('sieSponsorVal', fmt(d.sponsor));

    setText('sieTotal', fmt(d.gross));
    setText('sieGrowth', '+' + d.growthPct.toFixed(1) + '%');
    setText('sieScore', d.score);
    setText('sieTierLabel', d.tierLabel);
    $('sieMeter').style.width = d.score + '%';
    setText('sieGross', fmt(d.gross));
    setText('sieCapex', fmt(d.capex));
    setText('sieNet', fmt(d.net));
    setText('siePayback', d.payback.toFixed(1) + ' months');
    setText('sieNilYield', fmt(d.nilYield));

    var parts = { cabana: d.cabanaRev, vip: d.vipRev, events: d.eventsRev, sponsor: d.sponsorRev };
    SEGMENTS.forEach(function (s) {
      var pct = d.gross ? parts[s.key] / d.gross * 100 : 0;
      $('sieSeg-' + s.key).style.width = pct + '%';
      setText('sieAmt-' + s.key, fmt(parts[s.key]));
      setText('siePct-' + s.key, Math.round(pct) + '%');
    });
    setText('sieGap', fmt(d.footprintGap));
    setText('sieYield', fmt(d.yieldPerSqFt) + ' per sq ft yield potential');

    var max = Math.max(d.legacyTotal, d.gross) || 1;
    $('sieBarLegacy').style.width = (d.legacyTotal / max * 100) + '%';
    $('sieBarStadia').style.width = (d.gross / max * 100) + '%';
    setText('sieLegacyTotal', fmt(d.legacyTotal));
    setText('sieStadiaTotal', fmt(d.gross));

    setText('sieTbLegacySuites', fmt(d.legacySuites));
    setText('sieTbStadiaSuites', fmt(d.cabanaRev + d.vipRev));
    setText('sieTbLegacySponsor', fmt(d.legacySponsor));
    setText('sieTbStadiaSponsor', fmt(d.sponsorRev));
    setText('sieTbLegacyEvents', fmt(d.legacyEvents));
    setText('sieTbStadiaEvents', fmt(d.eventsRev));
    setText('sieTbStadiaNil', fmt(d.nilYield));
  }

  root.addEventListener('input', render);
  root.addEventListener('change', render);
  $('sieReset').addEventListener('click', function () {
    Object.keys(DEFAULTS).forEach(function (id) { $(id).value = DEFAULTS[id]; });
    $('sieNil').checked = true;
    render();
  });

  // ---------- Executive brief ----------
  var modal = $('sieModal');
  var opener = null;
  document.body.appendChild(modal); // direct child of <body> so print can isolate it

  function fillBrief() {
    var d = last || calculate();
    setText('sieBriefName', d.name);
    setText('sieBriefNameText', d.name);
    setText('sieBriefTier', d.tierText + ' | Capacity: ' + Math.round(d.capacity).toLocaleString());
    setText('sieBriefDate', new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' }));
    setText('sieBriefRev', fmt(d.gross));
    setText('sieBriefScore', d.score + ' / 100');
    setText('sieBriefCapex', fmt(d.capex));
    setText('sieBriefPayback', d.payback.toFixed(1) + ' mo');
    setText('sieBriefCabanas', d.cabanas);
    setText('sieBriefVip', d.vipPasses.toLocaleString());
    setText('sieBriefEvents', d.events);
    setText('sieBriefNil', fmt(d.nilYield));
  }
  function openBrief(event) {
    opener = event && event.currentTarget;
    fillBrief();
    modal.hidden = false;
    document.documentElement.style.overflow = 'hidden';
    $('sieModalClose').focus();
  }
  function closeBrief() {
    modal.hidden = true;
    document.documentElement.style.overflow = '';
    if (opener) opener.focus();
  }

  $('sieOpenBrief').addEventListener('click', openBrief);
  $('sieModalClose').addEventListener('click', closeBrief);
  $('sieCloseBrief').addEventListener('click', closeBrief);
  modal.addEventListener('click', function (e) { if (e.target === modal) closeBrief(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !modal.hidden) closeBrief(); });

  $('siePrintBrief').addEventListener('click', function () {
    document.documentElement.classList.add('sie-printing');
    window.print();
  });
  window.addEventListener('afterprint', function () { document.documentElement.classList.remove('sie-printing'); });

  $('sieCopyBrief').addEventListener('click', function () {
    var btn = this;
    var text = $('sieBrief').innerText;
    var done = function () {
      var label = btn.textContent;
      btn.textContent = 'Copied';
      setTimeout(function () { btn.textContent = label; }, 2000);
    };
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done, fallback);
    } else {
      fallback();
    }
    function fallback() {
      var area = document.createElement('textarea');
      area.value = text;
      area.setAttribute('readonly', '');
      area.style.position = 'fixed';
      area.style.opacity = '0';
      document.body.appendChild(area);
      area.select();
      try { document.execCommand('copy'); done(); } catch (err) { /* leave the label unchanged */ }
      document.body.removeChild(area);
    }
  });

  render();
})();
