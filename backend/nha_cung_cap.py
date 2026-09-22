from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from database import SessionLocal
from models import NhaCungCap


router = APIRouter(
    prefix="/nha-cung-cap",
    tags=["Nhà cung cấp"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================================================
# SCHEMA
# =========================================================

class NhaCungCapCreate(BaseModel):
    ten_ncc: str
    so_dien_thoai: str | None = None
    email: str | None = None
    dia_chi: str | None = None


class NhaCungCapResponse(BaseModel):
    id: int
    ten_ncc: str
    so_dien_thoai: str | None
    email: str | None
    dia_chi: str | None

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# GET DANH SÁCH
# =========================================================

@router.get(
    "",
    response_model=list[NhaCungCapResponse]
)
def get_nha_cung_cap(
    db: Session = Depends(get_db)
):
    return (
        db.query(NhaCungCap)
        .order_by(NhaCungCap.id)
        .all()
    )


# =========================================================
# GET THEO ID
# =========================================================

@router.get(
    "/{nha_cung_cap_id}",
    response_model=NhaCungCapResponse
)
def get_nha_cung_cap_by_id(
    nha_cung_cap_id: int,
    db: Session = Depends(get_db)
):
    nha_cung_cap = (
        db.query(NhaCungCap)
        .filter(NhaCungCap.id == nha_cung_cap_id)
        .first()
    )

    if nha_cung_cap is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy nhà cung cấp"
        )

    return nha_cung_cap


# =========================================================
# POST - THÊM NHÀ CUNG CẤP
# =========================================================

@router.post(
    "",
    response_model=NhaCungCapResponse
)
def create_nha_cung_cap(
    data: NhaCungCapCreate,
    db: Session = Depends(get_db)
):
    ten_ncc = data.ten_ncc.strip()

    if not ten_ncc:
        raise HTTPException(
            status_code=400,
            detail="Tên nhà cung cấp không được để trống"
        )

    nha_cung_cap = NhaCungCap(
        ten_ncc=ten_ncc,
        so_dien_thoai=data.so_dien_thoai,
        email=data.email,
        dia_chi=data.dia_chi
    )

    db.add(nha_cung_cap)
    db.commit()
    db.refresh(nha_cung_cap)

    return nha_cung_cap


# =========================================================
# PUT - SỬA NHÀ CUNG CẤP
# =========================================================

@router.put(
    "/{nha_cung_cap_id}",
    response_model=NhaCungCapResponse
)
def update_nha_cung_cap(
    nha_cung_cap_id: int,
    data: NhaCungCapCreate,
    db: Session = Depends(get_db)
):
    nha_cung_cap = (
        db.query(NhaCungCap)
        .filter(NhaCungCap.id == nha_cung_cap_id)
        .first()
    )

    if nha_cung_cap is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy nhà cung cấp"
        )

    ten_ncc = data.ten_ncc.strip()

    if not ten_ncc:
        raise HTTPException(
            status_code=400,
            detail="Tên nhà cung cấp không được để trống"
        )

    nha_cung_cap.ten_ncc = ten_ncc
    nha_cung_cap.so_dien_thoai = data.so_dien_thoai
    nha_cung_cap.email = data.email
    nha_cung_cap.dia_chi = data.dia_chi

    db.commit()
    db.refresh(nha_cung_cap)

    return nha_cung_cap


# =========================================================
# DELETE - XÓA NHÀ CUNG CẤP
# =========================================================

@router.delete("/{nha_cung_cap_id}")
def delete_nha_cung_cap(
    nha_cung_cap_id: int,
    db: Session = Depends(get_db)
):
    nha_cung_cap = (
        db.query(NhaCungCap)
        .filter(NhaCungCap.id == nha_cung_cap_id)
        .first()
    )

    if nha_cung_cap is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy nhà cung cấp"
        )

    db.delete(nha_cung_cap)
    db.commit()

    return {
        "success": True,
        "message": "Xóa nhà cung cấp thành công"
    }