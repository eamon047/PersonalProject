# 🚀 求职平台 MVP(Minimum Viable Product) (Job Platform)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![SQLModel](https://img.shields.io/badge/SQLModel-0.0.14+-orange.svg)](https://sqlmodel.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📖 项目概述

这是一个**求职平台MVP版本**，采用表单投递方式（而非文件上传），专注于展示后端开发的核心能力：

- 🏗️ **数据建模** - 完整的数据模型设计
- 🔐 **认证授权** - JWT + 角色权限系统
- 💾 **数据库设计** - SQLModel + SQLite，支持关系查询
- 📊 **业务逻辑** - 职位发布、投递管理、状态流转
- 🔍 **筛选查询** - 多条件筛选和分页
- 🧪 **测试覆盖** - 完整的测试体系
- 🚀 **部署就绪** - 支持容器化部署

## 🎯 核心功能

### 👥 用户角色
- **候选人 (Candidate)** - 投递职位、管理个人资料
- **企业方 (CompanyOwner)** - 发布职位、处理投递
- **管理员 (Admin)** - 只读权限，查看全量数据

### 🏢 业务流程
1. **企业发布职位** → 设置职位信息、薪资、地点
2. **候选人投递** → 填写表单、提交申请
3. **企业筛选** → 查看投递、处理申请状态
4. **状态管理** → 投递状态流转和记录

### 🔍 筛选功能
- **职位方向**: `frontend` | `backend` | `fullstack`
- **工作地点**: `tokyo` | `osaka`
- **薪资范围**: 自定义区间筛选
- **分页查询**: 支持分页和排序

## 🏗️ 技术架构

### 核心技术栈
```
FastAPI + SQLModel + SQLite + JWT + Pydantic
```

### 技术选型说明
- **FastAPI**: 现代、高性能的Python Web框架
- **SQLModel**: 结合SQLAlchemy和Pydantic的优势
- **SQLite**: MVP阶段使用，便于部署和演示
- **JWT**: 安全的用户认证系统
- **Pydantic**: 强大的数据验证和序列化

### 项目结构
```
app/
├── main.py              # 应用入口和路由挂载
├── config.py            # 配置管理
├── db.py               # 数据库连接和初始化
├── security.py         # JWT认证和密码哈希
├── deps.py             # 依赖注入和权限检查
├── admin_init.py       # 管理员账号初始化
├── models/             # 数据模型
│   ├── user.py         # 用户模型
│   ├── company.py      # 公司模型
│   ├── job.py          # 职位模型
│   ├── application.py  # 投递模型
│   └── candidate_profile.py  # 候选人资料
├── schemas/            # 请求响应模型
│   ├── auth.py         # 认证相关
│   ├── user.py         # 用户相关
│   ├── company.py      # 公司相关
│   ├── job.py          # 职位相关
│   ├── application.py  # 投递相关
│   └── profile.py      # 资料相关
├── routers/            # API路由
│   ├── auth.py         # 认证路由
│   ├── admin.py        # 管理员路由
│   ├── profile.py      # 资料管理
│   ├── companies.py    # 公司管理
│   ├── jobs.py         # 职位管理
│   └── applications.py # 投递管理
└── tests/              # 测试文件
```

## 🚀 快速开始

### 环境要求
- Python 3.8+
- pip 或 poetry

### 1. 克隆项目
```bash
git clone <your-repository-url>
cd PersonalProject
```

### 2. 创建虚拟环境
```bash
# 使用 venv
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 环境配置
```bash
# 复制环境变量模板
cp env.example .env

# 编辑 .env 文件，设置你的配置
# 特别注意修改 JWT_SECRET 和管理员密码
```

### 5. 运行应用
```bash
# 启动开发服务器
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# 或者使用项目提供的启动命令
source venv/bin/activate && uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 6. 访问应用
- **API文档**: http://127.0.0.1:8000/docs
- **ReDoc文档**: http://127.0.0.1:8000/redoc

## 📚 API 文档

### 🔐 认证接口

#### 用户注册
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password"
}
```

#### 用户登录
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password"
}
```

### 👤 用户资料

#### 获取个人资料
```http
GET /profile/me
Authorization: Bearer <your_jwt_token>
```

#### 更新个人资料
```http
PUT /profile
Authorization: Bearer <your_jwt_token>

{
  "full_name": "张三",
  "age": 25,
  "gender": "male",
  "phone": "+86-138-xxxx-xxxx",
  "intro": "我是一名后端开发工程师"
}
```

