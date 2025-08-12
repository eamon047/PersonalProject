# 求职平台（MVP）技术规格（表单投递版）

> 目标：两三周内完成、可部署演示、突出后端能力（建模、鉴权、事务、验证、分页、部署）。**取消文件上传，使用在线表单投递**。

---

## 0) 范围与非目标

**范围（MVP）**

- 角色：候选人（Candidate）、企业方（CompanyOwner）、管理员只读（Admin）。
- 主流程：企业发职位 → 候选人用**表单**投递 → 企业筛选（`applied → shortlisted/rejected`）。
- 筛选：\*\*position（职位方向）/ salary（工资）/ based\_in（工作地点）\*\*三项；`position ∈ {frontend, backend, fullstack}`；`based_in` 对外 API 使用 `tokyo|osaka`，后端存储使用代码 `0=tokyo, 1=osaka`。
- 管理员：单一只读管理员（通过 seed 创建），仅查看全量数据。

**非目标（MVP 不做）**

- 邮件/IM 通知、第三方登录、复杂搜索（地点/标签/排序算法）
- 简历 PDF 上传与解析、AI 职位推荐（下阶段加）
- 多公司管理员、复杂权限审批、CMS

---

## 1) 角色与权限（极简）

- **User**：统一用户模型，登录后可拥有：
  - **Candidate**：默认具备，允许投递。
  - **CompanyOwner**：可创建 1 家公司并管理其职位/投递。
- **Admin（只读）**：seed 超级用户，只能 GET 查看用户/公司/职位/投递列表与详情，无写权限。

权限要点：

- 只有**职位所属公司的拥有者**可创建/编辑/关闭该职位、查看与处理该职位的投递。
- 候选人仅能查看/管理自己的 Profile 与投递记录。
- `(user_id, job_id)` 在 Application 上全局唯一（防重复投递）。

---

## 2) 数据模型（SQLite/PG 皆可，MVP 推荐 SQLite）

> JSON 字段建议使用 SQLite JSON1/PG JSONB；后续若统计需求增加，可拆表。

### User

- `id` (PK)
- `email` (unique, not null)
- `password_hash` (not null)
- `created_at` (datetime, default now)

### Company

- `id` (PK)
- `owner_id` (FK → User.id, unique per owner，**一个用户最多 1 家公司**)
- `name` (not null)
- `website` (nullable)
- `created_at` (datetime)

**索引**：`idx_company_owner_id`

### Job

- `id` (PK)
- `company_id` (FK → Company.id)
- `title` (not null, 1..120)
- `position` (enum: `frontend|backend|fullstack`)
- `based_in_code` (tinyint enum: **0=tokyo, 1=osaka**)
- `[API 映射] based_in`（只读虚拟字段：对外返回 `tokyo|osaka`；查询参数亦支持 `based_in=tokyo|osaka` 或 `based_in=0|1`）
- `description` (TEXT, ≤ 10k)
- `salary_min` (int ≥0)
- `salary_max` (int ≥ salary\_min)
- `status` (enum: `open|closed`, default `open`)
- `created_at` (datetime)
- **[后续]** `max_hires` (int ≥0，可选) 或 `max_applications`（收到投递达到上限时自动关闭）

**索引**：`idx_job_company_id`, `idx_job_status_created_at`, `idx_job_salary_min_max`, `idx_job_position`, `idx_job_based_in_code`

### CandidateProfile（候选人可编辑的常驻资料）

> 按你的精简诉求，MVP 仅保留投递需要的最小字段；扩展项放入 [后续]。

- `user_id` (PK = FK → User.id)
- `full_name` (not null, 1..80)
- `age` (int 14..80)
- `gender` (enum: `male|female|other|unspecified`)
- `phone` (nullable，正则校验)
- `intro` (TEXT，≤ 1000，个人介绍)
- **[后续]**：`links_json` / `skills_json` / `education_json` / `experience_json` / `experience_years`
- `updated_at` (datetime)

### Application（每次投递的“快照”）

- `id` (PK)
- `user_id` (FK → User.id)
- `job_id` (FK → Job.id)
- `status` (enum: `applied|cancelled_by_candidate|shortlisted|rejected`, default `applied`)  // MVP 可先只用 `applied|cancelled_by_candidate`，其余为 [后续]
- `note` (TEXT, nullable)
- `expected_salary` (int, nullable)
- `answers_json` (JSON, nullable)  // 职位附加问答，MVP 可为空
- `profile_snapshot_json` (JSON, not null) // 投递时拷贝的 CandidateProfile
- `created_at` (datetime)

**唯一约束**：`uq_application_user_job (user_id, job_id)`

---

## 3) 业务流程（表单版）

**A. 候选人完善资料（可选但推荐）**

1. `PUT /profile` 写入/更新 `CandidateProfile`
2. `GET /profile/me` 查看当前资料

**B. 企业发布职位**

