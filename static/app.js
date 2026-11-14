const form=document.getElementById('chatForm'), input=document.getElementById('message'), messages=document.getElementById('messages');
function addMessage(text,who='bot',extra=null){
 const wrap=document.createElement('div');wrap.className='message '+who;
 if(who==='bot'){const av=document.createElement('div');av.className='avatar';av.textContent='✦';wrap.appendChild(av)}
 const bubble=document.createElement('div');bubble.className='bubble';
 const p=document.createElement('p');p.textContent=text;bubble.appendChild(p);
 if(extra){const wf=document.createElement('div');wf.className='workflow';const title=document.createElement('b');title.textContent='AGENT EXECUTION TRACE';wf.appendChild(title);const ol=document.createElement('ol');extra.steps.forEach(s=>{const li=document.createElement('li');li.innerHTML='<strong></strong><br><span></span>';li.querySelector('strong').textContent=s.name;li.querySelector('span').textContent=s.result;ol.appendChild(li)});wf.appendChild(ol);const st=document.createElement('span');st.className='status '+(extra.status==='Escalated'?'escalated':'');st.textContent=extra.status;wf.appendChild(st);bubble.appendChild(wf)}
 wrap.appendChild(bubble);messages.appendChild(wrap);messages.scrollTop=messages.scrollHeight;
}
async function refresh(){try{const r=await fetch('/api/requests');const rows=await r.json();const box=document.getElementById('requestList');box.innerHTML='';if(!rows.length){box.textContent='No requests yet.';box.className='request-list muted';return}box.className='request-list';rows.slice(0,6).forEach(x=>{const d=document.createElement('div');d.className='request-item';const b=document.createElement('b');b.textContent=x.service;const s=document.createElement('small');s.textContent=x.id+' · '+x.status;d.append(b,s);box.appendChild(d)})}catch(e){}}
form.addEventListener('submit',async e=>{e.preventDefault();const message=input.value.trim();if(!message)return;addMessage(message,'user');input.value='';const btn=form.querySelector('button');btn.disabled=true;btn.textContent='Working...';try{const res=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message,student:document.getElementById('student').value})});const data=await res.json();if(!res.ok)throw new Error(data.error||'Request failed');addMessage(data.reply,'bot',data);refresh()}catch(err){addMessage('Sorry, an error occurred: '+err.message)}finally{btn.disabled=false;btn.innerHTML='Send <span>➤</span>'}});
document.querySelectorAll('[data-prompt]').forEach(b=>b.addEventListener('click',()=>{input.value=b.dataset.prompt;input.focus()}));
document.getElementById('refreshBtn').addEventListener('click',refresh);
document.getElementById('clearBtn').addEventListener('click',()=>{messages.innerHTML='';addMessage("Chat cleared. What campus task can I help with?")});
refresh();
