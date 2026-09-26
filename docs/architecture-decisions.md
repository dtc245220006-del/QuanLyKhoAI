# Architecture Decisions

## ADR-001 — FastAPI + React
Giữ kiến trúc client/server vì frontend hiện tại đã sử dụng React và backend hiện tại dùng FastAPI.

## ADR-002 — MySQL dùng thống nhất
Bài Multi-Agent yêu cầu MySQL, vì vậy database ứng dụng được định hướng thống nhất về MySQL `quan_ly_kho`.

## ADR-003 — Multi-Agent module tách khỏi nghiệp vụ kho
Multi-Agent được tách module để giảm ảnh hưởng tới các API CRUD đang chạy.

## ADR-004 — Critic kiểm chứng trước Response
Critic là checkpoint để giảm hallucination và phát hiện claim không khớp DB.

## ADR-005 — Retry có giới hạn
Retry tối đa 2 lần để tránh vòng lặp vô hạn.