1. 若无公司：`POST /companies`
2. `POST /jobs` 创建职位（`title/position/based_in/description/salary_min/max`）

**C. 候选人投递（无文件）**

1. `POST /applications`：Body 含 `job_id`, `note?`, `expected_salary?`, `answers?`
   - 服务端在写入 Application 前，读取当前 `CandidateProfile` 并深拷贝到 `profile_snapshot_json`
2. `GET /me/applications`：查看自己的投递列表
3. `PATCH /applications/{id}/cancel`：**候选人主动取消投递**（状态置为 `cancelled_by_candidate`）

**D. 企业处理投递**

1. `GET /company/applications?job_id=` 查看该职位的所有投递（含快照）
2. `PATCH /applications/{id}/status`：`applied → shortlisted/rejected`

**E. 管理员只读**

- `GET /admin/users|companies|jobs|applications` 分页只读

---

## 4) API 设计（路由清单）

> 统一响应错误结构：`{"detail": "..."}`；分页：`{items, page, limit, total}`。

### Auth

- `POST /auth/register`\
  Body: `{ email, password }` → 201
- `POST /auth/login`\
  Body: `{ email, password }` → 200 `{ access_token, token_type }`

### Profile（候选人）

- `GET /profile/me` → 200 `CandidateProfile`
- `PUT /profile` → 200 `CandidateProfile`

**CandidateProfile 示例（精简版）**

```json
{
  "full_name": "Zhao Eamon",
  "age": 23,
  "gender": "unspecified",
  "phone": "+81-90-xxxx-xxxx",
  "intro": "Hi, I'm focusing on FastAPI backend and NLP."
}
```

### Company（企业）

- `POST /companies` → 201\
  Body: `{ name, website? }`（若 owner 已有公司 → 409）
- `GET /companies/me` → 200 `{ company, stats }`

### Jobs（职位）

- `POST /jobs`（公司拥有者） → 201 `{ id, ... }`
- `GET /jobs?position=&based_in=&salary_min=&salary_max=&page=&limit=` → 200 列表（默认 `created_at desc`）\
  说明：`position ∈ frontend|backend|fullstack`；`based_in` 支持 `tokyo|osaka` 或 `0|1`（内部映射到 `based_in_code`）。
- `GET /jobs/{id}` → 200 详情
- `PATCH /jobs/{id}`（公司拥有者） → 200（可改：title/category/description/salary）
- `PATCH /jobs/{id}/close` → 200（status=closed）

**创建职位示例**

```json
{
  "title": "Backend Engineer (Python)",
  "position": "fullstack",
  "based_in": "tokyo",
  "description": "Build REST APIs with FastAPI.",
  "salary_min": 400,
  "salary_max": 700
}
```

### Applications（投递）

- `POST /applications` → 201\
  Body: `{ job_id, note?, expected_salary?, answers? }` Response（含快照摘要）:

```json
{
  "id": 101,
  "status": "applied",
  "created_at": "2025-08-10T02:15:00Z",
  "profile_snapshot": {"full_name":"Zhao Eamon","age":23,"gender":"unspecified","phone":"+81-90-xxxx-xxxx","intro":"I love backend."}
}
```

- `GET /me/applications` → 200（仅本人）
- `PATCH /applications/{id}/cancel` → 200 `{ status: "cancelled_by_candidate" }`（仅本人，幂等）
- `GET /company/applications?job_id=` → 200（仅职位所属公司）
- **[后续]** `PATCH /applications/{id}/status`（公司→`shortlisted|rejected`）

### Admin（只读）

- `GET /admin/users`
- `GET /admin/companies`
- `GET /admin/jobs`
- `GET /admin/applications`

---

## 5) 校验与业务规则

**数值与单位**

- `salary_min/max` 单位：例如「千日元/月」或「万日元/年」——在 README 写死；校验：`0 ≤ min ≤ max`。

**唯一性与幂等**

- Application `(user_id, job_id)` 唯一，重复投递返回 409。

**可见性**

- 候选人仅能访问自己的 Profile 与 Applications。
- 公司只能访问自己公司 Job 的 Applications。

**快照一致性**

- `POST /applications` 时，将 `CandidateProfile` 当前状态深拷贝至 `profile_snapshot_json`；后续候选人再修改 Profile 不影响已投简历内容。

**分页**

- 默认 `page=1, limit=20`，上限 `limit≤100`。

**输入校验**

- `links` 中 URL 校验；`skills` 去重、每项 1..30 字；电话简单正则（兼容国际区号）。

---

## 6) 列表与筛选（极简）

- `GET /jobs?position=&based_in=&salary_min=&salary_max=`：
  - position：精确匹配（`frontend|backend|fullstack`）
  - based\_in：`tokyo|osaka` 或 `0|1`；内部映射到 `based_in_code`（0=tokyo, 1=osaka）
  - 工资：闭区间匹配（单位见 README）
