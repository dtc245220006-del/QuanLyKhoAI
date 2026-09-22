import { NavLink, Outlet, useNavigate } from "react-router-dom";

function Layout() {
  const navigate = useNavigate();

  const user = JSON.parse(
    localStorage.getItem("user") || "{}"
  );

  const menuItems = [
    { name: "Tổng quan", path: "/dashboard", icon: "📊" },
    { name: "Nhóm hàng", path: "/nhom-hang", icon: "📁" },
    { name: "Hàng hóa", path: "/hang-hoa", icon: "📦" },
    { name: "Nhà cung cấp", path: "/nha-cung-cap", icon: "🏢" },
    { name: "Phiếu nhập", path: "/phieu-nhap", icon: "📥" },
    { name: "Phiếu xuất", path: "/phieu-xuat", icon: "📤" },
    { name: "Tồn kho", path: "/ton-kho", icon: "📋" },
    { name: "Lịch sử kho", path: "/lich-su-kho", icon: "🕒" },
    { name: "Thống kê & báo cáo", path: "/bao-cao", icon: "📈" },
    { name: "AI phân tích tồn kho", path: "/ai", icon: "🤖" },
  ];

  if (user.role === "Quản Lý") {
    menuItems.push({
      name: "Quản lý tài khoản",
      path: "/tai-khoan",
      icon: "👥",
    });
  }

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    navigate("/");
  };

  return (
    <div className="app-layout">

      <aside className="sidebar">

        <div className="sidebar-logo">
          <div className="logo-icon">📦</div>

          <div>
            <strong>Quản Lý Kho</strong>
            <small>Tích hợp AI</small>
          </div>
        </div>

        <nav className="sidebar-menu">
          {menuItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `menu-item ${isActive ? "active" : ""}`
              }
            >
              <span className="menu-icon">
                {item.icon}
              </span>

              <span>{item.name}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-bottom">

          <div className="sidebar-user">
            <div className="avatar">
              {(user.full_name || "U")
                .charAt(0)
                .toUpperCase()}
            </div>

            <div>
              <strong>
                {user.full_name || user.username}
              </strong>

              <small>
                {user.role === "QuanLy"
                  ? "Quản lý"
                  : user.role}
              </small>
            </div>
          </div>

          <button
            className="logout-button"
            onClick={handleLogout}
          >
            Đăng xuất
          </button>

        </div>

      </aside>

      <main className="main-content">
        <Outlet />
      </main>

    </div>
  );
}

export default Layout;