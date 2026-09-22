import { useEffect, useState } from "react";
import api from "../api";

function HangHoa() {
  const [items, setItems] = useState([]);
  const [groups, setGroups] = useState([]);

  const [form, setForm] = useState({
    ma_nhom: "",
    ten_hang: "",
    don_vi_tinh: "",
    ma_barcode: "",
    gia_nhap: 0,
    gia_ban: 0,
    ton_toi_thieu: 0,
  });

  const [editingId, setEditingId] = useState(null);
  const [showForm, setShowForm] = useState(false);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const loadData = async () => {
    try {
      const [hangHoaRes, groupRes] =
        await Promise.all([
          api.get("/hang-hoa"),
          api.get("/nhom-hang"),
        ]);

      setItems(hangHoaRes.data);
      setGroups(groupRes.data);

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Không thể tải dữ liệu hàng hóa"
      );
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const resetForm = () => {
    setForm({
      ma_nhom: "",
      ten_hang: "",
      don_vi_tinh: "",
      ma_barcode: "",
      gia_nhap: 0,
      gia_ban: 0,
      ton_toi_thieu: 0,
    });
  };

  const openCreate = () => {
    setEditingId(null);
    resetForm();

    setError("");
    setMessage("");
    setShowForm(true);
  };

  const openEdit = (item) => {
    setEditingId(item.id);

    setForm({
      ma_nhom: item.ma_nhom,
      ten_hang: item.ten_hang,
      don_vi_tinh: item.don_vi_tinh,
      ma_barcode: item.ma_barcode || "",
      gia_nhap: item.gia_nhap,
      gia_ban: item.gia_ban,
      ton_toi_thieu: item.ton_toi_thieu,
    });

    setError("");
    setMessage("");
    setShowForm(true);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    setForm({
      ...form,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setMessage("");

    const data = {
      ma_nhom: Number(form.ma_nhom),
      ten_hang: form.ten_hang,
      don_vi_tinh: form.don_vi_tinh,
      ma_barcode:
        form.ma_barcode || null,
      gia_nhap: Number(form.gia_nhap),
      gia_ban: Number(form.gia_ban),
      ton_toi_thieu: Number(
        form.ton_toi_thieu
      ),
    };

    try {
      if (editingId) {
        await api.put(
          `/hang-hoa/${editingId}`,
          data
        );

        setMessage(
          "Cập nhật hàng hóa thành công"
        );
      } else {
        await api.post(
          "/hang-hoa",
          data
        );

        setMessage(
          "Thêm hàng hóa thành công"
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
      "Bạn có chắc muốn xóa hàng hóa này?"
    );

    if (!ok) return;

    try {
      await api.delete(
        `/hang-hoa/${id}`
      );

      setMessage(
        "Xóa hàng hóa thành công"
      );

      loadData();

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Không thể xóa hàng hóa"
      );
    }
  };

  const getGroupName = (id) => {
    const group = groups.find(
      (item) => item.id === id
    );

    return group?.ten_nhom || "—";
  };

  const formatMoney = (value) => {
    return Number(value || 0)
      .toLocaleString("vi-VN") + " ₫";
  };

  return (
    <div>

      <div className="page-header">

        <div>
          <h1>Hàng hóa</h1>

          <p>
            Quản lý sản phẩm và thông tin tồn tối thiểu
          </p>
        </div>

        <button
          className="primary-button"
          onClick={openCreate}
        >
          + Thêm hàng hóa
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
              <th>Tên hàng</th>
              <th>Nhóm hàng</th>
              <th>Đơn vị</th>
              <th>Giá nhập</th>
              <th>Giá bán</th>
              <th>Tồn tối thiểu</th>
              <th>Thao tác</th>
            </tr>
          </thead>

          <tbody>

            {items.length === 0 ? (
              <tr>
                <td
                  colSpan="8"
                  className="empty-cell"
                >
                  Chưa có hàng hóa
                </td>
              </tr>
            ) : (
              items.map((item) => (
                <tr key={item.id}>

                  <td>{item.id}</td>

                  <td>
                    <strong>
                      {item.ten_hang}
                    </strong>

                    <small className="barcode">
                      {item.ma_barcode || "Không có barcode"}
                    </small>
                  </td>

                  <td>
                    {getGroupName(item.ma_nhom)}
                  </td>

                  <td>
                    {item.don_vi_tinh}
                  </td>

                  <td>
                    {formatMoney(item.gia_nhap)}
                  </td>

                  <td>
                    {formatMoney(item.gia_ban)}
                  </td>

                  <td>
                    {item.ton_toi_thieu}
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
                  ? "Sửa hàng hóa"
                  : "Thêm hàng hóa"}
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
                  <label>Nhóm hàng</label>

                  <select
                    name="ma_nhom"
                    value={form.ma_nhom}
                    onChange={handleChange}
                    required
                  >
                    <option value="">
                      -- Chọn nhóm hàng --
                    </option>

                    {groups.map((group) => (
                      <option
                        key={group.id}
                        value={group.id}
                      >
                        {group.ten_nhom}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Tên hàng</label>

                  <input
                    name="ten_hang"
                    value={form.ten_hang}
                    onChange={handleChange}
                    placeholder="Ví dụ: Chuột Logitech"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Đơn vị tính</label>

                  <input
                    name="don_vi_tinh"
                    value={form.don_vi_tinh}
                    onChange={handleChange}
                    placeholder="Cái"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Barcode</label>

                  <input
                    name="ma_barcode"
                    value={form.ma_barcode}
                    onChange={handleChange}
                    placeholder="Có thể bỏ trống"
                  />
                </div>

                <div className="form-group">
                  <label>Giá nhập</label>

                  <input
                    type="number"
                    min="0"
                    name="gia_nhap"
                    value={form.gia_nhap}
                    onChange={handleChange}
                  />
                </div>

                <div className="form-group">
                  <label>Giá bán</label>

                  <input
                    type="number"
                    min="0"
                    name="gia_ban"
                    value={form.gia_ban}
                    onChange={handleChange}
                  />
                </div>

                <div className="form-group">
                  <label>Tồn tối thiểu</label>

                  <input
                    type="number"
                    min="0"
                    name="ton_toi_thieu"
                    value={form.ton_toi_thieu}
                    onChange={handleChange}
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
                    : "Thêm hàng hóa"}
                </button>

              </div>

            </form>

          </div>

        </div>
      )}

    </div>
  );
}

export default HangHoa;