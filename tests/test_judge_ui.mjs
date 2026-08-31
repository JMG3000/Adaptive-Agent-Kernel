import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const SCRIPT = readFileSync(new URL('../aak/judge_ui.js', import.meta.url), 'utf8');

class FakeElement {
  constructor() {
    this.disabled = false;
    this.focusCount = 0;
    this.listeners = new Map();
    this.textContent = '';
    this.value = '';
  }

  addEventListener(type, listener) {
    const listeners = this.listeners.get(type) ?? [];
    listeners.push(listener);
    this.listeners.set(type, listeners);
  }

  async emit(type, options = {}) {
    const event = {
      ctrlKey: false,
      key: '',
      metaKey: false,
      preventDefault() {
        this.defaultPrevented = true;
      },
      defaultPrevented: false,
      ...options,
    };
    for (const listener of this.listeners.get(type) ?? []) {
      await listener(event);
    }
    return event;
  }

  focus() {
    this.focusCount += 1;
  }
}

class FakeForm extends FakeElement {
  constructor(send) {
    super();
    this.send = send;
    this.requestSubmitCount = 0;
    this.submission = Promise.resolve();
  }

  querySelector(selector) {
    assert.equal(selector, 'button[type="submit"]');
    return this.send;
  }

  requestSubmit() {
    this.requestSubmitCount += 1;
    this.submission = this.emit('submit');
  }
}

function jsonResponse(body, {ok = true} = {}) {
  return {
    ok,
    async json() {
      return body;
    },
  };
}

function loadUi(fetchImpl) {
  const elements = {
    correction: new FakeElement(),
    'new-session': new FakeElement(),
    request: new FakeElement(),
    response: new FakeElement(),
    'session-status': new FakeElement(),
  };
  elements.send = new FakeElement();
  elements['interaction-form'] = new FakeForm(elements.send);
  const document = {
    getElementById(id) {
      return elements[id];
    },
  };
  vm.runInNewContext(SCRIPT, {document, fetch: fetchImpl});
  return elements;
}

test('empty and whitespace-only requests cannot submit', async () => {
  const payloads = [];
  const ui = loadUi(async (_url, options) => {
    payloads.push(JSON.parse(options.body));
    return jsonResponse({session_id: 'session-1', response: 'ok'});
  });

  assert.equal(ui.send.disabled, true);
  for (const value of ['', '   ', '\t\n']) {
    ui.request.value = value;
    await ui.request.emit('input');
    assert.equal(ui.send.disabled, true);
    await ui['interaction-form'].emit('submit');
  }
  assert.deepEqual(payloads, []);
});

test('Unicode non-whitespace request text can submit', async () => {
  const payloads = [];
  const ui = loadUi(async (_url, options) => {
    payloads.push(JSON.parse(options.body));
    return jsonResponse({session_id: 'session-1', response: 'ok'});
  });

  ui.request.value = 'こんにちは';
  await ui.request.emit('input');

  assert.equal(ui.send.disabled, false);
  await ui['interaction-form'].emit('submit');
  assert.equal(payloads[0].request, 'こんにちは');
});

test('Ctrl+Enter submits valid input through the form submit path', async () => {
  const payloads = [];
  const ui = loadUi(async (_url, options) => {
    payloads.push(JSON.parse(options.body));
    return jsonResponse({session_id: 'session-1', response: 'ok'});
  });
  ui.request.value = 'Help me decide.';
  await ui.request.emit('input');

  const event = await ui.request.emit('keydown', {ctrlKey: true, key: 'Enter'});
  await ui['interaction-form'].submission;

  assert.equal(event.defaultPrevented, true);
  assert.equal(ui['interaction-form'].requestSubmitCount, 1);
  assert.equal(payloads.length, 1);
});

test('plain Enter remains available for a newline and does not submit', async () => {
  let fetchCount = 0;
  const ui = loadUi(async () => {
    fetchCount += 1;
    return jsonResponse({session_id: 'session-1', response: 'ok'});
  });
  ui.request.value = 'First line';
  await ui.request.emit('input');

  const event = await ui.request.emit('keydown', {key: 'Enter'});

  assert.equal(event.defaultPrevented, false);
  assert.equal(ui['interaction-form'].requestSubmitCount, 0);
  assert.equal(fetchCount, 0);
});

test('successful submission clears inputs, restores focus, and preserves Session continuity', async () => {
  const payloads = [];
  const ui = loadUi(async (_url, options) => {
    payloads.push(JSON.parse(options.body));
    return jsonResponse({session_id: 'session-1', response: 'completed'});
  });
  ui.request.value = 'First request';
  ui.correction.value = 'Correct this';
  await ui.request.emit('input');

  await ui['interaction-form'].emit('submit');

  assert.equal(ui.request.value, '');
  assert.equal(ui.correction.value, '');
  assert.equal(ui.request.focusCount, 1);
  assert.equal(ui.response.textContent, 'completed');
  assert.equal(ui.send.disabled, true);

  ui.request.value = 'Continue';
  await ui.request.emit('input');
  await ui['interaction-form'].emit('submit');
  assert.equal(payloads[1].session_id, 'session-1');
});

test('failed submission preserves request and Correction text', async () => {
  const ui = loadUi(async () => jsonResponse({}, {ok: false}));
  ui.request.value = 'Please keep this';
  ui.correction.value = 'Keep this too';
  await ui.request.emit('input');

  await ui['interaction-form'].emit('submit');

  assert.equal(ui.request.value, 'Please keep this');
  assert.equal(ui.correction.value, 'Keep this too');
  assert.equal(ui.response.textContent, 'The interaction could not be completed.');
  assert.equal(ui.send.disabled, false);
});

test('Ctrl+Enter with invalid input does not submit', async () => {
  let fetchCount = 0;
  const ui = loadUi(async () => {
    fetchCount += 1;
    return jsonResponse({session_id: 'session-1', response: 'ok'});
  });
  ui.request.value = ' \n\t ';
  await ui.request.emit('input');

  const event = await ui.request.emit('keydown', {ctrlKey: true, key: 'Enter'});

  assert.equal(event.defaultPrevented, true);
  assert.equal(ui['interaction-form'].requestSubmitCount, 0);
  assert.equal(fetchCount, 0);
});

test('New Session clears inputs and browser-held Session state', async () => {
  const payloads = [];
  const ui = loadUi(async (_url, options) => {
    payloads.push(JSON.parse(options.body));
    return jsonResponse({session_id: 'session-1', response: 'ok'});
  });
  ui.request.value = 'Start';
  await ui.request.emit('input');
  await ui['interaction-form'].emit('submit');
  ui.request.value = 'Draft request';
  ui.correction.value = 'Draft correction';

  await ui['new-session'].emit('click');

  assert.equal(ui.request.value, '');
  assert.equal(ui.correction.value, '');
  assert.equal(ui.request.focusCount, 2);
  assert.equal(ui.send.disabled, true);
  assert.equal(ui['session-status'].textContent, 'New Session — no conversation continuity yet.');
  assert.equal(ui.response.textContent, 'Your response will appear here.');

  ui.request.value = 'Fresh request';
  await ui.request.emit('input');
  await ui['interaction-form'].emit('submit');
  assert.equal('session_id' in payloads[1], false);
});
