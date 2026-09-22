import { useEffect, useState } from "react";
import api from "../api";

function NhomHang() {
  const [items, setItems] = useState([]);

  const [form, setForm] = useState({
    ten_nhom: "",
    mo_ta: "",
  });

  const [editingId, setEditingId] = useState(null);
  const [showForm, setShowForm] = useState(false);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const loadData = async () => {
    try {
      const response = await api.get("/nhom-hang");
      setItems(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Không thể tải nhóm hàng"
      );
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const openCreate = () => {
    setEditingId(null);

    setForm({
      ten_nhom: "",
      mo_ta: "",
    });

    setError("");
    setMessage("");
    setShowForm(true);
  };

  const openEdit = (item) => {
    setEditingId(item.id);

    setForm({
      ten_nhom: item.ten_nhom,
      mo_ta: item.mo_ta || "",
    });

    setError("");
    setMessage("");
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

    setError("");
    setMessage("");

    try {
      if (editingId) {
        await api.put(
          `/nhom-hang/${editingId}`,
          form
        );

        setMessage(
          "Cập nhật nhóm hàng thành công"
        );
      } else {
        await api.post(
          "/nhom-hang",
          form
        );

        setMessage(
          "Thêm nhóm hàng thành công"
        );
      }

      setShowForm(false);
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
      "Bạn có chắc muốn xóa nhóm hàng này?"
    );

    if (!ok) return;

    try {
      await api.delete(`/nhom-hang/${id}`);

      setMessage(
        "Xóa nhóm hàng thành công"
      );

      loadData();

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Không thể xóa nhóm hàng"
      );
    }
  };

  return (
    <div>

      <div className="page-header">

        <div>
          <h1>Nhóm hàng</h1>

          <p>
            Quản lý các nhóm sản phẩm trong kho
          </p>
        </div>

        <button
          className="primary-button"
          onClick={openCreate}
        >
          + Thêm nhóm hàng
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
              <th>Tên nhóm hàng</th>
              <th>Mô tả</th>
              <th>Thao tác</th>
            </tr>
          </thead>

          <tbody>

            {items.length === 0 ? (
              <tr>
                <td colSpan="4" className="empty-cell">
                  Chưa có nhóm hàng
                </td>
              </tr>
            ) : (
              items.map((item) => (
                <tr key={item.id}>

                  <td>{item.id}</td>

                  <td>
                    <strong>
                      {item.ten_nhom}
                    </strong>
                  </td>

                  <td>
                    {item.mo_ta || "—"}
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

          <div className="modal">

            <div className="modal-header">

              <h2>
                {editingId
                  ? "Sửa nhóm hàng"
                  : "Thêm nhóm hàng"}
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

              <div className="form-group">
                <label>Tên nhóm hàng</label>

                <input
                  name="ten_nhom"
                  value={form.ten_nhom}
                  onChange={handleChange}
                  placeholder="Ví dụ: Máy tính & phụ kiện"
                  required
                />
              </div>

              <div className="form-group">
                <label>Mô tả</label>

                <textarea
                  name="mo_ta"
                  value={form.mo_ta}
                  onChange={handleChange}
                  placeholder="Nhập mô tả"
                  rows="4"
                />
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
                    : "Thêm nhóm hàng"}
                </button>

              </div>

            </form>

          </div>

        </div>
      )}

    </div>
  );
}

export default NhomHang;