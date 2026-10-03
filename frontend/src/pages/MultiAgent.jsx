import { useState } from "react";
import api from "../api";
import "./MultiAgent.css";

function MultiAgent() {
  const [question, setQuestion] = useState("Hàng nào đang dưới mức tồn tối thiểu?");
  const [loading, setLoading] = useState(false);
  const [singleLoading, setSingleLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [singleResult, setSingleResult] = useState(null);
  const [error, setError] = useState("");
  const [singleError, setSingleError] = useState("");

  const runAdvisor = async () => {
    if (!question.trim()) {
      setError("Vui lòng nhập câu hỏi.");
      return;
    }
    try {
      setLoading(true);
      setError("");
      const response = await api.post("/multi-agent/advisor", {
        question: question.trim(),
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Không thể chạy Multi-Agent.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const runSingleAgent = async () => {
    if (!question.trim()) {
      setSingleError("Vui lòng nhập câu hỏi.");
      return;
    }
    try {
      setSingleLoading(true);
      setSingleError("");
      const response = await api.post("/multi-agent/single-agent/advisor", {
        question: question.trim(),
      });
      setSingleResult(response.data);
    } catch (err) {
      setSingleError(
        err.response?.data?.detail || "Không thể chạy Single-Agent.",
      );
      setSingleResult(null);
    } finally {
      setSingleLoading(false);
    }
  };

  return (
    <div className="multi-agent-page">
      <div className="page-header">
        <div>
          <h1>Multi-Agent AI</h1>
          <p>Orchestrator điều phối các Agent để phân tích và kiểm chứng dữ liệu kho.</p>
        </div>
      </div>

      <div className="ma-flow">
        <span>Orchestrator</span><b>→</b><span>Analyst</span><b>→</b>
        <span>SQL + RAG</span><b>→</b><span>Reasoning</span><b>→</b>
        <span>Critic</span><b>→</b><span>Response</span>
      </div>

      <section className="ma-card">
        <h2>Đặt câu hỏi cho hệ thống</h2>
        <div className="ma-samples">
          {[
            "Hàng nào đang dưới mức tồn tối thiểu?",
            "Cho tôi xem tồn kho hiện tại.",
            "Có những mặt hàng nào trong kho?",
          ].map((item) => (
            <button key={item} className="ma-sample" onClick={() => setQuestion(item)}>
              {item}
            </button>
          ))}
        </div>

        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          rows={4}
          placeholder="Nhập câu hỏi về kho..."
        />

        <div className="ma-actions">
          <button
            className="primary-button"
            onClick={runAdvisor}
            disabled={loading || singleLoading}
          >
            {loading ? "Đang chạy workflow..." : "🤖 Chạy Multi-Agent"}
          </button>
          <button
            className="secondary-button"
            onClick={runSingleAgent}
            disabled={loading || singleLoading}
          >
            {singleLoading ? "Đang chạy..." : "🧩 Chạy Single-Agent"}
          </button>
        </div>
      </section>

      {error && <div className="error-message">{error}</div>}
      {singleError && <div className="error-message">{singleError}</div>}

      {result && (
        <>
          <div className="ma-metrics">
            <div><small>Multi-Agent Task ID</small><strong>{result.task_id}</strong></div>
            <div><small>Trạng thái</small><strong>{result.status}</strong></div>
            <div><small>Retry</small><strong>{result.retry_count}</strong></div>
            <div><small>Response time</small><strong>{result.time_ms ?? "-"} ms</strong></div>
            <div><small>LLM calls</small><strong>{result.llm_calls ?? "-"} lần</strong></div>
          </div>

          <section className="ma-card">
            <h2>Phản hồi Multi-Agent</h2>
            <div className="ma-answer">{result.answer}</div>
          </section>

          <section className="ma-card">
            <h2>Dữ liệu SQL Tool truy xuất</h2>
            {result.data?.length ? (
              <div className="table-wrapper">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Mã hàng</th>
                      <th>Tên hàng</th>
                      <th>Nhóm</th>
                      <th>Tồn</th>
                      <th>Tối thiểu</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.data.map((item) => (
                      <tr key={item.ma_hang}>
                        <td>{item.ma_hang}</td>
                        <td>{item.ten_hang}</td>
                        <td>{item.ten_nhom || "-"}</td>
                        <td>{item.so_luong_ton}</td>
                        <td>{item.ton_toi_thieu}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="empty-state">Không có dữ liệu phù hợp.</p>
            )}
          </section>

          <section className="ma-card">
            <h2>Knowledge Base / RAG</h2>
            {result.knowledge?.length ? (
              <ul className="ma-knowledge">
                {result.knowledge.map((doc, index) => <li key={index}>{doc.text}</li>)}
              </ul>
            ) : (
              <p className="empty-state">Không có tài liệu RAG.</p>
            )}
          </section>

          <section className="ma-card">
            <h2>Critic Agent</h2>
            <p>Trạng thái: <strong>{result.critic?.status || "-"}</strong></p>
            {result.critic?.errors?.length ? (
              <ul>
                {result.critic.errors.map((err, index) => <li key={index}>{err}</li>)}
              </ul>
            ) : (
              <p>Không phát hiện claim sai theo dữ liệu đã kiểm tra.</p>
            )}
          </section>
        </>
      )}

      {singleResult && (
        <>
          <div className="ma-metrics">
            <div><small>Single-Agent</small><strong>{singleResult.status}</strong></div>
            <div><small>Response time</small><strong>{singleResult.time_ms ?? "-"} ms</strong></div>
            <div><small>LLM calls</small><strong>{singleResult.llm_calls ?? "-"} lần</strong></div>
            <div>
              <small>Test Oracle</small>
              <strong>{singleResult.accuracy_check?.valid ? "Đạt" : "Không đạt"}</strong>
            </div>
            <div>
              <small>Claims</small>
              <strong>{singleResult.claims?.length ?? 0}</strong>
            </div>
          </div>

          <section className="ma-card">
            <h2>Phản hồi Single-Agent</h2>
            <div className="ma-answer">{singleResult.answer}</div>
          </section>
        </>
      )}
    </div>
  );
}

export default MultiAgent;
