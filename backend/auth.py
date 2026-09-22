from datetime import datetime, timedelta, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt

from database import SessionLocal
from models import User


# =========================================================
# CẤU HÌNH
# =========================================================

SECRET_KEY = "quan-ly-kho-ai-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# =========================================================
# MÃ HÓA MẬT KHẨU
# =========================================================

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# =========================================================
# HTTP BEARER
# =========================================================

security = HTTPBearer()


# =========================================================
# KẾT NỐI DATABASE
# =========================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================================================
# SCHEMA ĐĂNG NHẬP
# =========================================================

class LoginRequest(BaseModel):
    username: str
    password: str


# =========================================================
# KIỂM TRA MẬT KHẨU
# =========================================================

def verify_password(
    password: str,
    hashed_password: str
) -> bool:

    return pwd_context.verify(
        password,
        hashed_password
    )


# =========================================================
# TẠO JWT TOKEN
# =========================================================

def create_access_token(
    username: str,
    role: str
):

    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": username,
        "role": role,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# =========================================================
# LẤY USER HIỆN TẠI TỪ TOKEN
# =========================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không hợp lệ"
            )

    except Exception:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn"
        )

    user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Người dùng không tồn tại"
        )

    return user


# =========================================================
# KIỂM TRA QUYỀN
# =========================================================

def require_roles(*allowed_roles):

    def role_checker(
        current_user: User = Depends(get_current_user)
    ):

        if current_user.role not in allowed_roles:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền thực hiện chức năng này"
            )

        return current_user

    return role_checker


# =========================================================
# API ĐĂNG NHẬP
# =========================================================

@router.post("/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.username == data.username)
        .first()
    )

    # Không tìm thấy user
    if user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không đúng"
        )

    # Kiểm tra mật khẩu
    if not verify_password(
        data.password,
        user.password
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không đúng"
        )

    # Kiểm tra trạng thái tài khoản
    if hasattr(user, "trang_thai"):

        if user.trang_thai == "Khoa":

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản đã bị khóa"
            )

    # Tạo token
    token = create_access_token(
        username=user.username,
        role=user.role
    )

    return {
        "success": True,
        "message": "Đăng nhập thành công",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role
        }
    }


# =========================================================
# API KIỂM TRA USER ĐANG ĐĂNG NHẬP
# =========================================================

@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user)
):

    return {
        "success": True,
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "full_name": current_user.full_name,
            "role": current_user.role
        }
    }


# =========================================================
# API TEST QUYỀN QUẢN LÝ
# =========================================================

@router.get("/quan-ly-only")
def quan_ly_only(
    current_user: User = Depends(
        require_roles("QuanLy")
    )
):

    return {
        "success": True,
        "message": "Bạn là Quản lý và có quyền truy cập chức năng này",
        "user": current_user.username
    }


# =========================================================
# API TEST QUYỀN THỦ KHO
# =========================================================

@router.get("/thu-kho-only")
def thu_kho_only(
    current_user: User = Depends(
        require_roles("ThuKho")
    )
):

    return {
        "success": True,
        "message": "Bạn là Thủ kho và có quyền truy cập chức năng này",
        "user": current_user.username
    }


# =========================================================
# API TEST QUYỀN KẾ TOÁN
# =========================================================

@router.get("/ke-toan-only")
def ke_toan_only(
    current_user: User = Depends(
        require_roles("KeToan")
    )
):

    return {
        "success": True,
        "message": "Bạn là Kế toán và có quyền truy cập chức năng này",
        "user": current_user.username
    }