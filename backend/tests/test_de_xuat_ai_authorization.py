"""API authorization tests for AI-proposal approval and draft receipt creation.

The tests use FastAPI dependency overrides and an in-memory fake session. They
exercise JWT/role dependencies without connecting to MySQL or Gemini.
"""

import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(PROJECT_DIR))

os.environ["JWT_SECRET_KEY"] = "test-jwt-secret"
os.environ["GEMINI_API_KEY"] = "test-gemini-key"
os.environ["DB_USER"] = "qlk_test_user"
os.environ["DB_PASSWORD"] = "test-only-password"
os.environ["DB_NAME"] = "quanlykho_test"

import auth
import de_xuat_ai
from models import ChiTietDeXuatAI, DeXuatAI, HangHoa, NhaCungCap, PhieuNhap, User


class FakeQuery:
    def __init__(self, session, model):
        self.session = session
        self.model = model
        self.criteria = []

    def filter(self, *criteria):
        self.criteria.extend(criteria)
        return self

    def order_by(self, *args):
        return self

    def first(self):
        if self.model is User:
            username = self.criteria[-1].right.value
            return self.session.users.get(username)
        if self.model is DeXuatAI:
            return self.session.proposal
        if self.model is NhaCungCap:
            return self.session.supplier
        if self.model is HangHoa:
            return self.session.product
        return None

    def all(self):
        if self.model is ChiTietDeXuatAI:
            return self.session.proposal_items
        return []


class FakeSession:
    def __init__(self, proposal_status="ChoDuyet"):
        self.users = {
            "manager": SimpleNamespace(id=1, username="manager", role="QuanLy"),
            "keeper": SimpleNamespace(id=2, username="keeper", role="ThuKho"),
            "accountant": SimpleNamespace(id=3, username="accountant", role="KeToan"),
        }
        self.proposal = SimpleNamespace(id=10, trang_thai=proposal_status)
        self.supplier = SimpleNamespace(id=20)
        self.product = SimpleNamespace(id=30, ten_hang="Chuot", gia_nhap=100)
        self.proposal_items = [
            SimpleNamespace(ma_hang=30, so_luong_de_xuat=4, ly_do="Ton thap")
        ]
        self.added = []
        self.commits = 0
        self.stock_snapshot = {30: 7}

    def query(self, model):
        return FakeQuery(self, model)

    def add(self, item):
        self.added.append(item)

    def flush(self):
        for item in self.added:
            if isinstance(item, PhieuNhap) and item.id is None:
                item.id = 99

    def commit(self):
        self.commits += 1

    def refresh(self, item):
        return None


@pytest.fixture
def api_factory():
    def build(session):
        app = FastAPI()
        app.include_router(de_xuat_ai.router)
        app.dependency_overrides[de_xuat_ai.get_db] = lambda: session
        app.dependency_overrides[auth.get_db] = lambda: session
        return TestClient(app)

    return build


def bearer_for(username):
    user = {"manager": ("QuanLy"), "keeper": ("ThuKho"), "accountant": ("KeToan")}[username]
    token = auth.create_access_token(username, user)
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize(
    "path",
    [
        "/de-xuat-ai/10/duyet",
        "/de-xuat-ai/10/tu-choi",
        "/de-xuat-ai/10/tao-phieu-nhap?ma_ncc=20",
    ],
)
def test_mutating_proposal_endpoints_require_bearer_token(api_factory, path):
    session = FakeSession()

    if path.endswith("duyet") or path.endswith("tu-choi"):
        response = api_factory(session).put(path)
    else:
        response = api_factory(session).post(path)

    assert response.status_code == 401
    assert session.proposal.trang_thai == "ChoDuyet"
    assert session.commits == 0


def test_approval_rejects_invalid_token_without_state_change(api_factory):
    session = FakeSession()

    response = api_factory(session).put(
        "/de-xuat-ai/10/duyet",
        headers={"Authorization": "Bearer not-a-valid-token"},
    )

    assert response.status_code == 401
    assert session.proposal.trang_thai == "ChoDuyet"
    assert session.commits == 0


@pytest.mark.parametrize("endpoint", ["duyet", "tu-choi"])
@pytest.mark.parametrize("username", ["keeper", "accountant"])
def test_only_manager_can_change_proposal_status(api_factory, endpoint, username):
    session = FakeSession()

    response = api_factory(session).put(
        f"/de-xuat-ai/10/{endpoint}", headers=bearer_for(username)
    )

    assert response.status_code == 403
    assert session.proposal.trang_thai == "ChoDuyet"
    assert session.commits == 0


@pytest.mark.parametrize(
    ("endpoint", "expected_status"),
    [("duyet", "DaDuyet"), ("tu-choi", "TuChoi")],
)
def test_manager_can_change_pending_proposal_status(api_factory, endpoint, expected_status):
    session = FakeSession()

    response = api_factory(session).put(
        f"/de-xuat-ai/10/{endpoint}", headers=bearer_for("manager")
    )

    assert response.status_code == 200
    assert response.json()["trang_thai"] == expected_status
    assert session.proposal.trang_thai == expected_status
    assert session.commits == 1


@pytest.mark.parametrize("username", ["manager", "accountant"])
def test_only_warehouse_keeper_can_create_draft_receipt(api_factory, username):
    session = FakeSession(proposal_status="DaDuyet")
    stock_before = session.stock_snapshot.copy()

    response = api_factory(session).post(
        "/de-xuat-ai/10/tao-phieu-nhap?ma_ncc=20&ma_tai_khoan=1",
        headers=bearer_for(username),
    )

    assert response.status_code == 403
    assert session.proposal.trang_thai == "DaDuyet"
    assert not session.added
    assert session.commits == 0
    assert session.stock_snapshot == stock_before


@pytest.mark.parametrize("proposal_status", ["ChoDuyet", "TuChoi"])
def test_draft_receipt_requires_approved_proposal(api_factory, proposal_status):
    session = FakeSession(proposal_status=proposal_status)
    stock_before = session.stock_snapshot.copy()

    response = api_factory(session).post(
        "/de-xuat-ai/10/tao-phieu-nhap?ma_ncc=20",
        headers=bearer_for("keeper"),
    )

    assert response.status_code == 400
    assert session.proposal.trang_thai == proposal_status
    assert not session.added
    assert session.commits == 0
    assert session.stock_snapshot == stock_before


def test_warehouse_keeper_creates_draft_without_changing_stock(api_factory):
    session = FakeSession(proposal_status="DaDuyet")
    stock_before = session.stock_snapshot.copy()

    response = api_factory(session).post(
        "/de-xuat-ai/10/tao-phieu-nhap?ma_ncc=20&ma_tai_khoan=1",
        headers=bearer_for("keeper"),
    )

    assert response.status_code == 200
    draft = next(item for item in session.added if isinstance(item, PhieuNhap))
    assert draft.ma_tai_khoan == 2
    assert draft.trang_thai == "Nhap"
    assert session.proposal.trang_thai == "DaTaoPhieuNhap"
    assert session.commits == 1
    assert session.stock_snapshot == stock_before
