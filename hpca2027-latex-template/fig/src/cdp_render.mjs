// Render a local HTML page (the draw.io viewer page or the prototype) in headless Chrome over the
// DevTools protocol: wait for the drawing, place it at (0,0), then write a PNG, optionally a PDF of
// exactly 1048 x 278 pt, the console/exception log, every rendered text line with its box, and the
// rendered SVG.
// usage: node cdp_render.mjs <page.html> <out-prefix> [--pdf] [--scale 2]
import { spawn } from 'node:child_process';
import { mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';

const args = process.argv.slice(2);
const page = resolve(args[0]);
const out = resolve(args[1]);
const wantPdf = args.includes('--pdf');
const si = args.indexOf('--scale');
const scale = si >= 0 ? Number(args[si + 1]) : 2;
const W = 1048, H = 278;

const udd = mkdtempSync(join(process.env.CDP_UDD_ROOT || tmpdir(), 'cdp-'));  // keep TMPDIR short: Chrome's singleton socket path is length-limited
const chrome = spawn('google-chrome', ['--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
  '--remote-debugging-port=0', `--user-data-dir=${udd}`, 'about:blank'], { stdio: ['ignore', 'ignore', 'pipe'] });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let port;
chrome.stderr.on('data', (d) => { const m = /DevTools listening on ws:\/\/127\.0\.0\.1:(\d+)/.exec(String(d)); if (m) port = m[1]; });
for (let i = 0; i < 600 && !port; i++) await sleep(100);
if (!port) { console.error('chrome did not start'); chrome.kill(); process.exit(2); }
const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
const ws = new WebSocket(targets.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener('open', r));
let id = 0; const pending = new Map(); const log = [];
ws.addEventListener('message', (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Runtime.consoleAPICalled') log.push(`console.${m.params.type}: ` + m.params.args.map((a) => a.value ?? a.description).join(' '));
  if (m.method === 'Runtime.exceptionThrown') log.push('exception: ' + JSON.stringify(m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text));
  if (m.method === 'Log.entryAdded') log.push(`log.${m.params.entry.level}: ${m.params.entry.text} ${m.params.entry.url || ''}`);
});
const send = (method, params = {}) => new Promise((r) => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const evaluate = async (expr) => (await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true })).result?.result?.value;

await send('Runtime.enable'); await send('Log.enable'); await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: scale, mobile: false });
await send('Page.navigate', { url: 'file://' + page });
let ok = false;
for (let i = 0; i < 300 && !ok; i++) { await sleep(100); ok = await evaluate(`!!document.querySelector('svg') && document.readyState === 'complete'`); }
await evaluate('document.fonts.ready.then(() => true)');
await sleep(500);
const info = await evaluate(`(() => {
  const svg = document.querySelector('div.mxgraph svg') || document.querySelector('svg');
  const host = svg.closest('div.mxgraph') || svg.parentElement;
  document.body.style.margin = '0';
  for (const el of [host, svg]) { el.style.position = 'absolute'; el.style.left = '0px'; el.style.top = '0px'; el.style.margin = '0'; el.style.border = '0'; }
  // draw.io pads an edge's bounds by its arrow marker, so an arrowhead at the canvas edge widens the svg past
  // ${W} units and Chrome's print would shrink the whole figure to fit: clamp to the ${W} x ${H} canvas (1:1).
  document.body.style.overflow = 'hidden';
  for (const el of [host, svg]) { el.style.minWidth = '${W}px'; el.style.minHeight = '${H}px'; el.style.width = '${W}px'; el.style.height = '${H}px'; el.style.overflow = 'hidden'; }
  const r = svg.getBoundingClientRect();
  const texts = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n; while ((n = walker.nextNode())) {
    const t = n.textContent; if (!t.trim()) continue;
    const range = document.createRange(); range.selectNodeContents(n);
    const b = range.getBoundingClientRect();
    const cs = getComputedStyle(n.parentElement);
    texts.push({ text: t, x: b.left, y: b.top, w: b.width, h: b.height, fontSize: cs.fontSize, fontFamily: cs.fontFamily, fontWeight: cs.fontWeight });
  }
  const used = [...new Set(texts.map((t) => t.fontFamily))];
  return { svg: { x: r.left, y: r.top, w: r.width, h: r.height }, n_texts: texts.length, texts, families: used, svgHtml: svg.outerHTML };
})()`);
const shot = await send('Page.captureScreenshot', { format: 'png', clip: { x: 0, y: 0, width: W, height: H, scale: 1 }, captureBeyondViewport: true });
writeFileSync(out + '.png', Buffer.from(shot.result.data, 'base64'));
if (wantPdf) {
  const pdf = await send('Page.printToPDF', { paperWidth: W / 96, paperHeight: H / 96, marginTop: 0, marginBottom: 0,
    marginLeft: 0, marginRight: 0, scale: 1, printBackground: true, pageRanges: '1', preferCSSPageSize: false });
  writeFileSync(out + '.pdf', Buffer.from(pdf.result.data, 'base64'));
}
writeFileSync(out + '.svg', info.svgHtml);
delete info.svgHtml;
writeFileSync(out + '.json', JSON.stringify({ page, log, ...info }, null, 1));
console.log(JSON.stringify({ svg: info.svg, n_texts: info.n_texts, families: info.families, log }, null, 1));
ws.close(); chrome.kill();
process.exit(0);
