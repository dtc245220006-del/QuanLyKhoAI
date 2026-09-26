import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from sqlalchemy.orm import Session

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from auth import router as auth_router
from nhom_hang import router as nhom_hang_router
from hang_hoa import router as hang_hoa_router
from nha_cung_cap import router as nha_cung_cap_router
from phieu_nhap import router as phieu_nhap_router
from ton_kho import router as ton_kho_router
from lich_su_kho import router as lich_su_kho_router
from phieu_xuat import router as phieu_xuat_router
from bao_cao import router as bao_cao_router
from ai_controller import router as ai_router
from de_xuat_ai import router as de_xuat_ai_router
from tai_khoan import router as tai_khoan_router
from database import Base, engine, SessionLocal
from models import User
from multi_agent.multi_agent.router import router as multi_agent_router

Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def create_default_users():
    db: Session = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if admin is None:
            db.add(User(
                username="admin",
                password=pwd_context.hash("123456"),
                full_name="Quản lý",
                role="QuanLy",
            ))
            db.commit()
        elif admin.role != "QuanLy":
            admin.role = "QuanLy"
            db.commit()
    finally:
        db.close()


create_default_users()

app = FastAPI(title="Hệ thống quản lý kho tích hợp AI", version="1.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in [
    auth_router,
    nhom_hang_router,
    hang_hoa_router,
    nha_cung_cap_router,
    phieu_nhap_router,
    ton_kho_router,
    lich_su_kho_router,
    phieu_xuat_router,
    bao_cao_router,
    ai_router,
    de_xuat_ai_router,
    tai_khoan_router,
    multi_agent_router,
]:
    app.include_router(router)
