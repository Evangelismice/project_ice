// ICE Management System - vanilla JS frontend (no build step)
let token = localStorage.getItem('ice_token');
let registerMode = false;

const $ = (s, el = document) => el.querySelector(s);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const label = (s) => (s ? String(s).replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()) : '');
const money = (v, cur = 'NGN') => {
  try { return Number(v).toLocaleString('en-NG', { style: 'currency', currency: cur }); }
  catch { return `${cur} ${Number(v).toLocaleString()}`; }
};

function toast(msg, isErr = false) {
  const t = $('#toast');
  t.textContent = msg; t.className = isErr ? 'err' : ''; t.hidden = false;
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => (t.hidden = true), 3500);
}

async function api(path, { method = 'GET', json, form } = {}) {
  const headers = {};
  if (token) headers.Authorization = `Bearer ${token}`;
  let body;
  if (json) { headers['Content-Type'] = 'application/json'; body = JSON.stringify(json); }
  if (form) body = form;
  const res = await fetch(path, { method, headers, body });
  if (res.status === 401 && token) { logout(); throw new Error('Session expired. Please sign in again.'); }
  if (!res.ok) {
    let msg = 'Request failed';
    try {
      const j = await res.json();
      msg = typeof j.detail === 'string' ? j.detail : (j.detail || []).map((e) => `${(e.loc || []).slice(1).join('.')}: ${e.msg}`).join('; ');
    } catch { /* ignore */ }
    throw new Error(msg);
  }
  return res.status === 204 ? null : res.json();
}

// ---------- Options ----------
const OPT = {
  gender: ['male', 'female'],
  department: ['executive', 'school_of_evangelism', 'operations', 'ministry_team', 'kitchen', 'grounds', 'security'],
  staffStatus: ['active', 'on_leave', 'resigned', 'retired'],
  donorType: ['individual', 'church', 'organization'],
  payment: ['cash', 'bank_transfer', 'cheque', 'online'],
};

