# 学生管理系统 · 前后端启动与测试文档

本文说明如何启动 FastAPI 后端与 HTML 前端，并完成接口联调测试。

---

## 一、环境准备

### 1. 软件要求

| 项目 | 说明 |
|------|------|
| Python | 建议 3.10+ |
| MySQL | 本地已安装并可连接 |
| 浏览器 | Chrome / Edge 等现代浏览器 |

### 2. 数据库

1. 创建数据库：

```sql
CREATE DATABASE student_mgmt DEFAULT CHARACTER SET utf8mb4;
```

2. 确认 `app/core/config.py` 中的连接串与本机一致：

```python
DATABASE_URL= "mysql+pymysql://root:你的密码@localhost/student_mgmt"
```

> 启动后端时会自动 `create_all` 建表。若需测试数据，可按原 README 使用 `tests/insert_data.py` 插入（注意注释掉 `drop_all`）。

### 3. 安装依赖

在项目根目录 `student_mgmt/` 下：

```bash
# 建议先激活虚拟环境
pip install -r requirements.txt
```

若缺少 SQLAlchemy / pydantic / python-multipart（表单上传需要），可补充安装：

```bash
pip install sqlalchemy pydantic python-multipart
```

---

## 二、启动后端

在项目根目录执行：

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

启动成功后可访问：

| 地址 | 说明 |
|------|------|
| http://127.0.0.1:8000/docs | Swagger 接口文档 |
| http://127.0.0.1:8000/redoc | ReDoc 文档 |
| http://127.0.0.1:8000/ui/ | 前端联调页面（已挂载） |
| http://127.0.0.1:8000/student.com | OpenAPI JSON |

说明：

- 已开启 CORS，允许前端跨域调用。
- 认证中间件默认**未启用**（`AuthMiddleware` 在 `main.py` 中注释），测试时无需 Bearer Token。
- 用户管理接口仍需传管理员 `username` 查询参数做业务权限校验。

---

## 三、启动 / 打开前端

前端目录：`frontend/`（纯 HTML + CSS + JS，无构建）。

### 方式 A（推荐）：跟随后端一起访问

后端启动后直接打开：

```text
http://127.0.0.1:8000/ui/
```

### 方式 B：单独用静态服务器打开

另开一个终端，进入 `frontend` 目录：

```bash
cd frontend
python -m http.server 5500
```

浏览器打开：

```text
http://127.0.0.1:5500/
```

页面顶部「API 地址」默认是 `http://127.0.0.1:8000`，若后端端口不同，改完后点「保存 API 地址」。

---

## 四、前端功能与接口对照

页面为**业务管理界面**（非接口调试）：左侧菜单进入各模块，支持列表查询、弹窗新增/编辑、删除与统计报表。

### 演示数据

```bash
python tests/seed_demo_data.py
```

默认管理员：`admin001` / `123456`（用于「用户管理」模块）。

### 1. 用户管理 `/v1/user`

| 功能 | 方法 | 路径 |
|------|------|------|
| 查询所有用户 | GET | `/v1/user/query?username=` |
| 新增用户 | POST | `/v1/user/add?username=`（Form） |
| 修改用户 | PUT | `/v1/user/update?username=`（Form） |
| 删除用户 | DELETE | `/v1/user/{user_id}?username=` |

> 顶部「管理员用户名」必填，对应 query 参数 `username`。

### 2. 学生管理 `/v1/student`

| 功能 | 方法 | 路径 |
|------|------|------|
| 多条件列表 | GET | `/v1/student` |
| 按 ID 查询 | GET | `/v1/student/{stu_id}` |
| 创建学生 | POST | `/v1/student` |
| 更新学生 | PUT | `/v1/student/{stu_id}` |
| 逻辑删除 | DELETE | `/v1/student/{stu_id}` |

### 3. 班级管理 `/v1/class`

| 功能 | 方法 | 路径 |
|------|------|------|
| 分页列表 | GET | `/v1/class` |
| 按班级编号 | GET | `/v1/class/code/{class_code}` |
| 新增 | POST | `/v1/class` |
| 修改 | PUT | `/v1/class/{class_id}` |
| 删除 | DELETE | `/v1/class/{class_id}` |

### 4. 老师管理 `/v1/teacher`

| 功能 | 方法 | 路径 |
|------|------|------|
| 分页列表 | GET | `/v1/teacher` |
| 按教师编号 | GET | `/v1/teacher/code/{teacher_code}` |
| 新增 | POST | `/v1/teacher` |
| 修改 | PUT | `/v1/teacher/{teacher_id}` |
| 删除 | DELETE | `/v1/teacher/{teacher_id}` |

### 5. 就业管理 `/v1/employment`

| 功能 | 方法 | 路径 |
|------|------|------|
| 新增就业信息 | POST | `/v1/employment/students/{stu_id}` |
| 按学生查询 | GET | `/v1/employment/students/{stu_id}` |
| 按班级查询 | GET | `/v1/employment/class/{class_code}` |
| 按公司查询 | GET | `/v1/employment/company` |
| 按薪资范围 | GET | `/v1/employment/salary_range` |
| 修改 | PUT | `/v1/employment/students/{stu_id}` |
| 删除 | DELETE | `/v1/employment/students/{stu_id}` |

