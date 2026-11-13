/** API 与通用工具 */
function defaultApiBase() {
  if (window.location.protocol.startsWith("http") && window.location.host) {
    return window.location.origin;
  }
  return "http://127.0.0.1:8000";
}

/** 从 /ui/ 打开时优先与页面同源；自动纠正 localStorage 里残留的 8000 */
function initApiBase() {
  const def = defaultApiBase();
  const stored = localStorage.getItem("API_BASE");
  if (!stored) {
    localStorage.setItem("API_BASE", def);
    return;
  }
  try {
    const su = new URL(stored);
    const du = new URL(def);
    const fromUi = window.location.pathname.startsWith("/ui");
    if (fromUi && su.origin !== du.origin) {
      localStorage.setItem("API_BASE", def);
    }
  } catch {
    localStorage.setItem("API_BASE", def);
  }
}
initApiBase();

function getApiBase() {
  return localStorage.getItem("API_BASE") || defaultApiBase();
}

function setApiBase(url) {
  localStorage.setItem("API_BASE", (url || "").trim().replace(/\/$/, ""));
}

const SESSION_KEY = "CURRENT_USER";
const OPERATOR_PW_KEY = "OPERATOR_PASSWORD";

function getCurrentUser() {
  try {
    const raw = localStorage.getItem(SESSION_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function setCurrentUser(user) {
  localStorage.setItem(SESSION_KEY, JSON.stringify(user));
}

function clearCurrentUser() {
  localStorage.removeItem(SESSION_KEY);
  clearOperatorPassword();
}

/** 用户管理接口依赖的管理员登录密码（query 参数 password） */
function setOperatorPassword(password) {
  if (password != null && String(password).trim()) {
    sessionStorage.setItem(OPERATOR_PW_KEY, String(password));
  }
}

function getOperatorPassword() {
  return sessionStorage.getItem(OPERATOR_PW_KEY) || "";
}

function clearOperatorPassword() {
  sessionStorage.removeItem(OPERATOR_PW_KEY);
}

/** 用户管理写操作 / 查询所需的 query：username + password */
function buildUserMgmtQuery(extra = {}) {
  const username = getAdminUsername();
  const password = getOperatorPassword();
  if (!username) throw new Error("未登录或会话已失效，请重新登录");
  if (!password) throw new Error("请重新登录后再操作用户管理");
  return { username, password, ...extra };
}

function isAdmin() {
  return getCurrentUser()?.role_name === "admin";
}

/** 用户管理接口要求的操作者 query 参数 username */
function getOperatorUsername() {
  return getCurrentUser()?.user_name || "";
}

function getAdminUsername() {
  return getOperatorUsername();
}

/** 兼容 ApiResponse 与 FastAPI 默认 {"detail": ...} */
function parseApiMessage(data, status) {
  if (!data) return `请求失败（HTTP ${status}）`;
  if (typeof data.message === "string" && data.message.trim()) return data.message;

  const detail = data.detail;
  if (typeof detail === "string" && detail.trim()) return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (item && typeof item === "object") {
          const loc = item.loc ? item.loc.filter((x) => x !== "body").join(".") : "";
          const prefix = loc ? `${loc}: ` : "";
          return prefix + (item.msg || item.message || JSON.stringify(item));
        }
        return String(item);
      })
      .join("；");
  }
  if (detail && typeof detail === "object") {
    return detail.message || detail.msg || JSON.stringify(detail);
  }
  return `请求失败（code=${data.code ?? status}）`;
}

function isApiSuccess(data, status) {
  if (data && (data.code === 200 || data.code === 201)) return true;
  if (status >= 200 && status < 300 && data && data.code == null && data.detail == null) return true;
  return false;
}

