import { useEffect, useState } from "react";
import api from "../api";

function TaiKhoan() {
  const [users, setUsers] = useState([]);

  const [showForm, setShowForm] = useState(false);
  const [editingUser, setEditingUser] = useState(null);

  const [form, setForm] = useState({
    username: "",
    password: "",
    full_name: "",
    role: "ThuKho",
  });

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const adminUsername = "admin";


  const loadUsers = async () => {
    try {
      const response = await api.get(
        `/tai-khoan?username=${adminUsername}`
      );

      setUsers(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Không thể tải danh sách tài khoản"
      );
    }
  };


  useEffect(() => {
    loadUsers();
  }, []);


  const openCreate = () => {
    setEditingUser(null);

    setForm({
      username: "",
      password: "",
      full_name: "",
      role: "ThuKho",
    });

    setMessage("");
    setError("");
    setShowForm(true);
  };


  const openEdit = (user) => {
    setEditingUser(user);

    setForm({
      username: user.username,
      password: "",
      full_name: user.full_name,
      role: user.role,
    });

    setMessage("");
    setError("");
    setShowForm(true);
  };


  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };


  const handleSubmit = async (e) => {
    e.preventDefault();

    setMessage("");
    setError("");

    try {

      if (editingUser) {

        await api.put(
          `/tai-khoan/${editingUser.id}?username=${adminUsername}`,
          {
            password:
              form.password || null,
            full_name: form.full_name,
            role: form.role,
          }
        );

        setMessage(
          "Cập nhật tài khoản thành công"
        );

      } else {

        await api.post(
          `/tai-khoan?username=${adminUsername}`,
          {
            username: form.username,
            password: form.password,
            full_name: form.full_name,
            role: form.role,
          }
        );

        setMessage(
          "Thêm người dùng thành công"
        );
      }

      setShowForm(false);
      loadUsers();

    } catch (err) {

      setError(
        err.response?.data?.detail ||
        "Có lỗi xảy ra"
      );
    }
  };


  const handleDelete = async (user) => {

    if (user.username === "admin") {
      alert("Không thể xóa tài khoản admin");
      return;
    }

    const confirmDelete = window.confirm(
      `Bạn có chắc muốn xóa tài khoản "${user.username}"?`
    );

    if (!confirmDelete) return;

    try {

      await api.delete(
        `/tai-khoan/${user.id}?username=${adminUsername}`
      );

      setMessage(
        "Xóa tài khoản thành công"
      );

      loadUsers();

    } catch (err) {

      setError(
        err.response?.data?.detail ||
        "Không thể xóa tài khoản"
      );
    }
  };


  const getRoleName = (role) => {

    if (role === "QuanLy") {
      return "Quản lý";
    }

    if (role === "ThuKho") {
      return "Thủ kho";
    }

    if (role === "KeToan") {
      return "Kế toán";
    }

    return role;
  };


  return (
    <div>

      <div className="page-header">

        <div>

          <h1>
            Quản lý tài khoản
          </h1>

          <p>
            Chỉ admin có quyền thêm, sửa và xóa người dùng
          </p>

        </div>

        <button
          className="primary-button"
          onClick={openCreate}
        >
          + Thêm người dùng
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


      <div className="table-card">

        <table>

          <thead>

            <tr>
              <th>ID</th>
              <th>Tên đăng nhập</th>
              <th>Họ tên</th>
              <th>Vai trò</th>
              <th>Thao tác</th>
            </tr>

          </thead>


          <tbody>

            {users.map((user) => (

              <tr key={user.id}>

                <td>
                  {user.id}
                </td>

                <td>
                  <strong>
                    {user.username}
                  </strong>
                </td>

                <td>
                  {user.full_name}
                </td>

                <td>
                  <span className="role-badge">
                    {getRoleName(user.role)}
                  </span>
                </td>

                <td>

                  {user.username === "admin" ? (

                    <span
                      style={{
                        color: "#6b7280",
                        fontSize: "13px"
                      }}
                    >
                      Tài khoản hệ thống
                    </span>

                  ) : (

                    <div className="table-actions">

                      <button
                        className="edit-button"
                        onClick={() =>
                          openEdit(user)
                        }
                      >
                        Sửa
                      </button>

                      <button
                        className="delete-button"
                        onClick={() =>
                          handleDelete(user)
                        }
                      >
                        Xóa
                      </button>

                    </div>

                  )}

                </td>

              </tr>

            ))}

          </tbody>

        </table>

      </div>


      {showForm && (

        <div className="modal-overlay">

          <div className="modal">

            <div className="modal-header">

              <h2>
                {editingUser
                  ? "Sửa người dùng"
                  : "Thêm người dùng"}
              </h2>

              <button
                className="close-button"
                onClick={() =>
                  setShowForm(false)
                }
              >
                ×
              </button>

            </div>


            <form onSubmit={handleSubmit}>

              {!editingUser && (

                <div className="form-group">

                  <label>
                    Tên đăng nhập
                  </label>

                  <input
                    name="username"
                    value={form.username}
                    onChange={handleChange}
                    required
                  />

                </div>

              )}


              <div className="form-group">

                <label>
                  {editingUser
                    ? "Mật khẩu mới (để trống nếu không đổi)"
                    : "Mật khẩu"}
                </label>

                <input
                  type="password"
                  name="password"
                  value={form.password}
                  onChange={handleChange}
                  required={!editingUser}
                />

              </div>


              <div className="form-group">

                <label>
                  Họ tên
                </label>

                <input
                  name="full_name"
                  value={form.full_name}
                  onChange={handleChange}
                  required
                />

              </div>


              <div className="form-group">

                <label>
                  Vai trò
                </label>

                <select
                  name="role"
                  value={form.role}
                  onChange={handleChange}
                >

                  <option value="QuanLy">
                    Quản lý
                  </option>

                  <option value="ThuKho">
                    Thủ kho
                  </option>

                  <option value="KeToan">
                    Kế toán
                  </option>

                </select>

              </div>


              <div className="modal-actions">

                <button
                  type="button"
                  className="secondary-button"
                  onClick={() =>
                    setShowForm(false)
                  }
                >
                  Hủy
                </button>

                <button
                  type="submit"
                  className="primary-button"
                >
                  {editingUser
                    ? "Lưu thay đổi"
                    : "Tạo tài khoản"}
                </button>

              </div>

            </form>

          </div>

        </div>

      )}

    </div>
  );
}

export default TaiKhoan;