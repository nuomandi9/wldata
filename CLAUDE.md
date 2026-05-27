# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project context

“企业”物流数据管理系统 — internal LAN web app for an enterprise logistics center (~8 users) that replaces Excel-based reporting workflows. First version focuses on data dictionaries, Excel import + validation, fixed and ad-hoc reports, and Excel export. Design docs live under `docs/superpowers/specs/`.

Stack: Vue 3 + Element Plus + Vite (frontend) · FastAPI + SQLAlchemy 2.0 async + Pydantic v2 (backend) · PostgreSQL 15 · Alembic migrations · Docker Compose for deployment.

## Common commands

All commands assume PowerShell on Windows. Working dirs matter — alembic and uvicorn must run from `backend/` because `alembic.ini` uses `prepend_sys_path = .` and imports like `from database import Base` are root-relative.

### Backend (run from `backend/`)
- Activate venv: `./venv/Scripts/Activate.ps1`
- Install deps: `pip install -r requirements.txt`
- Dev server: `uvicorn main:app --reload --port 8000`
- Migrate to head: `alembic upgrade head`
- New autogen migration: `alembic revision --autogenerate -m "message"`
- Run all tests: `pytest` (requires a separate `tobacco_logistics_test` database on localhost; `conftest.py` creates/drops all tables per test)
- Single test: `pytest tests/test_dict_api.py::test_name -v`
- Seed initial admin (run once after `alembic upgrade head`): `python ../scripts/create_admin.py` → creates `admin / admin123`

### Frontend (run from `frontend/`)
- Install: `npm install`
- Dev server: `npm run dev` (port 3000; Vite proxies `/api` → `http://localhost:8000`)
- Production build: `npm run build` (output in `dist/`, served by nginx in prod)

### Full stack via Docker
- `docker-compose up -d` brings up postgres, backend, frontend build, and nginx (port 80). Set `SECRET_KEY` env var before bringing up in any non-local context.

## Architecture

### Backend: CRUD-factory pattern for dictionaries

The five dictionary domains (person, vehicle, route, customer, cigarette) all go through one generic generator instead of hand-rolled routers.

- `services/crud_factory.py::create_crud_router` builds a full `APIRouter` for any (model, create_schema, update_schema, out_schema) tuple. It produces: `GET /` (paginated list with `keyword` search + `is_active` filter), `GET /options` (active rows as `{id, label}` for FK dropdowns), `GET /{id}`, `POST /`, `PUT /{id}`, `DELETE /{id}`.
- `api/dict.py` is just five `create_crud_router(...)` calls wired into one parent `APIRouter`. **To add a new dictionary type:** add the model, the Create/Update/Out schemas, and one factory call here — do not write a new router by hand.
- **Soft delete** is the convention: `DELETE` sets `is_active = False`, it never removes rows.
- **Search** is a case-insensitive ILIKE OR across the `search_fields` list passed to the factory; `%` and `_` are escaped so user input cannot widen the pattern.
- **Auth**: list/get use `get_current_user` (any authenticated user); create/update/delete use `require_admin`. Both helpers live in `middleware/auth.py`.

### Backend: data model layout

- `models/base.py::DictBase` is the **mixin** every dict table inherits (id, `is_active`, `extra` JSONB, `created_at`, `updated_at`). New dict tables should `class Foo(DictBase, Base): __tablename__ = "dict_foo"` to stay consistent with the factory's assumptions (it reads `model.is_active` and `model.id` directly).
- `extra: JSONB` is the project's documented escape hatch for fields that don't justify a column yet — prefer it over schema churn for one-off attributes.
- `models/system.py` holds the auth table (`sys_user`) which deliberately does **not** use `DictBase` (no `is_active`/`extra` semantics; different lifecycle).
- `alembic/env.py` does `import models` (the package `__init__`) so every model file must be re-exported there for autogenerate to see it.

### Backend: schemas and async DB

- Pydantic v2 with `model_config = {"from_attributes": True}` on every `*Out` schema — the factory calls `out_schema.model_validate(orm_instance)`.
- DB is fully async (`asyncpg` + `AsyncSession`). All endpoints `async def`, all queries use `await db.execute(select(...))`. `IntegrityError` is caught in the factory and surfaced as HTTP 409.

### Backend: Excel import pipeline (`biz_*` tables)

Business data enters through a **stateless** import flow — the same xlsx is uploaded for both preview and commit, and the commit step re-validates server-side, so dict changes between the two calls cannot smuggle bad data through and the client can never supply trusted FK ids.

- `services/import_templates.py` declares each `ImportTemplate` (target model + `ImportColumn`s). A column may carry a `Lookup` (resolve a human-readable key like 车牌号/线路编码 to a dict-table FK id) and `warn_min`/`warn_max` numeric thresholds. **To add an importable table:** add the model + one `ImportTemplate` to `TEMPLATES`.
- `services/excel_parser.py` reads headers→fields (openpyxl read_only); `services/import_validator.py` runs the three-stage pipeline with batch-level lookup caching (a 1000-row import referencing 20 vehicles hits the DB 20×, not 1000×).
- Validation levels per design §5.3: **BLOCK** (type error / missing required / lookup miss / inactive dict row) is never insertable; **WARN** (numeric out of range) is insertable only with a per-row `warn_notes`. `api/import_excel.py` exposes `GET /templates`, `POST /{key}/preview`, `POST /{key}/commit`.

