from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import get_current_user
from database import SessionLocal
from models import User

router = APIRouter(prefix="/tai-khoan", tags=["Quản lý tài khoản"])
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    role: str


class UserUpdate(BaseModel):
    password: str | None = None
    full_name: str
    role: str


def require_admin(current_user: User):
    if current_user.username != "admin" or current_user.role != "QuanLy":
        raise HTTPException(
            status_code=403,
            detail="Chỉ tài khoản admin mới có quyền quản lý tài khoản",
        )


@router.get("")
def get_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_admin(current_user)
    users = db.query(User).order_by(User.id).all()
    return [
        {"id": u.id, "username": u.username, "full_name": u.full_name, "role": u.role}
        for u in users
    ]


@router.post("")
def create_user(
    data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_admin(current_user)
    username = data.username.strip()
    full_name = data.full_name.strip()
    allowed_roles = {"QuanLy", "ThuKho", "KeToan"}

    if not username or not data.password or not full_name:
        raise HTTPException(status_code=400, detail="Không được để trống thông tin bắt buộc")
    if data.role not in allowed_roles:
        raise HTTPException(status_code=400, detail="Vai trò không hợp lệ")
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại")

    user = User(
        username=username,
        password=pwd_context.hash(data.password),
        full_name=full_name,
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "success": True,
        "message": "Tạo tài khoản thành công",
        "user": {"id": user.id, "username": user.username, "full_name": user.full_name, "role": user.role},
    }


@router.put("/{user_id}")
def update_user(
    user_id: int,
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_admin(current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")
    if user.username == "admin":
        raise HTTPException(status_code=400, detail="Không thể sửa tài khoản admin")
    if data.role not in {"QuanLy", "ThuKho", "KeToan"}:
        raise HTTPException(status_code=400, detail="Vai trò không hợp lệ")
    if not data.full_name.strip():
        raise HTTPException(status_code=400, detail="Họ tên không được để trống")

    user.full_name = data.full_name.strip()
    user.role = data.role
    if data.password:
        user.password = pwd_context.hash(data.password)
    db.commit()
    db.refresh(user)
    return {
        "success": True,
        "message": "Cập nhật tài khoản thành công",
        "user": {"id": user.id, "username": user.username, "full_name": user.full_name, "role": user.role},
    }


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_admin(current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")
    if user.username == "admin":
        raise HTTPException(status_code=400, detail="Không thể xóa tài khoản admin")

    db.delete(user)
    db.commit()
    return {"success": True, "message": "Xóa tài khoản thành công"}
