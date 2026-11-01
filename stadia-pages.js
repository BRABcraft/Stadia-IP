// Inner-page helpers: keep content clear of the fixed header, and turn the
// contact form into a pre-filled email to Bill (the site has no form backend).
(function () {
  function syncHeaderHeight() {
    var header = document.getElementById('header');
    if (header && header.offsetHeight) {
      document.documentElement.style.setProperty('--sip-header', header.offsetHeight + 'px');
    }
  }
  syncHeaderHeight();
  window.addEventListener('load', syncHeaderHeight);
  window.addEventListener('resize', syncHeaderHeight);

  var form = document.getElementById('sip-contact-form');
  if (!form) return;
  form.addEventListener('submit', function (event) {
    event.preventDefault();
    if (!form.reportValidity()) return;
    var data = new FormData(form);
    var get = function (key) { return (data.get(key) || '').toString().trim(); };
    var org = get('organization');
    var subject = '30 Minute Call Request' + (org ? ' - ' + org : '');
    var body = [
      'Name: ' + get('name'),
      'Organization: ' + org,
      'Email: ' + get('email'),
      'Phone: ' + get('phone'),
      'Facility type: ' + get('facility'),
      'Location: ' + get('location'),
      'Desired timing: ' + get('timing'),
      '',
      'Goals:',
      get('goals')
    ].join('\n');
    window.location.href = 'mailto:Bill@StadiaIP.com?subject=' + encodeURIComponent(subject) +
      '&body=' + encodeURIComponent(body);
    var status = document.getElementById('sip-form-status');
    if (status) {
      status.textContent = 'Your email app should open with this message ready to send. If it does not, email Bill@StadiaIP.com directly.';
    }
  });
})();
