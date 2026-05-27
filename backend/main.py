import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.auth import router as auth_router
from api.dict import router as dict_router
from api.import_excel import router as import_router
from api.report import router as report_router
from api.audit import router as audit_router
from api.users import router as users_router

app = FastAPI(title="“企业”物流数据管理系统", version="1.0.0")

origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(dict_router)
app.include_router(import_router)
app.include_router(report_router)
app.include_router(audit_router)
app.include_router(users_router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
