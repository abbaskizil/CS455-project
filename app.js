const API = 'http://localhost:8000';

// Generate a session ID once per page load
const SESSION_ID = crypto.randomUUID();

// ── INDEX REPO ───────────────────────────────────────────────
async function indexRepo() {
  const url = document.getElementById('github-url').value.trim();
  if (!url) {
    setStatus('Enter a GitHub URL first.', 'error');
    return;
  }

  const btn = document.getElementById('index-btn');
  btn.disabled = true;
  btn.textContent = 'Indexing...';
  setStatus('Cloning & indexing...', 'loading');

  try {
    const res = await fetch(`${API}/index`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ github_url: url })
    });

    const data = await res.json();

    if (!res.ok) {
      setStatus(data.detail || 'Indexing failed.', 'error');
      await loadFiles();
      return;
    }

    setStatus('Loading files...', 'loading');
    await loadFiles();
    setStatus('Indexed successfully.', 'success');
  } catch (err) {
    setStatus('Cannot reach backend.', 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Index';
  }
}

// ── LOAD FILE LIST ───────────────────────────────────────────
async function loadFiles() {
  try {
    const res  = await fetch(`${API}/files`);
    const data = await res.json();
    
    document.getElementById('repo-name-value').style.color = 'var(--yellow)';
    document.getElementById('repo-name-value').textContent = data.repo || '';
    
    const list = document.getElementById('file-list');
    list.innerHTML = '';
    (data.files || []).sort().forEach(f => {
      const li = document.createElement('li');
      li.textContent = f;
      li.title = f;
      list.appendChild(li);
    });
  } catch (_) {}
}

// ── SEND CHAT MESSAGE ────────────────────────────────────────
async function sendMessage() {
  const input = document.getElementById('query-input');
  const query = input.value.trim();
  if (!query) return;

  input.value = '';

  appendMessage('user', query);
  const typingEl = appendTyping();

  const sendBtn = document.getElementById('send-btn');
  sendBtn.disabled = true;

  try {
    const res = await fetch(`${API}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, session_id: SESSION_ID })
    });

    const data = await res.json();
    typingEl.remove();

    if (!res.ok) {
      appendMessage('bot', `⚠ ${data.detail || 'Something went wrong.'}`);
      return;
    }

    appendMessage('bot', data.response);
  } catch (err) {
    typingEl.remove();
    appendMessage('bot', '⚠ Cannot reach backend. Is the server running?');
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
}

// ── UI HELPERS ───────────────────────────────────────────────
function appendMessage(role, text) {
  const messages = document.getElementById('messages');

  const wrap = document.createElement('div');
  wrap.className = `message ${role}`;

  const label = document.createElement('div');
  label.className = 'msg-label';
  label.textContent = role === 'user' ? 'you' : 'assistant';

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';

  if (role === 'bot') {
    bubble.innerHTML = marked.parse(text);
  } else {
    bubble.textContent = text;
  }

  wrap.appendChild(label);
  wrap.appendChild(bubble);
  messages.appendChild(wrap);
  messages.scrollTop = messages.scrollHeight;
  return wrap;
}

function appendTyping() {
  const messages = document.getElementById('messages');

  const wrap = document.createElement('div');
  wrap.className = 'message bot';

  const label = document.createElement('div');
  label.className = 'msg-label';
  label.textContent = 'assistant';

  const dots = document.createElement('div');
  dots.className = 'typing-dots';
  dots.innerHTML = '<span></span><span></span><span></span>';

  wrap.appendChild(label);
  wrap.appendChild(dots);
  messages.appendChild(wrap);
  messages.scrollTop = messages.scrollHeight;
  return wrap;
}

function setStatus(msg, type) {
  const el = document.getElementById('index-status');
  el.textContent = msg;
  el.className = `status-msg ${type}`;
}

// ── KEYBOARD SHORTCUT ────────────────────────────────────────
function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

// ── INIT ─────────────────────────────────────────────────────
loadFiles();
