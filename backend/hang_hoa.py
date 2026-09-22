from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from database import SessionLocal
from models import HangHoa, NhomHang


router = APIRouter(
    prefix="/hang-hoa",
    tags=["Hàng hóa"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


class HangHoaCreate(BaseModel):
    ma_nhom: int
    ten_hang: str
    don_vi_tinh: str
    ma_barcode: str | None = None
    gia_nhap: int = 0
    gia_ban: int = 0
    ton_toi_thieu: int = 0


class HangHoaResponse(BaseModel):
    id: int
    ma_nhom: int
    ten_hang: str
    don_vi_tinh: str
    ma_barcode: str | None
    gia_nhap: int
    gia_ban: int
    ton_toi_thieu: int

    model_config = ConfigDict(from_attributes=True)


# =========================
# Lấy danh sách hàng hóa
# =========================

@router.get("", response_model=list[HangHoaResponse])
def get_hang_hoa(
    db: Session = Depends(get_db)
):
    return (
        db.query(HangHoa)
        .order_by(HangHoa.id)
        .all()
    )


# =========================
# Lấy hàng hóa theo ID
# =========================

@router.get(
    "/{hang_hoa_id}",
    response_model=HangHoaResponse
)
def get_hang_hoa_by_id(
    hang_hoa_id: int,
    db: Session = Depends(get_db)
):
    hang_hoa = (
        db.query(HangHoa)
        .filter(HangHoa.id == hang_hoa_id)
        .first()
    )

    if hang_hoa is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy hàng hóa"
        )

    return hang_hoa


# =========================
# Thêm hàng hóa
# =========================

@router.post(
    "",
    response_model=HangHoaResponse
)
def create_hang_hoa(
    data: HangHoaCreate,
    db: Session = Depends(get_db)
):
    # Kiểm tra nhóm hàng
    nhom_hang = (
        db.query(NhomHang)
        .filter(NhomHang.id == data.ma_nhom)
        .first()
    )

    if nhom_hang is None:
        raise HTTPException(
            status_code=400,
            detail="Nhóm hàng không tồn tại"
        )

    # Kiểm tra barcode
    if data.ma_barcode:
        existing_barcode = (
            db.query(HangHoa)
            .filter(
                HangHoa.ma_barcode == data.ma_barcode
            )
            .first()
        )

        if existing_barcode:
            raise HTTPException(
                status_code=400,
                detail="Mã barcode đã tồn tại"
            )

    # Kiểm tra tên hàng
    ten_hang = data.ten_hang.strip()

    if not ten_hang:
        raise HTTPException(
            status_code=400,
            detail="Tên hàng không được để trống"
        )

    # Kiểm tra số liệu
    if data.gia_nhap < 0:
        raise HTTPException(
            status_code=400,
            detail="Giá nhập không được âm"
        )

    if data.gia_ban < 0:
        raise HTTPException(
            status_code=400,
            detail="Giá bán không được âm"
        )

    if data.ton_toi_thieu < 0:
        raise HTTPException(
            status_code=400,
            detail="Tồn tối thiểu không được âm"
        )

    hang_hoa = HangHoa(
        ma_nhom=data.ma_nhom,
        ten_hang=ten_hang,
        don_vi_tinh=data.don_vi_tinh,
        ma_barcode=data.ma_barcode,
        gia_nhap=data.gia_nhap,
        gia_ban=data.gia_ban,
        ton_toi_thieu=data.ton_toi_thieu
    )

    db.add(hang_hoa)
    db.commit()
    db.refresh(hang_hoa)

    return hang_hoa


# =========================
# Sửa hàng hóa
# =========================

@router.put(
    "/{hang_hoa_id}",
    response_model=HangHoaResponse
)
def update_hang_hoa(
    hang_hoa_id: int,
    data: HangHoaCreate,
    db: Session = Depends(get_db)
):
    hang_hoa = (
        db.query(HangHoa)
        .filter(HangHoa.id == hang_hoa_id)
        .first()
    )

    if hang_hoa is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy hàng hóa"
        )

    # Kiểm tra nhóm
    nhom_hang = (
        db.query(NhomHang)
        .filter(NhomHang.id == data.ma_nhom)
        .first()
    )

    if nhom_hang is None:
        raise HTTPException(
            status_code=400,
            detail="Nhóm hàng không tồn tại"
        )

    ten_hang = data.ten_hang.strip()

    if not ten_hang:
        raise HTTPException(
            status_code=400,
            detail="Tên hàng không được để trống"
        )

    # Kiểm tra barcode trùng
    if data.ma_barcode:
        existing_barcode = (
            db.query(HangHoa)
            .filter(
                HangHoa.ma_barcode == data.ma_barcode,
                HangHoa.id != hang_hoa_id
            )
            .first()
        )

        if existing_barcode:
            raise HTTPException(
                status_code=400,
                detail="Mã barcode đã tồn tại"
            )

    if data.gia_nhap < 0:
        raise HTTPException(
            status_code=400,
            detail="Giá nhập không được âm"
        )

    if data.gia_ban < 0:
        raise HTTPException(
            status_code=400,
            detail="Giá bán không được âm"
        )

    if data.ton_toi_thieu < 0:
        raise HTTPException(
            status_code=400,
            detail="Tồn tối thiểu không được âm"
        )

    hang_hoa.ma_nhom = data.ma_nhom
    hang_hoa.ten_hang = ten_hang
    hang_hoa.don_vi_tinh = data.don_vi_tinh
    hang_hoa.ma_barcode = data.ma_barcode
    hang_hoa.gia_nhap = data.gia_nhap
    hang_hoa.gia_ban = data.gia_ban
    hang_hoa.ton_toi_thieu = data.ton_toi_thieu

    db.commit()
    db.refresh(hang_hoa)

    return hang_hoa


# =========================
# Xóa hàng hóa
# =========================

@router.delete("/{hang_hoa_id}")
def delete_hang_hoa(
    hang_hoa_id: int,
    db: Session = Depends(get_db)
):
    hang_hoa = (
        db.query(HangHoa)
        .filter(HangHoa.id == hang_hoa_id)
        .first()
    )

    if hang_hoa is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy hàng hóa"
        )

    db.delete(hang_hoa)
    db.commit()

    return {
        "success": True,
        "message": "Xóa hàng hóa thành công"
    }