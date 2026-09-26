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
import Layout from "./components/Layout";
import NhaCungCap from "./pages/NhaCungCap";
import PhieuNhap from "./pages/PhieuNhap";
import PhieuXuat from "./pages/PhieuXuat";
import TonKho from "./pages/TonKho";
import LichSuKho from "./pages/LichSuKho";
import BaoCao from "./pages/BaoCao";
import AIPhanTich from "./pages/AIPhanTich";
import MultiAgent from "./pages/MultiAgent";

function ProtectedRoute({ children }) {
  return localStorage.getItem("access_token")
    ? children
    : <Navigate to="/" replace />;
}

function Home() {
  return localStorage.getItem("access_token")
    ? <Navigate to="/dashboard" replace />
    : <Login />;
}

function AdminRoute({ children }) {
  const token = localStorage.getItem("access_token");
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  if (!token) return <Navigate to="/" replace />;
  if (user.username !== "admin") return <Navigate to="/dashboard" replace />;
  return children;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/nhom-hang" element={<NhomHang />} />
          <Route path="/hang-hoa" element={<HangHoa />} />
          <Route path="/tai-khoan" element={<AdminRoute><TaiKhoan /></AdminRoute>} />
          <Route path="/nha-cung-cap" element={<NhaCungCap />} />
          <Route path="/phieu-nhap" element={<PhieuNhap />} />
          <Route path="/phieu-xuat" element={<PhieuXuat />} />
          <Route path="/ton-kho" element={<TonKho />} />
          <Route path="/lich-su-kho" element={<LichSuKho />} />
          <Route path="/bao-cao" element={<BaoCao />} />
          <Route path="/ai" element={<AIPhanTich />} />
          <Route path="/multi-agent" element={<MultiAgent />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
