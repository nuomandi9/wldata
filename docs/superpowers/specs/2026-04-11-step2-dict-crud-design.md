# 步骤 2：字典管理 CRUD — 设计文档

## 一、目标

为烟草物流系统建立基础字典/主数据管理模块，包含人员、车辆、线路、零售客户、卷烟品牌五类字典的增删改查功能。采用工厂模式实现高度可复用架构，后续新增字典类型只需加配置。

## 二、字典范围

| 字典表 | 说明 | 唯一标识 |
|--------|------|----------|
| dict_person | 人员（驾驶员/配送员/员工） | id_card |
| dict_vehicle | 车辆 | plate_number |
| dict_route | 配送线路 | route_code |
| dict_customer | 零售客户 | customer_code |
| dict_cigarette | 卷烟品牌（基础信息，不含订购流水） | product_code |

**不在此步骤范围：** 卷烟订购数据（客户×品牌×周期×数量）属于业务流水，放步骤 3 Excel 导入处理。

## 三、数据模型

### 3.1 公共基类 DictBase

所有字典表继承此 mixin：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| is_active | Boolean | 启用/停用，默认 True |
| extra | JSONB | 扩展字段，默认 {} |
| created_at | DateTime(tz) | 创建时间，server_default |
| updated_at | DateTime(tz) | 更新时间，onupdate |

### 3.2 dict_person（人员）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| name | VARCHAR(50) | NOT NULL | 姓名 |
| id_card | VARCHAR(18) | UNIQUE, NOT NULL | 身份证号码 |
| birth_date | DATE | | 出生年月 |
| join_date | DATE | | 进入单位时间 |
| position | VARCHAR(50) | | 岗位 |
| department | VARCHAR(50) | | 所在部门 |
| employment_type | VARCHAR(30) | | 用工类型 |
| school | VARCHAR(100) | | 毕业院校 |
| degree | VARCHAR(30) | | 学位 |

### 3.3 dict_vehicle（车辆）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| plate_number | VARCHAR(20) | UNIQUE, NOT NULL | 车牌号 |
| model | VARCHAR(50) | | 车型 |
| driver_id | Integer FK → dict_person.id | | 驾驶员 |
| cargo_size | VARCHAR(30) | | 车厢大小 |
| vehicle_type | VARCHAR(20) | | 油车/新能源 |
| tank_or_battery_size | DECIMAL(10,2) | | 油箱(L)/电池容量(kWh) |
| mileage | DECIMAL(12,2) | | 行驶里程(km) |
| status | VARCHAR(20) | DEFAULT '在用' | 在用/停用/维修 |

### 3.4 dict_route（线路）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| route_code | VARCHAR(30) | UNIQUE, NOT NULL | 线路编码 |
| route_name | VARCHAR(100) | NOT NULL | 线路名称 |
| driver_id | Integer FK → dict_person.id | | 驾驶员 |
| deliverer_id | Integer FK → dict_person.id | | 送货员 |
| customer_count | Integer | | 客户数量 |
| delivery_count | Integer | | 送货数量 |
| delivery_time | VARCHAR(50) | | 送货时间 |
| settlement_time | VARCHAR(50) | | 客户结算时间 |
| response_time_calc | VARCHAR(100) | | 响应时间计算方式 |
| toll_fee | DECIMAL(10,2) | | 过路费 |
| delivery_cycle | VARCHAR(30) | | 送货周期 |

### 3.5 dict_customer（零售客户）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| customer_code | VARCHAR(30) | UNIQUE, NOT NULL | 客户编码 |
| customer_name | VARCHAR(100) | NOT NULL | 客户名称 |
| address | VARCHAR(200) | | 客户地址 |
| phone | VARCHAR(20) | | 电话 |
| settlement_method | VARCHAR(30) | | 结算方式 |
| department | VARCHAR(50) | | 所属部门 |
| route_id | Integer FK → dict_route.id | | 配送线路 |
| delivery_zone | VARCHAR(50) | | 配送域 |
| delivery_order | Integer | | 送货顺序 |
| market_type | VARCHAR(30) | | 市场类型 |

### 3.6 dict_cigarette（卷烟品牌）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| product_code | VARCHAR(30) | UNIQUE, NOT NULL | 商品编码 |
| product_name | VARCHAR(100) | NOT NULL | 商品名称 |
| brand_owner | VARCHAR(100) | | 品牌拥有者 |
| price_category | VARCHAR(30) | | 价类 |

### 3.7 外键关系

```
dict_person
    ↑ driver_id
    ├── dict_vehicle
    ↑ driver_id, deliverer_id
    ├── dict_route
    ↓ route_id（一条线路有多个客户）
    dict_customer

dict_cigarette（独立，通过业务流水与客户关联）
```

### 3.8 扩展机制

- **新增字段（少量）：** 写入 `extra` JSONB 列，前端配置中声明 extra 字段即可渲染
- **新增字段（正式）：** Alembic 迁移加列 + Model 加属性 + 前端配置加一行
- **新增字典类型：** Model + Schema + 工厂注册 + 前端配置文件 + 路由/菜单各一条

## 四、后端架构

### 4.1 通用 CRUD 工厂

`services/crud_factory.py` — 核心复用组件：

