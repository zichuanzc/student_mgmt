/** 学生管理系统 — 业务前端 */
const STATE = {
  page: "dashboard",
  dashboard: { genderPage: 1, genderSize: 10 },
  students: { page: 1, size: 10, filters: {} },
  teachers: { page: 1, size: 10, teacher_code: "" },
  classes: { page: 1, size: 10, class_code: "" },
  employment: { mode: "class", page: 1, page_size: 10 },
  scoresTab: "list",
  scoreList: { page: 1, size: 10, stu_id: "", teacher_id: "", subject_id: "" },
  subjects: { page: 1, size: 10 },
  courses: { page: 1, size: 10 },
  users: { page: 1, size: 10 },
  statsTab: "basic",
  stats: {
    olderAge: "",
    olderPage: 1,
    genderPage: 1,
    genderSize: 10,
    olderSize: 10,
    geSize: 10,
    failSize: 10,
    avgSize: 10,
    empRankSize: 10,
    geScore: 80,
    gePage: 1,
    passScore: 60,
    failCount: 2,
    failPage: 1,
    avgPage: 1,
    empRank: 10,
    empRankPage: 1,
    empName: "",
    empNamePage: 1,
    empNameSize: 10,
    empClassCode: "",
    empClassTimePage: 1,
    empClassTimeSize: 10,
    empAvgClass: "",
    empClassAvgPage: 1,
    empClassAvgSize: 10,
  },
};

const PAGE_META = {
  dashboard: ["首页概览", "查看整体数据与快捷入口"],
  students: ["学生信息", "查询、维护学员档案"],
  classes: ["班级管理", "班级开班与班主任维护"],
  teachers: ["教师管理", "教师档案与任课信息"],
  employment: ["就业信息", "学员就业登记与查询"],
  scores: ["成绩管理", "科目、课程与成绩维护"],
  users: ["用户管理", "系统账号与角色（需管理员身份）"],
  stats: ["统计报表", "基础、成绩与就业统计分析"],
};

document.addEventListener("DOMContentLoaded", () => {
  if (!getCurrentUser()) {
    window.location.href = "./login.html";
    return;
  }
  refreshUserChrome();
  bindNav();
  document.getElementById("btnRefresh").onclick = () => renderPage(STATE.page);
  document.getElementById("btnSettings").onclick = showSettings;
  document.getElementById("btnLogout").onclick = () => {
    clearCurrentUser();
    window.location.href = "./login.html";
  };
  renderPage("dashboard");
});

function refreshUserChrome() {
  const u = getCurrentUser();
  document.getElementById("sideUserName").textContent = u?.full_name || u?.user_name || "-";
  document.getElementById("sideUserRole").textContent = u?.role_name || "-";
  const navUsers = document.getElementById("navUsers");
  if (isAdmin()) navUsers.classList.remove("hidden");
  else navUsers.classList.add("hidden");
}

function bindNav() {
  document.querySelectorAll("#mainMenu button").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("#mainMenu button").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      renderPage(btn.dataset.page);
    });
  });
}

function renderPage(name) {
  if (name === "users" && !isAdmin()) {
    toast("仅管理员可访问用户管理", "error");
    name = "dashboard";
  }
  STATE.page = name;
  const [title, sub] = PAGE_META[name] || ["", ""];
  document.getElementById("pageTitle").textContent = title;
  document.getElementById("pageSubtitle").textContent = sub;
  document.querySelectorAll(".page").forEach((p) => p.classList.remove("active"));
  document.getElementById(`page-${name}`).classList.add("active");
  const fn = { dashboard, students, classes, teachers, employment, scores, users, stats }[name];
  if (fn) fn();
}

function showSettings() {
  openModal(
    "系统设置",
    `<div class="form-grid">
      ${fieldRow("API 地址", "api", getApiBase())}
    </div>
    <p class="modal-tip">通过 FastAPI 挂载访问时一般无需修改。用户管理将自动使用当前登录的管理员账号。</p>`,
    async (close) => {
      const root = document.querySelector("#modalRoot .modal-body");
      setApiBase(root.querySelector('[name="api"]').value);
      toast("设置已保存", "success");
      close();
      renderPage(STATE.page);
    }
  );
}

function tableHtml(cols, rows, actions) {
  if (!rows?.length) return `<div class="empty">暂无数据</div>`;
  const head = cols.map((c) => `<th>${esc(c.label)}</th>`).join("") + (actions ? "<th>操作</th>" : "");
  const body = rows
    .map((row) => {
      const tds = cols.map((c) => `<td>${esc(c.fmt ? c.fmt(row[c.key], row) : row[c.key])}</td>`).join("");
      const act = actions ? `<td>${actions(row)}</td>` : "";
      return `<tr>${tds}${act}</tr>`;
    })
    .join("");
  return `<div class="table-wrap"><table class="data"><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
}

/* ========== 首页 ========== */
async function dashboard() {
  const el = document.getElementById("page-dashboard");
  el.innerHTML = `
    <div class="stats-grid" id="dashStats"><p>加载中…</p></div>
    <div class="card" id="dashExtra"><div class="card-head"><h3>班级人数与性别分布</h3></div><div id="dashGenderBody">加载中…</div></div>`;
  try {
    const [stu, cls, tea] = await Promise.all([
      request("GET", "/v0/student", { query: { page: 1, size: 1 } }),
      request("GET", "/v0/class", { query: { page: 1, size: 1 } }),
      request("GET", "/v0/teacher", { query: { page: 1, size: 1 } }),
    ]);
    const stuN = parsePagedResponse(stu.data, { page: 1, size: 1 }).total;
    const clsN = parsePagedResponse(cls.data, { page: 1, size: 1 }).total;
    const teaN = parsePagedResponse(tea.data, { page: 1, size: 1 }).total;
    document.getElementById("dashStats").innerHTML = `
      <div class="stat-box"><span>学生总数</span><strong>${stuN}</strong></div>
      <div class="stat-box"><span>班级数量</span><strong>${clsN}</strong></div>
      <div class="stat-box"><span>教师数量</span><strong>${teaN}</strong></div>
      <div class="stat-box"><span>概览数据</span><strong>实时</strong></div>`;
    await loadDashboardGender();
  } catch (e) {
    document.getElementById("dashStats").innerHTML = `<p class="empty">${esc(e.message)}</p>`;
  }
}

async function loadDashboardGender() {
  const d = STATE.dashboard;
  const res = await request("GET", "/v0/statistic/basic_info/class_gender", {
    query: { page: d.genderPage, page_size: d.genderSize },
  });
  const host = document.getElementById("dashGenderBody");
  if (!host) return;
  if (!res.ok) return (host.innerHTML = `<div class="empty">${esc(res.msg)}</div>`);
  const { rows, total } = parsePagedResponse(res.data, { page: d.genderPage, size: d.genderSize });
  host.innerHTML = `
    ${tableHtml(
      [
        { key: "class_code", label: "班级编号" },
        { key: "total", label: "总人数" },
        { key: "male_cnt", label: "男生" },
        { key: "female_cnt", label: "女生" },
      ],
      rows
    )}
    <div id="dashGenderPager"></div>`;
  renderPager(
    document.getElementById("dashGenderPager"),
    { page: d.genderPage, size: d.genderSize, total },
    (p) => {
      d.genderPage = p;
      loadDashboardGender();
    },
    (sz) => {
      d.genderSize = sz;
      d.genderPage = 1;
      loadDashboardGender();
    }
  );
}

/* ========== 学生 ========== */
async function students() {
  const el = document.getElementById("page-students");
  const f = STATE.students.filters;
  const classList = await loadClassOptions();
  const classOpts = buildSelectOptions(
    classList,
    (c) => c.id,
    (c) => `班编号 ${c.class_code}（id ${c.id}）`,
    { selected: f.class_id, allowEmpty: true, emptyLabel: "全部班级" }
  );
  el.innerHTML = `
    ${toolbarLayout(
      `${fieldRow("学生编号", "stu_id", f.stu_id || "", "number", "", { min: 1, placeholder: "正整数" })}
      ${fieldRow("姓名", "stu_name", f.stu_name || "", "text", "", { maxlength: 25 })}
      ${fieldRow("班级", "class_id", "", "select", classOpts)}
      ${queryActions({ queryId: "stuSearch", resetId: "stuReset" })}`,
      `<button type="button" class="btn primary" id="stuAdd">新增学生</button>`
    )}
    <div class="card" id="stuCard">加载中…</div>`;
  const bar = el.querySelector(".toolbar-fields");
  el.querySelector("#stuReset").onclick = () => {
    STATE.students.filters = {};
    STATE.students.page = 1;
    students();
  };
  bar.closest(".toolbar").querySelector("#stuSearch").onclick = () => {
    try {
      const stuRaw = bar.querySelector('[name="stu_id"]').value;
      const clsRaw = bar.querySelector('[name="class_id"]').value;
      STATE.students.filters = {
        stu_id: stuRaw ? validateNumber(stuRaw, { label: "学生编号", min: 1 }) : "",
        stu_name: validateText(bar.querySelector('[name="stu_name"]').value, { label: "姓名", maxLen: 25 }),
        class_id: clsRaw ? validateNumber(clsRaw, { label: "班级", min: 1 }) : "",
      };
      STATE.students.page = 1;
      loadStudents();
    } catch (e) {
      toast(e.message, "error");
    }
  };
  el.querySelector("#stuAdd").onclick = () => studentForm();
  await loadStudents();
}

async function loadStudents() {
  const card = document.getElementById("stuCard");
  const q = {
    ...STATE.students.filters,
    page: STATE.students.page,
    size: STATE.students.size,
  };
  const res = await request("GET", "/v0/student", { query: q });
  if (!res.ok) {
    card.innerHTML = `<div class="empty">${esc(res.msg)}</div>`;
    return;
  }
  const { rows, total } = parsePagedResponse(res.data, {
    page: STATE.students.page,
    size: STATE.students.size,
  });
  card.innerHTML = `
    <div class="card-head"><h3>学生列表（共 ${total} 人）</h3></div>
    ${tableHtml(
      [
        { key: "id", label: "编号" },
        { key: "name", label: "姓名" },
        { key: "gender", label: "性别" },
        { key: "age", label: "年龄" },
        { key: "class_id", label: "班级ID" },
        { key: "major", label: "专业" },
        { key: "native_place", label: "籍贯" },
      ],
      rows,
      (row) => `<button type="button" class="btn-link" data-edit="${row.id}">编辑</button>
                <button type="button" class="btn-link danger" data-del="${row.id}">删除</button>`
    )}
    <div class="pager" id="stuPager"></div>`;
  renderPager(
    document.getElementById("stuPager"),
    { page: STATE.students.page, size: STATE.students.size, total },
    (p) => {
      STATE.students.page = p;
      loadStudents();
    },
    (sz) => {
      STATE.students.size = sz;
      STATE.students.page = 1;
      loadStudents();
    }
  );
  card.querySelectorAll("[data-edit]").forEach((b) =>
    b.onclick = () => studentForm(rows.find((r) => r.id == b.dataset.edit))
  );
  card.querySelectorAll("[data-del]").forEach((b) =>
    b.onclick = () =>
      confirmDialog(`确定删除学生 #${b.dataset.del}？`, async () => {
        const r = await request("DELETE", `/v1/student/${b.dataset.del}`);
        if (r.ok) toast("已删除", "success"), loadStudents();
        else toast(r.msg, "error");
      })
  );
}

