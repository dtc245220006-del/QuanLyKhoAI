import { useEffect, useMemo, useState } from "react";
import api from "../api";

function LichSuKho() {
  const [items, setItems] = useState([]);
  const [search, setSearch] = useState("");
  const [filterType, setFilterType] = useState("ALL");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const loadData = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/lich-su-kho");
      setItems(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Không thể tải lịch sử kho"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const filteredItems = useMemo(() => {
    const keyword = search.toLowerCase().trim();

    return items.filter((item) => {
      const matchesSearch =
        !keyword ||
        item.ten_hang?.toLowerCase().includes(keyword) ||
        String(item.ma_hang).includes(keyword) ||
        item.nguoi_thuc_hien
          ?.toLowerCase()
          .includes(keyword);

      const matchesType =
        filterType === "ALL" ||
        item.loai_giao_dich === filterType;

      return matchesSearch && matchesType;
    });
  }, [items, search, filterType]);

  const totalNhap = items
    .filter((item) => item.loai_giao_dich === "Nhap")
    .reduce(
      (sum, item) => sum + Number(item.so_luong || 0),
      0
    );

  const totalXuat = items
    .filter((item) => item.loai_giao_dich === "Xuat")
    .reduce(
      (sum, item) => sum + Number(item.so_luong || 0),
      0
    );

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Lịch sử kho</h1>
          <p>Theo dõi toàn bộ giao dịch nhập và xuất</p>
        </div>

        <button
          className="secondary-button"
          onClick={loadData}
          disabled={loading}
        >
          ↻ Làm mới
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="history-summary">
        <div className="history-card">
          <span>📋</span>
          <div>
            <small>Tổng giao dịch</small>
            <strong>{items.length}</strong>
          </div>
        </div>

        <div className="history-card">
          <span>📥</span>
          <div>
            <small>Tổng đã nhập</small>
            <strong className="history-in">
              {totalNhap}
            </strong>
          </div>
        </div>

        <div className="history-card">
          <span>📤</span>
          <div>
            <small>Tổng đã xuất</small>
            <strong className="history-out">
              {totalXuat}
            </strong>
          </div>
        </div>
      </div>

      <div className="history-toolbar">
        <div className="inventory-search">
          <span>🔎</span>

          <input
            type="text"
            placeholder="Tìm theo hàng hóa, mã hàng hoặc người thực hiện..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className="history-filters">
          <button
            className={
              filterType === "ALL"
                ? "history-filter active"
                : "history-filter"
            }
            onClick={() => setFilterType("ALL")}
          >
            Tất cả
          </button>

          <button
            className={
              filterType === "Nhap"
                ? "history-filter active"
                : "history-filter"
            }
            onClick={() => setFilterType("Nhap")}
          >
            Nhập
          </button>

          <button
            className={
              filterType === "Xuat"
                ? "history-filter active"
                : "history-filter"
            }
            onClick={() => setFilterType("Xuat")}
          >
            Xuất
          </button>
        </div>
      </div>

      <div className="table-card">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Hàng hóa</th>
              <th>Người thực hiện</th>
              <th>Loại giao dịch</th>
              <th>Số lượng</th>
              <th>Thời gian</th>
              <th>Ghi chú</th>
            </tr>
          </thead>

          <tbody>
            {loading ? (
              <tr>
                <td colSpan="7" className="empty-cell">
                  Đang tải dữ liệu...
                </td>
              </tr>
            ) : filteredItems.length === 0 ? (
              <tr>
                <td colSpan="7" className="empty-cell">
                  Chưa có giao dịch phù hợp
                </td>
              </tr>
            ) : (
              filteredItems.map((item) => (
                <tr key={item.id}>
                  <td>#{item.id}</td>

                  <td>
                    <strong>{item.ten_hang}</strong>
                    <small className="barcode">
                      Mã: {item.ma_hang}
                    </small>
                  </td>

                  <td>
                    {item.nguoi_thuc_hien || "—"}
                  </td>

                  <td>
                    {item.loai_giao_dich === "Nhap" ? (
                      <span className="stock-status normal-status">
                        📥 Nhập
                      </span>
                    ) : (
                      <span className="stock-status low-status">
                        📤 Xuất
                      </span>
                    )}
                  </td>

                  <td>
                    <strong>
                      {item.so_luong}
                    </strong>
                  </td>

                  <td>
                    {item.thoi_gian}
                  </td>

                  <td>
                    {item.ghi_chu || "—"}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default LichSuKho;