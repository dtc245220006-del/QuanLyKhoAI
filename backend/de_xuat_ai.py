from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal

from models import (
    DeXuatAI,
    ChiTietDeXuatAI,
    HangHoa,
    TonKho,
    User,
    PhieuNhap,
    ChiTietPhieuNhap,
    NhaCungCap
)

from gemini_service import tao_de_xuat_nhap


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/de-xuat-ai",
    tags=["Đề xuất AI"]
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
# GET DANH SÁCH ĐỀ XUẤT
# =========================================================

@router.get("")
def get_de_xuat_ai(
    db: Session = Depends(get_db)
):
    danh_sach = (
        db.query(DeXuatAI)
        .order_by(DeXuatAI.id.desc())
        .all()
    )

    result = []

    for de_xuat in danh_sach:

        chi_tiet = (
            db.query(ChiTietDeXuatAI)
            .filter(
                ChiTietDeXuatAI.ma_de_xuat == de_xuat.id
            )
            .all()
        )

        result.append({
            "id": de_xuat.id,
            "ma_tai_khoan": de_xuat.ma_tai_khoan,
            "ngay_tao": de_xuat.ngay_tao,
            "noi_dung": de_xuat.noi_dung,
            "trang_thai": de_xuat.trang_thai,
            "ly_do": de_xuat.ly_do,
            "chi_tiet": [
                {
                    "id": item.id,
                    "ma_de_xuat": item.ma_de_xuat,
                    "ma_hang": item.ma_hang,
                    "so_luong_de_xuat": item.so_luong_de_xuat,
                    "ly_do": item.ly_do
                }
                for item in chi_tiet
            ]
        })

    return result


# =========================================================
# GET 1 ĐỀ XUẤT
# =========================================================

@router.get("/{de_xuat_id}")
def get_de_xuat_by_id(
    de_xuat_id: int,
    db: Session = Depends(get_db)
):
    de_xuat = (
        db.query(DeXuatAI)
        .filter(DeXuatAI.id == de_xuat_id)
        .first()
    )

    if de_xuat is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy đề xuất AI"
        )

    chi_tiet = (
        db.query(ChiTietDeXuatAI)
        .filter(
            ChiTietDeXuatAI.ma_de_xuat == de_xuat.id
        )
        .all()
    )

    return {
        "id": de_xuat.id,
        "ma_tai_khoan": de_xuat.ma_tai_khoan,
        "ngay_tao": de_xuat.ngay_tao,
        "noi_dung": de_xuat.noi_dung,
        "trang_thai": de_xuat.trang_thai,
        "ly_do": de_xuat.ly_do,
        "chi_tiet": [
            {
                "id": item.id,
                "ma_hang": item.ma_hang,
                "so_luong_de_xuat": item.so_luong_de_xuat,
                "ly_do": item.ly_do
            }
            for item in chi_tiet
        ]
    }


# =========================================================
# TẠO ĐỀ XUẤT AI TỪ GEMINI
# =========================================================

