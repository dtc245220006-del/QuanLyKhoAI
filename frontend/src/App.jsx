import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import TaiKhoan from "./pages/TaiKhoan";
import NhomHang from "./pages/NhomHang";
import HangHoa from "./pages/HangHoa";
import ComingSoon from "./pages/ComingSoon";
import Layout from "./components/Layout";
import NhaCungCap from "./pages/NhaCungCap";
import PhieuNhap from "./pages/PhieuNhap";
import PhieuXuat from "./pages/PhieuXuat";
import TonKho from "./pages/TonKho";
import LichSuKho from "./pages/LichSuKho";
import BaoCao from "./pages/BaoCao";
import AIPhanTich from "./pages/AIPhanTich";


function ProtectedRoute({ children }) {
  const token = localStorage.getItem("access_token");

  if (!token) {
    return <Navigate to="/" replace />;
  }

  return children;
}


function Home() {
  const token = localStorage.getItem("access_token");

  if (token) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Login />;
}


function AdminRoute({ children }) {
  const token = localStorage.getItem("access_token");

  const user = JSON.parse(
    localStorage.getItem("user") || "{}"
  );

  if (!token) {
    return <Navigate to="/" replace />;
  }

  if (user.username !== "admin") {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}


function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* LOGIN */}
        <Route
          path="/"
          element={<Home />}
        />

        {/* CÁC TRANG SAU ĐĂNG NHẬP */}
        <Route
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >

          <Route
            path="/dashboard"
            element={<Dashboard />}
          />

          <Route
            path="/nhom-hang"
            element={<NhomHang />}
          />

          <Route
            path="/hang-hoa"
            element={<HangHoa />}
          />

          {/* CHỈ ADMIN */}
          <Route
            path="/tai-khoan"
            element={
              <AdminRoute>
                <TaiKhoan />
              </AdminRoute>
            }
          />

          <Route
            path="/nha-cung-cap"
            element={<NhaCungCap />}
          />

          <Route
            path="/phieu-nhap"
            element={<PhieuNhap />}
          />
          <Route
  path="/phieu-xuat"
  element={<PhieuXuat />}
/>

         <Route
  path="/ton-kho"
  element={<TonKho />}
/>

          <Route
  path="/lich-su-kho"
  element={<LichSuKho />}
/>

            <Route
              path="/bao-cao"
              element={
                <BaoCao />
              }
            />

          <Route
  path="/ai"
  element={<AIPhanTich />}
/>

        </Route>

        {/* URL KHÔNG TỒN TẠI */}
        <Route
          path="*"
          element={<Navigate to="/" replace />}
        />

      </Routes>
    </BrowserRouter>
  );
}

export default App;