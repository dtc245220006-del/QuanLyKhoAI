from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext
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

from database import Base, engine, test_connection, SessionLocal
from models import User


Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)


def create_default_users():
    db: Session = SessionLocal()

    try:
        admin = (
            db.query(User)
            .filter(User.username == "admin")
            .first()
        )

        # Nếu chưa có admin thì tạo mới
        if admin is None:
            admin = User(
                username="admin",
                password=pwd_context.hash("123456"),
                full_name="Quản lý",
                role="QuanLy"
            )

            db.add(admin)
            db.commit()
            db.refresh(admin)

            print("Đã tạo tài khoản admin")
            print("Username: admin")
            print("Password: 123456")

        # Nếu đã có thì reset password về 123456
        else:
            admin.password = pwd_context.hash("123456")
            admin.full_name = "Quản lý"
            admin.role = "QuanLy"

            db.commit()

            print("Đã reset tài khoản admin")
            print("Username: admin")
            print("Password: 123456")

    finally:
        db.close()


create_default_users()

app = FastAPI(
    title="Hệ thống quản lý kho tích hợp AI",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(nhom_hang_router)
app.include_router(hang_hoa_router)
app.include_router(nha_cung_cap_router)
app.include_router(phieu_nhap_router)
app.include_router(ton_kho_router)
app.include_router(lich_su_kho_router)
app.include_router(phieu_xuat_router)
app.include_router(bao_cao_router)
app.include_router(ai_router)
app.include_router (de_xuat_ai_router)
app.include_router(tai_khoan_router)