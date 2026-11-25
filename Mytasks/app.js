// Web port of task_remainder.py (Task Scheduler).
// Tasks live in memory for the current browser session, like the desktop version.

const tasks = [];
const $ = (id) => document.getElementById(id);

// ---------- Algorithms (ported from Python) ----------
function mergeSort(list, key) {
  if (list.length <= 1) return list;
  const mid = Math.floor(list.length / 2);
  return merge(mergeSort(list.slice(0, mid), key), mergeSort(list.slice(mid), key), key);
}
function merge(left, right, key) {
  const out = [];
  let i = 0, j = 0;
  while (i < left.length && j < right.length) {
    out.push(key(left[i]) <= key(right[j]) ? left[i++] : right[j++]);
  }
  return out.concat(left.slice(i), right.slice(j));
}

// Dynamic programming: maximum total priority achievable within maxTime hours.
function scheduleTasks(list, maxTime) {
  const dp = new Array(maxTime + 1).fill(0);
  for (const t of mergeSort(list, (x) => x.end)) {
    const duration = Math.max(1, Math.round((t.end - t.start) / 3600000));
    for (let i = maxTime; i >= duration; i--) dp[i] = Math.max(dp[i], dp[i - duration] + t.priority);
  }
  return dp[maxTime];
}

function checkForReminders(list, now) {
  const out = [];
  for (const t of list) {
    const diff = t.deadline - now;
    if (diff >= 0 && diff <= 3600000) out.push({ cls: "soon", text: `Reminder: Task '${t.name}' deadline is approaching!` });
    else if (diff < 0) out.push({ cls: "missed", text: `Missed Deadline: Task '${t.name}' has missed its deadline!` });
  }
  return out;
}

const searchTaskByName = (list, name) => list.find((t) => t.name.toLowerCase() === name.trim().toLowerCase()) || null;

// ---------- Helpers ----------
const hhmm = (d) => d.toTimeString().slice(0, 5);
function timeToday(value) {
  const [h, m] = value.split(":").map(Number);
  const d = new Date();
  d.setHours(h, m, 0, 0);
  return d;
}
const describe = (t) => `${t.name} — Priority ${t.priority} — ${hhmm(t.start)} to ${hhmm(t.end)}`;
function el(tag, props = {}, ...children) {
  const n = Object.assign(document.createElement(tag), props);
  n.append(...children);
  return n;
}

// ---------- Rendering ----------
function renderTasks(list = tasks) {
  const ul = $("task-list");
  ul.replaceChildren();
  if (!list.length) ul.append(el("li", { className: "empty", textContent: "No tasks yet." }));
  for (const t of list) {
    const remove = el("button", { className: "remove", title: "Remove task", textContent: "✕" });
    remove.onclick = () => { tasks.splice(tasks.indexOf(t), 1); refresh(); };
    ul.append(el("li", {},
      el("span", {}, el("span", { className: `tag ${t.type}`, textContent: t.type }), describe(t),
        el("span", { className: "muted", textContent: ` · due ${t.deadline.toLocaleString()}` })),
      remove));
  }
  $("schedule-info").textContent = tasks.length
    ? `Max priority achievable in an 8-hour day: ${scheduleTasks(tasks, 8)}`
    : "";
}

function renderReminders() {
  const ul = $("reminders");
  ul.replaceChildren();
  const items = checkForReminders(tasks, new Date());
  if (!items.length) ul.append(el("li", { className: "empty", textContent: "No reminders." }));
  for (const r of items) ul.append(el("li", { className: r.cls, textContent: r.text }));
}

function renderGantt() {
  const card = $("chart-card");
  const box = $("chart");
  card.classList.remove("hidden");
  if (!tasks.length) { box.textContent = "Add tasks to see the chart."; return; }

  const NS = "http://www.w3.org/2000/svg";
  const rowH = 36, left = 140, right = 20, top = 20, width = 900;
  const height = top + tasks.length * rowH + 40;
  const min = Math.min(...tasks.map((t) => +t.start));
  const max = Math.max(...tasks.map((t) => +t.end));
  const span = Math.max(max - min, 1);
  const x = (v) => left + ((v - min) / span) * (width - left - right);
  const svg = document.createElementNS(NS, "svg");
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  const add = (tag, attrs, text) => {
    const n = document.createElementNS(NS, tag);
    for (const k in attrs) n.setAttribute(k, attrs[k]);
    if (text) n.textContent = text;
    svg.append(n);
  };

  // Hour gridlines
  const first = new Date(min); first.setMinutes(0, 0, 0);
  for (let h = +first; h <= max; h += 3600000) {
    if (h < min) continue;
    add("line", { x1: x(h), x2: x(h), y1: top, y2: height - 30, stroke: "#ddd" });
    add("text", { x: x(h), y: height - 12, "text-anchor": "middle", "font-size": 12, fill: "#333" }, hhmm(new Date(h)));
  }
  tasks.forEach((t, i) => {
    const y = top + i * rowH;
    add("text", { x: left - 8, y: y + rowH / 2 + 4, "text-anchor": "end", "font-size": 13, fill: "#333" }, t.name);
    add("rect", {
      x: x(+t.start), y: y + 6, width: Math.max(x(+t.end) - x(+t.start), 2), height: rowH - 12, rx: 4,
      fill: t.type === "Personal" ? "skyblue" : "orange",
    });
  });
  add("text", { x: left, y: 14, "font-size": 12, fill: "#555" }, "Time");
  box.replaceChildren(svg);
}

function refresh() {
  renderTasks();
  renderReminders();
  if (!$("chart-card").classList.contains("hidden")) renderGantt();
}

// ---------- Events ----------
$("task-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const f = e.target.elements;
  const msg = $("form-message");
  const show = (text, ok) => { msg.textContent = text; msg.className = `message ${ok ? "ok" : "error"}`; };

  const name = f.name.value.trim();
  const priority = Number(f.priority.value);
  if (!name) return show("Task name is required.");
  if (!Number.isInteger(priority) || priority < 1 || priority > 5) return show("Priority must be a whole number between 1 and 5.");
  if (!f.start.value || !f.end.value || !f.deadline.value) return show("Start time, end time and deadline are required.");
  const start = timeToday(f.start.value);
  const end = timeToday(f.end.value);
  const deadline = new Date(f.deadline.value);
  if (start >= end) return show("Start time must be before end time.");
  if (deadline <= start) return show("Deadline must be after the start time.");

  tasks.push({ name, type: f.type.value, priority, start, end, deadline });
  e.target.reset();
  show("Task added successfully!", true);
  refresh();
});

$("sort-btn").addEventListener("click", () => {
  const sorted = mergeSort(tasks, (t) => t.priority);
  tasks.splice(0, tasks.length, ...sorted);
  refresh();
});

$("chart-btn").addEventListener("click", renderGantt);

$("search-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const q = $("search-input").value;
  const out = $("search-result");
  const t = searchTaskByName(tasks, q);
  out.textContent = t ? `Task found: ${describe(t)}` : `No task found with the name '${q}'`;
  out.className = `message ${t ? "ok" : "error"}`;
});

// Periodic reminder check every 60 seconds, as in the desktop app.
setInterval(renderReminders, 60000);
refresh();