```python
def create_crud_router(
    model,              # SQLAlchemy Model 类
    create_schema,      # Pydantic 创建 Schema
    update_schema,      # Pydantic 更新 Schema
    list_schema,        # Pydantic 列表 Schema
    prefix: str,        # URL 前缀，如 "person"
    tag: str,           # API 文档标签，如 "人员管理"
    search_fields: list # 支持模糊搜索的字段名列表
) -> APIRouter:
```

自动生成 5 个标准端点：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/dict/{prefix} | 分页列表 + keyword 搜索 + is_active 过滤 |
| GET | /api/dict/{prefix}/{id} | 详情 |
| POST | /api/dict/{prefix} | 新增 |
| PUT | /api/dict/{prefix}/{id} | 修改 |
| DELETE | /api/dict/{prefix}/{id} | 软删除（is_active=False） |

### 4.2 分页与搜索规范

请求：
```
GET /api/dict/person?page=1&page_size=20&keyword=张&is_active=true
```

响应：
```json
{
  "items": [...],
  "total": 128,
  "page": 1,
  "page_size": 20
}
```

### 4.3 权限

所有 `/api/dict/*` 端点使用 `require_admin` 守卫，仅管理员可操作。
列表查询端点额外支持 `get_current_user`（operator 可查看但不可修改）。

### 4.4 外键下拉数据

新增轻量端点 `GET /api/dict/{prefix}/options`，返回 `[{id, label}]` 格式，供前端外键字段下拉选择器使用。

### 4.5 文件结构

```
backend/
├── models/
│   ├── system.py           # 已有 SysUser
│   ├── base.py             # NEW: DictBase mixin
│   └── dict.py             # NEW: 5 个字典 Model
├── schemas/
│   ├── auth.py             # 已有
│   ├── common.py           # NEW: PageParams, PageResult 通用分页
│   └── dict.py             # NEW: 5 组 Create/Update/List Schema
├── services/
│   ├── auth_service.py     # 已有
│   └── crud_factory.py     # NEW: 通用 CRUD 工厂
├── api/
│   ├── auth.py             # 已有
│   └── dict.py             # NEW: 注册 5 个字典路由
├── alembic/versions/
│   └── xxxx_create_dict_tables.py  # NEW: 迁移文件
└── main.py                 # 修改: 注册 dict router
```

## 五、前端架构

### 5.1 通用字典表格组件 DictTable.vue

配置驱动的万能组件，接收 props：
- `config` — 列定义、表单字段、API 路径
- 自动渲染：搜索框 + 新增按钮 + 数据表格 + 分页 + 新增/编辑弹窗

功能：
- 关键词搜索（debounce 300ms）
- 分页（前端切页时请求后端）
- 新增/编辑弹窗（根据配置自动生成表单字段）
- 软删除确认
- 外键字段渲染为下拉选择器（通过 /options 端点获取数据）
- 状态列渲染为开关或标签
- extra JSONB 字段支持（配置中声明即可渲染）

### 5.2 字典配置格式

```javascript
// dict-config/person.js
export default {
  api: '/api/dict/person',
  title: '人员管理',
  columns: [
    { prop: 'name', label: '姓名', required: true, searchable: true },
    { prop: 'id_card', label: '身份证号', required: true },
    { prop: 'birth_date', label: '出生年月', type: 'date' },
    { prop: 'join_date', label: '进入单位时间', type: 'date' },
    { prop: 'position', label: '岗位', searchable: true },
    { prop: 'department', label: '部门', searchable: true },
    { prop: 'employment_type', label: '用工类型' },
    { prop: 'school', label: '毕业院校' },
    { prop: 'degree', label: '学位' },
  ]
}
```

外键字段配置示例：
```javascript
{ prop: 'driver_id', label: '驾驶员', type: 'select', 
  options: { api: '/api/dict/person/options', labelField: 'name' } }
```

### 5.3 前端文件结构

```
frontend/src/
├── components/
│   └── DictTable.vue          # NEW: 通用字典表格组件
├── views/
│   ├── Login.vue              # 已有
│   ├── Home.vue               # 已有
│   └── dict/                  # NEW: 字典页面
│       ├── Person.vue
│       ├── Vehicle.vue
│       ├── Route.vue
│       ├── Customer.vue
│       └── Cigarette.vue
├── dict-config/               # NEW: 字典配置
│   ├── person.js
│   ├── vehicle.js
│   ├── route.js
│   ├── customer.js
│   └── cigarette.js
├── layout/
│   └── MainLayout.vue         # 修改: 增加字典管理子菜单
├── router/
│   └── index.js               # 修改: 增加字典路由
```

### 5.4 侧边栏菜单

```
首页
字典管理（可展开子菜单）
  ├── 人员管理
  ├── 车辆管理
  ├── 线路管理
  ├── 零售客户
  └── 卷烟品牌
```

### 5.5 美化风格

沿用已有的 Command Center 设计语言：
- 表格卡片白底 + 微阴影
- 琥珀金操作按钮
- 深色系弹窗标题栏
- 搜索框与已有 Login 页面风格一致

## 六、验证方案

1. 后端单元测试：对 CRUD 工厂生成的 person 端点做完整 CRUD 测试
2. Alembic 迁移成功，5 张表 + 外键创建正确
3. 前端 dev server 启动无报错
4. 浏览器测试：登录 → 字典管理 → 人员管理 → 新增/编辑/搜索/分页/停用 完整流程
5. 外键下拉：车辆页面选择驾驶员下拉正确加载人员列表