async function request(method, path, { query, form, json } = {}) {
  const url = new URL(getApiBase() + path);
  if (query) {
    Object.entries(query).forEach(([k, v]) => {
      if (v !== undefined && v !== null && String(v) !== "") url.searchParams.set(k, v);
    });
  }
  const headers = {};
  const opt = { method, headers };
  if (form) {
    opt.body = (() => {
      const fd = new FormData();
      Object.entries(form).forEach(([k, v]) => {
        if (v !== undefined && v !== null && String(v) !== "") fd.append(k, v);
      });
      return fd;
    })();
  } else if (json !== undefined) {
    headers["Content-Type"] = "application/json";
    opt.body = JSON.stringify(json);
  }
  let res;
  try {
    res = await fetch(url.toString(), opt);
  } catch (e) {
    const msg = "无法连接后端：" + e.message;
    return { ok: false, status: 0, data: null, msg, err: msg };
  }
  const text = await res.text();
  let data;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { code: res.status, message: text || "非 JSON 响应", data: null };
  }
  const msg = parseApiMessage(data, res.status);
  return { ok: isApiSuccess(data, res.status), status: res.status, data, msg };
}

function unwrap(payload) {
  if (!payload?.ok) throw new Error(payload?.msg || "请求失败");
  return payload.data?.data;
}

function toast(msg, type = "info") {
  let el = document.getElementById("toast");
  if (!el) {
    el = document.createElement("div");
    el.id = "toast";
    document.body.appendChild(el);
  }
  el.className = `toast toast-${type} show`;
  el.textContent = msg;
  clearTimeout(el._t);
  const ms = type === "error" ? 5000 : 2400;
  el._t = setTimeout(() => el.classList.remove("show"), ms);
}

function fmtDate(v) {
  if (!v) return "-";
  return String(v).slice(0, 10);
}

function fmtDateTime(v) {
  if (!v) return "-";
  return String(v).replace("T", " ").slice(0, 19);
}

function esc(s) {
  const d = document.createElement("div");
  d.textContent = s == null ? "" : String(s);
  return d.innerHTML;
}

function openModal(title, bodyHtml, onConfirm) {
  const root = document.getElementById("modalRoot");
  root.innerHTML = `
    <div class="modal-mask" data-act="close"></div>
    <div class="modal">
      <header><h4>${esc(title)}</h4><button type="button" class="modal-close" data-act="close">×</button></header>
      <div class="modal-body">${bodyHtml}</div>
      <footer>
        <button type="button" class="btn ghost" data-act="close">取消</button>
        <button type="button" class="btn primary" id="modalConfirm">确定</button>
      </footer>
    </div>`;
  root.classList.add("open");
  const close = () => {
    root.classList.remove("open");
    root.innerHTML = "";
  };
  root.querySelectorAll('[data-act="close"]').forEach((b) => b.addEventListener("click", close));
  document.getElementById("modalConfirm").onclick = async () => {
    try {
      await onConfirm(close);
    } catch (e) {
      toast(e.message, "error");
    }
  };
}

function confirmDialog(message, onOk) {
  openModal(
    "确认操作",
    `<p class="modal-tip">${esc(message)}</p>`,
    async (close) => {
      await onOk();
      close();
    }
  );
}

function toolbarLayout(fieldsHtml, rightActionsHtml = "") {
  const right = rightActionsHtml
    ? `<div class="toolbar-actions">${rightActionsHtml}</div>`
    : "";
  return `<div class="toolbar">
    <div class="toolbar-fields">${fieldsHtml}</div>
    ${right}
  </div>`;
}

/** 写入已有 toolbar 容器（避免嵌套两层 .toolbar） */
function fillToolbar(el, fieldsHtml, rightActionsHtml = "") {
  if (!el) return;
  el.className = "toolbar";
  const right = rightActionsHtml
    ? `<div class="toolbar-actions">${rightActionsHtml}</div>`
    : "";
  el.innerHTML = `<div class="toolbar-fields">${fieldsHtml}</div>${right}`;
}

function queryActions({ queryId = "btnQuery", resetId = "btnReset", extra = "" } = {}) {
  return `
    <button type="button" class="btn primary" id="${queryId}">查询</button>
    <button type="button" class="btn ghost" id="${resetId}">重置</button>
    ${extra}`;
}

