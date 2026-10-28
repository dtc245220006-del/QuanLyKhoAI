# Multi-Agent & Single-Agent — QuanLyKhoAI

Module AI trợ lý cho hệ thống quản lý kho. **Không thay thế** các API nhập/xuất/tồn kho và **không trực tiếp cập nhật** `TonKho`/`LichSuKho`.

## Kiến trúc thực tế

Multi-Agent: **Orchestrator → Analyst → Database Agent/SQL Tool + RAG Agent/Vector Search → Reasoning → Critic → Retry (tối đa 2 lần) → Response**.

Có 7 Agent (Orchestrator, Analyst, Database, RAG, Reasoning, Critic, Response); SQL Tool truy vấn MySQL `quan_ly_kho` với tham số, Vector Search dùng ChromaDB + SentenceTransformer. Câu trả lời dùng Gemini theo cấu hình runtime.

Single-Agent baseline: Question → SQL Tool + Vector Search Tool → Gemini → Answer.

## API

- `POST /multi-agent/advisor` — Multi-Agent.
- `POST /multi-agent/single-agent/advisor` — Single-Agent baseline.

Hai endpoint yêu cầu JWT (Bearer). Body: `{"question":"Hàng nào đang dưới mức tồn tối thiểu?"}`.

Backend FastAPI chạy tại `http://127.0.0.1:8000`; xem [hướng dẫn chạy](../docs/deployment.md).

## Kiểm thử

Có **20 unit/Agent tests** trong `multi_agent/multi_agent/tests/`. Tổng repo còn có **15 API authorization tests** và **6 MySQL integration tests** = **41 automated tests**, từng được nhóm ghi nhận PASS trên máy Windows, không phải kết quả CI. Lệnh chạy đúng thư mục/package ở [README](../README.md) và [Test Report](../docs/test-report.md).

## Benchmark

Tại thư mục `multi_agent`:

```powershell
python -m multi_agent.benchmark
```

Kết quả lưu `multi_agent/multi_agent_benchmark.json`. Lượt đo 10 câu đã ghi nhận Test Oracle 10/10 cho cả hai kiến trúc; thời gian TB Single-Agent **2732,84 ms**, Multi-Agent **1488,47 ms** và lần gọi Gemini TB **1 so với 3**. Đây là một lượt đo với dữ liệu/model tại thời điểm chạy; không khẳng định Multi-Agent luôn nhanh hơn. Xem [benchmark-guide](../docs/benchmark-guide.md) và [comparison](../docs/multi-agent-comparison.md).

## AI Skills và an toàn

`.agents/skills/` ở root là chỉ dẫn dành cho AI hỗ trợ phát triển phần mềm; **không** phải các Agent chạy trong module này. Không đưa secrets vào prompt/log; AI chỉ tư vấn, không xác nhận phiếu hoặc tự mutate kho.
