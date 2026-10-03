import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
CHROMA_PATH = os.getenv(
    "CHROMA_PATH",
    str(BASE_DIR / "data" / "chroma_db")
)
MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL",
    "all-MiniLM-L6-v2"
)

_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _client.get_or_create_collection(
    name="warehouse_knowledge"
)

_encoder = None

DEFAULT_DOCS = [
    "Hàng hóa có số lượng tồn thấp hơn mức tồn tối thiểu cần được kiểm tra để đề xuất nhập bổ sung.",
    "Quản lý là người xem xét và duyệt hoặc từ chối đề xuất nhập hàng do AI tạo.",
    "Thủ kho thực hiện nghiệp vụ nhập kho sau khi đề xuất AI đã được duyệt.",
    "Chỉ khi phiếu nhập được xác nhận thì số lượng tồn kho mới được cập nhật.",
    "AI chỉ có vai trò phân tích và đề xuất, không được trực tiếp thay đổi dữ liệu kho.",
]


def _get_encoder():
    global _encoder

    if _encoder is None:
        # Chỉ import khi thực sự cần dùng RAG
        from sentence_transformers import SentenceTransformer

        _encoder = SentenceTransformer(MODEL_NAME)

    return _encoder


def ensure_seeded():
    existing = _collection.count()

    if existing:
        return

    embeddings = _get_encoder().encode(DEFAULT_DOCS).tolist()

    _collection.add(
        ids=[f"doc-{i}" for i in range(len(DEFAULT_DOCS))],
        documents=DEFAULT_DOCS,
        embeddings=embeddings,
    )


def search_knowledge(question: str, top_k: int = 4):
    ensure_seeded()

    embedding = _get_encoder().encode([question]).tolist()

    result = _collection.query(
        query_embeddings=embedding,
        n_results=top_k
    )

    docs = result.get("documents", [[]])[0]

    return [{"text": text} for text in docs]