async function studentForm(row) {
  const isEdit = !!row;
  const [classList, teacherList] = await Promise.all([loadClassOptions(), loadTeacherOptions()]);
  const classOpts = buildSelectOptions(classList, (c) => c.id, (c) => `班编号 ${c.class_code}（id ${c.id}）`, {
    selected: row?.class_id,
    allowEmpty: isEdit,
    emptyLabel: "请选择班级",
  });
  const teaOpts = buildSelectOptions(
    teacherList,
    (t) => t.id,
    (t) => `${t.name}（编号 ${t.teacher_code}，id ${t.id}）`,
    { selected: row?.consultant_id, allowEmpty: isEdit, emptyLabel: "请选择顾问" }
  );
  const body = `<form class="form-grid" id="stuForm">
    ${fieldRow("所属班级", "class_id", "", "select", classOpts)}
    ${fieldRow("姓名", "name", row?.name ?? "", "text", "", { maxlength: 25, required: true })}
    ${fieldRow("性别", "gender", row?.gender ?? "", "select", `<option value="">请选择</option><option value="男">男</option><option value="女">女</option>`)}
    ${fieldRow("年龄", "age", row?.age ?? "", "number", "", { min: 0, max: 100, required: true })}
    ${fieldRow("籍贯", "native_place", row?.native_place ?? "", "text", "", { maxlength: 50, required: true })}
    ${fieldRow("毕业院校", "graduate_school", row?.graduate_school ?? "", "text", "", { maxlength: 25, required: true })}
    ${fieldRow("专业", "major", row?.major ?? "", "text", "", { maxlength: 25, required: true })}
    ${fieldRow("入学时间", "enrollment_time", fmtDate(row?.enrollment_time), "date", "", { required: true })}
    ${fieldRow("毕业时间", "graduate_time", fmtDate(row?.graduate_time), "date", "", { required: true })}
    ${fieldRow("顾问教师", "consultant_id", "", "select", teaOpts)}
  </form>`;
  openModal(isEdit ? "编辑学生" : "新增学生", body, async (close) => {
    const fm = document.getElementById("stuForm");
    const raw = Object.fromEntries(new FormData(fm));
    const data = {
      class_id: validateNumber(raw.class_id, { label: "所属班级", min: 1, required: !isEdit }),
      name: validateText(raw.name, { label: "姓名", required: true, maxLen: 25 }),
      gender: raw.gender === "男" || raw.gender === "女" ? raw.gender : (() => { throw new Error("请选择性别"); })(),
      age: validateNumber(raw.age, { label: "年龄", min: 0, max: 100, required: true }),
      native_place: validateText(raw.native_place, { label: "籍贯", required: true, maxLen: 50 }),
      graduate_school: validateText(raw.graduate_school, { label: "毕业院校", required: true, maxLen: 25 }),
      major: validateText(raw.major, { label: "专业", required: true, maxLen: 25 }),
      enrollment_time: validateText(raw.enrollment_time, { label: "入学时间", required: true }),
      graduate_time: validateText(raw.graduate_time, { label: "毕业时间", required: true }),
      consultant_id: validateNumber(raw.consultant_id, { label: "顾问教师", min: 1, required: !isEdit }),
    };
  if (isEdit) {
      Object.keys(data).forEach((k) => data[k] == null && delete data[k]);
    }
    const res = isEdit
      ? await request("PUT", `/v1/student/${row.id}`, { json: data })
      : await request("POST", "/v0/student", { json: data });
    if (!res.ok) throw new Error(res.msg);
    clearOptionCache("students");
    toast(isEdit ? "保存成功" : "新增成功", "success");
    close();
    loadStudents();
  });
}

/* ========== 班级 ========== */
async function classes() {
  const el = document.getElementById("page-classes");
  const classList = await loadClassOptions();
  const codeOpts = buildSelectOptions(
    classList,
    (c) => c.class_code,
    (c) => `班编号 ${c.class_code}（id ${c.id}）`,
    { selected: STATE.classes.class_code, allowEmpty: true, emptyLabel: "选择班级编号" }
  );
  el.innerHTML = `
    ${toolbarLayout(
      `${fieldRow("按班级编号", "class_code", "", "select", codeOpts)}
      ${queryActions({ queryId: "clsByCode", resetId: "clsReset" })}`,
      `<button type="button" class="btn primary" id="clsAdd">新增班级</button>`
    )}
    <div class="card" id="clsCard">加载中…</div>`;
  const bar = el.querySelector(".toolbar-fields");
  el.querySelector("#clsReset").onclick = () => {
    STATE.classes.class_code = "";
    STATE.classes.page = 1;
    classes();
  };
  bar.closest(".toolbar").querySelector("#clsByCode").onclick = () => {
    const code = bar.querySelector('[name="class_code"]').value;
    if (!code) return toast("请选择班级编号", "error");
    STATE.classes.class_code = code;
    loadClassByCode();
  };
  el.querySelector("#clsAdd").onclick = () => classForm();
  if (STATE.classes.class_code) await loadClassByCode();
  else await loadClasses();
}

async function loadClassByCode() {
  const code = STATE.classes.class_code;
  const card = document.getElementById("clsCard");
  if (!code) return loadClasses();
  const res = await request("GET", `/v1/class/code/${code}`);
  if (!res.ok) return (card.innerHTML = `<div class="empty">${esc(res.msg)}</div>`);
  const row = res.data?.data;
  card.innerHTML = `
    <div class="card-head"><h3>班级编号 ${code}</h3></div>
    ${tableHtml(
      [
        { key: "id", label: "ID" },
        { key: "class_code", label: "班级编号" },
        { key: "start_time", label: "开班", fmt: fmtDate },
        { key: "end_time", label: "结业", fmt: fmtDate },
        { key: "teacher_id", label: "班主任ID" },
      ],
      row ? [row] : [],
      (r) => `<button type="button" class="btn-link" data-edit="${r.id}">编辑</button>
              <button type="button" class="btn-link danger" data-del="${r.id}">删除</button>`
    )}`;
  if (!row) return;
  card.querySelector("[data-edit]")?.addEventListener("click", () => classForm(row));
  card.querySelector("[data-del]")?.addEventListener("click", () =>
    confirmDialog("确定删除该班级？", async () => {
      const r = await request("DELETE", `/v1/class/${row.id}`);
      if (r.ok) toast("已删除", "success"), loadClassByCode();
      else toast(r.msg, "error");
    })
  );
}

async function loadClasses() {
  const res = await request("GET", "/v0/class", {
    query: { page: STATE.classes.page, size: STATE.classes.size },
  });
  const card = document.getElementById("clsCard");
  if (!res.ok) return (card.innerHTML = `<div class="empty">${esc(res.msg)}</div>`);
  const { rows, total } = parsePagedResponse(res.data, {
    page: STATE.classes.page,
    size: STATE.classes.size,
  });
  card.innerHTML = `
    <div class="card-head"><h3>班级列表（共 ${total} 个）</h3></div>
    ${tableHtml(
      [
        { key: "id", label: "ID" },
        { key: "class_code", label: "班级编号" },
        { key: "start_time", label: "开班", fmt: fmtDate },
        { key: "end_time", label: "结业", fmt: fmtDate },
        { key: "teacher_id", label: "班主任ID" },
      ],
      rows,
      (row) => `<button type="button" class="btn-link" data-edit="${row.id}">编辑</button>
                <button type="button" class="btn-link danger" data-del="${row.id}">删除</button>`
    )}
    <div class="pager" id="clsPager"></div>`;
  renderPager(
    document.getElementById("clsPager"),
    { page: STATE.classes.page, size: STATE.classes.size, total },
    (p) => {
      STATE.classes.page = p;
      loadClasses();
    },
    (sz) => {
      STATE.classes.size = sz;
      STATE.classes.page = 1;
      loadClasses();
    }
  );
  card.querySelectorAll("[data-edit]").forEach((b) =>
    b.onclick = () => classForm(rows.find((r) => r.id == b.dataset.edit))
  );
  card.querySelectorAll("[data-del]").forEach((b) =>
    b.onclick = () =>
      confirmDialog("确定删除该班级？", async () => {
        const r = await request("DELETE", `/v1/class/${b.dataset.del}`);
        if (r.ok) {
          clearOptionCache("classes");
          toast("已删除", "success");
          loadClasses();
        } else toast(r.msg, "error");
      })
  );
}