// ---------- Entity config ----------
let donorMap = {};
const ENT = {
  staffs: {
    title: 'Staff', single: 'Staff Member', path: '/staffs/', search: true,
    filter: { param: 'department', label: 'All departments', options: OPT.department },
    cols: [
      { h: 'Name', v: (r) => `${r.first_name} ${r.last_name}` },
      { h: 'Department', v: (r) => label(r.department) },
      { h: 'Position', v: (r) => r.position },
      { h: 'Phone', v: (r) => r.phone },
      { h: 'Email', v: (r) => r.email },
      { h: 'Joined', v: (r) => r.date_joined },
      { h: 'Status', v: (r) => r.status, badge: true },
    ],
    fields: [
      { n: 'first_name', l: 'First name', req: true },
      { n: 'last_name', l: 'Last name', req: true },
      { n: 'gender', l: 'Gender', t: 'select', o: OPT.gender },
      { n: 'phone', l: 'Phone' },
      { n: 'email', l: 'Email', t: 'email' },
      { n: 'department', l: 'Department', t: 'select', o: OPT.department, req: true },
      { n: 'position', l: 'Position' },
      { n: 'date_joined', l: 'Date joined', t: 'date' },
      { n: 'status', l: 'Status', t: 'select', o: OPT.staffStatus, req: true, d: 'active' },
      { n: 'address', l: 'Address', full: true },
    ],
  },
  donors: {
    title: 'Donors', single: 'Donor', path: '/donors/', search: true,
    filter: { param: 'donor_type', label: 'All types', options: OPT.donorType },
    cols: [
      { h: 'Name', v: (r) => r.name },
      { h: 'Type', v: (r) => label(r.donor_type) },
      { h: 'Phone', v: (r) => r.phone },
      { h: 'Email', v: (r) => r.email },
      { h: 'Address', v: (r) => r.address },
    ],
    fields: [
      { n: 'name', l: 'Name', req: true, full: true },
      { n: 'donor_type', l: 'Type', t: 'select', o: OPT.donorType, req: true, d: 'individual' },
      { n: 'phone', l: 'Phone' },
      { n: 'email', l: 'Email', t: 'email', full: true },
      { n: 'address', l: 'Address', full: true },
      { n: 'notes', l: 'Notes', t: 'textarea', full: true },
    ],
  },
  events: {
    title: 'Events', single: 'Event', path: '/events/', search: true,
    cols: [
      { h: 'Photo', v: (r) => r.image_url, img: true },
      { h: 'Date', v: (r) => r.event_date },
      { h: 'Title', v: (r) => r.title },
      { h: 'Time', v: (r) => r.event_time },
      { h: 'Location', v: (r) => r.location },
    ],
    fields: [
      { n: 'title', l: 'Title', req: true, full: true },
      { n: 'event_date', l: 'Date', t: 'date', req: true },
      { n: 'event_time', l: 'Time' },
      { n: 'location', l: 'Location', full: true },
      { n: 'description', l: 'Description', t: 'textarea', full: true },
      { n: 'image_url', l: 'Event image', t: 'image', full: true },
    ],
  },
  gallery: {
    title: 'Gallery', single: 'Media', path: '/gallery/', search: true,
    filter: { param: 'resource_type', label: 'All types', options: ['image', 'video'] },
    cols: [
      { h: "Type", v: (r) => label(r.resource_type) },
      { h: "Media", v: (r) => r.image_url || r.video_url ? (r.video_url || r.image_url) : "—" },
      { h: "Description", v: (r) => r.description },
      { h: "Added", v: (r) => (r.created_at || "").slice(0, 10) },
    ],
    fields: [
      { n: 'image_url', l: 'Photo', t: 'image', full: true },
      { n: 'video_url', l: 'Video (MP4, MOV or AVI, up to 50 MB)', t: 'video', full: true },
      { n: 'description', l: 'Description', full: true },
    ],
  },
  messages: {
    title: 'Messages', single: 'Message', path: '/contact/', search: true, noAdd: true, noEdit: true, viewer: true,
    cols: [
      { h: 'Date', v: (r) => (r.created_at || '').slice(0, 10) },
      { h: 'From', v: (r) => r.name },
      { h: 'Email', v: (r) => r.email },
      { h: 'Subject', v: (r) => r.subject || '(none)' },
      { h: 'Status', v: (r) => (r.is_read ? 'read' : 'unread'), badge: true },
    ],
    fields: [],
  },
  donations: {
    title: 'Donations', single: 'Donation', path: '/donations/', noEdit: true,
    cols: [
      { h: 'Date', v: (r) => r.date_received },
      { h: 'Donor', v: (r) => donorMap[r.donor_id] || `#${r.donor_id}` },
      { h: 'Amount', v: (r) => money(r.amount, r.currency) },
      { h: 'Purpose', v: (r) => r.purpose },
      { h: 'Method', v: (r) => label(r.payment_method) },
    ],
    fields: [
      { n: 'donor_id', l: 'Donor', t: 'donor', req: true, full: true },
      { n: 'amount', l: 'Amount', t: 'number', req: true },
      { n: 'currency', l: 'Currency', req: true, d: 'NGN' },
      { n: 'payment_method', l: 'Payment method', t: 'select', o: OPT.payment, req: true, d: 'cash' },
      { n: 'date_received', l: 'Date received', t: 'date', req: true, d: new Date().toISOString().slice(0, 10) },
      { n: 'purpose', l: 'Purpose', full: true },
    ],
  },
};

// ---------- Auth ----------
function showLogin() { $('#login-view').hidden = false; $('#app-view').hidden = true; }
function showApp() { $('#login-view').hidden = true; $('#app-view').hidden = false; go('dashboard'); }
function logout() { token = null; localStorage.removeItem('ice_token'); showLogin(); }

$('#toggle-mode').addEventListener('click', (e) => {
  e.preventDefault();
  registerMode = !registerMode;
  $('#login-btn').textContent = registerMode ? 'Create admin account' : 'Sign in';
  e.target.textContent = registerMode ? 'Already have an account? Sign in' : 'First time? Create the admin account';
  $('#login-error').textContent = '';
});

