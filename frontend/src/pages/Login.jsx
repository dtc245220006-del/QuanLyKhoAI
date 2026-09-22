import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";

function Login() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();

    setError("");

    if (!username || !password) {
      setError(
        "Vui lòng nhập tên đăng nhập và mật khẩu"
      );
      return;
    }

    try {
      setLoading(true);

      const response = await api.post(
        "/auth/login",
        {
          username,
          password,
        }
      );

      localStorage.setItem(
        "access_token",
        response.data.access_token
      );

      localStorage.setItem(
        "user",
        JSON.stringify(response.data.user)
      );

      navigate("/dashboard");

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Đăng nhập thất bại"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">

      <div className="login-container">

        <div className="login-brand">

          <div className="login-logo">
            📦
          </div>

          <h1>
            Quản Lý Kho
          </h1>

          <p>
            Hệ thống quản lý kho
            <br />
            tích hợp trí tuệ nhân tạo
          </p>

          <div className="login-feature">
            <span>✓</span>
            Quản lý hàng hóa
          </div>

          <div className="login-feature">
            <span>✓</span>
            Theo dõi tồn kho
          </div>

          <div className="login-feature">
            <span>✓</span>
            AI phân tích và đề xuất nhập hàng
          </div>

        </div>

        <div className="login-form-side">

          <div className="login-form-header">
            <h2>
              Chào mừng trở lại
            </h2>

            <p>
              Đăng nhập để tiếp tục
            </p>
          </div>

          <form onSubmit={handleLogin}>

            <div className="form-group">
              <label>
                Tên đăng nhập
              </label>

              <input
                type="text"
                value={username}
                onChange={(e) =>
                  setUsername(e.target.value)
                }
                placeholder="Nhập tên đăng nhập"
              />
            </div>

            <div className="form-group">
              <label>
                Mật khẩu
              </label>

              <div className="password-wrapper">

                <input
                  type={
                    showPassword
                      ? "text"
                      : "password"
                  }
                  value={password}
                  onChange={(e) =>
                    setPassword(e.target.value)
                  }
                  placeholder="Nhập mật khẩu"
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() =>
                    setShowPassword(
                      !showPassword
                    )
                  }
                >
                  {showPassword
                    ? "Ẩn"
                    : "Hiện"}
                </button>

              </div>
            </div>

            {error && (
              <div className="login-error">
                {error}
              </div>
            )}

            <button
              type="submit"
              className="login-submit"
              disabled={loading}
            >
              {loading
                ? "Đang đăng nhập..."
                : "Đăng nhập"}
            </button>

          </form>

          <div className="login-footer">
            Hệ thống quản lý kho tích hợp AI
          </div>

        </div>

      </div>

    </div>
  );
}

export default Login;