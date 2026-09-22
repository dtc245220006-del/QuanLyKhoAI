import { useEffect, useState } from "react";
import api from "../api";

function AIPhanTich() {
  const [analysis, setAnalysis] = useState("");
  const [inventoryData, setInventoryData] = useState([]);
  const [proposals, setProposals] = useState([]);

  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [loadingProposal, setLoadingProposal] = useState(false);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const user = JSON.parse(
    localStorage.getItem("user") || "{}"
  );

  // =====================================================
  // PHÂN TÍCH TỒN KHO
  // =====================================================

  const analyzeInventory = async () => {
    try {
      setLoadingAnalysis(true);
      setError("");
      setMessage("");

      const response = await api.get(
        "/ai/phan-tich-ton-kho"
      );

      setInventoryData(
        response.data.data || []
      );

      setAnalysis(
        response.data.analysis || ""
      );

      setMessage(
        "AI đã phân tích dữ liệu tồn kho"
      );

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Không thể phân tích tồn kho"
      );
    } finally {
      setLoadingAnalysis(false);
    }
  };

  // =====================================================
  // LẤY DANH SÁCH ĐỀ XUẤT
  // =====================================================

  const loadProposals = async () => {
    try {
      const response = await api.get(
        "/de-xuat-ai"
      );

      setProposals(response.data);

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Không thể tải đề xuất AI"
      );
    }
  };

  useEffect(() => {
    loadProposals();
  }, []);

  // =====================================================
  // TẠO ĐỀ XUẤT TỪ GEMINI
  // =====================================================

  const createProposal = async () => {
    if (!user.id) {
      setError(
        "Không xác định được tài khoản hiện tại"
      );
      return;
    }

    try {
      setLoadingProposal(true);
      setError("");
      setMessage("");

      const response = await api.post(
        `/de-xuat-ai?ma_tai_khoan=${user.id}`
      );

      if (response.data.de_xuat) {
        setMessage(
          "Gemini đã tạo đề xuất nhập hàng"
        );
      } else {
        setMessage(
          response.data.message ||
          "Gemini không đề xuất nhập hàng"
        );
      }

      await loadProposals();

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Không thể tạo đề xuất AI"
      );
    } finally {
      setLoadingProposal(false);
    }
  };

  // =====================================================
  // DUYỆT
  // =====================================================

  const approveProposal = async (id) => {
    const ok = window.confirm(
      "Bạn có chắc muốn duyệt đề xuất này?"
    );

    if (!ok) return;

    try {
      setError("");
      setMessage("");

      await api.put(
        `/de-xuat-ai/${id}/duyet`
      );

      setMessage(
        "Đã duyệt đề xuất AI"
      );

      await loadProposals();

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Không thể duyệt đề xuất"
      );
    }
  };

  // =====================================================
  // TỪ CHỐI
  // =====================================================

  const rejectProposal = async (id) => {
    const ok = window.confirm(
      "Bạn có chắc muốn từ chối đề xuất này?"
    );

    if (!ok) return;

    try {
      setError("");
      setMessage("");

      await api.put(
        `/de-xuat-ai/${id}/tu-choi`
      );

      setMessage(
        "Đã từ chối đề xuất AI"
      );

      await loadProposals();

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Không thể từ chối đề xuất"
      );
    }
  };

  // =====================================================
  // TRẠNG THÁI
  // =====================================================

  const getStatus = (status) => {
    switch (status) {
      case "ChoDuyet":
        return {
          text: "Chờ duyệt",
          className: "ai-status-pending",
        };

      case "DaDuyet":
        return {
          text: "Đã duyệt",
          className: "ai-status-approved",
        };

      case "TuChoi":
        return {
          text: "Từ chối",
          className: "ai-status-rejected",
        };

      case "DaTaoPhieuNhap":
        return {
          text: "Đã tạo phiếu nhập",
          className: "ai-status-created",
        };

      default:
        return {
          text: status,
          className: "ai-status-pending",
        };
    }
  };

  return (
    <div>

      {/* =================================================
          HEADER
      ================================================= */}

      <div className="page-header">

        <div>
          <h1>AI phân tích tồn kho</h1>

          <p>
            Gemini phân tích tình trạng tồn kho
            và hỗ trợ đề xuất nhập hàng
          </p>
        </div>

        <button
          className="primary-button ai-main-button"
          onClick={analyzeInventory}
          disabled={loadingAnalysis}
        >
          {loadingAnalysis
            ? "Đang phân tích..."
            : "🤖 Phân tích ngay"}
        </button>

      </div>

      {message && (
        <div className="success-message">
          {message}
        </div>
      )}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* =================================================
          TỔNG QUAN DỮ LIỆU ĐƯỢC GỬI AI
      ================================================= */}

      <div className="ai-summary-grid">

        <div className="ai-summary-card">

          <span className="ai-summary-icon">
            📦
          </span>

          <div>
            <small>Mặt hàng được phân tích</small>

            <strong>
              {inventoryData.length}
            </strong>
          </div>

        </div>

        <div className="ai-summary-card">

          <span className="ai-summary-icon warning">
            ⚠️
          </span>

          <div>
            <small>Hàng dưới mức tối thiểu</small>

            <strong>
              {
                inventoryData.filter(
                  (item) =>
                    Number(item.so_luong_ton) <
                    Number(item.ton_toi_thieu)
                ).length
              }
            </strong>
          </div>

        </div>

        <div className="ai-summary-card">

          <span className="ai-summary-icon">
            🤖
          </span>

          <div>
            <small>Đề xuất AI</small>

            <strong>
              {proposals.length}
            </strong>
          </div>

        </div>

      </div>

      {/* =================================================
          KẾT QUẢ AI
      ================================================= */}

      <div className="ai-result-card">

        <div className="ai-card-header">

          <div>
            <h2>Phân tích từ Gemini</h2>

            <p>
              Kết quả được sinh từ dữ liệu tồn kho
              hiện tại
            </p>
          </div>

        </div>

        {analysis ? (
          <div className="ai-analysis-content">
            {analysis}
          </div>
        ) : (
          <div className="ai-empty">
            <div>🤖</div>

            <strong>
              Chưa có kết quả phân tích
            </strong>

            <p>
              Bấm "Phân tích ngay" để Gemini
              phân tích tình trạng kho.
            </p>
          </div>
        )}

      </div>

      {/* =================================================
          DỮ LIỆU TỒN KHO
      ================================================= */}

      {inventoryData.length > 0 && (
        <div className="ai-result-card">

          <div className="ai-card-header">

            <div>
              <h2>Dữ liệu tồn kho được phân tích</h2>
            </div>

          </div>

          <div className="table-card ai-table">

            <table>

              <thead>
                <tr>
                  <th>Mã hàng</th>
                  <th>Tên hàng</th>
                  <th>Tồn hiện tại</th>
                  <th>Tồn tối thiểu</th>
                  <th>Trạng thái</th>
                </tr>
              </thead>

              <tbody>

                {inventoryData.map((item) => {

                  const low =
                    Number(item.so_luong_ton) <
                    Number(item.ton_toi_thieu);

                  return (
                    <tr key={item.ma_hang}>

                      <td>
                        #{item.ma_hang}
                      </td>

                      <td>
                        <strong>
                          {item.ten_hang}
                        </strong>
                      </td>

                      <td>
                        {item.so_luong_ton}
                      </td>

                      <td>
                        {item.ton_toi_thieu}
                      </td>

                      <td>
                        {low ? (
                          <span className="stock-status low-status">
                            ⚠️ Cần chú ý
                          </span>
                        ) : (
                          <span className="stock-status normal-status">
                            ✓ Bình thường
                          </span>
                        )}
                      </td>

                    </tr>
                  );
                })}

              </tbody>

            </table>

          </div>

        </div>
      )}

      {/* =================================================
          ĐỀ XUẤT AI
      ================================================= */}

      <div className="ai-result-card">

        <div className="ai-card-header">

          <div>
            <h2>Đề xuất nhập hàng</h2>

            <p>
              Quản lý xem và quyết định duyệt
              đề xuất từ AI
            </p>
          </div>

          {user.username === "admin" && (
            <button
              className="secondary-button"
              onClick={createProposal}
              disabled={loadingProposal}
            >
              {loadingProposal
                ? "Đang tạo..."
                : "✨ Tạo đề xuất từ Gemini"}
            </button>
          )}

        </div>

        {proposals.length === 0 ? (
          <div className="ai-empty">

            <div>📋</div>

            <strong>
              Chưa có đề xuất AI
            </strong>

            <p>
              Hãy phân tích tồn kho và tạo
              đề xuất nhập hàng.
            </p>

          </div>
        ) : (
          <div className="proposal-list">

            {proposals.map((proposal) => {

              const status = getStatus(
                proposal.trang_thai
              );

              return (
                <div
                  className="proposal-card"
                  key={proposal.id}
                >

                  <div className="proposal-top">

                    <div>

                      <span className="proposal-id">
                        Đề xuất #{proposal.id}
                      </span>

                      <h3>
                        Đề xuất nhập hàng từ AI
                      </h3>

                      <small>
                        {proposal.ngay_tao}
                      </small>

                    </div>

                    <span
                      className={`ai-status ${status.className}`}
                    >
                      {status.text}
                    </span>

                  </div>

                  {proposal.noi_dung && (
                    <p className="proposal-description">
                      {proposal.noi_dung}
                    </p>
                  )}

                  {proposal.chi_tiet &&
                    proposal.chi_tiet.length > 0 && (

                    <div className="proposal-items">

                      {proposal.chi_tiet.map(
                        (item) => (

                          <div
                            className="proposal-item"
                            key={item.id}
                          >

                            <div>
                              <strong>
                                {item.ma_hang
                                  ? `Mã hàng #${item.ma_hang}`
                                  : "Hàng hóa"}
                              </strong>

                              <small>
                                {item.ly_do ||
                                  "AI đề xuất nhập bổ sung"}
                              </small>
                            </div>

                            <strong className="proposal-quantity">
                              +{item.so_luong_de_xuat}
                            </strong>

                          </div>

                        )
                      )}

                    </div>
                  )}

                  {proposal.trang_thai ===
                    "ChoDuyet" &&
                    user.username === "admin" && (

                    <div className="proposal-actions">

                      <button
                        className="approve-button"
                        onClick={() =>
                          approveProposal(
                            proposal.id
                          )
                        }
                      >
                        ✓ Duyệt đề xuất
                      </button>

                      <button
                        className="reject-button"
                        onClick={() =>
                          rejectProposal(
                            proposal.id
                          )
                        }
                      >
                        Từ chối
                      </button>

                    </div>
                  )}

                </div>
              );
            })}

          </div>
        )}

      </div>

    </div>
  );
}

export default AIPhanTich;