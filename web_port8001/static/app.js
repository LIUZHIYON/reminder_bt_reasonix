var A="/api/reminders";
function fmt(d){var t=new Date(d);return t.getMonth()+1+"/"+t.getDate()+" "+String(t.getHours()).padStart(2,"0")+":"+String(t.getMinutes()).padStart(2,"0")}
function rep(t){return {daily:"每天",weekly:"每周",monthly:"每月"}[t]||""}
function toast(m,e){var t=document.getElementById("toast");t.textContent=m;t.className="toast show"+(e?" err":"");setTimeout(function(){t.className="toast"},3000)}
function openModal(){document.getElementById("overlay").classList.add("show")}
function closeModal(e){if(e&&e.target!==e.currentTarget)return;document.getElementById("overlay").classList.remove("show");document.getElementById("msg").textContent="";document.getElementById("msg").className="msg"}
async function load(){
  try{var r=await fetch(A);var d=await r.json();var g=document.getElementById("grid");
    if(!d.length){g.innerHTML='<div class="empty-state"><div class="big-icon">&#x1F514;</div><h2>No Reminders</h2><p>Click "+ New Reminder</p></div>';return}
    g.innerHTML=d.sort(function(a,b){return b.created_at.localeCompare(a.created_at)}).map(function(r){var s=r.status||"pending";
      return '<div class="card"><div class="card-title">'+esc(r.title||"?")+' <span class="status-badge s-'+s+'">'+s+'</span></div><div class="card-content">'+esc(r.content||"")+'</div><div class="card-meta"><span>'+fmt(r.trigger_time)+'</span>'+((r.repeat_type&&r.repeat_type!=="none")?'<span class="card-repeat">'+rep(r.repeat_type)+'</span>':'')+'</div><div class="card-actions"><button class="btn btn-primary" onclick="trig(\''+r.id+'\')">Trigger</button><button class="btn btn-danger" onclick="del(\''+r.id+'\')">Delete</button></div></div>';
    }).join("")
  }catch(e){console.error(e)}
}
async function create(){
  var t=document.getElementById("title").value.trim();if(!t){showMsg("Title required","err");return}
  var tv=document.getElementById("time").value;var tt=tv?new Date(tv).toISOString():new Date().toISOString();
  var b={title:t,content:document.getElementById("content").value.trim(),trigger_time:tt,is_repeating:document.getElementById("repeat").value!=="none",repeat_type:document.getElementById("repeat").value};
  try{
    var r=await fetch(A,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(b)});
    if(r.ok){closeModal();toast("Created: "+t);load()}else{showMsg("Failed: "+r.status,"err")}
  }catch(e){showMsg("Error: "+e.message,"err")}
}
async function trig(id){try{await fetch(A+"/"+id+"/trigger",{method:"POST"});toast("Triggered!");load()}catch(e){toast("Error: "+e.message,true)}}
async function del(id){if(!confirm("Delete?"))return;try{await fetch(A+"/"+id,{method:"DELETE"});toast("Deleted");load()}catch(e){toast("Error",true)}}
function showMsg(t,c){var m=document.getElementById("msg");m.textContent=t;m.className="msg msg-"+c}
function esc(s){var d=document.createElement("div");d.textContent=s;return d.innerHTML}
setInterval(function(){document.getElementById("clock").textContent=new Date().toLocaleTimeString("zh-CN")},1000)
load();setInterval(load,5000)