async function classForm(row) {
  const isEdit = !!row;
  const teachers = await loadTeacherOptions();
  const teaOpts = buildSelectOptions(
    teachers,
    (t) => t.id,
    (t) => `${t.name}（编号 ${t.teacher_code}）`,
    { selected: row?.teacher_id, allowEmpty: !isEdit }
  );
  openModal(
    isEdit ? "编辑班级" : "新增班级",
    `<form class="form-grid" id="clsForm">
      ${fieldRow("班级编号", "class_code", row?.class_code ?? "", "number", "", { min: 1, required: true })}
      ${fieldRow("开班时间", "start_time", fmtDate(row?.start_time), "date", "", { required: true })}
      ${fieldRow("结业时间", "end_time", fmtDate(row?.end_time), "date")}
      ${fieldRow("班主任", "teacher_id", "", "select", teaOpts)}
    </form>`,
    async (close) => {
      const raw = Object.fromEntries(new FormData(document.getElementById("clsForm")));
      const data = {
        class_code: validateNumber(raw.class_code, { label: "班级编号", min: 1, required: true }),
        start_time: validateText(raw.start_time, { label: "开班时间", required: true }),
        teacher_id: validateNumber(raw.teacher_id, { label: "班主任", min: 1, required: true }),
      };
      if (raw.end_time) data.end_time = raw.end_time;
      const res = isEdit
        ? await request("PUT", `/v1/class/${row.id}`, { json: data })
        : await request("POST", "/v0/class", { json: data });
      if (!res.ok) throw new Error(res.msg);
      clearOptionCache("classes");
      toast("保存成功", "success");
      close();
      loadClasses();
    }
  );
}

/* ========== 教师 ========== */
async function teachers() {
  const el = document.getElementById("page-teachers");
  const teacherList = await loadTeacherOptions();
  const codeOpts = buildSelectOptions(
    teacherList,
    (t) => t.teacher_code,
    (t) => `${t.name}（编号 ${t.teacher_code}）`,
    { selected: STATE.teachers.teacher_code, allowEmpty: true, emptyLabel: "选择教师编号" }
  );
  el.innerHTML = `
    ${toolbarLayout(
      `${fieldRow("教师编号", "teacher_code", "", "select", codeOpts)}
      ${queryActions({ queryId: "teaByCode", resetId: "teaReset" })}`,
      `<button type="button" class="btn primary" id="teaAdd">新增教师</button>`
    )}
    <div class="card" id="teaCard">加载中…</div>`;
  const bar = el.querySelector(".toolbar-fields");
  el.querySelector("#teaReset").onclick = () => {
    STATE.teachers.teacher_code = "";
    STATE.teachers.page = 1;
    teachers();
  };
  bar.closest(".toolbar").querySelector("#teaByCode").onclick = () => {
    const code = bar.querySelector('[name="teacher_code"]').value;
    if (!code) return toast("请选择教师编号", "error");
    STATE.teachers.teacher_code = code;
    loadTeacherByCode();
  };
  el.querySelector("#teaAdd").onclick = () => teacherForm();
  if (STATE.teachers.teacher_code) await loadTeacherByCode();
  else await loadTeachers();
}

async function loadTeacherByCode() {
  const code = STATE.teachers.teacher_code;
  const card = document.getElementById("teaCard");
  if (!code) return loadTeachers();
  const res = await request("GET", `/v1/teacher/code/${code}`);
  if (!res.ok) return (card.innerHTML = `<div class="empty">${esc(res.msg)}</div>`);
  const row = res.data?.data;
  card.innerHTML = `
    <div class="card-head"><h3>教师编号 ${code}</h3></div>
    ${tableHtml(
      [
        { key: "id", label: "ID" },
        { key: "teacher_code", label: "教师编号" },
        { key: "name", label: "姓名" },
        { key: "email", label: "邮箱" },
        { key: "is_head", label: "班主任", fmt: (v) => (v == 1 ? "是" : "否") },
      ],
      row ? [row] : [],
      (r) => `<button type="button" class="btn-link" data-edit="${r.id}">编辑</button>
              <button type="button" class="btn-link danger" data-del="${r.id}">删除</button>`
    )}`;
  if (!row) return;
  card.querySelector("[data-edit]")?.addEventListener("click", () => teacherForm(row));
  card.querySelector("[data-del]")?.addEventListener("click", () =>
    confirmDialog("确定删除该教师？", async () => {
      const r = await request("DELETE", `/v1/teacher/${row.id}`);
      if (r.ok) toast("已删除", "success"), loadTeacherByCode();
      else toast(r.msg, "error");
    })
  );
}

async function loadTeachers() {
  const res = await request("GET", "/v0/teacher", {
    query: { page: STATE.teachers.page, size: STATE.teachers.size },
  });
  const card = document.getElementById("teaCard");
  if (!res.ok) return (card.innerHTML = `<div class="empty">${esc(res.msg)}</div>`);
  const { rows, total } = parsePagedResponse(res.data, {
    page: STATE.teachers.page,
    size: STATE.teachers.size,
  });
  card.innerHTML = `
    <div class="card-head"><h3>教师列表（共 ${total} 人）</h3></div>
    ${tableHtml(
      [
        { key: "id", label: "ID" },
        { key: "teacher_code", label: "教师编号" },
        { key: "name", label: "姓名" },
        { key: "email", label: "邮箱" },
        { key: "is_head", label: "班主任", fmt: (v) => (v == 1 ? "是" : "否") },
      ],
      rows,
      (row) => `<button type="button" class="btn-link" data-edit="${row.id}">编辑</button>
                <button type="button" class="btn-link danger" data-del="${row.id}">删除</button>`
    )}
    <div class="pager" id="teaPager"></div>`;
  renderPager(
    document.getElementById("teaPager"),
    { page: STATE.teachers.page, size: STATE.teachers.size, total },
    (p) => {
      STATE.teachers.page = p;
      loadTeachers();
    },
    (sz) => {
      STATE.teachers.size = sz;
      STATE.teachers.page = 1;
      loadTeachers();
    }
  );
  card.querySelectorAll("[data-edit]").forEach((b) =>
    b.onclick = () => teacherForm(rows.find((r) => r.id == b.dataset.edit))
  );
  card.querySelectorAll("[data-del]").forEach((b) =>
    b.onclick = () =>
      confirmDialog("确定删除该教师？", async () => {
        const r = await request("DELETE", `/v1/teacher/${b.dataset.del}`);
        if (r.ok) toast("已删除", "success"), loadTeachers();
        else toast(r.msg, "error");
      })
  );
}

function teacherForm(row) {
  const isEdit = !!row;
  openModal(
    isEdit ? "编辑教师" : "新增教师",
    `<form class="form-grid" id="teaForm">
      ${fieldRow("教师编号", "teacher_code", row?.teacher_code ?? "", "number", "", { min: 1 })}
      ${fieldRow("姓名", "name", row?.name ?? "", "text", "", { maxlength: 25, required: true })}
      ${fieldRow("邮箱", "email", row?.email ?? "", "email")}
      ${fieldRow("是否班主任", "is_head", String(row?.is_head ?? 0), "select", `<option value="0">否</option><option value="1">是</option>`)}
    </form>`,
    async (close) => {
      const raw = Object.fromEntries(new FormData(document.getElementById("teaForm")));
      const data = {
        name: validateText(raw.name, { label: "姓名", required: true, maxLen: 25 }),
        email: raw.email ? validateText(raw.email, { label: "邮箱", maxLen: 80 }) : undefined,
        is_head: validateNumber(raw.is_head, { label: "是否班主任", min: 0, max: 1, required: true }),
      };
      if (raw.teacher_code) data.teacher_code = validateNumber(raw.teacher_code, { label: "教师编号", min: 1 });
      const res = isEdit
        ? await request("PUT", `/v1/teacher/${row.id}`, { json: data })
        : await request("POST", "/v0/teacher", { json: data });
      if (!res.ok) throw new Error(res.msg);
      clearOptionCache("teachers");
      toast("保存成功", "success");
      close();
      loadTeachers();
    }
  );
}