### Backend: report querying (`sys_report_template`)

Fixed reports are **DB-stored templates**, not hand-written endpoints. A `ReportTemplate` row holds an admin-authored, parameterized `sql_template` (`:name` placeholders), a `params_schema`, and a `columns_schema`.

- `services/report_executor.py` is the **SQL trust boundary**: the `sql_template` is admin-trusted, but user params are coerced to declared types and bound via `text()` — never string-formatted. Undeclared keys are dropped. Optional FK params use `CAST(:p AS INTEGER)` in the SQL so asyncpg can resolve a `NULL` bind's type. Pagination wraps the template as `SELECT * FROM (...) AS _r LIMIT/OFFSET`; templates must therefore contain **no LIMIT/OFFSET** and **should** carry a stable total ORDER BY.
- Exports are capped at `MAX_EXPORT_ROWS` (50000) — the output-side analogue of the §十 50MB upload limit. `services/excel_exporter.py` renders xlsx via openpyxl.
- `api/report.py` exposes `GET /templates`, `GET /templates/{key}`, `POST /{key}/execute` (paginated JSON), `POST /{key}/export` (xlsx download). **SQL is never returned to clients.** Seed initial templates with `python ../scripts/seed_reports.py` (idempotent).

### Backend: audit log + user management (`sys_audit_log`, `sys_user`)

- `services/audit_service.py::record()` stages a `SysAuditLog` row in the **caller's** session and does NOT commit — the audited write and its audit row commit atomically. Read-only endpoints that audit (login) commit themselves. **`detail` is always a pre-built dict; never pass a raw request body** (that is how plaintext passwords leak). `scrub()` is the defense-in-depth net: it drops keys containing password/passwd/pwd/secret/token and ISO-stringifies dates (asyncpg JSONB has no date codec). The per-action `detail` shape is documented authoritatively in that module's docstring — keep it current when adding actions.
- Audited events: `login` (successful only), `dict.create/update/delete` (wired **once** in `crud_factory.py` so all 5 domains audit consistently — create uses `flush()` to get the id, and the whole `flush→audit→commit` is one try/except so a dup still maps to 409), and `import.commit_warn` (one row per forced commit, listing forced rows + notes — design §5.3).
- `api/audit.py`: `GET /api/audit/logs` is **admin-only, read-only** (append-only trail, no mutate endpoints), paginated with username/action/date filters.
- `api/users.py` (admin-only): list/create/update(role+is_active)/reset-password, **no hard delete**. Two guards: you cannot disable/demote yourself, and the last active admin cannot be disabled/demoted (`_is_last_active_admin`). `UserOut` never includes `password_hash`. Given `require_admin`, the only reachable zero-admin path is self-targeting, so the self-guard is the load-bearing one; the last-admin guard is defense-in-depth.
- Frontend `系统管理` submenu (`views/system/AuditLog.vue`, `Users.vue`) is gated both by `isAdmin` in `MainLayout.vue` and `meta.adminOnly` in the router `beforeEach`.

### Frontend: config-driven dictionary UI

The frontend deliberately mirrors the backend's factory pattern.

- `src/components/DictTable.vue` is one **generic** table component handling search (debounced), pagination, add/edit dialog with per-column input types (`date`/`number`/`enum`/`select`/text), required-field validation, and soft delete via popconfirm.
- `src/dict-config/*.js` files declare each domain's columns (`prop`, `label`, `width`, `required`, `searchable`, `type`, `choices`, `options.api` for FK lookups) and the backend `api` prefix.
- `src/views/dict/*.vue` are three-line wrappers: import config, pass to `<DictTable :config="config" />`. **To add a new dictionary view:** create the config file, create the wrapper view, register the route in `src/router/index.js`, and add a menu item in `src/layout/MainLayout.vue` — do not duplicate the table component.
- FK columns of `type: 'select'` auto-fetch their options from `${options.api}` (which on the backend is the factory-generated `/options` endpoint) and display the human-readable `label` in the table instead of the raw id.

### Frontend: auth + request layer

- `src/api/request.js` is the only axios instance — it auto-attaches `Bearer <token>` from `localStorage` and globally handles 401 (clear token, route to `/login`) and 403 (toast). Components should never construct their own axios.
- `src/router/index.js` gates all routes by checking `localStorage.token` + lazily fetching `userStore.fetchUser()` on first navigation; routes marked `meta: { public: true }` (only `/login`) bypass this.
- `src/stores/user.js` (Pinia) caches the current user info.

## Conventions worth knowing

- Response shape for paginated lists is `PageResult[T]` from `schemas/common.py` — `{ items, total, page, page_size }`. The frontend `DictTable` reads `data.items` / `data.total` directly.
- Backend module imports are root-relative (`from database import ...`, `from models.dict import ...`), not package-relative. Keep new files consistent or imports will break.
- Error messages returned to users are Chinese; UI strings in components are Chinese. Match this for new strings.
- Code review fixes recently consolidated into `services/crud_factory.py` (see commit `8057eb8`) — when extending the factory, check that commit for the contract it now enforces (e.g., `%`/`_` escaping in keyword search).
