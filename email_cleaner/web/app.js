const form = document.getElementById('scan-form');
const messages = document.getElementById('messages');
const results = document.getElementById('results');

function showMessage(text, kind = 'info') {
  messages.replaceChildren();
  const message = document.createElement('div');
  message.className = `message ${kind}`;
  message.textContent = text;
  messages.appendChild(message);
}

function formatSender(item) {
  const parts = [];
  if (item.from_name) {
    parts.push(item.from_name);
  }
  if (item.from_email) {
    parts.push(parts.length ? `<${item.from_email}>` : item.from_email);
  }
  return parts.join(' ') || '(Unknown sender)';
}

function formatClassification(item) {
  if (item.classification_status === 'not_classified') {
    return 'not classified';
  }

  return item.label || 'not classified';
}

function formatAction(item) {
  if (item.action === 'moved' && item.target_folder) {
    return `moved to ${item.target_folder}`;
  }
  if (item.action === 'suggested_move') {
    return 'analysis only';
  }
  if (item.classification_status === 'not_classified') {
    return 'search only';
  }

  return item.action_reason || 'label keep';
}

function createBadge(label) {
  const badge = document.createElement('span');
  badge.className = `badge badge-${label}`;
  badge.textContent = label;
  return badge;
}

function renderResults(items) {
  if (!items.length) {
    results.replaceChildren();
    return;
  }

  const tableWrapper = document.createElement('div');
  tableWrapper.className = 'table-wrapper';
  const table = document.createElement('table');
  table.className = 'results-table';

  const thead = document.createElement('thead');
  const headerRow = document.createElement('tr');
  ['From', 'Subject', 'Date/Time', 'Classification', 'Action', 'Snippet', 'Details'].forEach((label) => {
    const th = document.createElement('th');
    th.scope = 'col';
    th.textContent = label;
    headerRow.appendChild(th);
  });
  thead.appendChild(headerRow);
  table.appendChild(thead);

  const tbody = document.createElement('tbody');

  items.forEach((item) => {
    const row = document.createElement('tr');
    row.className = 'result-row';

    const fromCell = document.createElement('td');
    fromCell.textContent = formatSender(item);
    row.appendChild(fromCell);

    const subjectCell = document.createElement('td');
    subjectCell.textContent = item.subject || '(No subject)';
    row.appendChild(subjectCell);

    const dateCell = document.createElement('td');
    dateCell.className = 'secondary-column';
    dateCell.textContent = item.date || '';
    row.appendChild(dateCell);

    const classificationCell = document.createElement('td');
    if (item.classification_status === 'classified' && item.label) {
      classificationCell.appendChild(createBadge(item.label));
    } else {
      classificationCell.textContent = formatClassification(item);
    }
    row.appendChild(classificationCell);

    const actionCell = document.createElement('td');
    actionCell.textContent = formatAction(item);
    row.appendChild(actionCell);

    const snippetCell = document.createElement('td');
    snippetCell.className = 'snippet-cell';
    snippetCell.textContent = item.snippet;
    row.appendChild(snippetCell);

    const detailsCell = document.createElement('td');
    const details = document.createElement('details');
    details.className = 'details-toggle';
    const summary = document.createElement('summary');
    summary.textContent = 'View';
    details.appendChild(summary);

    const detailBody = document.createElement('div');
    detailBody.className = 'detail-body';

    const reason = document.createElement('p');
    reason.className = 'detail-line';
    const reasonLabel = document.createElement('strong');
    reasonLabel.textContent = 'Reason:';
    reason.appendChild(reasonLabel);
    reason.appendChild(document.createTextNode(` ${item.reason || 'not classified'}`));
    detailBody.appendChild(reason);

    const snippet = document.createElement('p');
    snippet.className = 'detail-line full-snippet';
    const snippetLabel = document.createElement('strong');
    snippetLabel.textContent = 'Snippet:';
    snippet.appendChild(snippetLabel);
    snippet.appendChild(document.createTextNode(` ${item.snippet}`));
    detailBody.appendChild(snippet);

    const pre = document.createElement('pre');
    pre.textContent = JSON.stringify(item.headers || {}, null, 2);
    detailBody.appendChild(pre);

    details.appendChild(detailBody);
    detailsCell.appendChild(details);
    row.appendChild(detailsCell);
    tbody.appendChild(row);
  });

  table.appendChild(tbody);
  tableWrapper.appendChild(table);
  results.replaceChildren(tableWrapper);
}

function getModeStatusText(data) {
  if (data.mode === 'search') {
    return `Loaded ${data.count} result(s). Search only; no classification was run.`;
  }
  if (data.mode === 'clean') {
    return `Loaded ${data.count} result(s). Applied ${data.applied_count} mailbox move(s).`;
  }

  return `Loaded ${data.count} result(s). Classify mode only; suggested moves were not applied.`;
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());

  if (!payload.limit) {
    delete payload.limit;
  }

  showMessage(`Running ${payload.mode} scan...`);
  results.replaceChildren();

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

  showMessage(getModeStatusText(data), 'success');
  renderResults(data.results || []);
});