### 6. 科目管理 `/v1/score/subject`

| 功能 | 方法 | 路径 |
|------|------|------|
| 分页查询 | GET | `/v1/score/subject` |
| 单个查询 | GET | `/v1/score/subject/{subject_id}` |
| 新增 | POST | `/v1/score/subject` |
| 修改 | PUT | `/v1/score/subject/{subject_id}` |
| 删除 | DELETE | `/v1/score/subject/{subject_id}` |

### 7. 课程管理 `/v1/score/course`

| 功能 | 方法 | 路径 |
|------|------|------|
| 分页查询 | GET | `/v1/score/course` |
| 单个查询 | GET | `/v1/score/course/{course_id}` |
| 新增 | POST | `/v1/score/course` |
| 修改 | PUT | `/v1/score/course/{course_id}` |
| 删除 | DELETE | `/v1/score/course/{course_id}` |

### 8. 成绩管理 `/v1/score/score`

| 功能 | 方法 | 路径 |
|------|------|------|
| 录入成绩 | POST | `/v1/score/score` |
| 分页查询 | GET | `/v1/score/score` |
| 按学生查询 | GET | `/v1/score/score/student/{stu_id}` |
| 按学生改分 | PUT | `/v1/score/score/student/{stu_id}` |
| 按老师查询 | GET | `/v1/score/score/teacher/{teacher_id}` |
| 按科目查询 | GET | `/v1/score/score/subject/{subject_id}` |
| 按学生删除 | DELETE | `/v1/score/score/student/{stu_id}` |

### 9. 统计分析

#### 基本信息 `/v1/statistic/basic_info`

| 功能 | 方法 | 路径 |
|------|------|------|
| 年龄以上学员 | GET | `/v1/statistic/basic_info/student_older` |
| 各班男女统计 | GET | `/v1/statistic/basic_info/class_gender` |

#### 成绩统计 `/v1/statistic/score`

| 功能 | 方法 | 路径 |
|------|------|------|
| 全部成绩达标 | GET | `/v1/statistic/score/score_all_ge` |
| 多次不及格 | GET | `/v1/statistic/score/fail_more2` |
| 班级考试平均分 | GET | `/v1/statistic/score/class_avg` |

#### 就业统计 `/v1/statistic/employment`

| 功能 | 方法 | 路径 |
|------|------|------|
| 薪资排名 | GET | `/v1/statistic/employment/rank` |
| 学生就业时长 | GET | `/v1/statistic/employment/name` |
| 班级就业时长 | GET | `/v1/statistic/employment/class_code` |
| 班级平均就业时长 | GET | `/v1/statistic/employment/class_avg` |

---

## 五、建议测试顺序

数据有外键依赖，建议按以下顺序造数并验证：

1. **老师** → 新增老师  
2. **班级** → 指定班主任 ID  
3. **学生** → 指定班级 ID、顾问教师 ID  
4. **科目** → **课程**（班级 + 科目 + 老师）→ **成绩**  
5. **就业** → 对学生录入就业信息  
6. **用户** → 用已有管理员账号测试增删改查  
7. **统计模块** → 验证聚合查询结果  

也可先跑 `tests/insert_data.py` 灌入测试数据，再在前端只做查询与修改测试。

---

## 六、常见问题

### 1. 前端提示「网络错误」

- 确认后端已启动：`http://127.0.0.1:8000/docs` 能打开。  
- 确认顶部 API 地址正确。  
- 若用方式 B 单独开前端，确认 CORS 已生效（本项目 `main.py` 已配置）。

### 2. 用户接口 401 / 403

- 顶部管理员用户名是否填写正确，且该用户 `is_active=1`、角色为 admin。  
- 非管理员账号无法操作用户模块。

### 3. 新增学生失败「所属班级不存在」

- 先创建班级，再使用真实的 `class_id`（注意是班级表主键 id，不是 class_code）。

### 4. 表单接口报错（用户新增）

- 需安装 `python-multipart`：`pip install python-multipart`

### 5. 数据库连接失败

- 检查 MySQL 是否启动、库名/账号密码是否与 `app/core/config.py` 一致。

---

## 七、目录说明（前端相关）

```text
student_mgmt/
├── app/main.py              # 后端入口（含 CORS + /ui 静态挂载）
├── frontend/
│   ├── index.html           # 页面结构（全模块表单）
│   ├── css/style.css        # 样式
│   └── js/
│       ├── api.js           # 请求封装、结果表格渲染
│       └── app.js           # 各模块交互逻辑
├── STARTUP.md               # 本启动测试文档
└── README.md                # 原项目说明
```

---

## 八、快速一键自检清单

- [ ] MySQL `student_mgmt` 已创建，连接串正确  
- [ ] `pip install -r requirements.txt` 完成  
- [ ] `uvicorn app.main:app --reload` 启动成功  
- [ ] 打开 http://127.0.0.1:8000/docs 能看到接口  
- [ ] 打开 http://127.0.0.1:8000/ui/ 能看到前端  
- [ ] 老师/班级/学生查询有数据或可新增  
- [ ] 用户模块填写管理员用户名后可查询用户列表  