@router.post("")
def tao_de_xuat_ai(
    ma_tai_khoan: int,
    db: Session = Depends(get_db)
):
    # -----------------------------------------------------
    # Kiểm tra tài khoản
    # -----------------------------------------------------

    user = (
        db.query(User)
        .filter(User.id == ma_tai_khoan)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=400,
            detail="Tài khoản không tồn tại"
        )

    # Chỉ Quản lý mới được tạo đề xuất chính thức
    if user.role != "QuanLy":
        raise HTTPException(
            status_code=403,
            detail="Chỉ Quản lý mới có quyền tạo đề xuất AI"
        )

    # -----------------------------------------------------
    # Lấy dữ liệu tồn kho
    # -----------------------------------------------------

    ton_kho_list = (
        db.query(TonKho)
        .order_by(TonKho.ma_hang)
        .all()
    )

    if not ton_kho_list:
        raise HTTPException(
            status_code=400,
            detail="Chưa có dữ liệu tồn kho"
        )

    du_lieu_ton_kho = []

    for ton_kho in ton_kho_list:

        hang_hoa = (
            db.query(HangHoa)
            .filter(
                HangHoa.id == ton_kho.ma_hang
            )
            .first()
        )

        if hang_hoa is None:
            continue

        du_lieu_ton_kho.append({
            "ma_hang": hang_hoa.id,
            "ten_hang": hang_hoa.ten_hang,
            "so_luong_ton": ton_kho.so_luong,
            "ton_toi_thieu": hang_hoa.ton_toi_thieu
        })

    if not du_lieu_ton_kho:
        raise HTTPException(
            status_code=400,
            detail="Không có dữ liệu hàng hóa hợp lệ"
        )

    # -----------------------------------------------------
    # GỌI GEMINI
    # -----------------------------------------------------

    try:
        ai_result = tao_de_xuat_nhap(
            du_lieu_ton_kho
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi gọi Gemini: {str(e)}"
        )

    nhan_xet = ai_result.get(
        "nhan_xet",
        ""
    )

    de_xuat_items = ai_result.get(
        "de_xuat",
        []
    )

    # -----------------------------------------------------
    # Kiểm tra Gemini trả đúng dạng
    # -----------------------------------------------------

    if not isinstance(de_xuat_items, list):
        raise HTTPException(
            status_code=500,
            detail="Gemini trả dữ liệu đề xuất không hợp lệ"
        )

    # -----------------------------------------------------
    # Kiểm tra từng đề xuất
    # -----------------------------------------------------

    valid_items = []

    for item in de_xuat_items:

        ma_hang = item.get("ma_hang")

        so_luong = item.get(
            "so_luong_de_xuat"
        )

        if not isinstance(ma_hang, int):
            continue

        if not isinstance(so_luong, int):
            continue

        if so_luong <= 0:
            continue

        hang_hoa = (
            db.query(HangHoa)
            .filter(
                HangHoa.id == ma_hang
            )
            .first()
        )

        if hang_hoa is None:
            continue

        valid_items.append({
            "ma_hang": ma_hang,
            "ten_hang": hang_hoa.ten_hang,
            "so_luong_de_xuat": so_luong,
            "ly_do": item.get(
                "ly_do",
                "AI đề xuất nhập bổ sung"
            )
        })

    # -----------------------------------------------------
    # Không có đề xuất
    # -----------------------------------------------------

    if not valid_items:
        return {
            "success": True,
            "message": "Gemini không đề xuất nhập hàng",
            "de_xuat": None,
            "analysis": nhan_xet
        }

    # -----------------------------------------------------
    # Tạo DeXuatAI
    # -----------------------------------------------------

    de_xuat = DeXuatAI(
        ma_tai_khoan=ma_tai_khoan,
        ngay_tao=datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        noi_dung=nhan_xet,
        trang_thai="ChoDuyet",
        ly_do="Đề xuất được tạo từ Gemini AI"
    )

    db.add(de_xuat)

    db.flush()

    # -----------------------------------------------------
    # Tạo ChiTietDeXuatAI
    # -----------------------------------------------------

    for item in valid_items:

        chi_tiet = ChiTietDeXuatAI(
            ma_de_xuat=de_xuat.id,
            ma_hang=item["ma_hang"],
            so_luong_de_xuat=item[
                "so_luong_de_xuat"
            ],
            ly_do=item["ly_do"]
        )

        db.add(chi_tiet)

    db.commit()
    db.refresh(de_xuat)

    # -----------------------------------------------------
    # Trả kết quả
    # -----------------------------------------------------

    return {
        "success": True,
        "message": "Gemini đã phân tích và tạo đề xuất AI",
        "analysis": nhan_xet,
        "de_xuat": {
            "id": de_xuat.id,
            "trang_thai": de_xuat.trang_thai,
            "ngay_tao": de_xuat.ngay_tao,
            "noi_dung": de_xuat.noi_dung,
            "chi_tiet": valid_items
        }
    }


# =========================================================
# DUYỆT ĐỀ XUẤT
# =========================================================

@router.put("/{de_xuat_id}/duyet")
def duyet_de_xuat(
    de_xuat_id: int,
    db: Session = Depends(get_db)
):
    de_xuat = (
        db.query(DeXuatAI)
        .filter(
            DeXuatAI.id == de_xuat_id
        )
        .first()
    )

    if de_xuat is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy đề xuất AI"
        )

    if de_xuat.trang_thai != "ChoDuyet":
        raise HTTPException(
            status_code=400,
            detail="Đề xuất không còn ở trạng thái chờ duyệt"
        )

    de_xuat.trang_thai = "DaDuyet"

    db.commit()
    db.refresh(de_xuat)

    return {
        "success": True,
        "message": "Đã duyệt đề xuất AI",
        "id": de_xuat.id,
        "trang_thai": de_xuat.trang_thai
    }


# =========================================================
# TỪ CHỐI ĐỀ XUẤT
# =========================================================

@router.put("/{de_xuat_id}/tu-choi")
def tu_choi_de_xuat(
    de_xuat_id: int,
    db: Session = Depends(get_db)
):
    de_xuat = (
        db.query(DeXuatAI)
        .filter(
            DeXuatAI.id == de_xuat_id
        )
        .first()
    )

    if de_xuat is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy đề xuất AI"
        )

    if de_xuat.trang_thai != "ChoDuyet":
        raise HTTPException(
            status_code=400,
            detail="Đề xuất không còn ở trạng thái chờ duyệt"
        )

    de_xuat.trang_thai = "TuChoi"

    db.commit()
    db.refresh(de_xuat)

    return {
        "success": True,
        "message": "Đã từ chối đề xuất AI",
        "id": de_xuat.id,
        "trang_thai": de_xuat.trang_thai
    }