/* ========== 就业 ========== */
async function employment() {
  const el = document.getElementById("page-employment");
  const mode = STATE.employment.mode;
  el.innerHTML = `
    <div class="tabs" id="empModeTabs">
      <button type="button" data-mode="class" class="${mode === "class" ? "active" : ""}">按班级</button>
      <button type="button" data-mode="company" class="${mode === "company" ? "active" : ""}">按公司</button>
      <button type="button" data-mode="salary" class="${mode === "salary" ? "active" : ""}">按薪资</button>
      <button type="button" data-mode="student" class="${mode === "student" ? "active" : ""}">按学生</button>
    </div>
    <div class="toolbar" id="empToolbar"></div>
    <div class="card" id="empCard"></div>`;
  el.querySelectorAll("#empModeTabs button").forEach((b) => {
    b.onclick = () => {
      STATE.employment.mode = b.dataset.mode;
      STATE.employment.page = 1;
      employment();
    };
  });
  const bar = document.getElementById("empToolbar");
  if (mode === "class") {
    const clsRes = await request("GET", "/v0/class", { query: { page: 1, size: 100 } });
    const classes = parsePagedResponse(clsRes.data, { page: 1, size: 100 }).rows;
    const opts = classes.map((c) => `<option value="${c.class_code}">${c.class_code}</option>`).join("");
    fillToolbar(
      bar,
      `<label class="field"><span>班级编号</span><select id="empClass">${opts || '<option value="">无班级</option>'}</select></label>
       ${queryActions({ queryId: "empLoad", resetId: "empReset" })}`,
      `<button type="button" class="btn primary" id="empAdd">登记就业</button>`
    );
    bar.querySelector("#empReset").onclick = () => {
      const sel = bar.querySelector("#empClass");
      if (sel?.options.length) sel.selectedIndex = 0;
      STATE.employment.page = 1;
      loadEmploymentList();
    };
    bar.querySelector("#empLoad").onclick = () => {
      STATE.employment.page = 1;
      loadEmploymentList();
    };
    bar.querySelector("#empAdd").onclick = () => empAddForm();
    if (classes.length) loadEmploymentList();
    else document.getElementById("empCard").innerHTML = `<div class="empty">请先创建班级与学生</div>`;
  } else if (mode === "company") {
    fillToolbar(
      bar,
      `${fieldRow("公司名称", "company", "", "text", "", { maxlength: 50 })}
       ${queryActions({ queryId: "empLoad", resetId: "empReset" })}`
    );
    bar.querySelector("#empReset").onclick = () => {
      const inp = bar.querySelector('[name="company"]');
      if (inp) inp.value = "";
      STATE.employment.page = 1;
      document.getElementById("empCard").innerHTML = `<div class="empty">输入公司名称后点击查询</div>`;
    };
    bar.querySelector("#empLoad").onclick = () => {
      STATE.employment.page = 1;
      loadEmploymentList();
    };
    document.getElementById("empCard").innerHTML = `<div class="empty">输入公司名称后点击查询</div>`;
  } else if (mode === "salary") {
    fillToolbar(
      bar,
      `${fieldRow("薪资下限", "salary_min", "", "number", "", { min: 0, step: "0.01" })}
       ${fieldRow("薪资上限", "salary_max", "", "number", "", { min: 0, step: "0.01" })}
       ${queryActions({ queryId: "empLoad", resetId: "empReset" })}`
    );
    bar.querySelector("#empReset").onclick = () => {
      bar.querySelector('[name="salary_min"]').value = "";
      bar.querySelector('[name="salary_max"]').value = "";
      STATE.employment.page = 1;
      document.getElementById("empCard").innerHTML = `<div class="empty">填写薪资区间后查询</div>`;
    };
    bar.querySelector("#empLoad").onclick = () => {
      STATE.employment.page = 1;
      loadEmploymentList();
    };
    document.getElementById("empCard").innerHTML = `<div class="empty">填写薪资区间后查询</div>`;
  } else {
    const students = await loadStudentOptions();
    const stuOpts = buildSelectOptions(students, (s) => s.id, (s) => `${s.name}（id ${s.id}）`, { allowEmpty: true });
    fillToolbar(
      bar,
      `${fieldRow("学生", "stu_id", "", "select", stuOpts)}
       ${queryActions({ queryId: "empLoad", resetId: "empReset" })}`,
      `<button type="button" class="btn primary" id="empAdd">登记就业</button>`
    );
    bar.querySelector("#empReset").onclick = () => {
      const sel = bar.querySelector('[name="stu_id"]');
      if (sel) sel.value = "";
      document.getElementById("empCard").innerHTML = `<div class="empty">选择学生后查询就业记录</div>`;
    };
    bar.querySelector("#empLoad").onclick = loadEmploymentByStudent;
    bar.querySelector("#empAdd").onclick = () => empAddForm();
    document.getElementById("empCard").innerHTML = `<div class="empty">选择学生后查询就业记录</div>`;
  }
}

async function loadEmploymentList() {
  const card = document.getElementById("empCard");
  const mode = STATE.employment.mode;
  let res;
  let title = "";
  if (mode === "class") {
    const code = document.getElementById("empClass")?.value;
    if (!code) return (card.innerHTML = `<div class="empty">请选择班级</div>`);
    title = `班级 ${code}`;
    res = await request("GET", `/v1/employment/class/${code}`, {
      query: { page: STATE.employment.page, page_size: STATE.employment.page_size },
    });
  } else if (mode === "company") {
    const company = document.querySelector('#empToolbar [name="company"]')?.value?.trim();
    if (!company) return toast("请填写公司名称", "error");
    validateText(company, { label: "公司名称", minLen: 1, maxLen: 50 });
    title = `公司含「${company}」`;
    res = await request("GET", "/v0/employment/company", {
      query: { company, page: STATE.employment.page, page_size: STATE.employment.page_size },
    });
  } else {
    const minEl = document.querySelector('#empToolbar [name="salary_min"]');
    const maxEl = document.querySelector('#empToolbar [name="salary_max"]');
    let range;
    try {
      range = validateSalaryRange(minEl?.value, maxEl?.value);
    } catch (e) {
      return (card.innerHTML = `<div class="empty">${esc(e.message)}</div>`);
    }
    title = "薪资区间";
    res = await request("GET", "/v0/employment/salary_range", {
      query: {
        salary_min: range.min ?? undefined,
        salary_max: range.max ?? undefined,
        page: STATE.employment.page,
        page_size: STATE.employment.page_size,
      },
    });
  }
  if (!res.ok) return (card.innerHTML = `<div class="empty">${esc(res.msg)}</div>`);
  const pack = res.data?.data;
  const rows = listRowsFromPack(pack);
  const total = pack?.total ?? 0;
  card.innerHTML = `
    <div class="card-head"><h3>${title} · 就业信息</h3></div>
    ${tableHtml(
      [
        { key: "student_id", label: "学生ID" },
        { key: "student_name", label: "学生" },
        { key: "class_code", label: "班级" },
        { key: "company", label: "公司" },
        { key: "salary", label: "薪资" },
        { key: "open_time", label: "开放时间", fmt: fmtDateTime },
        { key: "offer_time", label: "Offer时间", fmt: fmtDateTime },
      ],
      rows,
      (row) => `<button type="button" class="btn-link" data-edit="${row.student_id}">编辑</button>
                <button type="button" class="btn-link danger" data-del="${row.student_id}">删除</button>`
    )}
    <div class="pager" id="empPager"></div>`;
  renderPager(
    document.getElementById("empPager"),
    {
      page: pack?.page ?? STATE.employment.page,
      size: pack?.page_size ?? STATE.employment.page_size,
      total,
    },
    (p) => {
      STATE.employment.page = p;
      loadEmploymentList();
    },
    (sz) => {
      STATE.employment.page_size = sz;
      STATE.employment.page = 1;
      loadEmploymentList();
    }
  );
  bindEmploymentRowActions(rows, loadEmploymentList);
}

async function loadEmploymentByStudent() {
  const stuId = document.querySelector('#empToolbar [name="stu_id"]')?.value;
  const card = document.getElementById("empCard");
  let stuNum;
  try {
    stuNum = validateNumber(stuId, { label: "学生ID", min: 1, required: true });
  } catch (e) {
    return toast(e.message, "error");
  }
  const res = await request("GET", `/v1/employment/students/${stuNum}`);
  if (!res.ok) return (card.innerHTML = `<div class="empty">${esc(res.msg)}</div>`);
  const row = res.data?.data;
  card.innerHTML = `
    <div class="card-head"><h3>学生 #${stuNum}</h3></div>
    ${tableHtml(
      [
        { key: "student_name", label: "学生" },
        { key: "class_code", label: "班级" },
        { key: "company", label: "公司" },
        { key: "salary", label: "薪资" },
        { key: "open_time", label: "开放时间", fmt: fmtDateTime },
        { key: "offer_time", label: "Offer", fmt: fmtDateTime },
      ],
      row ? [row] : [],
      (r) => `<button type="button" class="btn-link" data-edit="${r.student_id}">编辑</button>
              <button type="button" class="btn-link danger" data-del="${r.student_id}">删除</button>`
    )}`;
  bindEmploymentRowActions(row ? [row] : [], loadEmploymentByStudent);
}

function bindEmploymentRowActions(rows, reload) {
  const card = document.getElementById("empCard");
  card.querySelectorAll("[data-edit]").forEach((b) =>
    b.onclick = () => empEditForm(rows.find((r) => String(r.student_id) === b.dataset.edit))
  );
  card.querySelectorAll("[data-del]").forEach((b) =>
    b.onclick = () =>
      confirmDialog("删除该就业记录？", async () => {
        const r = await request("DELETE", `/v1/employment/students/${b.dataset.del}`);
        if (r.ok) toast("已删除", "success"), reload();
        else toast(r.msg, "error");
      })
  );
}

async function empAddForm() {
  const students = await loadStudentOptions();
  const stuOpts = buildSelectOptions(
    students,
    (s) => s.id,
    (s) => `${s.name}（id ${s.id}，班 ${s.class_id}）`,
    { allowEmpty: true }
  );
  openModal(
    "登记就业",
    `<form class="form-grid">${fieldRow("学生", "stu_id", "", "select", stuOpts)}</form>
     <p class="modal-tip">将根据学生档案自动填充姓名与班级。</p>`,
    async (close) => {
      const stu_id = validateNumber(document.querySelector('#modalRoot [name="stu_id"]').value, {
        label: "学生",
        min: 1,
        required: true,
      });
      const res = await request("POST", `/v1/employment/students/${stu_id}`);
      if (!res.ok) throw new Error(res.msg);
      toast("登记成功，可继续编辑公司与薪资", "success");
      close();
      reloadEmploymentPage();
    }
  );
}

function reloadEmploymentPage() {
  if (STATE.employment.mode === "student") loadEmploymentByStudent();
  else if (document.getElementById("empCard")?.innerHTML && STATE.employment.mode !== "student") loadEmploymentList();
}

function empEditForm(row) {
  if (!row) return;
  openModal(
    "编辑就业信息",
    `<form class="form-grid" id="empForm">
      ${fieldRow("公司", "company", row.company ?? "")}
      ${fieldRow("薪资", "salary", row.salary ?? "", "number", "", { min: 0, step: "0.01" })}
      ${fieldRow("开放时间", "open_time", row.open_time ? String(row.open_time).slice(0, 16) : "", "datetime-local")}
      ${fieldRow("Offer时间", "offer_time", row.offer_time ? String(row.offer_time).slice(0, 16) : "", "datetime-local")}
    </form>`,
    async (close) => {
      const raw = Object.fromEntries(new FormData(document.getElementById("empForm")));
      const data = {
        company: raw.company ? validateText(raw.company, { label: "公司", maxLen: 50 }) : undefined,
        salary: raw.salary === "" ? undefined : validateNumber(raw.salary, { label: "薪资", min: 0, integer: false }),
        open_time: raw.open_time,
        offer_time: raw.offer_time,
      };
      ["open_time", "offer_time"].forEach((k) => {
        if (data[k] && data[k].length === 16) data[k] += ":00";
        if (!data[k]) delete data[k];
      });
      Object.keys(data).forEach((k) => data[k] === undefined && delete data[k]);
      const res = await request("PUT", `/v1/employment/students/${row.student_id}`, { json: data });
      if (!res.ok) throw new Error(res.msg);
      toast("保存成功", "success");
      close();
      reloadEmploymentPage();
    }
  );
}

