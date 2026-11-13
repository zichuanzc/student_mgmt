# 项目介绍

## 团队介绍

![img](https://img0.baidu.com/it/u=3952228189,342176583&fm=253&fmt=auto&app=120&f=JPEG?w=700&h=475)

## 项目结构
```bash
student_mgmt/
├── app/
│   ├── api/
│   ├── core/					# 应用核心层，连接数据库，基本配置、异常处理
│   ├── dao/					# 数据库操作层
│   ├── lib/					# 工具包
│   ├── log/					# 日志
│   ├── middlewares/			# 中间件
│   ├── models/					# 映射模型
│   ├── schemas/				# 请求响应模型
│   ├── __init__.py
│   └── main.py					# 应用入口：创建 app、注册路由
├── frontend/       			# 前端代码
│   ├── css/					
│   ├── js/
│   └── index.html				# 前端首页
│   └── login.html				# 前端登录页面
├── tests/
│   ├── __init__.py
│   ├── insert_data.py			# 插入数据脚本
│   ├── seed_demo_data.py		# 插入数据脚本
│   ├── test_students.py		# 测试脚本，内容随写随删
│   ├── tree.txt				# 项目树形结构（2层）
│   └── tree3.py				# 获取项目树形结构脚本
├── README.md					# 项目概况
├── requirements.txt			# 项目环境依赖
└── STARTUP.md					# 项目完整启动指导
```

## 项目配置启动
- 前提：
     1. 配置好自己的基本虚拟环境
     1. 新建一个 MySQL 数据库：student_mgmt

- 依赖导出导入：
  
  - 导出：
    - 安装：`pip install pip-chill`
    - 导出依赖：`pip-chill > requirements.txt `
  - 导入：`pip install -r requirements.txt`
  
- 启动：
  1. 在命令行窗口，先进入自己的虚拟环境，进入项目目录，命令参考：`cd path`
  2. 安装依赖：`pip install -r requirements.txt`，目前基本都装过了，这一步可以省略
  3. 启动命令：`uvicorn app.main:app --reload`
     示例：`(D:\projects\AI1007\AI1007) PS D:\projects\AI1007\student_mgmt> uvicorn app.main:app --reload`
  
- 测试数据导入：
	
  1. 先启动app
  
  2. 打开insert_data.py脚本
  
  3. 依次放开需要插入数据的表，右键运行
  
     > 注意：要注释掉一行代码：`Base.metadata.drop_all(engine)`，避免每次插入数据时，之前的数据被清掉，然后会导致失败

## 开发遵循规则

### 路由定义规则

1. 在接口定义位置声明子路由：
   1. 导入：`from fastapi import APIRouter`
   2. 定义：`router = APIRouter(prefix="/所在文件名", tags=["功能模块名"])`
      1. 示例：`router=APIRouter(prefix="/employment", tags=["就业统计"])`
2. 在同级的 `__init__.py` 中，注册新定义的子路由：
   1. 导入：
      1. `from fastapi import APIRouter`
      2. `from .层级名 import router as 所在文件名_router`，示例：`from .statistic import router as statistic_router`
   2. 注册：
      1. ` 所在目录名_router= APIRouter(prefix="/所在目录名")`
      2. `所在目录名_router.include_router(所在文件名_router)`，示例：`v1_router.include_router(statistic_router)`
3. 在 `main.py` 中注册路由器：`app.include_router(api_router)`


### 命名规则

- 参考PEP 8规范，见名知义
- 目录用复数，文件用单数
- 与数据库的映射模型表名与数据库中保持一致，一个文件对应一张表
- 同一个概念在四层（路由 / Schema / 模型 / 表）用同一个词根，只靠后缀区分职责（未实现，后续需优化）

### 请求响应模型

- 请求体模型：
  - 项目中暂未统一请求体模型
- 响应头模型：
  - 统一响应头格式：`{"code: 状态码", "message": "概要文字说明", "data": data_responsed}`
  - 响应头显式声明，使用响应类：`ApiResponse`

### 文档注释

- 详略得当，简要概括
- 包可在其内的 `__init__.py`  中添加文档注释，说明包主要功能（一般通过包名见名知义，可省略）
- 模块顶部添加文档注释，说明模块对应功能
- 类中顶部添加类的文档注释，说明类的作用
- 函数中添加对应文档注释，说明该函数对应功能
- 部分参数，应当添加必要说明性注释文字

## 版本迭代更新（每次提交前必须检查更新）

### student_mgmt_V0.x

#### student_mgmt_V0.0.x

- `student_mgmt_V0.0.1`：
  - 项目基本框架搭建完成
- `student_mgmt_V0.0.2`：
  - 完成与数据库中表的映射模型创建，实现插入测试数据脚本：`insert_data.py`
- `student_mgmt_V0.0.3`：
  - 完成统计分析模块下子模块-就业统计 的接口
    - 数据库操作层新增：`app/dao/employment.py`
    - 响应模型新增：`app/schemas/statistic/employment.py`
    - 接口新增：`api/v1/statistic/employment.py`
  - 调整项目模块导入，在项目根目录下即可启动应用，更新后启动命令：`uvicorn app.main:app --reload`
- `student_mgmt_V0.0.4`：
  - 调整项目路由集成规则，在浏览器页面中可查看每个层级下拥有的所有接口
  - 集成用户管理模块，映射模型新增：`role.py`、`user.py`，接口新增：`api/v1/user.py`
  - 同步完善插入测试数据脚本
- `student_mgmt_V0.0.5`：
  - 集成班级管理模块，响应模型新增：`app/schemas/class_schema.py`、接口新增：`api/v1/class_api.py`
  - 集成老师管理模块，响应模型新增：`app/schemas/teacher_schema.py`，接口新增：`api/v1/teacher.py`
- `student_mgmt_V0.0.6`：
  - 集成学生管理模块，数据库操作层新增：`app/dao/student.py`，响应模型新增：`app/schemas/student.py`、接口新增：`api/v1/student.py`
  - 定义规范的响应体格式，统一响应体，新增基础响应模型：`app/schemas/base.py`
- `student_mgmt_V0.0.7`：
  - 集成就业管理模块：
    - 数据库操作层更新：`app/dao/employment.py`
    - 响应模型新增：`app/schemas/employment.py`
    - 接口新增：`api/v1/employment.py`
- `student_mgmt_V0.0.8`：
  - 更新班级管理模块：数据库操作层新增：`app/dao/class_.py`
  - 更新老师管理模块：数据库操作层新增：`app/dao/teacher.py`
- `student_mgmt_V0.0.9`：
  - 集成成绩管理模块：
    - 数据库操作层更新：`app/dao/subject.py`、`app/dao/course.py`、`app/dao/score.py`
    - 响应模型新增：`app/schemas/subject.py`、`app/schemas/course.py`、`app/schemas/score.py`
    - 接口新增：`app/api/score/subject.py`、`app/api/score/course.py`、`app/api/score/score.py`
  - 更新响应体格式规范，使其中 data 能够同时接收字典和列表，默认为 None

#### student_mgmt_V0.1.x

- `student_mgmt_V0.1.0`：
  - 集成 统计分析子模块-基本信息统计 、统计分析子模块-成绩统计 模块：
    - 数据库操作层增加、更新：`app/dao/basic_info.py`、`app/dao/score.py`
    - 响应模型增加：`app/schemas/statistic/basic_info.py`、`app/schemas//statistic/score.py`
    - 接口新增：`app/api/v1/statistic/basic_info.py`、`app/api/v1/statistic/score.py`
  - 更新响应体格式规范，重新定义泛型，同步更新统一各接口响应模型校验方式，修复BUG
  - 项目基本接口功能已经全部打通
  
- `student_mgmt_V0.1.1`：
  - 更新用户管理模块
  - 更新就业管理模块
  - 更新统计分析模块
  - 更新响应体格式规范，泛型中增加总数响应体类：`TotalResponse`
#### student_mgmt_V0.2.x

- `student_mgmt_V0.2.0`：
  - 更新用户管理模块
  - 添加异常处理器，使框架响应体格式一致：`code / message / data`
  - 集成初版前端代码
- `student_mgmt_V0.2.1`：
  - 修复部分查询分页接口BUG
  - 重新集成前端代码
  - 用户管理模块用户密码改为密文保存
- `student_mgmt_V0.2.2`：
  - 添加了鉴权中间件，支持两种凭证：Header（Swagger 里手填）或 Cookie（浏览器自动带）：`app.core.auth_middleware.py`
  - 增加了自定义 OpenAPI：让 Swagger 文档支持填 Bearer token：`app.core.custom_openapi.py`
- `student_mgmt_V0.2.3`：
  - 修复BUG：就业信息修改指定字段，不影响其他字段
  - 修复BUG：学生信息修改指定字段，不影响其他字段

