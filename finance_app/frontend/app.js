const API = location.origin; // same host
let token = localStorage.getItem('token');
let offlineQueue = JSON.parse(localStorage.getItem('queue') || '[]');

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/service-worker.js');
}

function setStatus(msg){ document.getElementById('status').textContent = msg; }

function authHeaders(){
  return token ? { 'Authorization': 'Bearer ' + token } : {};
}

async function register(){
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const r = await fetch('/auth/register', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({email,password})});
  if(r.ok){ setStatus('Registrado! Agora faça login.'); } else { setStatus('Erro no registro.'); }
}

async function login(){
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const form = new URLSearchParams(); form.append('username',email); form.append('password',password);
  const r = await fetch('/auth/login', {method:'POST', headers:{}, body: form});
  const data = await r.json();
  if(r.ok){
    token = data.access_token; localStorage.setItem('token', token);
    document.getElementById('auth').classList.add('hidden');
    document.getElementById('app').classList.remove('hidden');
    load();
  }else{
    setStatus(data.detail || 'Erro no login');
  }
}

async function add(){
  const date = document.getElementById('date').value || new Date().toISOString().slice(0,10);
  const description = document.getElementById('desc').value;
  const type = document.getElementById('type').value;
  const amount = parseFloat(document.getElementById('amount').value || '0');
  const item = {date, description, type, amount};

  if (navigator.onLine && token){
    const r = await fetch('/finance/transactions', {method:'POST', headers:{'Content-Type':'application/json', ...authHeaders()}, body: JSON.stringify(item)});
    if(!r.ok){ offlineQueue.push(item); }
  } else {
    offlineQueue.push(item);
  }
  localStorage.setItem('queue', JSON.stringify(offlineQueue));
  await load();
}

async function sync(){
  if (!token){ setStatus('Faça login.'); return; }
  if (!navigator.onLine){ setStatus('Sem conexão.'); return; }
  if (offlineQueue.length === 0){ setStatus('Nada para sincronizar.'); return; }
  const r = await fetch('/finance/sync', {method:'POST', headers:{'Content-Type':'application/json', ...authHeaders()}, body: JSON.stringify(offlineQueue)});
  if(r.ok){ offlineQueue = []; localStorage.setItem('queue', '[]'); setStatus('Sincronizado!'); load(); }
}

window.addEventListener('online', sync);

async function load(){
  if (!token){ return; }
  const r = await fetch('/finance/transactions', {headers: {...authHeaders()}});
  if(!r.ok){ setStatus('Erro ao carregar.'); return; }
  const data = await r.json();
  const tbody = document.querySelector('#table tbody');
  tbody.innerHTML = '';
  let sum = 0;
  data.forEach(t => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${t.date}</td><td>${t.description}</td><td>${t.type}</td><td>${t.amount.toFixed(2)}</td>`;
    tbody.appendChild(tr);
    sum += (t.type === 'IN' ? 1 : -1) * t.amount;
  });
  document.getElementById('net').textContent = 'Saldo: R$ ' + sum.toFixed(2) + (offlineQueue.length? ` | Offline pendente: ${offlineQueue.length}` : '');
}