function renderPager(container, { page, size, total }, onChange, onSizeChange) {
  if (!container) return;
  const pages = Math.max(1, Math.ceil((total || 0) / size));
  const sizeOpts = [10, 20, 50, 100]
    .map((n) => `<option value="${n}" ${n === size ? "selected" : ""}>${n} 条/页</option>`)
    .join("");
  container.className = "pager";
  container.innerHTML = `
    <div class="pager-controls">
      <span class="pager-total">共 ${total || 0} 条</span>
      <button type="button" class="btn ghost sm pager-btn" ${page <= 1 ? "disabled" : ""} data-p="-1">上一页</button>
      <span class="pager-status">第 ${page} / ${pages} 页</span>
      <button type="button" class="btn ghost sm pager-btn" ${page >= pages ? "disabled" : ""} data-p="1">下一页</button>
      ${onSizeChange ? `<label class="pager-size">每页<select data-size>${sizeOpts}</select></label>` : ""}
    </div>`;
  container.querySelectorAll("[data-p]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const d = Number(btn.dataset.p);
      const np = page + d;
      if (np >= 1 && np <= pages) onChange(np);
    });
  });
  const sel = container.querySelector("[data-size]");
  if (sel && onSizeChange) {
    sel.addEventListener("change", () => onSizeChange(Number(sel.value)));
  }
}

/** 与接口 Query/Field 约束对齐的前端校验 */
function validateNumber(raw, { label, min, max, required = false, integer = true } = {}) {
  const s = raw == null ? "" : String(raw).trim();
  if (!s) {
    if (required) throw new Error(`${label}不能为空`);
    return null;
  }
  const n = integer ? parseInt(s, 10) : parseFloat(s);
  if (Number.isNaN(n)) throw new Error(`${label}必须是有效数字`);
  if (min != null && n < min) throw new Error(`${label}不能小于 ${min}`);
  if (max != null && n > max) throw new Error(`${label}不能大于 ${max}`);
  return n;
}

function validateText(raw, { label, required = false, minLen = 0, maxLen } = {}) {
  const s = raw == null ? "" : String(raw).trim();
  if (!s) {
    if (required) throw new Error(`${label}不能为空`);
    return "";
  }
  if (s.length < minLen) throw new Error(`${label}至少 ${minLen} 个字符`);
  if (maxLen != null && s.length > maxLen) throw new Error(`${label}不能超过 ${maxLen} 个字符`);
  return s;
}

function validateSalaryRange(minRaw, maxRaw) {
  const min = minRaw === "" || minRaw == null ? null : validateNumber(minRaw, { label: "薪资下限", min: 0, integer: false });
  const max = maxRaw === "" || maxRaw == null ? null : validateNumber(maxRaw, { label: "薪资上限", min: 0, integer: false });
  if (min != null && max != null && min > max) throw new Error("薪资下限不能大于上限");
  return { min, max };
}

function attrString(attrs = {}) {
  return Object.entries(attrs)
    .filter(([, v]) => v !== undefined && v !== null && v !== false)
    .map(([k, v]) => ` ${k}="${esc(String(v))}"`)
    .join("");
}

function fieldRow(label, name, value = "", type = "text", opts = "", attrs = {}) {
  if (type === "select") {
    return `<label class="field"><span>${esc(label)}</span><select name="${name}"${attrString(attrs)}>${opts}</select></label>`;
  }
  if (type === "textarea") {
    return `<label class="field span2"><span>${esc(label)}</span><textarea name="${name}" rows="3"${attrString(attrs)}>${esc(value)}</textarea></label>`;
  }
  const baseAttrs = type === "number" ? { step: attrs.step ?? 1, ...attrs } : attrs;
  return `<label class="field"><span>${esc(label)}</span><input name="${name}" type="${type}" value="${esc(value)}"${attrString(baseAttrs)} /></label>`;
}

function buildSelectOptions(items, valueFn, labelFn, { selected, allowEmpty, emptyLabel = "请选择" } = {}) {
  let html = allowEmpty ? `<option value="">${esc(emptyLabel)}</option>` : "";
  (items || []).forEach((item) => {
    const val = valueFn(item);
    const lab = labelFn(item);
    const sel = selected != null && String(selected) === String(val) ? " selected" : "";
    html += `<option value="${esc(val)}"${sel}>${esc(lab)}</option>`;
  });
  return html;
}

/** 从接口 data 中提取行数组（兼容直接数组、PageResponse、就业 items） */
function listRowsFromPack(pack) {
  if (pack == null) return [];
  if (Array.isArray(pack)) return pack;
  if (Array.isArray(pack.items)) return pack.items;
  const inner = pack.data;
  if (Array.isArray(inner)) return inner;
  if (inner && typeof inner === "object" && Array.isArray(inner.data)) return inner.data;
  return [];
}