/* ========== 成绩（科目/课程/成绩） ========== */
function scores() {
  const el = document.getElementById("page-scores");
  el.innerHTML = `
    <div class="tabs" id="scoreTabs">
      <button type="button" data-tab="list" class="${STATE.scoresTab === "list" ? "active" : ""}">成绩记录</button>
      <button type="button" data-tab="subject" class="${STATE.scoresTab === "subject" ? "active" : ""}">科目</button>
      <button type="button" data-tab="course" class="${STATE.scoresTab === "course" ? "active" : ""}">课程</button>
    </div>
    <div id="scoreBody"></div>`;
  el.querySelectorAll("#scoreTabs button").forEach((b) => {
    b.onclick = () => {
      STATE.scoresTab = b.dataset.tab;
      scores();
    };
  });
  if (STATE.scoresTab === "subject") loadSubjects();
  else if (STATE.scoresTab === "course") loadCourses();
  else loadScoreList();
}

async function loadScoreList() {
  const body = document.getElementById("scoreBody");
  const f = STATE.scoreList;
  const [students, teachers, subjects] = await Promise.all([
    loadStudentOptions(),
    loadTeacherOptions(),
    loadSubjectOptions(),
  ]);
  const stuOpts = buildSelectOptions(students, (s) => s.id, (s) => `${s.name}（id ${s.id}）`, {
    selected: f.stu_id,
    allowEmpty: true,
    emptyLabel: "不限",
  });
  const teaOpts = buildSelectOptions(teachers, (t) => t.id, (t) => `${t.name}（id ${t.id}）`, {
    selected: f.teacher_id,
    allowEmpty: true,
    emptyLabel: "不限",
  });
  const subOpts = buildSelectOptions(subjects, (s) => s.id, (s) => `${s.subject_name}（id ${s.id}）`, {
    selected: f.subject_id,
    allowEmpty: true,
    emptyLabel: "不限",
  });
  body.innerHTML = `
    ${toolbarLayout(
      `${fieldRow("学生", "stu_id", "", "select", stuOpts)}
       ${fieldRow("教师", "teacher_id", "", "select", teaOpts)}
       ${fieldRow("科目", "subject_id", "", "select", subOpts)}
       ${queryActions({ queryId: "scSearch", resetId: "scReset" })}`,
      `<button type="button" class="btn primary" id="scAdd">录入成绩</button>`
    )}
    <div class="card" id="scCard">加载中…</div>`;
  body.querySelector("#scAdd").onclick = () => scoreForm();
  body.querySelector("#scReset").onclick = () => {
    STATE.scoreList = { page: 1, size: 10, stu_id: "", teacher_id: "", subject_id: "" };
    loadScoreList();
  };
  body.querySelector("#scSearch").onclick = () => {
    const bar = body.querySelector(".toolbar-fields");
    const stu = bar.querySelector('[name="stu_id"]').value;
    const tea = bar.querySelector('[name="teacher_id"]').value;
    const sub = bar.querySelector('[name="subject_id"]').value;
  const picked = [stu, tea, sub].filter(Boolean).length;
    if (picked > 1) return toast("成绩查询请只选择学生、教师或科目其中一项", "error");
    STATE.scoreList.stu_id = stu;
    STATE.scoreList.teacher_id = tea;
    STATE.scoreList.subject_id = sub;
    STATE.scoreList.page = 1;
    loadScoreListData();
  };
  await loadScoreListData();
}

async function loadScoreListData() {
  const card = document.getElementById("scCard");
  const f = STATE.scoreList;
  let res;
  let title = "成绩记录";
  const pageQuery = { page: f.page, size: f.size };
  if (f.stu_id) {
    res = await request("GET", `/v1/score/score/student/${f.stu_id}`, { query: pageQuery });
    title = `学生成绩`;
  } else if (f.teacher_id) {
    res = await request("GET", `/v1/score/score/teacher/${f.teacher_id}`, { query: pageQuery });
    title = `教师任课成绩`;
  } else if (f.subject_id) {
    res = await request("GET", `/v1/score/score/subject/${f.subject_id}`, { query: pageQuery });
    title = `科目成绩`;
  } else {
    res = await request("GET", "/v0/score/score", { query: pageQuery });
  }
  if (!res.ok) return (card.innerHTML = `<div class="empty">${esc(res.msg)}</div>`);
  const { rows, total } = parsePagedResponse(res.data, { page: f.page, size: f.size });
  const cols = rows[0]?.student_name
    ? [
        { key: "student_name", label: "学生" },
        { key: "subject_name", label: "科目" },
        { key: "teacher_name", label: "教师" },
        { key: "score", label: "分数" },
        { key: "exam_order", label: "批次" },
      ]
    : [
        { key: "id", label: "ID" },
        { key: "stu_id", label: "学生ID" },
        { key: "course_id", label: "课程ID" },
        { key: "score", label: "分数" },
        { key: "exam_order", label: "批次" },
      ];
  card.innerHTML = `
    <div class="card-head"><h3>${title}（共 ${total} 条）</h3></div>
    ${tableHtml(cols, rows)}
    <div class="pager" id="scPager"></div>`;
  renderPager(
    document.getElementById("scPager"),
    { page: f.page, size: f.size, total },
    (p) => {
      STATE.scoreList.page = p;
      loadScoreListData();
    },
    (sz) => {
      STATE.scoreList.size = sz;
      STATE.scoreList.page = 1;
      loadScoreListData();
    }
  );
}

async function scoreForm() {
  const [students, courses] = await Promise.all([loadStudentOptions(), loadCourseOptions()]);
  const stuOpts = buildSelectOptions(students, (s) => s.id, (s) => `${s.name}（id ${s.id}）`, { allowEmpty: true });
  const couOpts = buildSelectOptions(
    courses,
    (c) => c.id,
    (c) => `课程 ${c.id}（班 ${c.class_id} / 科目 ${c.subject_id}）`,
    { allowEmpty: true }
  );
  openModal(
    "录入成绩",
    `<form class="form-grid" id="scForm">
      ${fieldRow("学生", "stu_id", "", "select", stuOpts)}
      ${fieldRow("课程", "course_id", "", "select", couOpts)}
      ${fieldRow("成绩", "score", "", "number", "", { min: 0, max: 100 })}
      ${fieldRow("考试批次", "exam_order", "1", "number", "", { min: 1 })}
    </form>`,
    async (close) => {
      const raw = Object.fromEntries(new FormData(document.getElementById("scForm")));
      const data = {
        stu_id: validateNumber(raw.stu_id, { label: "学生", min: 1, required: true }),
        course_id: validateNumber(raw.course_id, { label: "课程", min: 1, required: true }),
        score: raw.score === "" ? null : validateNumber(raw.score, { label: "成绩", min: 0, max: 100 }),
        exam_order: raw.exam_order === "" ? null : validateNumber(raw.exam_order, { label: "考试批次", min: 1 }),
      };
      const res = await request("POST", "/v0/score/score", { json: data });
      if (!res.ok) throw new Error(res.msg);
      toast("录入成功", "success");
      close();
      loadScoreListData();
    }
  );
}

async function loadSubjects() {
  const body = document.getElementById("scoreBody");
  const st = STATE.subjects;
  body.innerHTML = `${toolbarLayout("", `<button class="btn primary" id="subAdd">新增科目</button>`)}<div class="card" id="subCard">加载中…</div>`;
  body.querySelector("#subAdd").onclick = () => subjectForm();
  const res = await request("GET", "/v0/score/subject", { query: { page: st.page, size: st.size } });
  const card = document.getElementById("subCard");
  if (!res.ok) return (card.innerHTML = `<div class="empty">${esc(res.msg)}</div>`);
  const norm = parsePagedResponse(res.data, { page: st.page, size: st.size });
  card.innerHTML = `
    <div class="card-head"><h3>科目列表（共 ${norm.total} 条）</h3></div>
    ${tableHtml(
      [
        { key: "id", label: "ID" },
        { key: "subject_code", label: "科目编号" },
        { key: "subject_name", label: "名称" },
      ],
      norm.rows,
      (row) => `<button class="btn-link danger" data-del="${row.id}">删除</button>`
    )}
    <div class="pager" id="subPager"></div>`;
  renderPager(
    document.getElementById("subPager"),
    { page: st.page, size: st.size, total: norm.total },
    (p) => {
      STATE.subjects.page = p;
      loadSubjects();
    },
    (sz) => {
      STATE.subjects.size = sz;
      STATE.subjects.page = 1;
      loadSubjects();
    }
  );
  card.querySelectorAll("[data-del]").forEach((b) =>
    b.onclick = () =>
      confirmDialog("删除科目？", async () => {
        const r = await request("DELETE", `/v1/score/subject/${b.dataset.del}`);
        if (r.ok) clearOptionCache("subjects"), toast("已删除", "success");
        loadSubjects();
      })
  );
}

