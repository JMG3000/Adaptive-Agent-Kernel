(() => {
  let sessionId = null;
  let isSubmitting = false;
  const form = document.getElementById('interaction-form');
  const request = document.getElementById('request');
  const correction = document.getElementById('correction');
  const response = document.getElementById('response');
  const feedback = document.getElementById('interaction-feedback');
  const status = document.getElementById('session-status');
  const send = form.querySelector('button[type="submit"]');

  const hasValidRequest = () => request.value.trim().length > 0;
  const syncSendState = () => {
    send.disabled = isSubmitting || !hasValidRequest();
  };

  const appendInlineMarkdown = (parent, source) => {
    const tokenPattern = /(`[^`\n]+`|\*\*[^*\n]+\*\*|__[^_\n]+__|\*[^*\n]+\*|_[^_\n]+_|\[[^\]\n]+\]\([^)\s]+\))/g;
    let offset = 0;
    for (const match of source.matchAll(tokenPattern)) {
      if (match.index > offset) {
        parent.append(document.createTextNode(source.slice(offset, match.index)));
      }
      const token = match[0];
      if (token.startsWith('`')) {
        const code = document.createElement('code');
        code.textContent = token.slice(1, -1);
        parent.append(code);
      } else if (token.startsWith('**') || token.startsWith('__')) {
        const strong = document.createElement('strong');
        strong.textContent = token.slice(2, -2);
        parent.append(strong);
      } else if (token.startsWith('*') || token.startsWith('_')) {
        const emphasis = document.createElement('em');
        emphasis.textContent = token.slice(1, -1);
        parent.append(emphasis);
      } else {
        const linkMatch = token.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
        const label = linkMatch[1];
        const href = linkMatch[2];
        let safeUrl = null;
        try {
          const parsed = new URL(href);
          if (parsed.protocol === 'http:' || parsed.protocol === 'https:') {
            safeUrl = parsed.href;
          }
        } catch (_error) {
          safeUrl = null;
        }
        if (safeUrl === null) {
          parent.append(document.createTextNode(label));
        } else {
          const link = document.createElement('a');
          link.textContent = label;
          link.setAttribute('href', safeUrl);
          link.setAttribute('target', '_blank');
          link.setAttribute('rel', 'noopener noreferrer');
          parent.append(link);
        }
      }
      offset = match.index + token.length;
    }
    if (offset < source.length) {
      parent.append(document.createTextNode(source.slice(offset)));
    }
  };

  const headingMatch = (line) => line.match(/^(#{1,6})\s+(.+)$/);
  const unorderedItemMatch = (line) => line.match(/^\s*[-+*]\s+(.+)$/);
  const orderedItemMatch = (line) => line.match(/^\s*\d+[.)]\s+(.+)$/);
  const isFence = (line) => /^\s*```[^\n]*$/.test(line);
  const startsBlock = (line) =>
    line.trim() === '' ||
    isFence(line) ||
    headingMatch(line) !== null ||
    unorderedItemMatch(line) !== null ||
    orderedItemMatch(line) !== null;

  const renderMarkdown = (container, source) => {
    const lines = String(source).replace(/\r\n?/g, '\n').split('\n');
    const blocks = [];
    let index = 0;
    while (index < lines.length) {
      const line = lines[index];
      if (line.trim() === '') {
        index += 1;
        continue;
      }

      if (isFence(line)) {
        index += 1;
        const codeLines = [];
        while (index < lines.length && !/^\s*```\s*$/.test(lines[index])) {
          codeLines.push(lines[index]);
          index += 1;
        }
        if (index < lines.length) index += 1;
        const pre = document.createElement('pre');
        const code = document.createElement('code');
        code.textContent = codeLines.join('\n');
        pre.append(code);
        blocks.push(pre);
        continue;
      }

      const heading = headingMatch(line);
      if (heading !== null) {
        const element = document.createElement(`h${heading[1].length}`);
        appendInlineMarkdown(element, heading[2]);
        blocks.push(element);
        index += 1;
        continue;
      }

      const unordered = unorderedItemMatch(line);
      const ordered = orderedItemMatch(line);
      if (unordered !== null || ordered !== null) {
        const itemMatcher = unordered !== null ? unorderedItemMatch : orderedItemMatch;
        const list = document.createElement(unordered !== null ? 'ul' : 'ol');
        let item = itemMatcher(lines[index]);
        while (item !== null) {
          const listItem = document.createElement('li');
          appendInlineMarkdown(listItem, item[1]);
          list.append(listItem);
          index += 1;
          item = index < lines.length ? itemMatcher(lines[index]) : null;
        }
        blocks.push(list);
        continue;
      }

      const paragraphLines = [line];
      index += 1;
      while (index < lines.length && !startsBlock(lines[index])) {
        paragraphLines.push(lines[index]);
        index += 1;
      }
      const paragraph = document.createElement('p');
      appendInlineMarkdown(paragraph, paragraphLines.join(' '));
      blocks.push(paragraph);
    }
    container.replaceChildren(...blocks);
  };

  const buildMessage = (role, label) => {
    const message = document.createElement('article');
    message.className = `message message-${role}`;
    const messageLabel = document.createElement('p');
    messageLabel.className = 'message-label';
    messageLabel.textContent = label;
    const body = document.createElement('div');
    body.className = 'message-body';
    message.append(messageLabel, body);
    return {message, body};
  };

  let successfulTurns = 0;
  const appendTranscriptTurn = (userText, agentText) => {
    if (successfulTurns === 0) response.replaceChildren();
    const user = buildMessage('user', 'User');
    user.body.textContent = userText;
    const agent = buildMessage('agent', 'AAK');
    renderMarkdown(agent.body, agentText);
    response.append(user.message, agent.message);
    successfulTurns += 1;
  };

  request.addEventListener('input', syncSendState);
  request.addEventListener('keydown', (event) => {
    if (event.key !== 'Enter' || (!event.ctrlKey && !event.metaKey)) return;
    event.preventDefault();
    if (!isSubmitting && hasValidRequest()) form.requestSubmit();
  });

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (isSubmitting || !hasValidRequest()) {
      syncSendState();
      return;
    }
    const payload = {request: request.value};
    if (correction.value) payload.correction = correction.value;
    if (sessionId) payload.session_id = sessionId;
    isSubmitting = true;
    syncSendState();
    feedback.textContent = 'Working…';
    try {
      const result = await fetch('/v1/interactions', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload),
      });
      if (!result.ok) throw new Error('The interaction could not be completed.');
      const body = await result.json();
      sessionId = body.session_id;
      appendTranscriptTurn(payload.request, body.response);
      feedback.textContent = '';
      status.textContent = 'Session continuity active.';
      request.value = '';
      correction.value = '';
      request.focus();
    } catch (error) {
      feedback.textContent = error.message;
    } finally {
      isSubmitting = false;
      syncSendState();
    }
  });

  document.getElementById('new-session').addEventListener('click', () => {
    sessionId = null;
    successfulTurns = 0;
    status.textContent = 'New Session — no conversation continuity yet.';
    response.textContent = 'Your response will appear here.';
    feedback.textContent = '';
    request.value = '';
    correction.value = '';
    syncSendState();
    request.focus();
  });

  syncSendState();
})();
