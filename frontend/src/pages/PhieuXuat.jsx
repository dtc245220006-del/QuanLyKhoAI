import { useEffect, useMemo, useState } from "react";
import api from "../api";

function PhieuXuat() {
  const [phieuXuat, setPhieuXuat] = useState([]);
  const [hangHoa, setHangHoa] = useState([]);

  const [showForm, setShowForm] = useState(false);
  const [showDetail, setShowDetail] = useState(false);

  const [selectedPhieu, setSelectedPhieu] = useState(null);

  const [form, setForm] = useState({
    ly_do: "",
    chi_tiet: [
      {
        ma_hang: "",
        so_luong: 1,
      },
    ],
  });

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const currentUser = JSON.parse(
    localStorage.getItem("user") || "{}"
  );

  // =====================================================
  // LOAD DATA
  // =====================================================

  const loadData = async () => {
    try {
      const [phieuRes, hangRes] = await Promise.all([
        api.get("/phieu-xuat"),
        api.get("/hang-hoa"),
      ]);

      setPhieuXuat(phieuRes.data);
      setHangHoa(hangRes.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Không thể tải dữ liệu phiếu xuất"
      );
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // =====================================================
  // FORM
  // =====================================================

  const resetForm = () => {
    setForm({
      ly_do: "",
      chi_tiet: [
        {
          ma_hang: "",
          so_luong: 1,
        },
      ],
    });
  };

  const openCreate = () => {
    resetForm();
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

  const handleItemChange = (index, field, value) => {
    const newItems = [...form.chi_tiet];

    newItems[index] = {
      ...newItems[index],
      [field]: value,
    };

    setForm({
      ...form,
      chi_tiet: newItems,
    });
  };

  const addItem = () => {
    setForm({
      ...form,
      chi_tiet: [
        ...form.chi_tiet,
        {
          ma_hang: "",
          so_luong: 1,
        },
      ],
    });
  };

  const removeItem = (index) => {
    if (form.chi_tiet.length === 1) {
      return;
    }

    const newItems = form.chi_tiet.filter(
      (_, i) => i !== index
    );

    setForm({
      ...form,
      chi_tiet: newItems,
    });
  };

  const getHangName = (id) => {
    const item = hangHoa.find(
      (x) => x.id === id
    );

    return item?.ten_hang || "—";
  };

  const getTonToiThieu = (id) => {
    const item = hangHoa.find(
      (x) => x.id === id
    );

    return item?.ton_toi_thieu ?? 0;
  };

  // =====================================================
  // TỔNG SỐ LƯỢNG
  // =====================================================

  const tongSoLuong = useMemo(() => {
    return form.chi_tiet.reduce(
      (total, item) =>
        total + Number(item.so_luong || 0),
      0
    );
  }, [form.chi_tiet]);

  // =====================================================
  // TẠO PHIẾU XUẤT
  // =====================================================

  const handleCreate = async (e) => {
    e.preventDefault();

    setMessage("");
    setError("");

    const validItems = form.chi_tiet.filter(
      (item) => item.ma_hang
    );

    if (validItems.length === 0) {
      setError(
        "Phiếu xuất phải có ít nhất một mặt hàng"
      );
      return;
    }

    const data = {
      ma_tai_khoan: Number(
        currentUser.id
      ),
      ly_do: form.ly_do || null,
      chi_tiet: validItems.map((item) => ({
        ma_hang: Number(item.ma_hang),
        so_luong: Number(item.so_luong),
      })),
    };

    try {
      await api.post(
        "/phieu-xuat",
        data
      );

      setMessage(
        "Tạo phiếu xuất thành công"
      );

      setShowForm(false);
      resetForm();
      loadData();

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Không thể tạo phiếu xuất"
      );
    }
  };

  // =====================================================
  // XÁC NHẬN
  // =====================================================

  const handleConfirm = async (id) => {
    const ok = window.confirm(
      "Xác nhận phiếu xuất này? Hệ thống sẽ trừ tồn kho."
    );

    if (!ok) return;

    try {
      await api.put(
        `/phieu-xuat/${id}/xac-nhan`
      );

      setMessage(
        "Xác nhận phiếu xuất thành công"
      );

      loadData();

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Không thể xác nhận phiếu xuất"
      );
    }
  };

  // =====================================================
  // XÓA
  // =====================================================

  const handleDelete = async (id) => {
    const ok = window.confirm(
      "Bạn có chắc muốn xóa phiếu xuất này?"
    );

    if (!ok) return;

    try {
      await api.delete(
        `/phieu-xuat/${id}`
      );

      setMessage(
        "Xóa phiếu xuất thành công"
      );

      loadData();

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Không thể xóa phiếu xuất"
      );
    }
  };

  // =====================================================
  // XEM CHI TIẾT
  // =====================================================

  const handleViewDetail = async (id) => {
    try {
      const response = await api.get(
        `/phieu-xuat/${id}`
      );

      setSelectedPhieu(
        response.data
      );

      setShowDetail(true);

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Không thể lấy chi tiết phiếu xuất"
      );
    }
  };

  return (
    <div>

      {/* HEADER */}

      <div className="page-header">
        <div>
          <h1>Phiếu xuất</h1>

          <p>
            Quản lý các phiếu xuất kho
          </p>
        </div>

        <button
          className="primary-button"
          onClick={openCreate}
        >
          + Tạo phiếu xuất
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

      {/* TABLE */}

      <div className="table-card">

        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Người thực hiện</th>
              <th>Ngày xuất</th>
              <th>Lý do</th>
              <th>Trạng thái</th>
              <th>Thao tác</th>
            </tr>
          </thead>

          <tbody>

            {phieuXuat.length === 0 ? (
              <tr>
                <td
                  colSpan="6"
                  className="empty-cell"
                >
                  Chưa có phiếu xuất
                </td>
              </tr>
            ) : (
              phieuXuat.map((phieu) => (
                <tr key={phieu.id}>

                  <td>
                    <strong>
                      #{phieu.id}
                    </strong>
                  </td>

                  <td>
                    {phieu.ma_tai_khoan}
                  </td>

                  <td>
                    {phieu.ngay_xuat}
                  </td>

                  <td>
                    {phieu.ly_do || "—"}
                  </td>

                  <td>
                    <span
                      className={`status-badge ${
                        phieu.trang_thai ===
                        "DaXuat"
                          ? "status-success"
                          : "status-pending"
                      }`}
                    >
                      {phieu.trang_thai ===
                      "DaXuat"
                        ? "Đã xuất"
                        : "Nháp"}
                    </span>
                  </td>

                  <td>
                    <div className="table-actions">

                      <button
                        className="view-button"
                        onClick={() =>
                          handleViewDetail(
                            phieu.id
                          )
                        }
                      >
                        Xem
                      </button>

                      {phieu.trang_thai ===
                        "Nhap" && (
                        <>
                          <button
                            className="confirm-button"
                            onClick={() =>
                              handleConfirm(
                                phieu.id
                              )
                            }
                          >
                            Xác nhận
                          </button>

                          <button
                            className="delete-button"
                            onClick={() =>
                              handleDelete(
                                phieu.id
                              )
                            }
                          >
                            Xóa
                          </button>
                        </>
                      )}

                    </div>
                  </td>

                </tr>
              ))
            )}

          </tbody>
        </table>

      </div>

      {/* =================================================
          MODAL TẠO PHIẾU
      ================================================= */}

      {showForm && (
        <div className="modal-overlay">

          <div className="modal modal-xl">

            <div className="modal-header">

              <h2>
                Tạo phiếu xuất
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

            <form onSubmit={handleCreate}>

              <div className="form-group">

                <label>
                  Lý do xuất
                </label>

                <input
                  name="ly_do"
                  value={form.ly_do}
                  onChange={handleChange}
                  placeholder="Ví dụ: Xuất bán hàng"
                />

              </div>

              <div className="import-detail-header">

                <h3>
                  Danh sách hàng hóa
                </h3>

                <button
                  type="button"
                  className="secondary-button"
                  onClick={addItem}
                >
                  + Thêm dòng
                </button>

              </div>

              <div className="import-items">

                {form.chi_tiet.map(
                  (item, index) => (
                    <div
                      className="import-item export-item"
                      key={index}
                    >

                      <div className="form-group">

                        <label>
                          Hàng hóa
                        </label>

                        <select
                          value={
                            item.ma_hang
                          }
                          onChange={(e) =>
                            handleItemChange(
                              index,
                              "ma_hang",
                              e.target.value
                            )
                          }
                          required
                        >

                          <option value="">
                            -- Chọn hàng --
                          </option>

                          {hangHoa.map(
                            (hang) => (
                              <option
                                key={hang.id}
                                value={hang.id}
                              >
                                {hang.ten_hang}
                              </option>
                            )
                          )}

                        </select>

                      </div>

                      <div className="form-group">

                        <label>
                          Số lượng
                        </label>

                        <input
                          type="number"
                          min="1"
                          value={
                            item.so_luong
                          }
                          onChange={(e) =>
                            handleItemChange(
                              index,
                              "so_luong",
                              e.target.value
                            )
                          }
                          required
                        />

                      </div>

                      <div className="export-stock">

                        <span>
                          Tồn tối thiểu
                        </span>

                        <strong>
                          {item.ma_hang
                            ? getTonToiThieu(
                                Number(
                                  item.ma_hang
                                )
                              )
                            : "—"}
                        </strong>

                      </div>

                      <div className="export-quantity">

                        <span>
                          Số lượng
                        </span>

                        <strong>
                          {item.so_luong}
                        </strong>

                      </div>

                      <button
                        type="button"
                        className="remove-line-button"
                        onClick={() =>
                          removeItem(index)
                        }
                      >
                        ×
                      </button>

                    </div>
                  )
                )}

              </div>

              <div className="import-total">

                <span>
                  Tổng số lượng
                </span>

                <strong>
                  {tongSoLuong}
                </strong>

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
                  Tạo phiếu xuất
                </button>

              </div>

            </form>

          </div>

        </div>
      )}

      {/* =================================================
          MODAL CHI TIẾT
      ================================================= */}

      {showDetail &&
        selectedPhieu && (
        <div className="modal-overlay">

          <div className="modal modal-large">

            <div className="modal-header">

              <div>
                <h2>
                  Phiếu xuất #{selectedPhieu.id}
                </h2>

                <p className="modal-subtitle">
                  {selectedPhieu.ngay_xuat}
                </p>
              </div>

              <button
                className="close-button"
                onClick={() =>
                  setShowDetail(false)
                }
              >
                ×
              </button>

            </div>

            <div className="detail-info">

              <div>
                <span>
                  Người thực hiện
                </span>

                <strong>
                  {selectedPhieu.ma_tai_khoan}
                </strong>
              </div>

              <div>
                <span>
                  Lý do
                </span>

                <strong>
                  {selectedPhieu.ly_do || "—"}
                </strong>
              </div>

            </div>

            <div className="table-card detail-table">

              <table>

                <thead>
                  <tr>
                    <th>Hàng hóa</th>
                    <th>Số lượng</th>
                  </tr>
                </thead>

                <tbody>

                  {selectedPhieu.chi_tiet.map(
                    (item) => (
                      <tr key={item.id}>

                        <td>
                          {getHangName(
                            item.ma_hang
                          )}
                        </td>

                        <td>
                          {item.so_luong}
                        </td>

                      </tr>
                    )
                  )}

                </tbody>

              </table>

            </div>

          </div>

        </div>
      )}

    </div>
  );
}

export default PhieuXuat;