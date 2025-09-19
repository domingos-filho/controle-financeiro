
const API_BASE = "https://appfinanceiro.domingos-automacoes.shop"; 
// mesmo que app.js

const adminLink = document.getElementById("adminLink");
function checkAdmin(user) {
  if (user.role === "admin") {
    adminLink.classList.remove("hidden");
  } else {
    adminLink.classList.add("hidden");
  }
}
const userList=document.getElementById("userList");
const newUserForm=document.getElementById("newUserForm");

async function loadUsers(){
  const res=await fetch(API_BASE+"/users",{headers:authHeader()});
  if(!res.ok) return;
  const users=await res.json();
  userList.innerHTML=users.map(u=>`<div class="card">${u.email} - ${u.role||""}
    <button onclick="deleteUser(${u.id})">🗑️</button></div>`).join("");
}

async function deleteUser(id){
  if(!confirm("Excluir usuário?")) return;
  await fetch(API_BASE+"/users/"+id,{method:"DELETE",headers:authHeader()});
  loadUsers();
}

newUserForm.addEventListener("submit",async e=>{
  e.preventDefault();
  const data={name:newName.value,email:newEmail.value,password:newPassword.value,role:newRole.value};
  await fetch(API_BASE+"/users",{method:"POST",headers:{...authHeader(),"Content-Type":"application/json"},body:JSON.stringify(data)});
  newUserForm.reset();loadUsers();
});

function authHeader(){return {"Authorization":"Bearer "+localStorage.getItem("token")};}