$('#login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  $('#login-error').textContent = '';
  try {
    if (registerMode) {
      await api('/auth/register', { method: 'POST', json: { username: fd.get('username'), password: fd.get('password') } });
    }
    const data = await api('/auth/login', { method: 'POST', form: new URLSearchParams({ username: fd.get('username'), password: fd.get('password') }) });
    token = data.access_token;
    localStorage.setItem('ice_token', token);
    e.target.reset();
    showApp();
  } catch (err) { $('#login-error').textContent = err.message; }
});

$('#logout').addEventListener('click', logout);

// ---------- Navigation ----------
$('#nav').addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) go(b.dataset.view); });

function go(view) {
  document.querySelectorAll('#nav button').forEach((b) => b.classList.toggle('active', b.dataset.view === view));
  $('#page-title').textContent = view === 'dashboard' ? 'Dashboard' : ENT[view].title;
  const run = view === 'dashboard' ? renderDashboard() : renderList(view);
  run.catch((err) => toast(err.message, true));
}

// ---------- Dashboard ----------
async function renderDashboard() {
  const [sum, staffs, donations, , unread] = await Promise.all([
    api('/donations/summary'), api('/staffs/?limit=1000'), api('/donations/?limit=5'),
    loadDonors(), api('/contact/?is_read=false&limit=1000'),
  ]);
  const active = staffs.filter((s) => s.status === 'active').length;
  const byDept = {};
  staffs.forEach((s) => { byDept[s.department] = (byDept[s.department] || 0) + 1; });
  $('#content').innerHTML = `
    <div class="cards">
      <div class="card"><div class="muted">Total staff</div><div class="num">${staffs.length}</div></div>
      <div class="card"><div class="muted">Active staff</div><div class="num">${active}</div></div>
      <div class="card"><div class="muted">Donors</div><div class="num">${sum.donor_count}</div></div>
      <div class="card"><div class="muted">Total donations</div><div class="num">${money(sum.total_donations)}</div></div>
      <div class="card"><div class="muted">Unread messages</div><div class="num">${unread.length}</div></div>
    </div>
    <div class="two">
      <div class="panel"><h2>Staff by department</h2>
        ${Object.keys(byDept).length ? `<table>${Object.entries(byDept).map(([d, n]) => `<tr><td>${esc(label(d))}</td><td><b>${n}</b></td></tr>`).join('')}</table>` : '<div class="empty">No staff yet</div>'}
      </div>
      <div class="panel"><h2>Recent donations</h2>
        ${donations.length ? `<table>${donations.map((d) => `<tr><td>${esc(d.date_received)}</td><td>${esc(donorMap[d.donor_id] || '#' + d.donor_id)}</td><td><b>${esc(money(d.amount, d.currency))}</b></td></tr>`).join('')}</table>` : '<div class="empty">No donations yet</div>'}
      </div>
    </div>`;
}

async function loadDonors() {
  const donors = await api('/donors/?limit=1000');
  donorMap = Object.fromEntries(donors.map((d) => [d.id, d.name]));
  return donors;
}

// ---------- Generic list ----------
let current = { key: null, rows: [] };

async function renderList(key) {
  const e = ENT[key];
  current.key = key;
  $('#content').innerHTML = `
    <div class="toolbar">
      ${e.search ? '<input id="q" type="search" placeholder="Search...">' : ''}
      ${e.filter ? `<select id="flt"><option value="">${e.filter.label}</option>${e.filter.options.map((o) => `<option value="${o}">${esc(label(o))}</option>`).join('')}</select>` : ''}
      <span class="spacer"></span>
      <button class="btn" id="export">Export CSV</button>
      ${e.noAdd ? '' : `<button class="btn primary" id="add">+ Add ${e.single}</button>`}
    </div>
    <div class="table-wrap" id="table"></div>`;
  if ($('#add')) $('#add').onclick = () => openForm(key);
  $('#export').onclick = exportCsv;
  if ($('#q')) $('#q').oninput = debounce(refresh, 300);
  if ($('#flt')) $('#flt').onchange = refresh;
  await refresh();
}