### 🏢 公司管理

#### 创建公司
```http
POST /companies
Authorization: Bearer <your_jwt_token>

{
  "name": "科技公司",
  "website": "https://example.com"
}
```

#### 获取我的公司
```http
GET /companies/me
Authorization: Bearer <your_jwt_token>
```

### 💼 职位管理

#### 发布职位
```http
POST /jobs
Authorization: Bearer <your_jwt_token>

{
  "title": "Python后端工程师",
  "position": "backend",
  "based_in": "tokyo",
  "description": "负责公司核心业务的后端开发",
  "salary": 50
}
```

#### 获取职位列表
```http
GET /jobs?position=backend&based_in=tokyo&page=1&limit=20
```

#### 获取职位详情
```http
GET /jobs/{job_id}
```

### 📝 投递管理

#### 投递职位
```http
POST /applications
Authorization: Bearer <your_jwt_token>

{
  "job_id": 1,
  "application_note": "我对这个职位很感兴趣",
  "expected_salary": 45
}
```

#### 获取我的投递
```http
GET /me/applications
Authorization: Bearer <your_jwt_token>
```

#### 取消投递
```http
PATCH /applications/{application_id}/cancel
Authorization: Bearer <your_jwt_token>
```

### 🔍 筛选查询

#### 职位筛选参数
- `position`: `frontend` | `backend` | `fullstack`
- `based_in`: `tokyo` | `osaka`
- `salary_min`: 最低薪资（万日元）
- `salary_max`: 最高薪资（万日元）
- `page`: 页码（默认1）
- `limit`: 每页数量（默认20，最大100）

#### 筛选示例
```http
# 筛选东京地区的后端职位，薪资40-60万日元
GET /jobs?position=backend&based_in=tokyo&salary_min=40&salary_max=60

# 分页查询
GET /jobs?page=2&limit=10
```

## 🗄️ 数据模型

### 核心实体关系
```
User (用户)
├── 1:1 Company (公司) - 一个用户最多拥有一家公司
├── 1:1 CandidateProfile (候选人资料)
└── 1:N Application (投递记录)

Company (公司)
├── N:1 User (拥有者)
└── 1:N Job (职位)

Job (职位)
├── N:1 Company (所属公司)
└── 1:N Application (投递记录)

Application (投递)
├── N:1 User (候选人)
└── N:1 Job (目标职位)
```

### 关键设计特点
- **快照机制**: 投递时保存候选人资料快照，确保数据一致性
- **唯一约束**: 防止重复投递 `(user_id, job_id)`
- **状态管理**: 完整的投递状态流转
- **权限控制**: 基于角色的数据访问控制

## 🧪 测试

### 运行测试
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_auth.py

# 运行测试并显示覆盖率
pytest --cov=app

# 运行测试并生成HTML报告
pytest --cov=app --cov-report=html
```

### 测试结构
```
tests/
├── test_auth.py        # 认证测试
├── test_profile.py     # 资料管理测试
├── test_companies.py   # 公司管理测试
├── test_jobs.py        # 职位管理测试
└── test_applications.py # 投递管理测试
```

## 🚀 部署

### 生产环境配置
```bash
# 修改 .env 文件
APP_ENV=production
DATABASE_URL=postgresql://user:password@localhost/dbname
JWT_SECRET=your-super-secure-production-secret
JWT_EXPIRE_MINUTES=1440  # 24小时
```


### 环境变量说明
| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `APP_ENV` | 应用环境 | `dev` |
| `DATABASE_URL` | 数据库连接字符串 | `sqlite:///./app.db` |
| `JWT_SECRET` | JWT密钥 | `your-super-secret-jwt-key-change-in-production` |
| `JWT_EXPIRE_MINUTES` | JWT过期时间(分钟) | `60` |
| `ADMIN_EMAIL` | 管理员邮箱 | `eamonzhaowork@gmail.com` |
| `ADMIN_PASSWORD` | 管理员密码 | `zym1010.` |

## 🔧 开发指南

### 代码规范
- 使用 **Black** 进行代码格式化
- 遵循 **PEP 8** Python代码规范
- 使用 **Type Hints** 进行类型注解

### 提交规范
```
feat: 添加新功能
fix: 修复bug
docs: 更新文档
style: 代码格式调整
refactor: 代码重构
test: 添加测试
chore: 构建过程或辅助工具的变动
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情