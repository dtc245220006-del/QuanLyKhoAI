"""Regression coverage: every warehouse-facing router rejects an anonymous call.

These tests deliberately use only requests without a token.  Authentication
must fail before any database query or Gemini call is made.
"""

import os
import sys
from pathlib import Path

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

import ai_controller
import bao_cao
import de_xuat_ai
import hang_hoa
import lich_su_kho
import nha_cung_cap
import nhom_hang
import phieu_nhap
import phieu_xuat
import ton_kho


@pytest.mark.parametrize(
    ("router", "path"),
    [
        (nhom_hang.router, "/nhom-hang"),
        (hang_hoa.router, "/hang-hoa"),
        (nha_cung_cap.router, "/nha-cung-cap"),
        (ton_kho.router, "/ton-kho"),
        (lich_su_kho.router, "/lich-su-kho"),
        (bao_cao.router, "/bao-cao/dashboard"),
        (phieu_nhap.router, "/phieu-nhap"),
        (phieu_xuat.router, "/phieu-xuat"),
        (de_xuat_ai.router, "/de-xuat-ai"),
        (ai_controller.router, "/ai/phan-tich-ton-kho"),
    ],
)
def test_sec_001_anonymous_call_is_rejected_before_business_logic(router, path):
    app = FastAPI()
    app.include_router(router)

    response = TestClient(app).get(path)

    assert response.status_code == 401
    assert "token" in response.json()["detail"].lower()
