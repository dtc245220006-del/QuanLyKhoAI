import { useEffect, useState } from "react";
import api from "../api";
import { useNavigate } from "react-router-dom";

function Dashboard() {
  const navigate = useNavigate();

  const [stats, setStats] = useState({
    tong_hang_hoa: 0,
    tong_nhom_hang: 0,
    tong_tien_nhap: 0,
    tong_so_luong_xuat: 0,
    tong_so_luong_ton: 0,
  });

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const response = await api.get(
          "/bao-cao/dashboard"
        );

        setStats(response.data);
      } catch (error) {
        console.error(error);
      }
    };

    loadDashboard();
  }, []);

  return (
    <div>

      <div className="content-header">
        <div>
          <h1>Dashboard</h1>
          <p>
            Tổng quan hoạt động kho
          </p>
        </div>
      </div>

      <div className="stat-grid">

        <div className="stat-card">
          <div className="stat-icon">📦</div>

          <div>
            <p>Tổng hàng hóa</p>
            <strong>
              {stats.tong_hang_hoa}
            </strong>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📋</div>

          <div>
            <p>Tổng tồn kho</p>
            <strong>
              {stats.tong_so_luong_ton}
            </strong>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📥</div>

          <div>
            <p>Tổng tiền nhập</p>
            <strong>
              {Number(
                stats.tong_tien_nhap || 0
              ).toLocaleString("vi-VN")} ₫
            </strong>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📤</div>

          <div>
            <p>Số lượng xuất</p>
            <strong>
              {stats.tong_so_luong_xuat}
            </strong>
          </div>
        </div>

      </div>

      <div className="section">

        <div className="section-header">
          <h2>Thao tác nhanh</h2>
        </div>

        <div className="quick-grid">

          <button
            className="quick-card"
            onClick={() => navigate("/nhom-hang")}
          >
            <span>📁</span>
            <strong>Nhóm hàng</strong>
            <small>
              Quản lý nhóm hàng
            </small>
          </button>

          <button
            className="quick-card"
            onClick={() => navigate("/hang-hoa")}
          >
            <span>📦</span>
            <strong>Hàng hóa</strong>
            <small>
              Quản lý sản phẩm
            </small>
          </button>

          <button
            className="quick-card"
            onClick={() => navigate("/phieu-nhap")}
          >
            <span>📥</span>
            <strong>Nhập kho</strong>
            <small>
              Tạo phiếu nhập
            </small>
          </button>

          <button
            className="quick-card"
            onClick={() => navigate("/ai")}
          >
            <span>🤖</span>
            <strong>AI phân tích</strong>
            <small>
              Phân tích tồn kho
            </small>
          </button>

        </div>

      </div>

    </div>
  );
}

export default Dashboard;