# =========================================================
# THỦ KHO TẠO PHIẾU NHẬP TỪ ĐỀ XUẤT AI ĐÃ DUYỆT
# =========================================================

@router.post("/{de_xuat_id}/tao-phieu-nhap")
def tao_phieu_nhap_tu_de_xuat(
    de_xuat_id: int,
    ma_tai_khoan: int,
    ma_ncc: int,
    db: Session = Depends(get_db)
):
    # -----------------------------------------------------
    # Kiểm tra tài khoản
    # -----------------------------------------------------

    user = (
        db.query(User)
        .filter(User.id == ma_tai_khoan)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=400,
            detail="Tài khoản không tồn tại"
        )

    # Chỉ Thủ kho được tạo phiếu từ đề xuất
    if user.role != "ThuKho":
        raise HTTPException(
            status_code=403,
            detail="Chỉ Thủ kho mới có quyền tạo phiếu nhập từ đề xuất AI"
        )

    # -----------------------------------------------------
    # Kiểm tra đề xuất
    # -----------------------------------------------------

    de_xuat = (
        db.query(DeXuatAI)
        .filter(DeXuatAI.id == de_xuat_id)
        .first()
    )

    if de_xuat is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy đề xuất AI"
        )

    if de_xuat.trang_thai != "DaDuyet":
        raise HTTPException(
            status_code=400,
            detail="Đề xuất phải được Quản lý duyệt trước"
        )

    # -----------------------------------------------------
    # Kiểm tra nhà cung cấp
    # -----------------------------------------------------

    nha_cung_cap = (
        db.query(NhaCungCap)
        .filter(NhaCungCap.id == ma_ncc)
        .first()
    )

    if nha_cung_cap is None:
        raise HTTPException(
            status_code=400,
            detail="Nhà cung cấp không tồn tại"
        )

    # -----------------------------------------------------
    # Lấy chi tiết đề xuất
    # -----------------------------------------------------

    chi_tiet_de_xuat = (
        db.query(ChiTietDeXuatAI)
        .filter(
            ChiTietDeXuatAI.ma_de_xuat == de_xuat.id
        )
        .all()
    )

    if not chi_tiet_de_xuat:
        raise HTTPException(
            status_code=400,
            detail="Đề xuất AI không có sản phẩm"
        )

    # -----------------------------------------------------
    # Tính chi tiết phiếu nhập
    # Dùng giá nhập hiện tại của hàng hóa
    # -----------------------------------------------------

    chi_tiet_phieu = []
    tong_tien = 0

    for item in chi_tiet_de_xuat:

        hang_hoa = (
            db.query(HangHoa)
            .filter(
                HangHoa.id == item.ma_hang
            )
            .first()
        )

        if hang_hoa is None:
            raise HTTPException(
                status_code=400,
                detail=f"Hàng hóa ID {item.ma_hang} không tồn tại"
            )

        if item.so_luong_de_xuat <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"Số lượng đề xuất của hàng ID {item.ma_hang} không hợp lệ"
            )

        don_gia = hang_hoa.gia_nhap
        thanh_tien = (
            item.so_luong_de_xuat * don_gia
        )

        tong_tien += thanh_tien

        chi_tiet_phieu.append({
            "ma_hang": hang_hoa.id,
            "so_luong": item.so_luong_de_xuat,
            "don_gia": don_gia,
            "thanh_tien": thanh_tien
        })

    # -----------------------------------------------------
    # Tạo phiếu nhập nháp
    # -----------------------------------------------------

    phieu = PhieuNhap(
        ma_ncc=ma_ncc,
        ma_tai_khoan=ma_tai_khoan,
        ngay_nhap=datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        tong_tien=tong_tien,
        trang_thai="Nhap"
    )

    db.add(phieu)
    db.flush()

    # -----------------------------------------------------
    # Tạo chi tiết phiếu nhập
    # -----------------------------------------------------

    for item in chi_tiet_phieu:

        chi_tiet = ChiTietPhieuNhap(
            ma_phieu_nhap=phieu.id,
            ma_hang=item["ma_hang"],
            so_luong=item["so_luong"],
            don_gia=item["don_gia"],
            thanh_tien=item["thanh_tien"]
        )

        db.add(chi_tiet)

    # -----------------------------------------------------
    # Đánh dấu đề xuất đã được chuyển thành phiếu nhập
    # -----------------------------------------------------

    de_xuat.trang_thai = "DaTaoPhieuNhap"

    db.commit()
    db.refresh(phieu)

    return {
        "success": True,
        "message": "Đã tạo phiếu nhập nháp từ đề xuất AI",
        "de_xuat_id": de_xuat.id,
        "phieu_nhap": {
            "id": phieu.id,
            "ma_ncc": phieu.ma_ncc,
            "ma_tai_khoan": phieu.ma_tai_khoan,
            "ngay_nhap": phieu.ngay_nhap,
            "tong_tien": phieu.tong_tien,
            "trang_thai": phieu.trang_thai
        }
    }