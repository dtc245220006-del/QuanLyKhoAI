from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal
from models import User


router = APIRouter(
    prefix="/tai-khoan",
    tags=["Quản lý tài khoản"]
)

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)


# =========================================================
# DATABASE
# =========================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================================================
# SCHEMA
# =========================================================

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    role: str


class UserUpdate(BaseModel):
    password: str | None = None
    full_name: str
    role: str


# =========================================================
# KIỂM TRA ADMIN
# =========================================================

def check_admin(
    db: Session,
    username: str
):
    admin = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if admin is None:
        raise HTTPException(
            status_code=401,
            detail="Tài khoản không tồn tại"
        )

    # Chỉ đúng tài khoản admin
    if admin.username != "admin":
        raise HTTPException(
            status_code=403,
            detail="Chỉ tài khoản admin mới có quyền quản lý tài khoản"
        )

    return admin


# =========================================================
# DANH SÁCH TÀI KHOẢN
# =========================================================

@router.get("")
def get_users(
    username: str,
    db: Session = Depends(get_db)
):
    check_admin(db, username)

    users = (
        db.query(User)
        .order_by(User.id)
        .all()
    )

    return [
        {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role
        }
        for user in users
    ]


# =========================================================
# THÊM TÀI KHOẢN
# =========================================================

@router.post("")
def create_user(
    data: UserCreate,
    username: str,
    db: Session = Depends(get_db)
):
    check_admin(db, username)

    username_new = data.username.strip()
    full_name = data.full_name.strip()

    if not username_new:
        raise HTTPException(
            status_code=400,
            detail="Tên đăng nhập không được để trống"
        )

    if not data.password:
        raise HTTPException(
            status_code=400,
            detail="Mật khẩu không được để trống"
        )

    if not full_name:
        raise HTTPException(
            status_code=400,
            detail="Họ tên không được để trống"
        )

    allowed_roles = [
        "QuanLy",
        "ThuKho",
        "KeToan"
    ]

    if data.role not in allowed_roles:
        raise HTTPException(
            status_code=400,
            detail="Vai trò không hợp lệ"
        )

    existing = (
        db.query(User)
        .filter(User.username == username_new)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Tên đăng nhập đã tồn tại"
        )

    user = User(
        username=username_new,
        password=pwd_context.hash(
            data.password
        ),
        full_name=full_name,
        role=data.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "success": True,
        "message": "Tạo tài khoản thành công",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role
        }
    }


# =========================================================
# SỬA TÀI KHOẢN
# =========================================================

@router.put("/{user_id}")
def update_user(
    user_id: int,
    data: UserUpdate,
    username: str,
    db: Session = Depends(get_db)
):
    check_admin(db, username)

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy tài khoản"
        )

    # Không cho sửa chính tài khoản admin
    if user.username == "admin":
        raise HTTPException(
            status_code=400,
            detail="Không thể sửa tài khoản admin"
        )

    allowed_roles = [
        "QuanLy",
        "ThuKho",
        "KeToan"
    ]

    if data.role not in allowed_roles:
        raise HTTPException(
            status_code=400,
            detail="Vai trò không hợp lệ"
        )

    full_name = data.full_name.strip()

    if not full_name:
        raise HTTPException(
            status_code=400,
            detail="Họ tên không được để trống"
        )

    user.full_name = full_name
    user.role = data.role

    # Chỉ đổi mật khẩu nếu admin nhập mật khẩu mới
    if data.password:
        user.password = pwd_context.hash(
            data.password
        )

    db.commit()
    db.refresh(user)

    return {
        "success": True,
        "message": "Cập nhật tài khoản thành công",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role
        }
    }


# =========================================================
# XÓA TÀI KHOẢN
# =========================================================

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    username: str,
    db: Session = Depends(get_db)
):
    check_admin(db, username)

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy tài khoản"
        )

    # Không cho xóa admin
    if user.username == "admin":
        raise HTTPException(
            status_code=400,
            detail="Không thể xóa tài khoản admin"
        )

    db.delete(user)
    db.commit()

    return {
        "success": True,
        "message": "Xóa tài khoản thành công"
    }