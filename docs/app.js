// Suno Latin Producer in the browser. Runs the repo's own Python scripts (copied to ./py/, checked in CI)
// with Pyodide, so the page and the CLI give the same answer. Nothing is sent anywhere.
const S = window.S || {};
const L = S.lang || "en";
const $ = (id) => document.getElementById(id);
const PYODIDE = "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/";
let py = null, loading = null, data = null;

function status(t) { const el = $("pystatus"); if (el) el.textContent = t || ""; }

async function boot() {
  if (py) return py;
  if (loading) return loading;
  loading = (async () => {
    status(S.loading);
    await new Promise((ok, bad) => { const s = document.createElement("script"); s.src = PYODIDE + "pyodide.js"; s.onload = ok; s.onerror = bad; document.head.appendChild(s); });
    const p = await window.loadPyodide({ indexURL: PYODIDE });
    p.FS.mkdirTree("/app/scripts"); p.FS.mkdirTree("/app/references");
    for (const f of ["brief.py", "lyric_meter.py", "suno_lint.py"]) p.FS.writeFile("/app/scripts/" + f, await (await fetch(S.up + "py/" + f)).text());
    p.FS.writeFile("/app/references/genres.json", await (await fetch(S.up + "py/genres.json")).text());
    p.runPython("import sys, json; sys.path.insert(0, '/app/scripts'); import brief, lyric_meter, suno_lint");
    py = p; status(""); return p;
  })().catch((e) => { loading = null; status(S.failed); throw e; });
  return loading;
}

async function loadData() {
  data = await (await fetch(S.up + "py/genres.json")).json();
  const g = $("genre"), m = $("mood"), v = $("vocal");
  const groups = S.groups;
  for (const [label, names] of groups) {
    const og = document.createElement("optgroup"); og.label = label;
    for (const n of names) if (data.genres[n]) { const o = document.createElement("option"); o.value = n; o.textContent = n; og.appendChild(o); }
    g.appendChild(og);
  }
  const rest = Object.keys(data.genres).filter((n) => !groups.some(([, ns]) => ns.includes(n))).sort();
  const og = document.createElement("optgroup"); og.label = S.other;
  for (const n of rest) { const o = document.createElement("option"); o.value = n; o.textContent = n; og.appendChild(o); }
  g.appendChild(og);
  g.value = S.defaultGenre;
  for (const k of Object.keys(data.moods)) { const o = document.createElement("option"); o.value = k; o.textContent = (S.moods[k] || k); m.appendChild(o); }
  m.value = S.defaultMood;
  const vo = document.createElement("option"); vo.value = ""; vo.textContent = S.genreDefault; v.appendChild(vo);
  for (const k of Object.keys(data.vocals)) { const o = document.createElement("option"); o.value = k; o.textContent = (S.vocals[k] || k); v.appendChild(o); }
}

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const copyBtn = (text) => `<button class="copy" type="button" data-copy="${esc(text)}">${esc((window.T || {}).copy || "Copy")}</button>`;

async function makeBrief(ev) {
  if (ev) ev.preventDefault();
  const out = $("bout"); out.innerHTML = `<p class="muted">${esc(S.working)}</p>`;
  const p = await boot();
  const args = { genre: $("genre").value, mood: $("mood").value, vocal: $("vocal").value || null, lang: $("blang").value, dj: $("dj").checked, seed: Number($("seed").value) || 1 };
  p.globals.set("A", JSON.stringify(args));
  const b = JSON.parse(p.runPython(`a = json.loads(A); json.dumps(brief.build(brief.load_data('/app/references/genres.json'), a['genre'], mood=a['mood'], vocal=a['vocal'], lang=a['lang'], seed=a['seed'], dj=a['dj']), ensure_ascii=False)`));
  const skeleton = b.sections.map((s) => `[${s}]\n`).join("\n");
  let h = `<div class="card"><h3>${esc(S.style_h)}</h3><p class="small muted">${esc(S.style_sub)}</p>`;
  for (const v of b.style_prompts) h += `<div class="cmd" style="margin:10px 0"><pre style="white-space:pre-wrap;padding-right:80px"><code style="background:none;padding:0"><span class="pill">${v.id}${v.axis === "base" ? "" : " · " + esc(S.axes[v.axis] || v.axis)}</span> ${esc(v.prompt)}</code></pre>${copyBtn(v.prompt)}</div>`;
  h += `</div><div class="card" style="margin-top:14px"><h3>${esc(S.lyrics_h)}</h3><p class="small muted">${esc(S.lyrics_sub)}</p><div class="cmd"><pre style="padding-right:80px"><code style="background:none;padding:0">${esc(skeleton)}</code></pre>${copyBtn(skeleton)}</div>`;
  h += `<table style="margin-top:12px"><tbody>${b.lyric_brief.map((i) => `<tr><td><span class="pill">[${esc(i.section)}]</span></td><td>${esc(i.note)}</td></tr>`).join("")}</tbody></table>`;
  h += `<p class="small muted" style="margin:12px 0 0">${esc(S.tempo)}: ${b.bpm} BPM (${b.bpm_range[0]}–${b.bpm_range[1]}) · ${esc(S.key)}: ${esc(b.key)} · <a href="${S.cw}">${esc(S.cw_link)}</a></p></div>`;
  out.innerHTML = h;
  $("style").value = b.style_prompts[0].prompt; $("ldj").checked = b.dj;
  document.dispatchEvent(new CustomEvent("tool_used", { detail: { tool: "suno-brief", genre: args.genre, lang: args.lang, dj: args.dj } }));
}

