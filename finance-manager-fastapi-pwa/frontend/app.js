const API_BASE = "https://www.appfinanceiro.domingos-automacoes.shop"; 

// Redirecionar para login se não houver token
if(!localStorage.getItem("token")){
  show("login");
} else {
  show("dashboard");
}

const screens = {
  login: document.getElementById("login"),
  dashboard: document.getElementById("dashboard"),
  transactions: document.getElementById("transactions"),
  wallets: document.getElementById("wallets"),
  reports: document.getElementById("reports"),
  admin: document.getElementById("admin")
};

function show(screen){
  Object.entries(screens).forEach(([k,el])=>{
    if(k===screen){el.classList.remove("hidden");el.style.opacity=0;requestAnimationFrame(()=>el.style.opacity=1);}
    else el.classList.add("hidden");
  });
  document.querySelectorAll(".tab").forEach(t=>t.classList.toggle("active",t.dataset.screen===screen));
}

document.querySelectorAll(".tab,.drawer-link").forEach(el=>el.addEventListener("click",e=>{
  const screen=el.dataset.screen;if(screen) show(screen);
}));

// Theme toggle
const root=document.documentElement;const themeToggle=document.getElementById("themeToggle");
function applyTheme(theme){root.setAttribute("data-theme",theme);localStorage.setItem("theme",theme);themeToggle.textContent=theme==="dark"?"🌙":"☀️";}
themeToggle.addEventListener("click",()=>{const current=root.getAttribute("data-theme")||"dark";applyTheme(current==="dark"?"light":"dark");});
applyTheme(localStorage.getItem("theme")||"dark");

// Login handler
document.getElementById("loginForm").addEventListener("submit", async e => {
  e.preventDefault();
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  const res = await fetch(`${API_BASE}/login/access-token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ username: email, password: password })
  });

  if(res.ok){
    const data = await res.json();
    localStorage.setItem("token", data.access_token);
    show("dashboard");
  } else {
    alert("Login inválido!");
  }
});

// Logout
document.getElementById("logoutBtn").addEventListener("click", () => {
  localStorage.removeItem("token");
  show("login");
});


document.querySelector(".fab").addEventListener("click", () => {
  const desc = prompt("Descrição da transação:");
  const valor = prompt("Valor (positivo = receita, negativo = despesa):");

  if(desc && valor){
    fetch(`${API_BASE}/transactions`, {
      method: "POST",
      headers: { 
        "Authorization": "Bearer " + localStorage.getItem("token"),
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ description: desc, amount: parseFloat(valor) })
    }).then(r=>{
      if(r.ok){
        alert("Transação lançada!");
        // recarregar lista depois
      } else {
        alert("Erro ao salvar!");
      }
    });
  }
});
