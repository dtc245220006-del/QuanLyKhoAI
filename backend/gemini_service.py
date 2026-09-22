import json
import os
import re
import time

from dotenv import load_dotenv
from google import genai


# =========================================================
# CẤU HÌNH GEMINI
# =========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "Chưa cấu hình GEMINI_API_KEY trong file .env"
    )

client = genai.Client(
    api_key=GEMINI_API_KEY
)

MODEL_NAME = "gemini-3.1-flash-lite"


# =========================================================
# HÀM PARSE JSON TỪ GEMINI
# =========================================================

def _parse_json_response(text: str):
    text = text.strip()

    # Trường hợp Gemini trả:
    # ```json
    # {...}
    # ```
    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^```\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Trường hợp Gemini có thêm text trước/sau JSON
    match = re.search(
        r"\{.*\}",
        text,
        flags=re.DOTALL
    )

    if not match:
        raise ValueError(
            "Gemini không trả về JSON hợp lệ"
        )

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Không thể đọc JSON từ Gemini: {e}"
        )


# =========================================================
# PHÂN TÍCH TỒN KHO
# =========================================================

def phan_tich_ton_kho(du_lieu_ton_kho):

    prompt = f"""
Bạn là AI hỗ trợ quản lý kho.

Dữ liệu tồn kho:

{json.dumps(
    du_lieu_ton_kho,
    ensure_ascii=False,
    indent=2
)}

Hãy phân tích:

1. Hàng nào đang dưới mức tồn tối thiểu.
2. Hàng nào có tồn kho cao.
3. Nhận xét tình trạng kho.
4. Đưa ra đề xuất nhập hàng nếu cần.

Không được tự ý thay đổi dữ liệu kho.

Trả lời bằng tiếng Việt.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text


# =========================================================
# TẠO ĐỀ XUẤT NHẬP HÀNG BẰNG GEMINI
# =========================================================

def tao_de_xuat_nhap(du_lieu_ton_kho):

    prompt = f"""
Bạn là AI hỗ trợ quản lý kho.

Dữ liệu tồn kho hiện tại:

{json.dumps(
    du_lieu_ton_kho,
    ensure_ascii=False,
    indent=2
)}

Hãy phân tích dữ liệu và tạo đề xuất nhập hàng.

QUY TẮC:
- Chỉ đề xuất những mặt hàng thực sự cần nhập.
- Nếu tồn kho không cần nhập thì danh sách de_xuat phải rỗng.
- Không được tự ý thay đổi tồn kho.
- Số lượng đề xuất phải là số nguyên dương.
- Không tạo mặt hàng mới.
- Chỉ sử dụng ma_hang có trong dữ liệu đầu vào.

BẮT BUỘC trả về JSON thuần, KHÔNG markdown,
KHÔNG ```json, KHÔNG giải thích bên ngoài JSON.

Định dạng chính xác:

{{
  "nhan_xet": "Nhận xét tổng quan về tình trạng tồn kho",
  "de_xuat": [
    {{
      "ma_hang": 1,
      "ten_hang": "Tên hàng",
      "so_luong_de_xuat": 50,
      "ly_do": "Lý do đề xuất"
    }}
  ]
}}

Dữ liệu đầu vào:
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    if not response.text:
        raise ValueError(
            "Gemini không trả về kết quả"
        )

    return _parse_json_response(
        response.text
    )