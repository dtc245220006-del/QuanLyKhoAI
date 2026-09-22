import { useEffect, useState } from "react";
import api from "../api";

function BaoCao() {
  const [dashboard, setDashboard] = useState({
    tong_hang_hoa: 0,
    tong_nhom_hang: 0,
    tong_tien_nhap: 0,
    tong_so_luong_xuat: 0,
    tong_so_luong_ton: 0,
  });

  const [baoCaoNhap, setBaoCaoNhap] = useState([]);
  const [baoCaoXuat, setBaoCaoXuat] = useState([]);
  const [baoCaoTon, setBaoCaoTon] = useState([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const loadData = async () => {
    try {
      setLoading(true);
      setError("");

      const [
        dashboardRes,
        nhapRes,
        xuatRes,
        tonRes,
      ] = await Promise.all([
        api.get("/bao-cao/dashboard"),
        api.get("/bao-cao/nhap"),
        api.get("/bao-cao/xuat"),
        api.get("/bao-cao/ton-kho"),
      ]);

      setDashboard(dashboardRes.data);
      setBaoCaoNhap(nhapRes.data);
      setBaoCaoXuat(xuatRes.data);
      setBaoCaoTon(tonRes.data);

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Không thể tải dữ liệu báo cáo"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const money = (value) =>
    Number(value || 0).toLocaleString("vi-VN") + " ₫";

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Thống kê & báo cáo</h1>
          <p>
            Tổng hợp tình hình hoạt động của kho
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

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="report-summary">
        <div className="report-card">
          <small>Tổng hàng hóa</small>
          <strong>
            {dashboard.tong_hang_hoa}
          </strong>
        </div>

        <div className="report-card">
          <small>Tổng nhóm hàng</small>
          <strong>
            {dashboard.tong_nhom_hang}
          </strong>
        </div>

        <div className="report-card">
          <small>Tổng tiền nhập</small>
          <strong>
            {money(dashboard.tong_tien_nhap)}
          </strong>
        </div>

        <div className="report-card">
          <small>Số lượng xuất</small>
          <strong>
            {dashboard.tong_so_luong_xuat}
          </strong>
        </div>

        <div className="report-card">
          <small>Số lượng tồn</small>
          <strong>
            {dashboard.tong_so_luong_ton}
          </strong>
        </div>
      </div>

      <div className="report-section">
        <div className="section-header">
          <h2>Báo cáo nhập kho</h2>
        </div>

        <div className="table-card">
          <table>
            <thead>
              <tr>
                <th>Mã phiếu</th>
                <th>Ngày nhập</th>
                <th>Nhà cung cấp</th>
                <th>Tài khoản</th>
                <th>Tổng tiền</th>
              </tr>
            </thead>

            <tbody>
              {baoCaoNhap.length === 0 ? (
                <tr>
                  <td colSpan="5" className="empty-cell">
                    Chưa có dữ liệu
                  </td>
                </tr>
              ) : (
                baoCaoNhap.map((item) => (
                  <tr key={item.ma_phieu_nhap}>
                    <td>#{item.ma_phieu_nhap}</td>
                    <td>{item.ngay_nhap}</td>
                    <td>#{item.ma_ncc}</td>
                    <td>#{item.ma_tai_khoan}</td>
                    <td>
                      {money(item.tong_tien)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="report-section">
        <div className="section-header">
          <h2>Báo cáo xuất kho</h2>
        </div>

        <div className="table-card">
          <table>
            <thead>
              <tr>
                <th>Mã phiếu</th>
                <th>Ngày xuất</th>
                <th>Tài khoản</th>
                <th>Lý do</th>
              </tr>
            </thead>

            <tbody>
              {baoCaoXuat.length === 0 ? (
                <tr>
                  <td colSpan="4" className="empty-cell">
                    Chưa có dữ liệu
                  </td>
                </tr>
              ) : (
                baoCaoXuat.map((item) => (
                  <tr key={item.ma_phieu_xuat}>
                    <td>#{item.ma_phieu_xuat}</td>
                    <td>{item.ngay_xuat}</td>
                    <td>#{item.ma_tai_khoan}</td>
                    <td>
                      {item.ly_do || "—"}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="report-section">
        <div className="section-header">
          <h2>Báo cáo tồn kho</h2>
        </div>

        <div className="table-card">
          <table>
            <thead>
              <tr>
                <th>Mã hàng</th>
                <th>Tên hàng</th>
                <th>Số lượng tồn</th>
                <th>Tồn tối thiểu</th>
                <th>Trạng thái</th>
              </tr>
            </thead>

            <tbody>
              {baoCaoTon.length === 0 ? (
                <tr>
                  <td colSpan="5" className="empty-cell">
                    Chưa có dữ liệu
                  </td>
                </tr>
              ) : (
                baoCaoTon.map((item) => (
                  <tr key={item.ma_hang}>
                    <td>#{item.ma_hang}</td>
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
                      {item.canh_bao ? (
                        <span className="stock-status low-status">
                          ⚠️ Tồn thấp
                        </span>
                      ) : (
                        <span className="stock-status normal-status">
                          ✓ Bình thường
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default BaoCao;