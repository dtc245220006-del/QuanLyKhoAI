import { useEffect, useState } from "react";
import api from "../api";

function TonKho() {
  const [items, setItems] = useState([]);
  const [warnings, setWarnings] = useState([]);

  const [search, setSearch] = useState("");
  const [showWarningOnly, setShowWarningOnly] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // =====================================================
  // LOAD TỒN KHO
  // =====================================================

  const loadData = async () => {
    try {
      setLoading(true);
      setError("");

      const [tonKhoRes, warningRes] =
        await Promise.all([
          api.get("/ton-kho"),
          api.get("/ton-kho/canh-bao/thap"),
        ]);

      setItems(tonKhoRes.data);
      setWarnings(warningRes.data);

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Không thể tải dữ liệu tồn kho"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // =====================================================
  // LỌC
  // =====================================================

  const filteredItems = items.filter((item) => {
    const keyword = search.toLowerCase().trim();

    const matchesSearch =
      !keyword ||
      item.ten_hang?.toLowerCase().includes(keyword) ||
      String(item.ma_hang).includes(keyword);

    const matchesWarning =
      !showWarningOnly ||
      item.canh_bao === true ||
      Number(item.so_luong) <
        Number(item.ton_toi_thieu);

    return matchesSearch && matchesWarning;
  });

  // =====================================================
  // FORMAT
  // =====================================================

  const isLowStock = (item) => {
    return (
      Number(item.so_luong) <
      Number(item.ton_toi_thieu)
    );
  };

  // =====================================================
  // UI
  // =====================================================

  return (
    <div>

      {/* HEADER */}

      <div className="page-header">

        <div>
          <h1>Tồn kho</h1>

          <p>
            Theo dõi số lượng hàng hóa hiện tại
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={loadData}
          disabled={loading}
        >
          ↻ Làm mới
        </button>

      </div>


      {/* SUMMARY */}

      <div className="inventory-summary">

        <div className="inventory-summary-card">
          <span className="inventory-summary-icon">
            📦
          </span>

          <div>
            <small>Tổng mặt hàng</small>

            <strong>
              {items.length}
            </strong>
          </div>
        </div>


        <div className="inventory-summary-card">
          <span className="inventory-summary-icon warning">
            ⚠️
          </span>

          <div>
            <small>Hàng tồn thấp</small>

            <strong className="warning-number">
              {warnings.length}
            </strong>
          </div>
        </div>


        <div className="inventory-summary-card">
          <span className="inventory-summary-icon">
            📋
          </span>

          <div>
            <small>Tổng số lượng tồn</small>

            <strong>
              {items.reduce(
                (sum, item) =>
                  sum + Number(item.so_luong || 0),
                0
              )}
            </strong>
          </div>
        </div>

      </div>


      {/* ERROR */}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}


      {/* FILTER */}

      <div className="inventory-toolbar">

        <div className="inventory-search">

          <span>🔎</span>

          <input
            type="text"
            placeholder="Tìm theo mã hoặc tên hàng..."
            value={search}
            onChange={(e) =>
              setSearch(e.target.value)
            }
          />

        </div>


        <button
          className={
            showWarningOnly
              ? "warning-filter active"
              : "warning-filter"
          }
          onClick={() =>
            setShowWarningOnly(
              !showWarningOnly
            )
          }
        >
          ⚠️ Chỉ xem hàng tồn thấp
        </button>

      </div>


      {/* TABLE */}

      <div className="table-card inventory-table">

        <table>

          <thead>
            <tr>
              <th>Mã hàng</th>
              <th>Tên hàng</th>
              <th>Số lượng tồn</th>
              <th>Tồn tối thiểu</th>
              <th>Trạng thái</th>
              <th>Cập nhật</th>
            </tr>
          </thead>

          <tbody>

            {loading ? (
              <tr>
                <td
                  colSpan="6"
                  className="empty-cell"
                >
                  Đang tải dữ liệu...
                </td>
              </tr>
            ) : filteredItems.length === 0 ? (
              <tr>
                <td
                  colSpan="6"
                  className="empty-cell"
                >
                  Không tìm thấy dữ liệu phù hợp
                </td>
              </tr>
            ) : (
              filteredItems.map((item) => {

                const lowStock =
                  isLowStock(item);

                return (
                  <tr key={item.id}>

                    <td>
                      <strong>
                        #{item.ma_hang}
                      </strong>
                    </td>

                    <td>
                      <strong>
                        {item.ten_hang}
                      </strong>
                    </td>

                    <td>
                      <span
                        className={
                          lowStock
                            ? "stock-number low"
                            : "stock-number"
                        }
                      >
                        {item.so_luong}
                      </span>
                    </td>

                    <td>
                      {item.ton_toi_thieu}
                    </td>

                    <td>

                      {lowStock ? (
                        <span className="stock-status low-status">
                          ⚠️ Tồn thấp
                        </span>
                      ) : (
                        <span className="stock-status normal-status">
                          ✓ Bình thường
                        </span>
                      )}

                    </td>

                    <td>
                      <span className="inventory-date">
                        {item.ngay_cap_nhat || "—"}
                      </span>
                    </td>

                  </tr>
                );
              })
            )}

          </tbody>

        </table>

      </div>


      {/* WARNING */}

      {warnings.length > 0 && (

        <div className="inventory-warning-box">

          <div className="inventory-warning-title">
            ⚠️ Cảnh báo tồn kho
          </div>

          <p>
            Có <strong>{warnings.length}</strong> mặt hàng
            đang thấp hơn mức tồn tối thiểu.
            Bạn nên kiểm tra và cân nhắc nhập bổ sung.
          </p>

        </div>

      )}

    </div>
  );
}

export default TonKho;