function subjectForm() {
  openModal(
    "新增科目",
    `<form class="form-grid">
      ${fieldRow("科目编号", "subject_code", "", "number", "", { min: 1, required: true })}
      ${fieldRow("科目名称", "subject_name", "", "text", "", { maxlength: 25, required: true })}
    </form>`,
    async (close) => {
      const raw = Object.fromEntries(new FormData(document.querySelector("#modalRoot form")));
      const data = {
        subject_code: validateNumber(raw.subject_code, { label: "科目编号", min: 1, required: true }),
        subject_name: validateText(raw.subject_name, { label: "科目名称", required: true, maxLen: 25 }),
      };
      const res = await request("POST", "/v0/score/subject", { json: data });
      if (!res.ok) throw new Error(res.msg);
      clearOptionCache("subjects");
      toast("已新增", "success");
      close();
      loadSubjects();
    }
  );
}

async function loadCourses() {
  const body = document.getElementById("scoreBody");
  const st = STATE.courses;
  body.innerHTML = `${toolbarLayout("", `<button class="btn primary" id="couAdd">新增课程</button>`)}<div class="card" id="couCard">加载中…</div>`;
  body.querySelector("#couAdd").onclick = () => courseForm();
  const res = await request("GET", "/v0/score/course", { query: { page: st.page, size: st.size } });
  const card = document.getElementById("couCard");
  if (!res.ok) return (card.innerHTML = `<div class="empty">${esc(res.msg)}</div>`);
  const norm = parsePagedResponse(res.data, { page: st.page, size: st.size });
  card.innerHTML = `
    <div class="card-head"><h3>课程列表（共 ${norm.total} 条）</h3></div>
    ${tableHtml(
      [
        { key: "id", label: "ID" },
        { key: "class_id", label: "班级" },
        { key: "subject_id", label: "科目" },
        { key: "teacher_id", label: "教师" },
        { key: "start_time", label: "开始", fmt: fmtDate },
        { key: "end_time", label: "结束", fmt: fmtDate },
      ],
      norm.rows,
      (row) => `<button class="btn-link danger" data-del="${row.id}">删除</button>`
    )}
    <div class="pager" id="couPager"></div>`;
  renderPager(
    document.getElementById("couPager"),
    { page: st.page, size: st.size, total: norm.total },
    (p) => {
      STATE.courses.page = p;
      loadCourses();
    },
    (sz) => {
      STATE.courses.size = sz;
      STATE.courses.page = 1;
      loadCourses();
    }
  );
  card.querySelectorAll("[data-del]").forEach((b) =>
    b.onclick = () =>
      confirmDialog("删除课程？", async () => {
        const r = await request("DELETE", `/v1/score/course/${b.dataset.del}`);
        if (r.ok) clearOptionCache("courses"), toast("已删除", "success");
        loadCourses();
      })
  );
}

async function courseForm() {
  const [classList, subjectList, teacherList] = await Promise.all([
    loadClassOptions(),
    loadSubjectOptions(),
    loadTeacherOptions(),
  ]);
  openModal(
    "新增课程",
    `<form class="form-grid" id="couForm">
      ${fieldRow(
        "班级",
        "class_id",
        "",
        "select",
        buildSelectOptions(classList, (c) => c.id, (c) => `班编号 ${c.class_code}`, { allowEmpty: true })
      )}
      ${fieldRow(
        "科目",
        "subject_id",
        "",
        "select",
        buildSelectOptions(subjectList, (s) => s.id, (s) => s.subject_name, { allowEmpty: true })
      )}
      ${fieldRow(
        "教师",
        "teacher_id",
        "",
        "select",
        buildSelectOptions(teacherList, (t) => t.id, (t) => t.name, { allowEmpty: true })
      )}
      ${fieldRow("开始日期", "start_time", "", "date", "", { required: true })}
      ${fieldRow("结束日期", "end_time", "", "date", "", { required: true })}
    </form>`,
    async (close) => {
      const raw = Object.fromEntries(new FormData(document.getElementById("couForm")));
      const data = {
        class_id: validateNumber(raw.class_id, { label: "班级", min: 1, required: true }),
        subject_id: validateNumber(raw.subject_id, { label: "科目", min: 1, required: true }),
        teacher_id: validateNumber(raw.teacher_id, { label: "教师", min: 1, required: true }),
        start_time: validateText(raw.start_time, { label: "开始日期", required: true }),
        end_time: validateText(raw.end_time, { label: "结束日期", required: true }),
      };
      const res = await request("POST", "/v0/score/course", { json: data });
      if (!res.ok) throw new Error(res.msg);
      clearOptionCache("courses");
      toast("已新增", "success");
      close();
      loadCourses();
    }
  );
}

/* ========== 用户 ========== */
async function users() {
  if (!isAdmin()) {
    document.getElementById("page-users").innerHTML =
      `<div class="empty">仅管理员可访问用户管理，请使用管理员账号登录。</div>`;
    return;
  }
  const el = document.getElementById("page-users");
  el.innerHTML = `
    <div class="toolbar">
      <button type="button" class="btn primary" id="usrAdd">新增用户</button>
      <button type="button" class="btn ghost" id="usrReload">刷新列表</button>
    </div>
    <div class="card" id="usrCard">加载中…</div>`;
  el.querySelector("#usrAdd").onclick = () => userForm();
  el.querySelector("#usrReload").onclick = () => loadUsers();
  await loadUsers();
}

async function loadUsers() {
  const st = STATE.users || { page: 1, size: 10 };
  const card = document.getElementById("usrCard");
  if (!card) return;
  let query;
  try {
    query = buildUserMgmtQuery({ page: st.page, size: st.size });
  } catch (e) {
    card.innerHTML = `<div class="empty">${esc(e.message)} <a href="./login.html">去登录</a></div>`;
    return;
  }
  const res = await request("GET", "/v0/user/query", { query });
  if (!res.ok) {
    card.innerHTML = `<div class="empty">${esc(res.msg || "无权限或会话失效，请重新登录")}</div>`;
    return;
  }
  const { rows, total } = parsePagedResponse(res.data, { page: st.page, size: st.size });
  card.innerHTML = `
    <div class="card-head"><h3>系统用户（共 ${total} 人）</h3></div>
    ${tableHtml(
      [
        { key: "id", label: "ID" },
        { key: "username", label: "用户名" },
        { key: "full_name", label: "姓名" },
        { key: "role_name", label: "角色" },
        { key: "is_active", label: "状态", fmt: (v) => (v == 1 ? "正常" : "禁用") },
      ],
      rows,
      (row) =>
        row.role_name !== "admin" || row.username === getAdminUsername()
          ? `<button class="btn-link" data-edit="${row.id}">编辑</button>
             <button class="btn-link danger" data-del="${row.id}">删除</button>`
          : "-"
    )}
    <div class="pager" id="usrPager"></div>`;
  renderPager(
    document.getElementById("usrPager"),
    { page: st.page, size: st.size, total },
    (p) => {
      st.page = p;
      loadUsers();
    },
    (sz) => {
      st.size = sz;
      st.page = 1;
      loadUsers();
    }
  );
  card.querySelectorAll("[data-edit]").forEach((b) =>
    b.onclick = () => userForm(rows.find((r) => r.id == b.dataset.edit))
  );
  card.querySelectorAll("[data-del]").forEach((b) =>
    b.onclick = () =>
      confirmDialog("删除该用户？", async () => {
        try {
          const r = await request("DELETE", `/v1/user/${b.dataset.del}`, {
            query: buildUserMgmtQuery(),
          });
          if (r.ok) toast("已删除", "success"), loadUsers();
          else toast(r.msg, "error");
        } catch (e) {
          toast(e.message, "error");
        }
      })
  );
}

function userForm(row) {
  const isEdit = !!row;
  openModal(
    isEdit ? "编辑用户" : "新增用户",
    isEdit
      ? `<form class="form-grid" id="usrForm">
          ${fieldRow("用户ID", "user_id", row.id, "number")}
          ${fieldRow("用户名", "username", row.username)}
          ${fieldRow("姓名", "full_name", row.full_name)}
          ${fieldRow("状态", "is_active", "", "select", `<option value="1">正常</option><option value="0">禁用</option>`)}
        </form>`
      : `<form class="form-grid" id="usrForm">
          ${fieldRow("用户名", "username", "")}
          ${fieldRow("密码", "password", "", "password")}
          ${fieldRow("确认密码", "confirm_password", "", "password")}
          ${fieldRow("姓名", "full_name", "")}
          ${fieldRow("角色", "role_id", "", "select", `<option value="2">教师</option><option value="3">学生</option>`)}
        </form>`,
    async (close) => {
      const raw = Object.fromEntries(new FormData(document.getElementById("usrForm")));
      const mgmtQuery = buildUserMgmtQuery();
      let form;
      if (isEdit) {
        form = {
          user_id: row.id,
          username: raw.username ? validateText(raw.username, { label: "用户名", minLen: 6, maxLen: 50 }) : undefined,
          full_name: raw.full_name ? validateText(raw.full_name, { label: "姓名", minLen: 2, maxLen: 20 }) : undefined,
          is_active: raw.is_active,
        };
      } else {
        validateText(raw.password, { label: "密码", required: true, minLen: 6, maxLen: 20 });
        if (raw.password !== raw.confirm_password) throw new Error("两次密码输入不一致");
        form = {
          username: validateText(raw.username, { label: "用户名", required: true, minLen: 3, maxLen: 50 }),
          password: raw.password,
          confirm_password: raw.confirm_password,
          full_name: validateText(raw.full_name, { label: "姓名", required: true, minLen: 2, maxLen: 20 }),
          role_id: validateNumber(raw.role_id, { label: "角色", min: 2, max: 3, required: true }),
        };
      }
      const res = isEdit
        ? await request("PUT", "/v0/user/update", { query: mgmtQuery, form })
        : await request("POST", "/v0/user/add", { query: mgmtQuery, form });
      if (!res.ok) throw new Error(res.msg);
      toast("保存成功", "success");
      close();
      loadUsers();
    }
  );
  if (isEdit) document.querySelector('#usrForm [name="is_active"]').value = String(row.is_active);
}

