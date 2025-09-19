const API_BASE = window.location.origin;

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
