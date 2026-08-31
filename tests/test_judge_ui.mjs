import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const SCRIPT = readFileSync(new URL('../aak/judge_ui.js', import.meta.url), 'utf8');

class FakeElement {
  constructor(tagName = 'div') {
    this.attributes = new Map();
    this.children = [];
    this.className = '';
    this.disabled = false;
    this.focusCount = 0;
    this.listeners = new Map();
    this.tagName = tagName.toUpperCase();
    this._textContent = '';
    this.value = '';
  }

  get innerHTML() {
    return '';
  }

  set innerHTML(_value) {
    throw new Error('Model output must not be rendered with innerHTML');
  }

  get textContent() {
    return this._textContent + this.children.map((child) => child.textContent).join('');
  }

  set textContent(value) {
    this._textContent = String(value);
    this.children = [];
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

  append(...children) {
    this.children.push(...children);
  }

  appendChild(child) {
    this.append(child);
    return child;
  }

  replaceChildren(...children) {
    this._textContent = '';
    this.children = [];
    this.append(...children);
  }

  setAttribute(name, value) {
    this.attributes.set(name, String(value));
  }
}

class FakeTextNode {
  constructor(value) {
    this.textContent = String(value);
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
    'interaction-feedback': new FakeElement(),
    'new-session': new FakeElement(),
    request: new FakeElement(),
    response: new FakeElement(),
    'session-status': new FakeElement(),
  };
  elements.send = new FakeElement();
  elements['interaction-form'] = new FakeForm(elements.send);
  const document = {
    createElement(tagName) {
      return new FakeElement(tagName);
    },
    createTextNode(value) {
      return new FakeTextNode(value);
    },
    getElementById(id) {
      return elements[id];
    },
  };
  vm.runInNewContext(SCRIPT, {document, fetch: fetchImpl, URL});
  return elements;
}

function descendants(node, tagName) {
  const expected = tagName.toUpperCase();
  const matches = [];
  for (const child of node.children ?? []) {
    if (child.tagName === expected) matches.push(child);
    matches.push(...descendants(child, expected));
  }
  return matches;
}

function descendantsWithClass(node, className) {
  const matches = [];
  for (const child of node.children ?? []) {
    if ((child.className ?? '').split(/\s+/).includes(className)) matches.push(child);
    matches.push(...descendantsWithClass(child, className));
  }
  return matches;
}

async function renderMarkdown(markdown) {
  const ui = loadUi(async () =>
    jsonResponse({session_id: 'session-1', response: markdown}),
  );
  ui.request.value = 'Render this response';
  await ui.request.emit('input');
  await ui['interaction-form'].emit('submit');
  return descendantsWithClass(ui.response, 'message-body')[1];
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
  assert.equal(descendantsWithClass(ui.response, 'message')[0].className, 'message message-user');
  assert.equal(descendantsWithClass(ui.response, 'message')[1].className, 'message message-agent');
  assert.deepEqual(
    descendantsWithClass(ui.response, 'message-label').map((label) => label.textContent),
    ['User', 'AAK'],
  );
  assert.equal(descendantsWithClass(ui.response, 'message-body')[0].textContent, 'First request');
  assert.equal(descendantsWithClass(ui.response, 'message-body')[1].textContent, 'completed');
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
  assert.equal(ui['interaction-feedback'].textContent, 'The interaction could not be completed.');
  assert.equal(descendantsWithClass(ui.response, 'message').length, 0);
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
  assert.equal(descendantsWithClass(ui.response, 'message').length, 0);

  ui.request.value = 'Fresh request';
  await ui.request.emit('input');
  await ui['interaction-form'].emit('submit');
  assert.equal('session_id' in payloads[1], false);
});

test('Markdown headings render as heading elements', async () => {
  const response = await renderMarkdown('# Main heading\n\n## Detail heading');

  assert.equal(descendants(response, 'h1')[0].textContent, 'Main heading');
  assert.equal(descendants(response, 'h2')[0].textContent, 'Detail heading');
});

test('Markdown bold and emphasis render as semantic elements', async () => {
  const response = await renderMarkdown('Use **strong guidance** with *careful emphasis*.');

  assert.equal(descendants(response, 'strong')[0].textContent, 'strong guidance');
  assert.equal(descendants(response, 'em')[0].textContent, 'careful emphasis');
});

test('Markdown ordered and unordered lists render as list elements', async () => {
  const response = await renderMarkdown('- First\n- Second\n\n1. Plan\n2. Verify');

  assert.equal(descendants(response, 'ul').length, 1);
  assert.equal(descendants(response, 'ol').length, 1);
  assert.deepEqual(
    descendants(response, 'li').map((item) => item.textContent),
    ['First', 'Second', 'Plan', 'Verify'],
  );
});

test('Markdown inline and fenced code render as code elements', async () => {
  const response = await renderMarkdown('Use `uv sync`.\n\n```python\nprint("safe")\n```');
  const code = descendants(response, 'code');

  assert.equal(code[0].textContent, 'uv sync');
  assert.equal(descendants(response, 'pre')[0].children[0].textContent, 'print("safe")');
});

test('ordinary plain text remains unchanged in a paragraph', async () => {
  const response = await renderMarkdown('A normal response remains readable.');

  assert.equal(descendants(response, 'p').length, 1);
  assert.equal(response.textContent, 'A normal response remains readable.');
});

test('model-produced HTML and script remain inert text', async () => {
  const modelOutput = '<script>globalThis.compromised = true</script> <img src=x onerror=alert(1)>';
  const response = await renderMarkdown(modelOutput);

  assert.equal(descendants(response, 'script').length, 0);
  assert.equal(descendants(response, 'img').length, 0);
  assert.equal(response.textContent, modelOutput);
});

test('only HTTP and HTTPS Markdown links become anchors', async () => {
  const response = await renderMarkdown(
    '[unsafe](javascript:alert(1)) [safe](https://example.com/docs)',
  );
  const links = descendants(response, 'a');

  assert.equal(links.length, 1);
  assert.equal(links[0].textContent, 'safe');
  assert.equal(links[0].attributes.get('href'), 'https://example.com/docs');
  assert.equal(links[0].attributes.get('rel'), 'noopener noreferrer');
  assert.equal(response.textContent.includes('unsafe'), true);
});

test('a second successful turn preserves the first pair and appends the second pair', async () => {
  const replies = ['First reply', 'Second reply'];
  const ui = loadUi(async () =>
    jsonResponse({session_id: 'session-1', response: replies.shift()}),
  );

  ui.request.value = 'First request';
  await ui.request.emit('input');
  await ui['interaction-form'].emit('submit');
  ui.request.value = 'Second request';
  await ui.request.emit('input');
  await ui['interaction-form'].emit('submit');

  assert.deepEqual(
    descendantsWithClass(ui.response, 'message-body').map((message) => message.textContent),
    ['First request', 'First reply', 'Second request', 'Second reply'],
  );
});

test('user-provided HTML and script syntax remain inert transcript text', async () => {
  const userInput = '<script>globalThis.userCompromised = true</script><img onerror=alert(1)>';
  const ui = loadUi(async () =>
    jsonResponse({session_id: 'session-1', response: 'Safe response'}),
  );
  ui.request.value = userInput;
  await ui.request.emit('input');

  await ui['interaction-form'].emit('submit');

  const userBody = descendantsWithClass(ui.response, 'message-body')[0];
  assert.equal(userBody.textContent, userInput);
  assert.equal(descendants(userBody, 'script').length, 0);
  assert.equal(descendants(userBody, 'img').length, 0);
});