async function refresh() {
  const key = current.key; const e = ENT[key];
  const params = new URLSearchParams({ limit: 1000 });
  const q = $('#q')?.value.trim(); if (q) params.set('q', q);
  const f = $('#flt')?.value; if (f) params.set(e.filter.param, f);
  if (key === 'donations') await loadDonors();
  current.rows = await api(`${e.path}?${params}`);
  drawTable();
}

function drawTable() {
  const e = ENT[current.key]; const rows = current.rows;
  if (!rows.length) { $('#table').innerHTML = '<div class="empty">Nothing here yet.</div>'; return; }
  $('#table').innerHTML = `<table><thead><tr>${e.cols.map((c) => `<th>${c.h}</th>`).join('')}<th></th></tr></thead><tbody>
    ${rows.map((r) => `<tr>${e.cols.map((c) => {
      const v = c.v(r);
      if (c.img) return `<td>${v ? `<img class="thumb-sm" src="${esc(v)}" alt="">` : ''}</td>`;
      return `<td>${c.badge ? `<span class="badge ${esc(v)}">${esc(label(v))}</span>` : esc(v)}</td>`;
    }).join('')}<td class="actions">
      ${e.viewer ? `<button class="btn sm" data-view="${r.id}">View</button>` : ''}
      ${e.noEdit ? '' : `<button class="btn sm" data-edit="${r.id}">Edit</button>`}
      <button class="btn sm danger" data-del="${r.id}">Delete</button></td></tr>`).join('')}
  </tbody></table>`;
  $('#table').onclick = (ev) => {
    const ed = ev.target.closest('[data-edit]'); const del = ev.target.closest('[data-del]');
    const vw = ev.target.closest('[data-view]');
    if (vw) openMessage(current.rows.find((r) => r.id == vw.dataset.view));
    if (ed) openForm(current.key, current.rows.find((r) => r.id == ed.dataset.edit));
    if (del) removeRow(Number(del.dataset.del));
  };
}

async function removeRow(id) {
  if (!confirm('Delete this record? This cannot be undone.')) return;
  try { await api(`${ENT[current.key].path}${id}`, { method: 'DELETE' }); toast('Deleted'); await refresh(); }
  catch (err) { toast(err.message, true); }
}

// ---------- Message viewer ----------
async function openMessage(r) {
  const m = $('#modal');
  const when = (r.created_at || '').slice(0, 16).replace('T', ' ');
  m.innerHTML = `<h2>${esc(r.subject || '(No subject)')}</h2>
    <p class="muted small">From ${esc(r.name)} &lt;${esc(r.email)}&gt; &middot; ${esc(when)}</p>
    <p style="white-space:pre-wrap">${esc(r.message)}</p>
    <div class="form-actions"><a class="btn" href="mailto:${esc(r.email)}?subject=${encodeURIComponent('Re: ' + (r.subject || ''))}">Reply</a>
    <button class="btn primary" id="close-msg">Close</button></div>`;
  $('#close-msg').onclick = () => m.close();
  m.showModal();
  if (!r.is_read) {
    try { await api(`/contact/${r.id}/read`, { method: 'PATCH' }); r.is_read = true; drawTable(); } catch { /* ignore */ }
  }
}

