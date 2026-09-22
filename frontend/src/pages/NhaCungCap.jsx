import { useEffect, useState } from "react";
import api from "../api";

function NhaCungCap() {
  const [items, setItems] = useState([]);

  const [form, setForm] = useState({
    ten_ncc: "",
    so_dien_thoai: "",
    email: "",
    dia_chi: "",
  });

  const [editingId, setEditingId] = useState(null);
  const [showForm, setShowForm] = useState(false);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const loadData = async () => {
    try {
      const response = await api.get("/nha-cung-cap");
      setItems(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Không thể tải danh sách nhà cung cấp"
      );
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const resetForm = () => {
    setForm({
      ten_ncc: "",
      so_dien_thoai: "",
      email: "",
      dia_chi: "",
    });
  };

  const openCreate = () => {
    setEditingId(null);
    resetForm();
    setMessage("");
    setError("");
    setShowForm(true);
  };

  const openEdit = (item) => {
    setEditingId(item.id);

    setForm({
      ten_ncc: item.ten_ncc || "",
      so_dien_thoai: item.so_dien_thoai || "",
      email: item.email || "",
      dia_chi: item.dia_chi || "",
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
      if (editingId) {
        await api.put(
          `/nha-cung-cap/${editingId}`,
          form
        );

        setMessage(
          "Cập nhật nhà cung cấp thành công"
        );
      } else {
        await api.post(
          "/nha-cung-cap",
          form
        );

        setMessage(
          "Thêm nhà cung cấp thành công"
        );
      }

      setShowForm(false);
      resetForm();
      loadData();

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Có lỗi xảy ra"
      );
    }
  };

  const handleDelete = async (id) => {
    const ok = window.confirm(
      "Bạn có chắc muốn xóa nhà cung cấp này?"
    );

    if (!ok) return;

    try {
      await api.delete(
        `/nha-cung-cap/${id}`
      );

      setMessage(
        "Xóa nhà cung cấp thành công"
      );

      loadData();

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Không thể xóa nhà cung cấp"
      );
    }
  };

  return (
    <div>

      <div className="page-header">

        <div>
          <h1>Nhà cung cấp</h1>

          <p>
            Quản lý thông tin các nhà cung cấp
          </p>
        </div>

        <button
          className="primary-button"
          onClick={openCreate}
        >
          + Thêm nhà cung cấp
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
              <th>Tên nhà cung cấp</th>
              <th>Số điện thoại</th>
              <th>Email</th>
              <th>Địa chỉ</th>
              <th>Thao tác</th>
            </tr>
          </thead>

          <tbody>

            {items.length === 0 ? (
              <tr>
                <td
                  colSpan="6"
                  className="empty-cell"
                >
                  Chưa có nhà cung cấp
                </td>
              </tr>
            ) : (
              items.map((item) => (
                <tr key={item.id}>

                  <td>{item.id}</td>

                  <td>
                    <strong>
                      {item.ten_ncc}
                    </strong>
                  </td>

                  <td>
                    {item.so_dien_thoai || "—"}
                  </td>

                  <td>
                    {item.email || "—"}
                  </td>

                  <td>
                    {item.dia_chi || "—"}
                  </td>

                  <td>
                    <div className="table-actions">

                      <button
                        className="edit-button"
                        onClick={() =>
                          openEdit(item)
                        }
                      >
                        Sửa
                      </button>

                      <button
                        className="delete-button"
                        onClick={() =>
                          handleDelete(item.id)
                        }
                      >
                        Xóa
                      </button>

                    </div>
                  </td>

                </tr>
              ))
            )}

          </tbody>

        </table>

      </div>

      {showForm && (
        <div className="modal-overlay">

          <div className="modal modal-large">

            <div className="modal-header">

              <h2>
                {editingId
                  ? "Sửa nhà cung cấp"
                  : "Thêm nhà cung cấp"}
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

              <div className="form-grid">

                <div className="form-group">
                  <label>
                    Tên nhà cung cấp
                  </label>

                  <input
                    name="ten_ncc"
                    value={form.ten_ncc}
                    onChange={handleChange}
                    placeholder="Ví dụ: Công ty ABC"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>
                    Số điện thoại
                  </label>

                  <input
                    name="so_dien_thoai"
                    value={form.so_dien_thoai}
                    onChange={handleChange}
                    placeholder="0901234567"
                  />
                </div>

                <div className="form-group">
                  <label>Email</label>

                  <input
                    type="email"
                    name="email"
                    value={form.email}
                    onChange={handleChange}
                    placeholder="abc@gmail.com"
                  />
                </div>

                <div className="form-group">
                  <label>Địa chỉ</label>

                  <input
                    name="dia_chi"
                    value={form.dia_chi}
                    onChange={handleChange}
                    placeholder="Hà Nội"
                  />
                </div>

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
                  {editingId
                    ? "Lưu thay đổi"
                    : "Thêm nhà cung cấp"}
                </button>

              </div>

            </form>

          </div>

        </div>
      )}

    </div>
  );
}

export default NhaCungCap;