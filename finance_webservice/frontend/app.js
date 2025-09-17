// Simple client with offline queue via localStorage
const API = '/api';
let token = localStorage.getItem('token') || null;

function qs(id){ return document.getElementById(id); }
function showLogin(){
  qs('registerSection').style.display='none';
  qs('loginSection').style.display='block';
  qs('loginSection').innerHTML = `
   <h3>Entrar</h3>
   <div class=row>
     <input id="email" placeholder="E-mail">
     <input id="password" type="password" placeholder="Senha">
     <button onclick="login()">Entrar</button>
   </div>
  `;
}
function showRegister(){
  qs('loginSection').style.display='none';
  qs('registerSection').style.display='block';
  qs('registerSection').innerHTML = `
   <h3>Cadastrar</h3>
   <div class=row>
     <input id="remail" placeholder="E-mail">
     <input id="rname" placeholder="Nome">
     <input id="rpass" type="password" placeholder="Senha">
     <button onclick="register()">Criar conta</button>
   </div>`;
}

async function login(){
  const fd = new FormData();
  fd.append('username', qs('email').value);
  fd.append('password', qs('password').value);
  const res = await fetch(API+'/auth/token', {method:'POST', body:fd});
  if(!res.ok){ alert('Falha no login'); return;}
  const data = await res.json();
  token = data.access_token; localStorage.setItem('token', token);
  afterAuth();
}

async function register(){
  const body = {email:qs('remail').value, full_name:qs('rname').value, password:qs('rpass').value};
  const res = await fetch(API+'/auth/register', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
  if(!res.ok){ alert('Falha no cadastro'); return;}
  alert('Cadastro realizado! Agora faça login.');
}

function afterAuth(){
  qs('authBox').innerHTML = '<button onclick="logout()">Sair</button>';
  qs('loginSection').style.display='none';
  qs('registerSection').style.display='none';
  qs('appSection').style.display='block';
  qs('txDate').valueAsDate = new Date();
  loadAll();
}
function logout(){ localStorage.removeItem('token'); location.reload(); }

async function api(path, options={}){
  options.headers = options.headers || {};
  if(token) options.headers['Authorization'] = 'Bearer '+token;
  const res = await fetch(API+path, options);
  if(res.status===401){ alert('Faça login novamente.'); logout(); }
  return res;
}

async function loadAll(){
  await loadCategories();
  await loadTransactions();
  await loadSummary();
}

async function loadCategories(){
  const res = await api('/categories');
  const cats = await res.json();
  const sel = qs('txCategory');
  sel.innerHTML = '<option value="">Sem categoria</option>';
  cats.forEach(c=>{
    const o=document.createElement('option'); o.value=c.id; o.textContent = c.name + ' ('+c.type+')'; sel.appendChild(o);
  });
}

async function loadTransactions(){
  const month = qs('monthSel').value || '';
  const res = await api('/transactions'+(month?`?month=${month}`:''));
  const items = await res.json();
  const list = qs('txList'); list.innerHTML = '';
  items.forEach(t=>{
    const div = document.createElement('div');
    div.style.display='flex'; div.style.justifyContent='space-between'; div.style.padding='6px 0'; div.style.borderBottom='1px solid #1f2937';
    div.innerHTML = `<span>${t.date} — ${t.description}</span><span>${t.amount.toFixed(2)}</span>`;
    list.appendChild(div);
  })
}

async function loadSummary(){
  const month = qs('monthSel').value || '';
  const res = await api('/reports/summary'+(month?`?month=${month}`:''));
  const s = await res.json();
  qs('summary').innerHTML = `
    <div class="card"><div>Receitas</div><h2>R$ ${Number(s.income).toFixed(2)}</h2></div>
    <div class="card"><div>Despesas</div><h2>R$ ${Number(s.expense).toFixed(2)}</h2></div>
    <div class="card"><div>Resultado</div><h2>R$ ${Number(s.total).toFixed(2)}</h2></div>`;
  const ctx = document.getElementById('chartCat');
  const labels = s.by_category.map(x=>x.category);
  const data = s.by_category.map(x=>x.amount);
  if(window._chart) window._chart.destroy();
  window._chart = new Chart(ctx, {type:'bar', data:{labels, datasets:[{label:'Por categoria', data}]}});
}

function queueTxn(tx){ // offline queue
  const q = JSON.parse(localStorage.getItem('offline_q')||'[]');
  q.push(tx); localStorage.setItem('offline_q', JSON.stringify(q));
}

async function addTxn(){
  const tx = {
    date: qs('txDate').value,
    description: qs('txDesc').value,
    amount: parseFloat(qs('txAmount').value),
    category_id: qs('txCategory').value || null,
    client_uuid: crypto.randomUUID()
  };
  try {
    const res = await api('/transactions', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(tx)});
    if(!res.ok) throw new Error('offline?');
  } catch(e){
    queueTxn(tx);
    alert('Sem conexão: transação salva para sincronizar.');
  }
  loadAll();
}

async function syncNow(){
  const q = JSON.parse(localStorage.getItem('offline_q')||'[]');
  if(q.length===0){ alert('Nada para sincronizar.'); return; }
  const res = await api('/sync/push', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({transactions:q})});
  if(res.ok){ localStorage.removeItem('offline_q'); alert('Sincronizado!'); loadAll(); }
  else alert('Falha ao sincronizar.');
}

// auto-login if token exists
if(token){ afterAuth(); }
