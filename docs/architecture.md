# Architecture — QuanLyKhoAI

```text
React Frontend
      |
      v
FastAPI REST API
      |
      +--> Authentication / Authorization
      +--> Warehouse Services
      +--> Gemini AI Analysis
      +--> AI Proposal Workflow
      +--> Multi-Agent Router
                  |
                  v
             Orchestrator
                  |
        +---------+---------+
        |                   |
     Analyst            Database Agent
        |                   |
        |                SQL Tool
        |                   |
        +-------+-----------+
                |
             RAG Agent
                |
          Vector Search Tool
                |
             Reasoning
                |
              Critic
                |
          reject -> retry
                |
             Response
```

## Database
MySQL `quan_ly_kho` dùng chung cho module kho và SQL Tool của Multi-Agent.

## AI boundary
AI đọc dữ liệu cần thiết để phân tích. Việc thay đổi TonKho/LichSuKho chỉ xảy ra qua API nghiệp vụ sau khi người dùng thực hiện/ xác nhận giao dịch.
