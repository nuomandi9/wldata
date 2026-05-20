"""Seed the initial three fixed reports for the delivery_record table.

Run once after `alembic upgrade head`:
    cd backend && python ../scripts/seed_reports.py

Re-running is idempotent — existing keys are skipped.
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from sqlalchemy import select
from database import async_session
from models.report import ReportTemplate


# ── SQL templates ─────────────────────────────────────────────────────────────
# All parameters are bound via SQLAlchemy text() — never interpolated.
# Optional FK params use CAST(:p AS INTEGER) so asyncpg can resolve NULL types.

DELIVERY_DETAIL_SQL = """
SELECT
  dr.record_date AS record_date,
  v.plate_number AS plate_number,
  dp.name AS driver_name,
  dpd.name AS deliverer_name,
  dro.route_code AS route_code,
  dro.route_name AS route_name,
  dr.customer_count AS customer_count,
  dr.delivery_count AS delivery_count,
  dr.remark AS remark,
  dr.warn_notes AS warn_notes
FROM biz_delivery_record dr
LEFT JOIN dict_vehicle v ON v.id = dr.vehicle_id
LEFT JOIN dict_person dp ON dp.id = dr.driver_id
LEFT JOIN dict_person dpd ON dpd.id = dr.deliverer_id
LEFT JOIN dict_route dro ON dro.id = dr.route_id
WHERE dr.record_date BETWEEN :start_date AND :end_date
  AND (CAST(:route_id AS INTEGER) IS NULL OR dr.route_id = CAST(:route_id AS INTEGER))
  AND (CAST(:vehicle_id AS INTEGER) IS NULL OR dr.vehicle_id = CAST(:vehicle_id AS INTEGER))
  AND (CAST(:driver_id AS INTEGER) IS NULL OR dr.driver_id = CAST(:driver_id AS INTEGER))
ORDER BY dr.record_date DESC, dr.id DESC
"""

DELIVERY_DAILY_SUMMARY_SQL = """
SELECT
  dr.record_date AS record_date,
  COUNT(*) AS record_count,
  SUM(dr.customer_count) AS total_customers,
  SUM(dr.delivery_count) AS total_deliveries
FROM biz_delivery_record dr
WHERE dr.record_date BETWEEN :start_date AND :end_date
  AND (CAST(:route_id AS INTEGER) IS NULL OR dr.route_id = CAST(:route_id AS INTEGER))
GROUP BY dr.record_date
ORDER BY dr.record_date DESC
"""

DELIVERY_ROUTE_SUMMARY_SQL = """
SELECT
  dro.id AS route_id,
  dro.route_code AS route_code,
  dro.route_name AS route_name,
  COUNT(*) AS record_count,
  SUM(dr.customer_count) AS total_customers,
  SUM(dr.delivery_count) AS total_deliveries
FROM biz_delivery_record dr
LEFT JOIN dict_route dro ON dro.id = dr.route_id
WHERE dr.record_date BETWEEN :start_date AND :end_date
GROUP BY dro.id, dro.route_code, dro.route_name
ORDER BY total_deliveries DESC NULLS LAST
"""


SEEDS = [
    {
        "key": "delivery_detail",
        "name": "送货流水明细",
        "description": "按日期范围查询送货流水明细，可选按线路/车辆/驾驶员过滤。",
        "sql_template": DELIVERY_DETAIL_SQL,
        "params_schema": [
            {"name": "start_date", "label": "开始日期", "type": "date", "required": True, "widget": "date"},
            {"name": "end_date", "label": "结束日期", "type": "date", "required": True, "widget": "date"},
            {"name": "route_id", "label": "线路", "type": "int", "required": False,
             "widget": "select", "options_api": "/api/dict/route/options"},
            {"name": "vehicle_id", "label": "车辆", "type": "int", "required": False,
             "widget": "select", "options_api": "/api/dict/vehicle/options"},
            {"name": "driver_id", "label": "驾驶员", "type": "int", "required": False,
             "widget": "select", "options_api": "/api/dict/person/options"},
        ],
        "columns_schema": [
            {"key": "record_date", "label": "日期", "type": "date"},
            {"key": "plate_number", "label": "车牌号", "type": "str"},
            {"key": "driver_name", "label": "驾驶员", "type": "str"},
            {"key": "deliverer_name", "label": "送货员", "type": "str"},
            {"key": "route_code", "label": "线路编码", "type": "str"},
            {"key": "route_name", "label": "线路名称", "type": "str"},
            {"key": "customer_count", "label": "客户数", "type": "int"},
            {"key": "delivery_count", "label": "送货数", "type": "int"},
            {"key": "remark", "label": "备注", "type": "str"},
            {"key": "warn_notes", "label": "预警说明", "type": "str"},
        ],
    },
    {
        "key": "delivery_daily_summary",
        "name": "送货日汇总",
        "description": "按日期汇总送货记录数、客户数、送货数。",
        "sql_template": DELIVERY_DAILY_SUMMARY_SQL,
        "params_schema": [
            {"name": "start_date", "label": "开始日期", "type": "date", "required": True, "widget": "date"},
            {"name": "end_date", "label": "结束日期", "type": "date", "required": True, "widget": "date"},
            {"name": "route_id", "label": "线路", "type": "int", "required": False,
             "widget": "select", "options_api": "/api/dict/route/options"},
        ],
        "columns_schema": [
            {"key": "record_date", "label": "日期", "type": "date"},
            {"key": "record_count", "label": "记录数", "type": "int"},
            {"key": "total_customers", "label": "客户数合计", "type": "int"},
            {"key": "total_deliveries", "label": "送货数合计", "type": "int"},
        ],
    },
    {
        "key": "delivery_route_summary",
        "name": "送货线路汇总",
        "description": "按线路汇总送货记录数、客户数、送货数。",
        "sql_template": DELIVERY_ROUTE_SUMMARY_SQL,
        "params_schema": [
            {"name": "start_date", "label": "开始日期", "type": "date", "required": True, "widget": "date"},
            {"name": "end_date", "label": "结束日期", "type": "date", "required": True, "widget": "date"},
        ],
        "columns_schema": [
            {"key": "route_code", "label": "线路编码", "type": "str"},
            {"key": "route_name", "label": "线路名称", "type": "str"},
            {"key": "record_count", "label": "记录数", "type": "int"},
            {"key": "total_customers", "label": "客户数合计", "type": "int"},
            {"key": "total_deliveries", "label": "送货数合计", "type": "int"},
        ],
    },
]


async def main():
    async with async_session() as session:
        created, skipped = 0, 0
        for seed in SEEDS:
            existing = await session.execute(
                select(ReportTemplate).where(ReportTemplate.key == seed["key"])
            )
            if existing.scalar_one_or_none():
                print(f"[skip] {seed['key']} 已存在")
                skipped += 1
                continue
            session.add(ReportTemplate(**seed))
            created += 1
            print(f"[create] {seed['key']} — {seed['name']}")
        if created:
            await session.commit()
        print(f"\n完成：新建 {created} 个，跳过 {skipped} 个。")


if __name__ == "__main__":
    asyncio.run(main())