function normalizeListPayload(pack, { page, size } = {}) {
  if (!pack) return { rows: [], total: 0, page: page ?? 1, size: size ?? 10 };
  if (Array.isArray(pack)) {
    const p = page ?? 1;
    const sz = size ?? 10;
    return {
      rows: pack,
      total: pagedArrayTotal(pack, p, sz),
      page: p,
      size: sz,
    };
  }
  const rows = listRowsFromPack(pack);
  const total =
    pack.total ??
    (typeof pack.data === "object" && pack.data != null && !Array.isArray(pack.data) ? pack.data.total : undefined) ??
    rows.length;
  return {
    rows,
    total,
    page: pack.page ?? page ?? 1,
    size: pack.size ?? pack.page_size ?? size ?? 10,
  };
}

/** 解析接口外层 ApiResponse（code/message/data）中的分页载荷 */
function parsePagedResponse(apiEnvelope, { page, size } = {}) {
  const pack = apiEnvelope?.data;
  return normalizeListPayload(pack, { page, size });
}

/** 后端仅返回当前页数组（内存分页）时估算 total，maxItems 为结果上限（如薪资 TOP N） */
function pagedArrayTotal(rows, page, size, maxItems) {
  const n = (rows || []).length;
  const p = Math.max(1, page);
  const sz = Math.max(1, size);
  if (n === 0 && p === 1) return 0;
  const lowerBound = (p - 1) * sz + n;
  if (maxItems != null) {
    if (n < sz) return Math.min(maxItems, lowerBound);
    return Math.min(maxItems, p * sz);
  }
  return n < sz ? lowerBound : p * sz + 1;
}

const OPT_CACHE = { classes: null, teachers: null, students: null, subjects: null, courses: null };

function clearOptionCache(which) {
  if (which) OPT_CACHE[which] = null;
  else Object.keys(OPT_CACHE).forEach((k) => (OPT_CACHE[k] = null));
}

async function fetchAllPages(path, { pageParam = "page", sizeParam = "size", size = 100, extraQuery = {} } = {}) {
  const all = [];
  let page = 1;
  let total = null;
  for (;;) {
    const res = await request("GET", path, { query: { ...extraQuery, [pageParam]: page, [sizeParam]: size } });
    if (!res.ok) throw new Error(res.msg);
    const raw = res.data?.data;
    if (Array.isArray(raw)) {
      all.push(...raw);
      if (raw.length < size) break;
      page += 1;
      continue;
    }
    const norm = normalizeListPayload(raw, { page, size });
    all.push(...norm.rows);
    total = norm.total;
    if (all.length >= total || norm.rows.length < size) break;
    page += 1;
    if (page > 200) break;
  }
  return all;
}

async function loadClassOptions(force) {
  if (!force && OPT_CACHE.classes) return OPT_CACHE.classes;
  OPT_CACHE.classes = await fetchAllPages("/v0/class", { size: 100 });
  return OPT_CACHE.classes;
}

async function loadTeacherOptions(force) {
  if (!force && OPT_CACHE.teachers) return OPT_CACHE.teachers;
  OPT_CACHE.teachers = await fetchAllPages("/v0/teacher", { size: 100 });
  return OPT_CACHE.teachers;
}

async function loadStudentOptions(force) {
  if (!force && OPT_CACHE.students) return OPT_CACHE.students;
  OPT_CACHE.students = await fetchAllPages("/v0/student", { size: 100 });
  return OPT_CACHE.students;
}

async function loadSubjectOptions(force) {
  if (!force && OPT_CACHE.subjects) return OPT_CACHE.subjects;
  OPT_CACHE.subjects = await fetchAllPages("/v0/score/subject", { size: 100 });
  return OPT_CACHE.subjects;
}

async function loadCourseOptions(force) {
  if (!force && OPT_CACHE.courses) return OPT_CACHE.courses;
  OPT_CACHE.courses = await fetchAllPages("/v0/score/course", { size: 100 });
  return OPT_CACHE.courses;
}
