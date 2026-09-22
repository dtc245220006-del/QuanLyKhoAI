from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from database import SessionLocal
from models import NhomHang


router = APIRouter(
    prefix="/nhom-hang",
    tags=["Nhóm hàng"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


class NhomHangCreate(BaseModel):
    ten_nhom: str
    mo_ta: str | None = None


class NhomHangResponse(BaseModel):
    id: int
    ten_nhom: str
    mo_ta: str | None

    model_config = ConfigDict(from_attributes=True)


# =========================
# Lấy danh sách nhóm hàng
# =========================

@router.get("", response_model=list[NhomHangResponse])
def get_nhom_hang(
    db: Session = Depends(get_db)
):
    return db.query(NhomHang).order_by(NhomHang.id).all()


# =========================
# Lấy 1 nhóm hàng
# =========================

@router.get("/{nhom_hang_id}", response_model=NhomHangResponse)
def get_nhom_hang_by_id(
    nhom_hang_id: int,
    db: Session = Depends(get_db)
):
    nhom_hang = (
        db.query(NhomHang)
        .filter(NhomHang.id == nhom_hang_id)
        .first()
    )

    if nhom_hang is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy nhóm hàng"
        )

    return nhom_hang


# =========================
# Thêm nhóm hàng
# =========================

@router.post("", response_model=NhomHangResponse)
def create_nhom_hang(
    data: NhomHangCreate,
    db: Session = Depends(get_db)
):
    ten_nhom = data.ten_nhom.strip()

    if not ten_nhom:
        raise HTTPException(
            status_code=400,
            detail="Tên nhóm hàng không được để trống"
        )

    existing = (
        db.query(NhomHang)
        .filter(NhomHang.ten_nhom == ten_nhom)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Nhóm hàng đã tồn tại"
        )

    nhom_hang = NhomHang(
        ten_nhom=ten_nhom,
        mo_ta=data.mo_ta
    )

    db.add(nhom_hang)
    db.commit()
    db.refresh(nhom_hang)

    return nhom_hang


# =========================
# Sửa nhóm hàng
# =========================

@router.put("/{nhom_hang_id}", response_model=NhomHangResponse)
def update_nhom_hang(
    nhom_hang_id: int,
    data: NhomHangCreate,
    db: Session = Depends(get_db)
):
    nhom_hang = (
        db.query(NhomHang)
        .filter(NhomHang.id == nhom_hang_id)
        .first()
    )

    if nhom_hang is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy nhóm hàng"
        )

    ten_nhom = data.ten_nhom.strip()

    if not ten_nhom:
        raise HTTPException(
            status_code=400,
            detail="Tên nhóm hàng không được để trống"
        )

    existing = (
        db.query(NhomHang)
        .filter(
            NhomHang.ten_nhom == ten_nhom,
            NhomHang.id != nhom_hang_id
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Tên nhóm hàng đã được sử dụng"
        )

    nhom_hang.ten_nhom = ten_nhom
    nhom_hang.mo_ta = data.mo_ta

    db.commit()
    db.refresh(nhom_hang)

    return nhom_hang


# =========================
# Xóa nhóm hàng
# =========================

@router.delete("/{nhom_hang_id}")
def delete_nhom_hang(
    nhom_hang_id: int,
    db: Session = Depends(get_db)
):
    nhom_hang = (
        db.query(NhomHang)
        .filter(NhomHang.id == nhom_hang_id)
        .first()
    )

    if nhom_hang is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy nhóm hàng"
        )

    db.delete(nhom_hang)
    db.commit()

    return {
        "success": True,
        "message": "Xóa nhóm hàng thành công"
    }