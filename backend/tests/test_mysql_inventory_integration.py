"""Read/write integration coverage against the isolated quanlykho_test schema.

Run only with ``--run-mysql-integration``.  Credentials are requested with
``getpass`` and exist only in the in-memory SQLAlchemy URL for this process.
The application database module is deliberately never imported because it
loads .env and targets the application database.
"""

from __future__ import annotations

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from getpass import getpass
from importlib import import_module
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, delete, func, select, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker


EXPECTED_DATABASE = "quanlykho_test"
EXPECTED_USER = "qlk_test_user"
EXPECTED_PORT = 3306
BACKEND_DIR = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.mysql_integration


def _install_isolated_imports():
    """Import business modules without importing database.py, .env, or main.py."""
    sys.path.insert(0, str(BACKEND_DIR))

    database = ModuleType("database")
    database.Base = declarative_base()
    database.SessionLocal = None
    sys.modules["database"] = database

    auth = ModuleType("auth")

    def require_roles(*_roles):
        def dependency():
            return None

        return dependency

    auth.require_roles = require_roles
    auth.get_current_user = lambda: None
    sys.modules["auth"] = auth

    gemini = ModuleType("gemini_service")
    gemini.phan_tich_ton_kho = lambda _data: "mock analysis"
    gemini.tao_de_xuat_nhap = lambda _data: {"nhan_xet": "mock", "de_xuat": []}
    sys.modules["gemini_service"] = gemini

    import models
    import ai_controller
    import de_xuat_ai
    import phieu_nhap
    import phieu_xuat

    return models, ai_controller, de_xuat_ai, phieu_nhap, phieu_xuat


@pytest.fixture(scope="session")
def business_modules():
    return _install_isolated_imports()


@pytest.fixture(scope="session")
def mysql_engine(pytestconfig):
    if not pytestconfig.getoption("--run-mysql-integration"):
        pytest.skip("pass --run-mysql-integration to opt in to the isolated MySQL suite")

    password = getpass(f"Password for {EXPECTED_USER}: ")
    if not password:
        pytest.fail("A password is required for the isolated MySQL test account.")

    url = URL.create(
        drivername="mysql+pymysql",
        username=EXPECTED_USER,
        password=password,
        host="localhost",
        port=EXPECTED_PORT,
        database=EXPECTED_DATABASE,
    )
    engine = create_engine(url, pool_pre_ping=False)
    try:
        with engine.connect() as connection:
            database, current_user = connection.execute(
                text("SELECT DATABASE(), CURRENT_USER()")
            ).one()
        actual_user = str(current_user).split("@", 1)[0]
        if database != EXPECTED_DATABASE or actual_user != EXPECTED_USER:
            pytest.fail("Refusing to write: MySQL test database identity did not match.")
        yield engine
    except pytest.fail.Exception:
        raise
    except Exception:
        pytest.fail("MySQL integration setup failed without exposing credentials.")
    finally:
        engine.dispose()


