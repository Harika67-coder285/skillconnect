
/* Simple localStorage-based demo backend for SkillConnect.
   - users: [{id,email,password,firstName,lastName,role,bio}]
   - currentUser: email
   - projects: [{id,title,desc,budget,ownerEmail}]
   - proposals: [{id,projectId,freelancerEmail,message,bid}]
*/
window.SkillConnect = (function(){
  function _id(prefix){ return prefix + '_' + Math.random().toString(36).slice(2,9); }

  function load(key){ try{ return JSON.parse(localStorage.getItem(key)||'null'); }catch(e){ return null; } }
  function save(key,val){ localStorage.setItem(key, JSON.stringify(val)); }

  function init(){
    if(!load('users')) save('users', []);
    if(!load('projects')) save('projects', []);
    if(!load('proposals')) save('proposals', []);
    // Attach simple page initializers
    if(document.getElementById('loginForm')) {
      // nothing extra
    }
    renderCommon();
    renderCurrentPageData();
  }

  function renderCommon(){
    // replace sitename in header if exists
    document.querySelectorAll('.sitename').forEach(el=>{
      el.textContent = 'SkillConnect';
    });
  }

  function signup(e){
    e.preventDefault();
    const users = load('users') || [];
    const email = document.getElementById('signupEmail').value.trim();
    if(users.find(u=>u.email===email)){ document.getElementById('signupMsg').textContent = 'Email already used.'; return false; }
    const user = {
      id: _id('u'),
      email,
      password: document.getElementById('signupPassword').value,
      firstName: document.getElementById('firstName').value.trim(),
      lastName: document.getElementById('lastName').value.trim(),
      role: document.getElementById('userRole').value,
      bio: document.getElementById('bio').value || ''
    };
    users.push(user);
    save('users', users);
    save('currentUser', user.email);
    document.getElementById('signupMsg').textContent = 'Account created. Redirecting to dashboard...';
    setTimeout(()=> location.href = 'dashboard.html', 800);
    return false;
  }

  function login(e){
    e.preventDefault();
    const email = document.getElementById('loginEmail').value.trim();
    const pwd = document.getElementById('loginPassword').value;
    const users = load('users') || [];
    const u = users.find(x=>x.email===email && x.password===pwd);
    if(!u){ document.getElementById('loginMsg').textContent = 'Invalid credentials'; return false; }
    save('currentUser', u.email);
    location.href = 'dashboard.html';
    return false;
  }

  function logout(){
    localStorage.removeItem('currentUser');
    location.href = 'index.html';
  }

  function getCurrentUser(){
    const email = localStorage.getItem('currentUser');
    const users = load('users') || [];
    return users.find(u=>u.email===email) || null;
  }

  function postProject(e){
    e.preventDefault();
    const user = getCurrentUser();
    if(!user || (user.role!=='client' && user.role!=='both')){ document.getElementById('postMsg').textContent = 'You must be logged in as a client to post.'; return false; }
    const projects = load('projects') || [];
    const project = {
      id: _id('p'),
      title: document.getElementById('projectTitle').value,
      desc: document.getElementById('projectDesc').value,
      budget: document.getElementById('projectBudget').value,
      ownerEmail: user.email,
      createdAt: Date.now()
    };
    projects.unshift(project);
    save('projects', projects);
    document.getElementById('postMsg').textContent = 'Project posted!';
    renderMyProjects();
    return false;
  }

  function renderMyProjects(){
    const user = getCurrentUser();
    if(!user) return;
    const projects = load('projects') || [];
    const mine = projects.filter(p=>p.ownerEmail===user.email);
    const el = document.getElementById('myProjects');
    if(!el) return;
    el.innerHTML = mine.map(p=>`<div class="card mb-2 p-2"><strong>${p.title}</strong><div>${p.desc}</div><small>Budget: ${p.budget}</small></div>`).join('') || '<p>No projects yet.</p>';
  }

  function renderProjectsList(){
    const projects = load('projects') || [];
    const el = document.getElementById('projectsList');
    if(!el) return;
    if(projects.length===0) { el.innerHTML = '<p>No projects posted yet.</p>'; return; }
    el.innerHTML = projects.map(p=>{
      const owner = p.ownerEmail || 'Unknown';
      return `<div class="card mb-3 p-3">
        <h5>${p.title}</h5>
        <p>${p.desc}</p>
        <p><strong>Budget:</strong> ${p.budget} • <strong>Client:</strong> ${owner}</p>
        <a href="project.html?id=${p.id}" class="btn btn-sm btn-primary">View</a>
      </div>`;
    }).join('');
  }

  function renderFreelancersList(){
    const users = load('users') || [];
    const freelancers = users.filter(u=> u.role==='freelancer' || u.role==='both');
    const el = document.getElementById('freelancersList');
    if(!el) return;
    if(freelancers.length===0) { el.innerHTML = '<p>No freelancers yet.</p>'; return; }
    el.innerHTML = freelancers.map(f=>{
      return `<div class="card mb-2 p-2">
        <strong>${f.firstName} ${f.lastName}</strong>
        <p>${(f.bio||'No bio provided').slice(0,120)}</p>
        <a href="profile.html?email=${encodeURIComponent(f.email)}" class="btn btn-sm btn-outline-primary">View Profile</a>
      </div>`;
    }).join('');
  }

  function renderProfilePage(){
    const params = new URLSearchParams(location.search);
    const email = params.get('email');
    const users = load('users')||[];
    const u = users.find(x=>x.email===email);
    const el = document.getElementById('profileCard');
    if(!el) return;
    if(!u){ el.innerHTML = '<p>User not found.</p>'; return; }
    el.innerHTML = `<div class="card p-3 mb-3"><h3>${u.firstName} ${u.lastName}</h3><p>${u.bio||'No bio'}</p><p><strong>Role:</strong> ${u.role}</p></div>`;
    // show user's projects if any
    const projects = (load('projects')||[]).filter(p=>p.ownerEmail===u.email);
    const pEl = document.getElementById('profileProjects');
    pEl.innerHTML = projects.map(p=>`<div class="card p-2 mb-2"><strong>${p.title}</strong><div>${p.desc}</div></div>`).join('') || '<p>No projects.</p>';
  }

  function renderProjectPage(){
    const params = new URLSearchParams(location.search);
    const id = params.get('id');
    const projects = load('projects')||[];
    const project = projects.find(p=>p.id===id);
    const el = document.getElementById('projectView');
    if(!el) return;
    if(!project){ el.innerHTML = '<p>Project not found.</p>'; return; }
    el.innerHTML = `<div class="card p-3"><h3>${project.title}</h3><p>${project.desc}</p><p><strong>Budget:</strong> ${project.budget}</p><p><strong>Client:</strong> ${project.ownerEmail}</p></div>`;
    // proposals list
    const proposals = (load('proposals')||[]).filter(pr=>pr.projectId===id);
    const pEl = document.getElementById('proposalsList');
    pEl.innerHTML = proposals.map(pr=>`<div class="card p-2 mb-2"><strong>${pr.freelancerEmail}</strong><p>${pr.message}</p><small>Bid: ${pr.bid}</small></div>`).join('') || '<p>No proposals yet.</p>';
    // proposal form if logged in as freelancer
    const user = getCurrentUser();
    const formContainer = document.getElementById('proposalFormContainer');
    if(user && (user.role==='freelancer' || user.role==='both')){
      formContainer.innerHTML = `<h4>Send Proposal</h4>
        <form onsubmit="return SkillConnect.sendProposal(event,'${id}')">
          <div class="mb-2"><textarea id="proposalMsg" class="form-control" required placeholder="Your message"></textarea></div>
          <div class="mb-2"><input id="proposalBid" class="form-control" placeholder="Your bid (e.g., 250)" required></div>
          <button class="btn btn-primary">Send Proposal</button>
        </form>`;
    } else {
      formContainer.innerHTML = '<p>Login as a freelancer to send proposals.</p>';
    }
  }

  function sendProposal(e, projectId){
    e.preventDefault();
    const user = getCurrentUser();
    if(!user) return alert('Login as freelancer to send proposal');
    const proposals = load('proposals') || [];
    const proposal = {
      id: _id('pr'),
      projectId,
      freelancerEmail: user.email,
      message: document.getElementById('proposalMsg').value,
      bid: document.getElementById('proposalBid').value,
      createdAt: Date.now()
    };
    proposals.unshift(proposal);
    save('proposals', proposals);
    alert('Proposal sent!');
    renderProjectPage();
    return false;
  }

  function renderDashboard(){
    const el = document.getElementById('dashboardContent');
    if(!el) return;
    const user = getCurrentUser();
    if(!user){ el.innerHTML = '<p>Please <a href="login.html">login</a> or <a href="signup.html">signup</a>.</p>'; return; }
    let html = `<p>Welcome, <strong>${user.firstName} ${user.lastName}</strong> (${user.role})</p>`;
    if(user.role==='client' || user.role==='both'){
      const myProjects = (load('projects')||[]).filter(p=>p.ownerEmail===user.email);
      html += `<h4>Your Projects</h4>` + (myProjects.map(p=>`<div class="card p-2 mb-2"><strong>${p.title}</strong><div>${p.desc}</div><a href="project.html?id=${p.id}" class="btn btn-sm btn-link">View</a></div>`).join('') || '<p>No projects posted.</p>');
    }
    if(user.role==='freelancer' || user.role==='both'){
      const proposals = (load('proposals')||[]).filter(pr=>pr.freelancerEmail===user.email);
      html += `<h4>Your Proposals</h4>` + (proposals.map(pr=>`<div class="card p-2 mb-2"><strong>Project:</strong> ${pr.projectId}<div>${pr.message}</div><small>Bid: ${pr.bid}</small></div>`).join('') || '<p>No proposals yet.</p>');
      html += `<h4>Your Profile</h4><div class="card p-2 mb-2"><strong>${user.firstName} ${user.lastName}</strong><p>${user.bio||''}</p></div>`;
    }
    el.innerHTML = html;
  }

  function renderCurrentPageData(){
    renderProjectsList();
    renderFreelancersList();
    renderMyProjects();
    renderProfilePage();
    renderProjectPage();
    renderDashboard();
  }

  // Auto-init when DOM loaded
  document.addEventListener('DOMContentLoaded', init);

  return {
    signup, login, logout, postProject, sendProposal, renderCurrentPageData
  };
})();