// ---------- Form modal ----------
async function openForm(key, row = null) {
  const e = ENT[key];
  if (key === 'donations') await loadDonors();
  const input = (f) => {
    const val = row ? row[f.n] ?? '' : f.d ?? '';
    const req = f.req ? 'required' : '';
    if (f.t === 'select') return `<select name="${f.n}" ${req}><option value=""></option>${f.o.map((o) => `<option value="${o}" ${o === val ? 'selected' : ''}>${esc(label(o))}</option>`).join('')}</select>`;
    if (f.t === 'donor') return `<select name="${f.n}" ${req}><option value=""></option>${Object.entries(donorMap).map(([id, n]) => `<option value="${id}" ${id == val ? 'selected' : ''}>${esc(n)}</option>`).join('')}</select>`;
    if (f.t === 'image') return `<input type="hidden" name="${f.n}" value="${esc(val)}"><input type="file" accept="image/jpeg,image/png,image/webp,video/mp4,video/quicktime,video/x-msvideo" data-upload="${f.n}"><img class="thumb" data-preview="${f.n}" ${val ? `src="${esc(val)}"` : 'hidden'}><span class="muted small" data-status="${f.n}"></span>`;
    if (f.t === 'video') return `<input type="hidden" name="${f.n}" value="${esc(val)}"><input type="file" accept="video/mp4,video/quicktime,video/x-msvideo" data-upload="${f.n}"><video class="thumb" data-preview="${f.n}" controls preload="metadata" ${val ? `src="${esc(val)}"` : 'hidden'}></video><span class="muted small" data-status="${f.n}"></span>`;
    if (f.t === 'textarea') return `<textarea name="${f.n}" rows="3">${esc(val)}</textarea>`;
    return `<input name="${f.n}" type="${f.t || 'text'}" value="${esc(val)}" ${f.max ? `maxlength="${f.max}"` : ''} ${f.t === 'number' ? 'step="0.01" min="0.01"' : ''} ${req}>`;
  };
  const m = $('#modal');
  m.innerHTML = `<form id="rec-form"><h2>${row ? 'Edit' : 'Add'} ${e.single}</h2>
    <div class="form-grid">${e.fields.map((f) => `<label class="${f.full ? 'full' : ''}">${f.l}${f.req ? ' *' : ''}${input(f)}</label>`).join('')}</div>
    <div class="form-actions"><button type="button" class="btn" id="cancel">Cancel</button><button class="btn primary" type="submit">Save</button></div></form>`;
  $('#cancel').onclick = () => m.close();
  m.querySelectorAll('[data-upload]').forEach((inp) => inp.addEventListener('change', async () => {
    const name = inp.dataset.upload; const file = inp.files[0];
    if (!file) return;
    const status = m.querySelector(`[data-status="${name}"]`);
    status.textContent = 'Uploading...';
    try {
      const fd = new FormData(); fd.append('file', file);
      const res = await api('/uploads/', { method: 'POST', form: fd });
      m.querySelector(`input[name="${name}"]`).value = res.url;
      const img = m.querySelector(`[data-preview="${name}"]`); img.src = res.url; img.hidden = false;
      status.textContent = 'Uploaded. Click Save to keep it.';
    } catch (err) { status.textContent = ''; toast(err.message, true); }
  }));
  $('#rec-form').onsubmit = async (ev) => {
    ev.preventDefault();
    const fd = new FormData(ev.target); const body = {};
    e.fields.forEach((f) => {
      let v = fd.get(f.n); v = v === '' ? null : v;
      if (v !== null && f.t === 'number') v = Number(v);
      if (v !== null && f.t === 'donor') v = Number(v);
      body[f.n] = v;
    });
    if (e.fields.some((f) => f.t === 'image' && f.req && !body[f.n])) return toast('Please upload a photo first', true);
    if (e === ENT.gallery) {
      if (body.video_url) { body.resource_type = 'video'; body.image_url = null; }
      else if (body.image_url) { body.resource_type = 'image'; }
      else return toast('Please upload a photo or a video first', true);
    }
    try {
      await api(row ? `${e.path}${row.id}` : e.path, { method: row ? 'PUT' : 'POST', json: body });
      m.close(); toast('Saved'); await refresh();
    } catch (err) { toast(err.message, true); }
  };
  m.showModal();
}

// ---------- Helpers ----------
function debounce(fn, ms) { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; }

function exportCsv() {
  const e = ENT[current.key];
  const q = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
  const lines = [e.cols.map((c) => q(c.h)).join(',')].concat(current.rows.map((r) => e.cols.map((c) => q(c.v(r))).join(',')));
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([lines.join('\n')], { type: 'text/csv' }));
  a.download = `ice-${current.key}.csv`; a.click(); URL.revokeObjectURL(a.href);
}

// ---------- Start ----------
token ? showApp() : showLogin();