/* ========== 统计 ========== */
function stats() {
  const el = document.getElementById("page-stats");
  el.innerHTML = `
    <div class="tabs" id="statTabs">
      <button data-tab="basic" class="${STATE.statsTab === "basic" ? "active" : ""}">基本信息</button>
      <button data-tab="score" class="${STATE.statsTab === "score" ? "active" : ""}">成绩分析</button>
      <button data-tab="emp" class="${STATE.statsTab === "emp" ? "active" : ""}">就业分析</button>
    </div>
    <div id="statBody"></div>`;
  el.querySelectorAll("#statTabs button").forEach((b) => {
    b.onclick = () => {
      STATE.statsTab = b.dataset.tab;
      stats();
    };
  });
  if (STATE.statsTab === "score") loadStatScore();
  else if (STATE.statsTab === "emp") loadStatEmp();
  else loadStatBasic();
}

async function loadStatBasic() {
  const s = STATE.stats;
  const box = document.getElementById("statBody");
  box.innerHTML = `
    ${toolbarLayout(
      `<strong class="toolbar-title">各班性别统计</strong>
       ${queryActions({ queryId: "stGenderGo", resetId: "stGenderReset" })}`
    )}
    <div class="card" id="stGender" style="margin-bottom:14px">加载中…</div>
    ${toolbarLayout(
      `${fieldRow("年龄阈值（岁以上，留空=全部）", "age_threshold", s.olderAge, "number", "", {
        min: 0,
        max: 120,
        placeholder: "不填查全部",
      })}
      ${queryActions({ queryId: "stOlderGo", resetId: "stOlderReset" })}`
    )}
    <div class="card" id="stOlder">加载中…</div>`;
  box.querySelector("#stGenderGo").onclick = () => {
    STATE.stats.genderPage = 1;
    runStatGender();
  };
  box.querySelector("#stGenderReset").onclick = () => {
    STATE.stats.genderPage = 1;
    runStatGender();
  };
  box.querySelector("#stOlderGo").onclick = () => {
    try {
      const raw = box.querySelector('[name="age_threshold"]').value;
      s.olderAge = raw === "" ? "" : validateNumber(raw, { label: "年龄阈值", min: 0, max: 120 });
      s.olderPage = 1;
      runStatOlder();
    } catch (e) {
      toast(e.message, "error");
    }
  };
  box.querySelector("#stOlderReset").onclick = () => {
    s.olderAge = "";
    s.olderPage = 1;
    const inp = box.querySelector('[name="age_threshold"]');
    if (inp) inp.value = "";
    runStatOlder();
  };
  await Promise.all([runStatGender(), runStatOlder()]);
}

async function runStatGender() {
  const s = STATE.stats;
  const res = await request("GET", "/v0/statistic/basic_info/class_gender", {
    query: { page: s.genderPage, page_size: s.genderSize },
  });
  const { rows, total } = parsePagedResponse(res.data, { page: s.genderPage, size: s.genderSize });
  const card = document.getElementById("stGender");
  card.innerHTML = `
    <div class="card-head"><h3>各班人数与性别统计（共 ${total} 班）</h3></div>
    ${tableHtml(
      [
        { key: "class_code", label: "班级" },
        { key: "total", label: "总人数" },
        { key: "male_cnt", label: "男" },
        { key: "female_cnt", label: "女" },
      ],
      rows
    )}
    <div class="pager" id="stGenderPager"></div>`;
  renderPager(
    document.getElementById("stGenderPager"),
    { page: s.genderPage, size: s.genderSize, total },
    (p) => {
      s.genderPage = p;
      runStatGender();
    },
    (sz) => {
      s.genderSize = sz;
      s.genderPage = 1;
      runStatGender();
    }
  );
}

async function runStatOlder() {
  const s = STATE.stats;
  const card = document.getElementById("stOlder");
  card.innerHTML = "加载中…";
  const q = { page: s.olderPage, page_size: s.olderSize };
  if (s.olderAge !== "" && s.olderAge != null) q.age_threshold = s.olderAge;
  const res = await request("GET", "/v0/statistic/basic_info/student_older", { query: q });
  if (!res.ok) return (card.innerHTML = `<div class="empty">${esc(res.msg)}</div>`);
  const { rows, total } = parsePagedResponse(res.data, { page: s.olderPage, size: s.olderSize });
  const ageLabel = s.olderAge !== "" && s.olderAge != null ? `${s.olderAge} 岁以上` : "全部年龄";
  card.innerHTML = `
    <div class="card-head"><h3>学员查询（${ageLabel}，共 ${total} 人）</h3></div>
    ${tableHtml(
      [
        { key: "id", label: "学号" },
        { key: "name", label: "姓名" },
        { key: "age", label: "年龄" },
        { key: "class_id", label: "班级ID" },
      ],
      rows
    )}
    <div class="pager" id="stOlderPager"></div>`;
  renderPager(
    document.getElementById("stOlderPager"),
    { page: s.olderPage, size: s.olderSize, total },
    (p) => {
      s.olderPage = p;
      runStatOlder();
    },
    (sz) => {
      s.olderSize = sz;
      s.olderPage = 1;
      runStatOlder();
    }
  );
}

async function loadStatScore() {
  const s = STATE.stats;
  const box = document.getElementById("statBody");
  box.innerHTML = `
    ${toolbarLayout(
      `${fieldRow("达标分数线", "min_target_score", s.geScore, "number", "", { min: 0, max: 100 })}
      ${queryActions({ queryId: "stGeGo", resetId: "stGeReset" })}`
    )}
    <div class="card" id="stGe" style="margin-bottom:12px">加载中…</div>
    ${toolbarLayout(
      `${fieldRow("及格线", "pass_score", s.passScore, "number", "", { min: 0, max: 100 })}
       ${fieldRow("最少不及格次数", "min_fail_count", s.failCount, "number", "", { min: 1 })}
       ${queryActions({ queryId: "stFailGo", resetId: "stFailReset" })}`
    )}
    <div class="card" id="stFail" style="margin-bottom:12px">加载中…</div>
    ${toolbarLayout(
      `<span class="toolbar-title">班级考试平均分</span>
       <button type="button" class="btn primary" id="stAvgGo">刷新</button>
       <button type="button" class="btn ghost" id="stAvgReset">重置</button>`
    )}
    <div class="card" id="stAvg">加载中…</div>`;
  box.querySelector("#stGeGo").onclick = () => {
    try {
      const raw = box.querySelector('[name="min_target_score"]').value;
      s.geScore = raw === "" ? 80 : validateNumber(raw, { label: "达标分数线", min: 0, max: 100 });
      s.gePage = 1;
      runStatGe();
    } catch (e) {
      toast(e.message, "error");
    }
  };
  box.querySelector("#stFailGo").onclick = () => {
    try {
      s.passScore = validateNumber(box.querySelector('[name="pass_score"]').value || 60, {
        label: "及格线",
        min: 0,
        max: 100,
      });
      s.failCount = validateNumber(box.querySelector('[name="min_fail_count"]').value || 2, {
        label: "最少不及格次数",
        min: 1,
      });
      s.failPage = 1;
      runStatFail();
    } catch (e) {
      toast(e.message, "error");
    }
  };
  box.querySelector("#stGeReset").onclick = () => {
    s.geScore = 80;
    s.gePage = 1;
    box.querySelector('[name="min_target_score"]').value = "80";
    runStatGe();
  };
  box.querySelector("#stFailReset").onclick = () => {
    s.passScore = 60;
    s.failCount = 2;
    s.failPage = 1;
    box.querySelector('[name="pass_score"]').value = "60";
    box.querySelector('[name="min_fail_count"]').value = "2";
    runStatFail();
  };
  box.querySelector("#stAvgGo").onclick = () => {
    s.avgPage = 1;
    runStatAvg();
  };
  box.querySelector("#stAvgReset").onclick = () => {
    s.avgPage = 1;
    runStatAvg();
  };
  await Promise.all([runStatGe(), runStatFail(), runStatAvg()]);
}

async function runStatGe() {
  const s = STATE.stats;
  const res = await request("GET", "/v0/statistic/score/score_all_ge", {
    query: { min_target_score: s.geScore, page: s.gePage, page_size: s.geSize },
  });
  const { rows, total } = parsePagedResponse(res.data, { page: s.gePage, size: s.geSize });
  const card = document.getElementById("stGe");
  card.innerHTML = `
    <div class="card-head"><h3>全科达标（≥${s.geScore}，共 ${total} 人）</h3></div>
    ${tableHtml(
      [
        { key: "stu_id", label: "学号" },
        { key: "name", label: "姓名" },
        { key: "scores", label: "各科成绩", fmt: (v) => (Array.isArray(v) ? v.join(", ") : v) },
      ],
      rows
    )}
    <div class="pager" id="stGePager"></div>`;
  renderPager(
    document.getElementById("stGePager"),
    { page: s.gePage, size: s.geSize, total },
    (p) => {
      s.gePage = p;
      runStatGe();
    },
    (sz) => {
      s.geSize = sz;
      s.gePage = 1;
      runStatGe();
    }
  );
}

async function runStatFail() {
  const s = STATE.stats;
  const res = await request("GET", "/v0/statistic/score/fail_more2", {
    query: { pass_score: s.passScore, min_fail_count: s.failCount, page: s.failPage, page_size: s.failSize },
  });
  const { rows, total } = parsePagedResponse(res.data, { page: s.failPage, size: s.failSize });
  const card = document.getElementById("stFail");
  card.innerHTML = `
    <div class="card-head"><h3>不及格≥${s.failCount}次（及格线${s.passScore}，共 ${total} 人）</h3></div>
    ${tableHtml(
      [
        { key: "name", label: "姓名" },
        { key: "class_code", label: "班级" },
        { key: "fail_scores", label: "不及格分数", fmt: (v) => (Array.isArray(v) ? v.join(", ") : v) },
      ],
      rows
    )}
    <div class="pager" id="stFailPager"></div>`;
  renderPager(
    document.getElementById("stFailPager"),
    { page: s.failPage, size: s.failSize, total },
    (p) => {
      s.failPage = p;
      runStatFail();
    },
    (sz) => {
      s.failSize = sz;
      s.failPage = 1;
      runStatFail();
    }
  );
}

