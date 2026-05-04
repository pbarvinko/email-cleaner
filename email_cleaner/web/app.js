const form = document.getElementById('scan-form');
const messages = document.getElementById('messages');
const results = document.getElementById('results');

let currentResults = [];

function showMessage(text, kind = 'info') {
  messages.replaceChildren();
  const message = document.createElement('div');
  message.className = `message ${kind}`;
  message.textContent = text;
  messages.appendChild(message);
}

function renderResults() {
  if (!currentResults.length) {
    results.replaceChildren();
    return;
  }

  const fragment = document.createDocumentFragment();

  currentResults.forEach((item, index) => {
    const article = document.createElement('article');
    article.className = 'card';

    const header = document.createElement('header');
    header.className = 'card-header';

    const meta = document.createElement('div');
    const subject = document.createElement('h2');
    subject.textContent = item.subject || '(No subject)';
    meta.appendChild(subject);

    const from = document.createElement('p');
    const fromParts = [];
    if (item.from_name) {
      fromParts.push(item.from_name);
    }
    if (item.from_email) {
      fromParts.push(`<${item.from_email}>`);
    }
    from.textContent = fromParts.join(' ');
    meta.appendChild(from);

    const date = document.createElement('p');
    date.textContent = item.date || '';
    meta.appendChild(date);

    header.appendChild(meta);

    const labelWrapper = document.createElement('label');
    labelWrapper.textContent = 'Label';
    const select = document.createElement('select');
    select.dataset.index = String(index);
    select.className = 'label-select';
    ['keep', 'move', 'uncertain'].forEach((label) => {
      const option = document.createElement('option');
      option.value = label;
      option.textContent = label;
      option.selected = item.label === label;
      select.appendChild(option);
    });
    labelWrapper.appendChild(select);
    header.appendChild(labelWrapper);

    article.appendChild(header);

    const reason = document.createElement('p');
    reason.className = 'reason';
    const reasonLabel = document.createElement('strong');
    reasonLabel.textContent = 'Reason:';
    reason.appendChild(reasonLabel);
    reason.appendChild(document.createTextNode(` ${item.reason}`));
    article.appendChild(reason);

    const snippet = document.createElement('p');
    snippet.className = 'snippet';
    snippet.textContent = item.snippet;
    article.appendChild(snippet);

    const details = document.createElement('details');
    const summary = document.createElement('summary');
    summary.textContent = 'Selected headers';
    details.appendChild(summary);
    const pre = document.createElement('pre');
    pre.textContent = JSON.stringify(item.headers || {}, null, 2);
    details.appendChild(pre);
    article.appendChild(details);

    fragment.appendChild(article);
  });

  results.replaceChildren(fragment);

  results.querySelectorAll('.label-select').forEach((select) => {
    select.addEventListener('change', (event) => {
      const index = Number(event.target.dataset.index);
      currentResults[index].label = event.target.value;
      renderResults();
    });
  });
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());

  if (!payload.limit) {
    delete payload.limit;
  }

  showMessage('Running read-only scan...');
  results.replaceChildren();
  currentResults = [];

  const response = await fetch('/api/scan', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    const errorText = data?.error?.details?.[0]?.msg || data?.error?.message || 'Scan failed';
    showMessage(errorText, 'error');
    return;
  }

  currentResults = data.results || [];
  showMessage(`Loaded ${data.count} result(s). Label changes stay in this browser only.`, 'success');
  renderResults();
});
