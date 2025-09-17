let token = localStorage.getItem('token') || null;
const api = (path, opts={}) => {
  opts.headers = opts.headers || {};
  if (token) opts.headers['Authorization'] = 'Bearer ' + token;
  return fetch(path, opts);
};

// PWA install
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault(); deferredPrompt = e;
  const btn = document.getElementById('installBtn');
  btn.hidden = false;
  btn.onclick = async () => { deferredPrompt.prompt(); btn.hidden=true; };
});

// Register SW
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/static/service-worker.js');
}

// IndexedDB outbox
const dbp = new Promise((resolve, reject) => {
  const open = indexedDB.open('finance-db', 1);
  open.onupgradeneeded = () => {
    const db = open.result;
    db.createObjectStore('outbox', {keyPath: 'uuid'});
  };
  open.onsuccess = () => resolve(open.result);
  open.onerror = () => reject(open.error);
});

async function outboxAdd(item) {
  const db = await dbp;
  const tx = db.transaction('outbox', 'readwrite');
  tx.objectStore('outbox').put(item);
  return tx.complete;
}
async function outboxAll() {
  const db = await dbp;
  return new Promise((res) => {
    const tx = db.transaction('outbox', 'readonly');
    const req = tx.objectStore('outbox').getAll();
    req.onsuccess = () => res(req.result || []);
  });
}
async function outboxClear() {
  const db = await dbp;
  const tx = db.transaction('outbox', 'readwrite');
  tx.objectStore('outbox').clear();
}

// UI elements
const authSec = document.getElementById('auth');
const appSec = document.getElementById('app');
const loginForm = document.getElementById('loginForm');
const txForm = document.getElementById('txForm');
const txList = document.getElementById('txList');
const offlineHint = document.getElementById('offlineHint');

function uuid() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random()*16|0, v = c=='x'?r:(r&0x3|0x8); return v.toString(16);
  });
}

function showApp() {
  authSec.classList.add('hidden');
  appSec.classList.remove('hidden');
  loadAll();
}
function showAuth() {
  appSec.classList.add('hidden');
  authSec.classList.remove('hidden');
}

document.getElementById('logoutBtn').onclick = () => { localStorage.removeItem('token'); token=null; showAuth(); }

loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const body = new URLSearchParams();
  body.set('username', document.getElementById('email').value);
  body.set('password', document.getElementById('password').value);
  body.set('grant_type', 'password');
  const r = await fetch('/api/auth/token', { method:'POST', body });
  if (r.ok) {
    const j = await r.json(); token = j.access_token; localStorage.setItem('token', token); showApp();
  } else { alert('Login falhou'); }
});

txForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const item = {
    uuid: uuid(),
    type: document.getElementById('txType').value,
    amount: parseFloat(document.getElementById('txAmount').value),
    description: document.getElementById('txDesc').value || null,
    category_id: null,
    date: new Date(document.getElementById('txDate').value || new Date()).toISOString(),
    deleted: false,
    updated_at: new Date().toISOString()
  };
  try {
    const r = await api('/api/transactions', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(item) });
    if (!r.ok) throw new Error('offline?');
    offlineHint.textContent = '';
  } catch (err) {
    offlineHint.textContent = 'Sem conexão. Salvo localmente e será sincronizado.';
    await outboxAdd({kind:'transaction', ...item});
  }
  loadTransactions();
});

document.getElementById('syncBtn').onclick = () => syncNow();

window.addEventListener('online', syncNow);

async function syncNow() {
  const items = await outboxAll();
  if (!items.length) return;
  const payload = { categories:[], budgets:[], goals:[], transactions: items.filter(i=>i.kind==='transaction').map(i=>{const {kind, ...t}=i; return t;}) };
  const r = await api('/api/sync/push', { method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
  if (r.ok) { await outboxClear(); loadAll(); }
}

// Load data + charts
let catChart, flowChart;
async function loadAll() { loadTransactions(); loadReports(); loadTips(); }

async function loadTransactions() {
  const r = await api('/api/transactions'); if (!r.ok) return;
  const data = await r.json();
  txList.innerHTML = data.slice(0,12).map(t => `<li>${new Date(t.date).toLocaleString()} - ${t.type==='expense'?'🟥':'🟩'} R$ ${t.amount.toFixed(2)} <em>${t.description||''}</em></li>`).join('');
}

async function loadReports() {
  const bycat = await (await api('/api/reports/by-category')).json();
  const ctx = document.getElementById('catChart');
  if (catChart) catChart.destroy();
  catChart = new Chart(ctx, {type:'doughnut', data: {labels: bycat.map(x=>x.category), datasets:[{data: bycat.map(x=>x.value)}]}});

  const flow = await (await api('/api/reports/summary')).json();
  const fctx = document.getElementById('flowChart');
  if (flowChart) flowChart.destroy();
  flowChart = new Chart(fctx, {type:'line', data:{labels: flow.map(x=>x.month), datasets:[{label:'Receitas', data: flow.map(x=>x.income)}, {label:'Despesas', data: flow.map(x=>x.expenses)}]}});
}

async function loadTips() {
  const r = await api('/api/suggestions'); if (!r.ok) return;
  const tips = await r.json();
  document.getElementById('tips').innerHTML = tips.map(t=>`<li>${t}</li>`).join('');
}

// Init
if (token) showApp(); else showAuth();