- 默认排序：`created_at desc`。
- 列表摘要字段：`id, title, company_name, position, based_in, salary_min, salary_max, created_at`。

---

## 7) 项目结构（建议）

```
app/
  main.py
  db.py
  deps.py                 # 当前用户、权限依赖
  models/
    user.py company.py job.py application.py candidate_profile.py
  schemas/
    auth.py user.py company.py job.py application.py profile.py common.py
  routers/
    auth.py companies.py jobs.py applications.py profile.py admin.py
  services/
    applications.py       # 生成快照、状态机
  security.py             # JWT + bcrypt
  config.py               # pydantic-settings 读 .env
  utils/
    pagination.py validators.py errors.py
migrations/
tests/
README.md
```

---

## 8) 环境与依赖

**requirements.txt（建议）**

```
fastapi
uvicorn[standard]
sqlmodel
SQLAlchemy
alembic
python-jose[cryptography]
passlib[bcrypt]
pydantic-settings
python-multipart
httpx
pytest
```

**.env 示例**

```
APP_ENV=dev
DATABASE_URL=sqlite:///./app.db
JWT_SECRET=change_me
JWT_EXPIRE_MINUTES=60
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=ChangeMe123!
```

---

## 9) 种子数据与演示

- 管理员：从 `.env` 读取创建。
- 公司：2 家（示例 A/B）。
- 职位：4 条（frontend/backend 各 2）。
- 候选人：2 个 demo 账号 + 典型 `CandidateProfile`。
- 演示脚本：
  1. 注册/登录 → `PUT /profile` → `POST /applications`
  2. 切换公司 → `GET /company/applications` → `PATCH status`

---

## 10) 测试清单（最小但有力）

- Auth：注册/登录（成功/失败）
- Profile：PUT 校验（年龄区间、性别枚举、电话正则），GET 正确返回
- Company：创建（成功；已有公司返回 409）
- Jobs：
  - 创建/编辑/关闭（权限与工资区间校验）
  - position 三类校验（frontend/backend/fullstack）
  - based\_in 接受 `tokyo|osaka` 或 `0|1`；内部映射到 `based_in_code`
- Applications：
  - 首投成功、重复投递 409
  - 取消：`PATCH /applications/{id}/cancel` 幂等；取消后不可再次取消
  - 快照保持（修改 Profile 后，已投记录不变）
  - 公司仅能看自己职位投递；越权 403
  - **[后续]** 状态机：`applied→shortlisted/rejected`，非法状态 422
- 列表与分页：position/based\_in/工资区间组合过滤、limit 上限

---

## 11) 非功能性

- 安全：JWT、密码哈希（bcrypt）、CORS（允许本地前端来源）
- 错误：统一 `{"detail":"..."}`；日志记录关键事件（创建职位、投递、改状态）
- 部署：Dockerfile +（可选）docker-compose（app+db），Render/Railway 均可

---

## 12) 迭代路线图

1. MVP（本规格：表单投递 + 取消功能 + 三项过滤）
2. 简单关键词搜索（title LIKE，多字段 OR）
3. **[后续] 招募人数上限**：`max_hires` 或 `max_applications` + 自动关闭职位
4. **[后续] 企业端状态机**：`shortlisted/rejected/hired` + 审计
5. **[后续] AI 简历解析与职位匹配**：`/ai/parse_resume` → 填充 `CandidateProfile`；`/match?profile_id=` 返回匹配职位（可解释）

---

## 13) Open Questions（待确认）

- 工资单位：定为「千日元/月」还是「万日元/年」？（README 固定）
- based\_in 后续是否加入 `remote` 或其他城市？若加入，是否继续采用 0/1/2… 代码映射？
- 公司端最简状态机（`shortlisted|rejected`）何时纳入 MVP？（目前放入 [后续]）
- 招募人数上限采用 `max_hires`（录用数达阈值自动关闭）还是 `max_applications`（投递数達阈值即关闭）？
- require_company_owner - 公司拥有者`权限作用：确保只有拥有公司的用户才能调用公司相关接口`
- ensure_job_owned - 职位所有权检查 `作用：确保用户只能操作自己公司的职位`


## 14) 个人记录
激活环境(相对于conda的方式更轻量)
source venv/bin/activate

第一步：基础配置
创建 requirements.txt - 定义项目依赖
创建环境变量文件 - 配置数据库、JWT等
创建配置文件 - 读取环境变量

第二步：数据库设置
创建数据库连接 - 设置SQLModel和数据库引擎
创建数据模型 - 一个一个创建User、Company、Job等模型

第三步：认证和安全
创建JWT认证 - 用户登录注册功能
创建权限依赖 - 用户权限管理

第四步：API路由
创建Pydantic schemas - 请求响应模型
创建API路由 - 一个一个实现各个功能模块

第五步：测试和部署
创建测试 - 单元测试
创建部署配置 - Docker等