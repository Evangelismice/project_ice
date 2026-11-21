// ICE public website: shared header/footer plus small page modules (events, gallery, giving, forms).
const $ = (s, el = document) => el.querySelector(s);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const page = document.body.dataset.page;

const NAV = [['home', 'index.html', 'Home'], ['about', 'about.html', 'About'], ['ministries', 'ministries.html', 'Ministries'],
  ['events', 'events.html', 'Events'], ['gallery', 'gallery.html', 'Gallery'], ['contact', 'contact.html', 'Contact']];

const http = {
  async get(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error('Request failed');
    return res.json();
  },
  async post(url, body) {
    const res = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    let data = null;
    try { data = await res.json(); } catch { /* no body */ }
    if (!res.ok) throw new Error(typeof data?.detail === 'string' ? data.detail : 'Something went wrong. Please check your details and try again.');
    return data;
  },
};

// ---------- shared layout ----------
$('#site-header').innerHTML = `
<header class="nav"><div class="wrap nav-in">
  <a href="index.html" class="brand"><img src="assets/logo.jpeg" alt="ICE logo"><span>International Center<br>of Evangelism</span></a>
  <button class="burger" id="burger" aria-label="Menu" aria-expanded="false">&#9776;</button>
  <nav id="menu">${NAV.map(([id, href, text]) => `<a href="${href}" class="${id === page ? 'on' : ''}">${text}</a>`).join('')}<a href="give.html" class="btn small">Give</a></nav>
</div></header>`;

$('#site-footer').innerHTML = `
<footer class="foot"><div class="wrap foot-in">
  <div class="brand light"><img src="assets/logo.jpeg" alt="ICE logo"><span>International Center<br>of Evangelism</span></div>
  <div><p>A ministry of Evangelism Resources<br>Dong Kasa, Miango Road, Jos, Nigeria</p>
    <div class="foot-links">${NAV.map(([, href, text]) => `<a href="${href}">${text}</a>`).join('')}<a href="give.html">Give</a></div></div>
  <p>&copy; ${new Date().getFullYear()} International Center of Evangelism<br><a href="/admin/">Staff login</a></p>
</div></footer>`;

const menu = $('#menu'); const burger = $('#burger');
burger.addEventListener('click', () => burger.setAttribute('aria-expanded', menu.classList.toggle('open')));
menu.addEventListener('click', (e) => { if (e.target.tagName === 'A') menu.classList.remove('open'); });

const io = new IntersectionObserver((entries) => entries.forEach((en) => {
  if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
}), { threshold: 0.12 });
document.querySelectorAll('.reveal').forEach((el) => io.observe(el));

// ---------- helpers ----------
const fmtDate = (d) => new Date(`${d}T00:00:00`);

function eventCard(ev, withButton) {
  const d = fmtDate(ev.event_date);
  const meta = [ev.event_time, ev.location].filter(Boolean).map(esc).join(' &middot; ');
  return `<article class="event">
    <div class="date"><b>${d.getDate()}</b><span>${d.toLocaleString('en-GB', { month: 'short' })} ${d.getFullYear()}</span></div>
    <div><h3>${esc(ev.title)}</h3>${meta ? `<p class="meta">${meta}</p>` : ''}${ev.description ? `<p>${esc(ev.description)}</p>` : ''}</div>
    ${withButton ? `<button class="btn" data-reg="${ev.id}" data-title="${esc(ev.title)}">Register</button>` : ''}
  </article>`;
}

function bindForm(form, note, url, extra = () => ({}), okMessage = 'Thank you! We have received your message.') {
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    note.textContent = 'Sending...';
    try {
      await http.post(url, { ...Object.fromEntries(new FormData(form)), ...extra() });
      note.textContent = okMessage;
      form.reset();
    } catch (err) { note.textContent = err.message; }
  });
}

// ---------- pages ----------
async function initHome() {
  const box = $('#home-events');
  try {
    const list = (await http.get('/public/events')).slice(0, 3);
    box.innerHTML = list.length ? list.map((ev) => eventCard(ev, false)).join('') : '<p class="muted">New events will be announced here soon.</p>';
  } catch { box.innerHTML = ''; }
}

async function initEvents() {
  const box = $('#events'); const dialog = $('#reg-dialog'); const form = $('#reg-form'); const note = $('#reg-note');
  try {
    const list = await http.get('/public/events');
    box.innerHTML = list.length ? list.map((ev) => eventCard(ev, true)).join('') : '<p class="muted">There are no upcoming events right now. Please check back soon.</p>';
  } catch { box.innerHTML = '<p class="muted">Events could not be loaded. Please try again later.</p>'; }
  box.addEventListener('click', (e) => {
    const b = e.target.closest('[data-reg]'); if (!b) return;
    $('#reg-event-id').value = b.dataset.reg; $('#reg-title').textContent = b.dataset.title; note.textContent = ''; dialog.showModal();
  });
  $('#reg-cancel').onclick = () => dialog.close();
  bindForm(form, note, '/registrations/', () => ({ event_id: Number($('#reg-event-id').value) }), 'You are registered. God bless you!');
}

async function initGallery() {
  const box = $('#gallery');
  try {
    const items = await http.get('/public/gallery?limit=50');
    box.innerHTML = items.length
      ? items.map((i) => `<figure><img src="${esc(i.image_url.replace('/upload/', '/upload/w_700,q_auto,f_auto/'))}" alt="${esc(i.description || 'ICE gallery photo')}" loading="lazy">${i.description ? `<figcaption>${esc(i.description)}</figcaption>` : ''}</figure>`).join('')
      : '<p class="muted">Photos will be added soon.</p>';
  } catch { box.innerHTML = '<p class="muted">The gallery could not be loaded.</p>'; }
}

function initContact() { bindForm($('#contact-form'), $('#form-note'), '/contact/'); }

function initGive() {
  const form = $('#give-form'); const amount = $('#amount'); const note = $('#give-note'); const banner = $('#give-banner');
  const chips = document.querySelectorAll('.chip');
  chips.forEach((c) => c.addEventListener('click', () => {
    amount.value = c.dataset.amt; chips.forEach((x) => x.classList.toggle('on', x === c));
  }));
  amount.addEventListener('input', () => chips.forEach((x) => x.classList.toggle('on', x.dataset.amt === amount.value)));

  const ref = new URLSearchParams(location.search).get('reference');
  if (ref) {
    banner.hidden = false; banner.className = 'alert'; banner.textContent = 'Confirming your gift...';
    http.get(`/give/verify/${encodeURIComponent(ref)}`).then((r) => {
      if (r.status === 'success') banner.textContent = 'Thank you! Your gift has been received. God bless you.';
      else if (r.status === 'failed') { banner.className = 'alert bad'; banner.textContent = 'The payment was not completed. You have not been charged. Please try again.'; }
      else banner.textContent = 'Your payment is still being confirmed. Thank you for giving.';
    }).catch(() => { banner.className = 'alert bad'; banner.textContent = 'We could not confirm your payment yet. If you were charged, please contact us.'; });
    history.replaceState(null, '', location.pathname);
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    note.textContent = 'Taking you to secure payment...';
    try {
      const d = await http.post('/give/initialize', {
        name: form.name.value, email: form.email.value, amount: Number(amount.value), purpose: form.purpose.value || null,
      });
      location.href = d.authorization_url;
    } catch (err) { note.textContent = err.message; }
  });
}

({ home: initHome, events: initEvents, gallery: initGallery, contact: initContact, give: initGive })[page]?.();