@pytest.fixture
def db(mysql_engine, business_modules):
    models, *_ = business_modules
    Session = sessionmaker(bind=mysql_engine, autoflush=False, expire_on_commit=False)
    session = Session()
    run_tag = f"it-{uuid4().hex}"
    created = {}

    try:
        _assert_test_identity(session)

        user = models.User(
            username=f"{run_tag}-manager",
            password="test-only-hash",
            full_name="Integration Test Manager",
            role="QuanLy",
        )
        group = models.NhomHang(ten_nhom=f"{run_tag}-group", mo_ta="test fixture")
        supplier = models.NhaCungCap(ten_ncc=f"{run_tag}-supplier")
        session.add_all([user, group, supplier])
        session.flush()
        product = models.HangHoa(
            ma_nhom=group.id,
            ten_hang=f"{run_tag}-product",
            don_vi_tinh="unit",
            ma_barcode=f"{run_tag}-barcode",
            gia_nhap=100,
            gia_ban=150,
            ton_toi_thieu=10,
        )
        session.add(product)
        session.flush()
        stock = models.TonKho(
            ma_hang=product.id,
            so_luong=10,
            ngay_cap_nhat=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        session.add(stock)
        session.commit()
        created.update(user_id=user.id, group_id=group.id, supplier_id=supplier.id, product_id=product.id)
        yield session, created
    finally:
        session.rollback()
        # This fixture deletes only rows whose primary keys it recorded, in FK order.
        if created:
            _assert_test_identity(session)
            session.execute(delete(models.LichSuKho).where(models.LichSuKho.ma_hang == created["product_id"]))
            receipts = select(models.PhieuNhap.id).where(models.PhieuNhap.ma_tai_khoan == created["user_id"])
            receipt_ids = list(session.scalars(receipts))
            if receipt_ids:
                session.execute(delete(models.ChiTietPhieuNhap).where(models.ChiTietPhieuNhap.ma_phieu_nhap.in_(receipt_ids)))
                session.execute(delete(models.PhieuNhap).where(models.PhieuNhap.id.in_(receipt_ids)))
            issues = select(models.PhieuXuat.id).where(models.PhieuXuat.ma_tai_khoan == created["user_id"])
            issue_ids = list(session.scalars(issues))
            if issue_ids:
                session.execute(delete(models.ChiTietPhieuXuat).where(models.ChiTietPhieuXuat.ma_phieu_xuat.in_(issue_ids)))
                session.execute(delete(models.PhieuXuat).where(models.PhieuXuat.id.in_(issue_ids)))
            proposals = select(models.DeXuatAI.id).where(models.DeXuatAI.ma_tai_khoan == created["user_id"])
            proposal_ids = list(session.scalars(proposals))
            if proposal_ids:
                session.execute(delete(models.ChiTietDeXuatAI).where(models.ChiTietDeXuatAI.ma_de_xuat.in_(proposal_ids)))
                session.execute(delete(models.DeXuatAI).where(models.DeXuatAI.id.in_(proposal_ids)))
            session.execute(delete(models.TonKho).where(models.TonKho.ma_hang == created["product_id"]))
            session.execute(delete(models.HangHoa).where(models.HangHoa.id == created["product_id"]))
            session.execute(delete(models.NhaCungCap).where(models.NhaCungCap.id == created["supplier_id"]))
            session.execute(delete(models.NhomHang).where(models.NhomHang.id == created["group_id"]))
            session.execute(delete(models.User).where(models.User.id == created["user_id"]))
            session.commit()
        session.close()


def _stock(session, models, product_id):
    return session.scalar(select(models.TonKho.so_luong).where(models.TonKho.ma_hang == product_id))


def _assert_test_identity(session):
    database, current_user = session.execute(
        text("SELECT DATABASE(), CURRENT_USER()")
    ).one()
    if database != EXPECTED_DATABASE or str(current_user).split("@", 1)[0] != EXPECTED_USER:
        pytest.fail("Refusing to write: MySQL test database identity did not match.")


def _receipt_data(phieu_nhap, ids, quantity=4):
    return phieu_nhap.PhieuNhapCreate(
        ma_ncc=ids["supplier_id"],
        ma_tai_khoan=ids["user_id"],
        chi_tiet=[phieu_nhap.ChiTietPhieuNhapCreate(ma_hang=ids["product_id"], so_luong=quantity, don_gia=100)],
    )


def _issue_data(phieu_xuat, ids, quantity=4):
    return phieu_xuat.PhieuXuatCreate(
        ma_tai_khoan=ids["user_id"],
        chi_tiet=[phieu_xuat.ChiTietPhieuXuatCreate(ma_hang=ids["product_id"], so_luong=quantity)],
    )


def _actor(ids):
    """Direct service calls still model the actor authenticated by the route."""
    return SimpleNamespace(id=ids["user_id"], role="ThuKho")


def test_it_001_draft_receipt_does_not_increase_stock(db, business_modules):
    models, _, _, phieu_nhap, _ = business_modules
    session, ids = db
    before = _stock(session, models, ids["product_id"])

    _assert_test_identity(session)
    result = phieu_nhap.create_phieu_nhap(_receipt_data(phieu_nhap, ids), session, _actor(ids))

    assert result["phieu_nhap"]["trang_thai"] == "Nhap"
    assert _stock(session, models, ids["product_id"]) == before


def test_it_002_confirmed_receipt_increases_stock_once(db, business_modules):
    models, _, _, phieu_nhap, _ = business_modules
    session, ids = db
    _assert_test_identity(session)
    receipt = phieu_nhap.create_phieu_nhap(_receipt_data(phieu_nhap, ids, quantity=4), session, _actor(ids))
    receipt_id = receipt["phieu_nhap"]["id"]

    _assert_test_identity(session)
    phieu_nhap.xac_nhan_phieu_nhap(receipt_id, session, _actor(ids))
    assert _stock(session, models, ids["product_id"]) == 14
    with pytest.raises(HTTPException):
        phieu_nhap.xac_nhan_phieu_nhap(receipt_id, session, _actor(ids))
    assert _stock(session, models, ids["product_id"]) == 14


def test_it_003_draft_issue_does_not_decrease_stock(db, business_modules):
    models, _, _, _, phieu_xuat = business_modules
    session, ids = db
    _assert_test_identity(session)
    issue = phieu_xuat.create_phieu_xuat(_issue_data(phieu_xuat, ids), session, _actor(ids))

    assert issue["phieu_xuat"]["trang_thai"] == "Nhap"
    assert _stock(session, models, ids["product_id"]) == 10


def test_it_004_issue_beyond_stock_is_rejected_without_changing_stock(db, business_modules):
    models, _, _, _, phieu_xuat = business_modules
    session, ids = db
    _assert_test_identity(session)
    issue = phieu_xuat.create_phieu_xuat(_issue_data(phieu_xuat, ids, quantity=11), session, _actor(ids))

    _assert_test_identity(session)
    with pytest.raises(HTTPException) as error:
        phieu_xuat.xac_nhan_phieu_xuat(issue["phieu_xuat"]["id"], session, _actor(ids))
    assert error.value.status_code == 400
    assert _stock(session, models, ids["product_id"]) == 10


def test_it_005_receipt_failure_rolls_back_without_partial_stock_update(db, business_modules, monkeypatch):
    models, _, _, phieu_nhap, _ = business_modules
    session, ids = db
    _assert_test_identity(session)
    receipt = phieu_nhap.create_phieu_nhap(_receipt_data(phieu_nhap, ids, quantity=4), session, _actor(ids))

    def fail_history(*_args, **_kwargs):
        raise RuntimeError("injected persistence failure")

    monkeypatch.setattr(phieu_nhap, "LichSuKho", fail_history)
    _assert_test_identity(session)
    with pytest.raises(RuntimeError):
        phieu_nhap.xac_nhan_phieu_nhap(receipt["phieu_nhap"]["id"], session, _actor(ids))

    assert not session.in_transaction(), "business transaction must roll back after a write failure"
    assert _stock(session, models, ids["product_id"]) == 10


def test_it_006_issue_failure_rolls_back_without_partial_stock_update(db, business_modules, monkeypatch):
    models, _, _, _, phieu_xuat = business_modules
    session, ids = db
    _assert_test_identity(session)
    issue = phieu_xuat.create_phieu_xuat(_issue_data(phieu_xuat, ids, quantity=4), session, _actor(ids))

    def fail_history(*_args, **_kwargs):
        raise RuntimeError("injected persistence failure")

    monkeypatch.setattr(phieu_xuat, "LichSuKho", fail_history)
    _assert_test_identity(session)
    with pytest.raises(RuntimeError):
        phieu_xuat.xac_nhan_phieu_xuat(issue["phieu_xuat"]["id"], session, _actor(ids))

    assert not session.in_transaction(), "business transaction must roll back after a write failure"
    assert _stock(session, models, ids["product_id"]) == 10


def test_it_007_mocked_ai_analysis_and_proposal_do_not_change_stock(db, business_modules, monkeypatch):
    models, ai_controller, de_xuat_ai, _, _ = business_modules
    session, ids = db
    before = _stock(session, models, ids["product_id"])
    monkeypatch.setattr(ai_controller, "phan_tich_ton_kho", lambda _data: "mocked analysis")
    monkeypatch.setattr(
        de_xuat_ai,
        "tao_de_xuat_nhap",
        lambda _data: {
            "nhan_xet": "mocked proposal",
            "de_xuat": [{"ma_hang": ids["product_id"], "so_luong_de_xuat": 5, "ly_do": "below minimum"}],
        },
    )

    analysis = ai_controller.ai_phan_tich_ton_kho(session)
    _assert_test_identity(session)
    proposal = de_xuat_ai.tao_de_xuat_ai(session, SimpleNamespace(id=ids["user_id"], role="QuanLy"))

    assert analysis["analysis"] == "mocked analysis"
    assert proposal["success"] is True
    assert _stock(session, models, ids["product_id"]) == before


def test_it_008_duplicate_product_in_issue_is_rejected_before_stock_can_change(db, business_modules):
    models, _, _, _, phieu_xuat = business_modules
    session, ids = db
    duplicate_issue = phieu_xuat.PhieuXuatCreate(
        chi_tiet=[
            phieu_xuat.ChiTietPhieuXuatCreate(ma_hang=ids["product_id"], so_luong=6),
            phieu_xuat.ChiTietPhieuXuatCreate(ma_hang=ids["product_id"], so_luong=5),
        ]
    )

    _assert_test_identity(session)
    with pytest.raises(HTTPException) as error:
        phieu_xuat.create_phieu_xuat(duplicate_issue, session, _actor(ids))

    assert error.value.status_code == 400
    assert _stock(session, models, ids["product_id"]) == 10


def test_it_009_confirmed_receipt_cannot_be_deleted(db, business_modules):
    models, _, _, phieu_nhap, _ = business_modules
    session, ids = db
    _assert_test_identity(session)
    receipt = phieu_nhap.create_phieu_nhap(_receipt_data(phieu_nhap, ids, quantity=4), session, _actor(ids))
    phieu_nhap.xac_nhan_phieu_nhap(receipt["phieu_nhap"]["id"], session, _actor(ids))

    _assert_test_identity(session)
    with pytest.raises(HTTPException) as error:
        phieu_nhap.delete_phieu_nhap(receipt["phieu_nhap"]["id"], session, _actor(ids))

    assert error.value.status_code == 400
    assert _stock(session, models, ids["product_id"]) == 14


def test_it_010_referenced_product_cannot_be_deleted(db, business_modules):
    models, _, _, _, _ = business_modules
    session, ids = db
    hang_hoa = import_module("hang_hoa")

    _assert_test_identity(session)
    with pytest.raises(HTTPException) as error:
        hang_hoa.delete_hang_hoa(ids["product_id"], session)

    assert error.value.status_code == 400
    assert session.get(models.HangHoa, ids["product_id"]) is not None


def test_it_011_concurrent_receipt_confirmation_updates_stock_once(db, business_modules, mysql_engine):
    models, _, _, phieu_nhap, _ = business_modules
    session, ids = db
    _assert_test_identity(session)
    receipt = phieu_nhap.create_phieu_nhap(_receipt_data(phieu_nhap, ids, quantity=4), session, _actor(ids))
    receipt_id = receipt["phieu_nhap"]["id"]
    Session = sessionmaker(bind=mysql_engine, autoflush=False, expire_on_commit=False)

    def confirm_once():
        worker_session = Session()
        try:
            _assert_test_identity(worker_session)
            phieu_nhap.xac_nhan_phieu_nhap(receipt_id, worker_session, _actor(ids))
            return 200
        except HTTPException as error:
            return error.status_code
        finally:
            worker_session.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = [future.result(timeout=15) for future in (executor.submit(confirm_once), executor.submit(confirm_once))]

    assert sorted(results) == [200, 400]

    # The fixture session may still own a REPEATABLE READ snapshot that began
    # when create_phieu_nhap refreshed the draft.  expire_all() clears only
    # SQLAlchemy's identity map; it does not end that database transaction.
    # Use a session created after both workers finish as the committed-data
    # oracle, and verify its database identity before any business query.
    with Session() as committed_session:
        _assert_test_identity(committed_session)
        committed_stock = _stock(committed_session, models, ids["product_id"])
        receipt_status = committed_session.scalar(
            select(models.PhieuNhap.trang_thai).where(
                models.PhieuNhap.id == receipt_id
            )
        )
        history_filters = (
            models.LichSuKho.ma_hang == ids["product_id"],
            models.LichSuKho.loai_giao_dich == "Nhap",
            models.LichSuKho.ghi_chu == f"Nhập kho từ phiếu nhập #{receipt_id}",
        )
        history_count = committed_session.scalar(
            select(func.count()).select_from(models.LichSuKho).where(*history_filters)
        )
        history_quantity = committed_session.scalar(
            select(models.LichSuKho.so_luong).where(*history_filters)
        )

    assert committed_stock == 14
    assert receipt_status == "DaNhap"
    assert history_count == 1
    assert history_quantity == 4


def test_it_012_receipt_and_issue_use_authenticated_actor_not_client_user_id(db, business_modules):
    _, _, _, phieu_nhap, phieu_xuat = business_modules
    session, ids = db
    actor = _actor(ids)
    receipt_data = phieu_nhap.PhieuNhapCreate(
        ma_ncc=ids["supplier_id"],
        ma_tai_khoan=999999,
        chi_tiet=[phieu_nhap.ChiTietPhieuNhapCreate(ma_hang=ids["product_id"], so_luong=1, don_gia=100)],
    )
    issue_data = phieu_xuat.PhieuXuatCreate(
        ma_tai_khoan=999999,
        chi_tiet=[phieu_xuat.ChiTietPhieuXuatCreate(ma_hang=ids["product_id"], so_luong=1)],
    )

    _assert_test_identity(session)
    receipt = phieu_nhap.create_phieu_nhap(receipt_data, session, actor)
    issue = phieu_xuat.create_phieu_xuat(issue_data, session, actor)

    assert receipt["phieu_nhap"]["ma_tai_khoan"] == actor.id
    assert issue["phieu_xuat"]["ma_tai_khoan"] == actor.id
