(() => {
  let sessionId = null;
  let isSubmitting = false;
  const form = document.getElementById('interaction-form');
  const request = document.getElementById('request');
  const correction = document.getElementById('correction');
  const response = document.getElementById('response');
  const status = document.getElementById('session-status');
  const send = form.querySelector('button[type="submit"]');

  const hasValidRequest = () => request.value.trim().length > 0;
  const syncSendState = () => {
    send.disabled = isSubmitting || !hasValidRequest();
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
    response.textContent = 'Working…';
    try {
      const result = await fetch('/v1/interactions', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload),
      });
      if (!result.ok) throw new Error('The interaction could not be completed.');
      const body = await result.json();
      sessionId = body.session_id;
      response.textContent = body.response;
      status.textContent = 'Session continuity active.';
      request.value = '';
      correction.value = '';
      request.focus();
    } catch (error) {
      response.textContent = error.message;
    } finally {
      isSubmitting = false;
      syncSendState();
    }
  });

  document.getElementById('new-session').addEventListener('click', () => {
    sessionId = null;
    status.textContent = 'New Session — no conversation continuity yet.';
    response.textContent = 'Your response will appear here.';
    request.value = '';
    correction.value = '';
    syncSendState();
    request.focus();
  });

  syncSendState();
})();
