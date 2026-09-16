const escapeHtml = (value) => String(value ?? "").replace(/[&<>'"]/g, ch => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;"
}[ch]));

document.querySelectorAll(".tab").forEach(button => button.addEventListener("click", () => {
  document.querySelectorAll(".tab, .panel").forEach(item => item.classList.remove("active"));
  button.classList.add("active");
  document.getElementById(button.dataset.panel).classList.add("active");
}));

function render(data) {
  let main = data.answer || data.analysis || data.guide || data.response;
  if (data.zero_shot) {
    main = `ZERO-SHOT\n${data.zero_shot.category} · ${Math.round(data.zero_shot.confidence * 100)}%\n${data.zero_shot.rationale}\n\nFEW-SHOT\n${data.few_shot.category} · ${Math.round(data.few_shot.confidence * 100)}%\n${data.few_shot.rationale}\n\nAgreement: ${data.same_category ? "Yes" : "No"}`;
  }
  let html = `<div class="result">${escapeHtml(main || JSON.stringify(data, null, 2))}</div>`;
  if (data.messages) {
    html += `<div class="sources">${data.messages.map(message => `<div class="source"><b>${escapeHtml(message.role.toUpperCase())}</b><br>${escapeHtml(message.content)}</div>`).join("")}</div>`;
  }
  if (data.sources?.length) {
    html += `<div class="sources">${data.sources.map(source => `<div class="source"><b>${escapeHtml(source.source)}, page ${source.page}</b> · score ${source.score}<br>${escapeHtml(source.excerpt)}</div>`).join("")}</div>`;
  }
  if (data.usage) html += `<div class="meta">TOKENS · prompt ${data.usage.prompt_tokens ?? "n/a"} · completion ${data.usage.completion_tokens ?? "n/a"} · total ${data.usage.total_tokens ?? "n/a"}</div>`;
  return html;
}

document.querySelectorAll("form").forEach(form => form.addEventListener("submit", async event => {
  event.preventDefault();
  const output = form.parentElement.querySelector(".output");
  const button = form.querySelector("button[type=submit]");
  button.disabled = true;
  output.innerHTML = '<div class="result">Working…</div>';
  try {
    let options;
    if (form.dataset.upload) {
      options = { method: "POST", body: new FormData(form) };
    } else {
      const textarea = form.querySelector("textarea");
      options = { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ [form.dataset.jsonField]: textarea.value }) };
    }
    const response = await fetch(form.dataset.endpoint, options);
    const data = await response.json();
    if (!response.ok) throw new Error(data.error?.message || "The request failed.");
    output.innerHTML = render(data);
  } catch (error) {
    output.innerHTML = `<div class="result error">${escapeHtml(error.message)}</div>`;
  } finally { button.disabled = false; }
}));

Promise.all([fetch("/ready").then(r => r.json()), fetch("/api/kb/status").then(r => r.json())])
  .then(([ready, kb]) => {
    const element = document.getElementById("system-status");
    element.textContent = ready.status === "ready" ? `${kb.documents} documents · ${kb.chunks} chunks` : "Setup required";
    element.classList.add(ready.status);
    element.title = ready.missing_configuration?.length ? `Missing: ${ready.missing_configuration.join(", ")}` : "";
  }).catch(() => { document.getElementById("system-status").textContent = "Status unavailable"; });
