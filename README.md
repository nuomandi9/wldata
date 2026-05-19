# 烟草物流数据管理系统

内网部署的物流数据管理 Web 应用，替代物流中心人员日常 Excel 统计工作。第一版聚焦字典管理、Excel 导入与校验、固定与灵活报表、Excel 导出。

## 技术栈

| 层 | 选型 |
|---|---|
| 前端 | Vue 3 · Element Plus · Vite · Pinia · Vue Router |
| 后端 | FastAPI · SQLAlchemy 2.0 (async) · Pydantic v2 |
| 数据库 | PostgreSQL 15 |
| 迁移 | Alembic |
| 部署 | Docker Compose (nginx + backend + postgres) |

## 快速开始

### 数据库
```powershell
docker-compose up -d postgres
```

### 后端（在 `backend/` 下执行）
```powershell
python -m venv venv
./venv/Scripts/Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python ../scripts/create_admin.py    # 初始化 admin / admin123
uvicorn main:app --reload --port 8000
```

### 前端（在 `frontend/` 下执行）
```powershell
npm install
npm run dev    # http://localhost:3000, /api 反向代理到 :8000
```

### 一键启动
```powershell
docker-compose up -d
```
nginx 暴露在 80 端口，前端构建产物经由 nginx 提供，`/api/*` 转发到后端。

## 项目结构

```
backend/
  api/               FastAPI 路由
  models/            SQLAlchemy ORM（dict 类共享 DictBase 混入）
  schemas/           Pydantic v2 Create/Update/Out 三件套
  services/          业务逻辑，含通用 CRUD 工厂
  middleware/        JWT 鉴权
  alembic/           数据库迁移
  tests/             pytest + httpx
frontend/
  src/
    components/      DictTable 等通用组件
    dict-config/     各字典页面的列定义（驱动 DictTable）
    views/           页面（多为 DictTable 的薄包装）
    api/             axios 实例与拦截器
    stores/          Pinia
nginx/               生产环境反向代理配置
scripts/             一次性脚本（如建管理员账号）
docs/                设计文档
```

## 架构要点

- **后端 CRUD 工厂**：`services/crud_factory.py` 提供 `create_crud_router(...)`，新增字典只需定义 model + schema 并在 `api/dict.py` 调用工厂一次，无需手写路由。删除为软删（`is_active = False`），关键字搜索基于 `search_fields` 做 ILIKE OR。
- **DictBase 混入**：所有字典表共享 `id / is_active / extra (JSONB) / created_at / updated_at`，非确定性字段写 `extra` 而非加列。
- **前端配置驱动**：`components/DictTable.vue` 是通用增删改查表格，各字典页面用 `dict-config/*.js` 的列声明驱动。新增字典页面 = 新建 config + 三行 view + 路由 + 菜单。
- **鉴权**：JWT，写操作要求 `admin` 角色（`middleware/auth.py::require_admin`）。

详见 [`CLAUDE.md`](CLAUDE.md) 与 [`docs/superpowers/specs/`](docs/superpowers/specs/)。

## 测试

后端集成测试用一个独立的 `tobacco_logistics_test` 数据库，`conftest.py` 会按测试创建/销毁全部表。

```powershell
cd backend
pytest
pytest tests/test_dict_api.py::test_name -v   # 单个用例
```

## 许可证

专有软件，保留所有权利。详见 [`LICENSE`](LICENSE)。