async function check(ev) {
  if (ev) ev.preventDefault();
  const out = $("cout"); out.innerHTML = `<p class="muted">${esc(S.working)}</p>`;
  const p = await boot();
  p.globals.set("LY", $("lyrics").value); p.globals.set("ST", $("style").value); p.globals.set("DJ", $("ldj").checked); p.globals.set("LG", $("clang").value);
  const r = JSON.parse(p.runPython(`rep = lyric_meter.analyse(LY, LG); iss = suno_lint.lint(LY, ST if ST.strip() else None, dj=bool(DJ)); json.dumps({"rep": rep, "iss": iss}, ensure_ascii=False)`));
  const lvl = { error: ["warn", "✕"], warn: ["warn", "!"], info: ["", "i"] };
  const errs = r.iss.filter((i) => i.level === "error").length, warns = r.iss.filter((i) => i.level === "warn").length;
  let h = `<div class="card"><h3>${esc(S.lint_h)}</h3>`;
  h += r.iss.length ? `<p>${errs} ${esc(S.errors)}, ${warns} ${esc(S.warnings)}</p><ul style="padding-left:18px;margin:8px 0 0">${r.iss.sort((a, b) => (a.line || 0) - (b.line || 0)).map((i) => `<li><span class="pill ${lvl[i.level][0]}">${i.rule}</span> ${i.line ? esc(S.line) + " " + i.line + ": " : ""}${esc(i.message)}</li>`).join("")}</ul>` : `<p><span class="pill ok">✓ ${esc(S.clean)}</span></p>`;
  h += `</div><div class="card" style="margin-top:14px"><h3>${esc(S.meter_h)} <span class="small muted">(${esc(S.langname[r.rep.lang] || r.rep.lang)})</span></h3><p class="small muted">${esc(S.meter_sub)}</p><div class="tablewrap"><table><thead><tr><th>${esc(S.section)}</th><th>#</th><th>${esc(S.syll)}</th><th>${esc(S.rhyme)}</th><th>${esc(S.text)}</th></tr></thead><tbody>`;
  for (const s of r.rep.sections) {
    if (!s.lines.length) { h += `<tr><td><span class="pill">[${esc(s.tag)}]</span></td><td colspan="4" class="muted">${esc(S.empty)}</td></tr>`; continue; }
    s.lines.forEach((ln, i) => { h += `<tr><td>${i ? "" : `<span class="pill">[${esc(s.tag || "?")}]</span><br><span class="small muted">${esc(s.scheme)}</span>`}</td><td>${ln.n}</td><td><b>${ln.syllables}</b></td><td>${esc(ln.rhyme)}</td><td>${esc(ln.text)}</td></tr>`; });
  }
  h += `</tbody></table></div>${r.rep.warnings.length ? `<ul style="padding-left:18px;margin:12px 0 0">${r.rep.warnings.map((w) => `<li>${esc(w)}</li>`).join("")}</ul>` : `<p class="small" style="margin:12px 0 0"><span class="pill ok">✓</span> ${esc(S.no_drift)}</p>`}</div>`;
  out.innerHTML = h;
  document.dispatchEvent(new CustomEvent("tool_used", { detail: { tool: "suno-lyrics-check", lang: r.rep.lang, errors: errs, warnings: warns } }));
}

$("bf").addEventListener("submit", makeBrief);
$("shuffle").addEventListener("click", () => { $("seed").value = 1 + Math.floor(Math.random() * 999); makeBrief(); });
$("cf").addEventListener("submit", check);
$("sample").addEventListener("click", async () => { $("lyrics").value = await (await fetch(S.up + "py/" + S.sampleFile)).text(); $("style").value = await (await fetch(S.up + "py/" + S.sampleStyle)).text(); $("ldj").checked = true; check(); });
loadData().then(() => {
  // warm up Python while the user reads; the first click then answers at once
  const warm = () => boot().catch(() => {});
  if ("requestIdleCallback" in window) requestIdleCallback(warm, { timeout: 2500 }); else setTimeout(warm, 1200);
});