async function runStatAvg() {
  const s = STATE.stats;
  const res = await request("GET", "/v0/statistic/score/class_avg", {
    query: { page: s.avgPage, page_size: s.avgSize },
  });
  const { rows, total } = parsePagedResponse(res.data, { page: s.avgPage, size: s.avgSize });
  const card = document.getElementById("stAvg");
  card.innerHTML = `
    <div class="card-head"><h3>班级考试平均分（共 ${total} 条）</h3></div>
    ${tableHtml(
      [
        { key: "class_code", label: "班级" },
        { key: "exam_order", label: "批次" },
        { key: "avg_score", label: "平均分" },
      ],
      rows
    )}
    <div class="pager" id="stAvgPager"></div>`;
  renderPager(
    document.getElementById("stAvgPager"),
    { page: s.avgPage, size: s.avgSize, total },
    (p) => {
      s.avgPage = p;
      runStatAvg();
    },
    (sz) => {
      s.avgSize = sz;
      s.avgPage = 1;
      runStatAvg();
    }
  );
}

async function loadStatEmp() {
  const s = STATE.stats;
  const classList = await loadClassOptions();
  const classOpts = buildSelectOptions(classList, (c) => c.class_code, (c) => `班编号 ${c.class_code}`, {
    allowEmpty: true,
    emptyLabel: "全部班级",
  });
  const box = document.getElementById("statBody");
  box.innerHTML = `
    ${toolbarLayout(
      `${fieldRow("薪资排名前 N", "rank", s.empRank, "number", "", { min: 1 })}
      ${queryActions({ queryId: "stRankGo", resetId: "stRankReset" })}`
    )}
    <div class="card" id="stRank" style="margin-bottom:12px">加载中…</div>
    ${toolbarLayout(
      `${fieldRow("学员姓名（可选）", "emp_name", s.empName, "text", "", { maxlength: 25 })}
      ${queryActions({ queryId: "stNameGo", resetId: "stNameReset" })}`
    )}
    <div class="card" id="stName" style="margin-bottom:12px"></div>
    ${toolbarLayout(
      `${fieldRow("班级编号", "class_code", "", "select", classOpts)}
      ${queryActions({ queryId: "stClassTimeGo", resetId: "stClassTimeReset" })}`
    )}
    <div class="card" id="stClassTime" style="margin-bottom:12px"></div>
    ${toolbarLayout(
      `${fieldRow("班级编号", "avg_class", "", "select", classOpts)}
      ${queryActions({ queryId: "stClassAvgGo", resetId: "stClassAvgReset" })}`
    )}
    <div class="card" id="stClassAvg"></div>`;
  box.querySelector("#stRankGo").onclick = () => {
    try {
      const raw = box.querySelector('[name="rank"]').value;
      s.empRank = raw === "" ? 10 : validateNumber(raw, { label: "排名数量", min: 1 });
      s.empRankPage = 1;
      runStatRank();
    } catch (e) {
      toast(e.message, "error");
    }
  };
  box.querySelector("#stNameGo").onclick = () => {
    s.empName = box.querySelector('[name="emp_name"]').value;
    s.empNamePage = 1;
    runStatEmpName();
  };
  box.querySelector("#stClassTimeGo").onclick = () => {
    const v = box.querySelector('[name="class_code"]').value;
    s.empClassCode = v ? validateNumber(v, { label: "班级编号", min: 1 }) : "";
    s.empClassTimePage = 1;
    runStatClassTime();
  };
  box.querySelector("#stClassAvgGo").onclick = () => {
    const v = box.querySelector('[name="avg_class"]').value;
    s.empAvgClass = v ? validateNumber(v, { label: "班级编号", min: 1 }) : "";
    s.empClassAvgPage = 1;
    runStatClassAvg();
  };
  box.querySelector("#stRankReset").onclick = () => {
    s.empRank = 10;
    s.empRankPage = 1;
    box.querySelector('[name="rank"]').value = "10";
    runStatRank();
  };
  box.querySelector("#stNameReset").onclick = () => {
    s.empName = "";
    s.empNamePage = 1;
    box.querySelector('[name="emp_name"]').value = "";
    runStatEmpName();
  };
  box.querySelector("#stClassTimeReset").onclick = () => {
    s.empClassCode = "";
    s.empClassTimePage = 1;
    box.querySelector('[name="class_code"]').value = "";
    runStatClassTime();
  };
  box.querySelector("#stClassAvgReset").onclick = () => {
    s.empAvgClass = "";
    s.empClassAvgPage = 1;
    box.querySelector('[name="avg_class"]').value = "";
    runStatClassAvg();
  };
  await runStatRank();
}

async function runStatRank() {
  const s = STATE.stats;
  const res = await request("GET", "/v0/statistic/employment/rank", {
    query: { rank: s.empRank, page: s.empRankPage, size: s.empRankSize },
  });
  const card = document.getElementById("stRank");
  if (!res.ok) return (card.innerHTML = `<div class="empty">${esc(res.msg)}</div>`);
  const { rows, total } = parsePagedResponse(res.data, { page: s.empRankPage, size: s.empRankSize });
  card.innerHTML = `
    <div class="card-head"><h3>薪资 TOP ${s.empRank}（当前页 ${rows.length} 条）</h3></div>
    ${tableHtml(
      [
        { key: "student_name", label: "姓名" },
        { key: "class_code", label: "班级" },
        { key: "company", label: "公司" },
        { key: "salary", label: "薪资" },
      ],
      rows
    )}
    <div class="pager" id="stRankPager"></div>`;
  renderPager(
    document.getElementById("stRankPager"),
    { page: s.empRankPage, size: s.empRankSize, total },
    (p) => {
      s.empRankPage = p;
      runStatRank();
    },
    (sz) => {
      s.empRankSize = sz;
      s.empRankPage = 1;
      runStatRank();
    }
  );
}

async function runStatEmpName() {
  const s = STATE.stats;
  const q = { page: s.empNamePage, size: s.empNameSize };
  if (s.empName) q.name = s.empName.trim();
  const res = await request("GET", "/v0/statistic/employment/name", { query: q });
  const card = document.getElementById("stName");
  if (!res.ok) return (card.innerHTML = `<div class="empty">${esc(res.msg)}</div>`);
  const { rows, total } = parsePagedResponse(res.data, { page: s.empNamePage, size: s.empNameSize });
  card.innerHTML = `
    <div class="card-head"><h3>学生就业时长（共 ${total} 人）</h3></div>
    ${tableHtml(
      [
        { key: "student_name", label: "姓名" },
        { key: "class_code", label: "班级" },
        { key: "emp_days", label: "天数" },
      ],
      rows
    )}
    <div class="pager" id="stEmpNamePager"></div>`;
  renderPager(
    document.getElementById("stEmpNamePager"),
    { page: s.empNamePage, size: s.empNameSize, total },
    (p) => {
      s.empNamePage = p;
      runStatEmpName();
    },
    (sz) => {
      s.empNameSize = sz;
      s.empNamePage = 1;
      runStatEmpName();
    }
  );
}

async function runStatClassTime() {
  const s = STATE.stats;
  const q = { page: s.empClassTimePage, size: s.empClassTimeSize };
  if (s.empClassCode !== "" && s.empClassCode != null) q.class_code = s.empClassCode;
  const res = await request("GET", "/v0/statistic/employment/class_code", { query: q });
  const card = document.getElementById("stClassTime");
  if (!res.ok) return (card.innerHTML = `<div class="empty">${esc(res.msg)}</div>`);
  const { rows, total } = parsePagedResponse(res.data, { page: s.empClassTimePage, size: s.empClassTimeSize });
  card.innerHTML = `
    <div class="card-head"><h3>班级就业时长（共 ${total} 人）</h3></div>
    ${tableHtml(
      [
        { key: "student_name", label: "姓名" },
        { key: "class_code", label: "班级" },
        { key: "emp_days", label: "天数" },
      ],
      rows
    )}
    <div class="pager" id="stClassTimePager"></div>`;
  renderPager(
    document.getElementById("stClassTimePager"),
    { page: s.empClassTimePage, size: s.empClassTimeSize, total },
    (p) => {
      s.empClassTimePage = p;
      runStatClassTime();
    },
    (sz) => {
      s.empClassTimeSize = sz;
      s.empClassTimePage = 1;
      runStatClassTime();
    }
  );
}

async function runStatClassAvg() {
  const s = STATE.stats;
  const q = { page: s.empClassAvgPage, size: s.empClassAvgSize };
  if (s.empAvgClass !== "" && s.empAvgClass != null) q.class_code = s.empAvgClass;
  const res = await request("GET", "/v0/statistic/employment/class_avg", { query: q });
  const card = document.getElementById("stClassAvg");
  if (!res.ok) return (card.innerHTML = `<div class="empty">${esc(res.msg)}</div>`);
  const { rows, total } = parsePagedResponse(res.data, { page: s.empClassAvgPage, size: s.empClassAvgSize });
  card.innerHTML = `
    <div class="card-head"><h3>班级平均就业时长（共 ${total} 条）</h3></div>
    ${tableHtml(
      [
        { key: "class_code", label: "班级" },
        { key: "emp_days", label: "平均天数" },
      ],
      rows
    )}
    <div class="pager" id="stClassAvgPager"></div>`;
  renderPager(
    document.getElementById("stClassAvgPager"),
    { page: s.empClassAvgPage, size: s.empClassAvgSize, total },
    (p) => {
      s.empClassAvgPage = p;
      runStatClassAvg();
    },
    (sz) => {
      s.empClassAvgSize = sz;
      s.empClassAvgPage = 1;
      runStatClassAvg();
    }
  );
}
