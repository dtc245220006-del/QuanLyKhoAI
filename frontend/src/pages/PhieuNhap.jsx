import { useEffect, useMemo, useState } from "react";
import api from "../api";

function PhieuNhap() {
  const [phieuNhap, setPhieuNhap] = useState([]);
  const [nhaCungCap, setNhaCungCap] = useState([]);
  const [hangHoa, setHangHoa] = useState([]);

  const [showForm, setShowForm] = useState(false);
  const [showDetail, setShowDetail] = useState(false);

  const [selectedPhieu, setSelectedPhieu] = useState(null);

  const [form, setForm] = useState({
    ma_ncc: "",
    chi_tiet: [
      {
        ma_hang: "",
        so_luong: 1,
        don_gia: 0,
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
      const [
        phieuRes,
        nccRes,
        hangRes,
      ] = await Promise.all([
        api.get("/phieu-nhap"),
        api.get("/nha-cung-cap"),
        api.get("/hang-hoa"),
      ]);

      setPhieuNhap(phieuRes.data);
      setNhaCungCap(nccRes.data);
      setHangHoa(hangRes.data);

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Không thể tải dữ liệu phiếu nhập"
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
      ma_ncc: "",
      chi_tiet: [
        {
          ma_hang: "",
          so_luong: 1,
          don_gia: 0,
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

  const handleNccChange = (e) => {
    setForm({
      ...form,
      ma_ncc: e.target.value,
    });
  };

  const handleItemChange = (index, field, value) => {
    const newItems = [...form.chi_tiet];

    newItems[index] = {
      ...newItems[index],
      [field]: value,
    };

    // Khi chọn hàng hóa, tự lấy giá nhập
    if (field === "ma_hang") {
      const selected = hangHoa.find(
        (item) => item.id === Number(value)
      );

      if (selected) {
        newItems[index].don_gia =
          selected.gia_nhap || 0;
      }
    }

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
          don_gia: 0,
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

  // =====================================================
  // TỔNG TIỀN
  // =====================================================

  const tongTien = useMemo(() => {
    return form.chi_tiet.reduce(
      (total, item) => {
        return (
          total +
          Number(item.so_luong || 0) *
            Number(item.don_gia || 0)
        );
      },
      0
    );
  }, [form.chi_tiet]);

  const formatMoney = (value) => {
    return Number(value || 0).toLocaleString("vi-VN");
  };

  const getNccName = (id) => {
    const item = nhaCungCap.find(
      (x) => x.id === id
    );

    return item?.ten_ncc || "—";
  };

  const getHangName = (id) => {
    const item = hangHoa.find(
      (x) => x.id === id
    );

    return item?.ten_hang || "—";
  };

  // =====================================================
  // TẠO PHIẾU
  // =====================================================

  const handleCreate = async (e) => {
    e.preventDefault();

    setMessage("");
    setError("");

    if (!form.ma_ncc) {
      setError(
        "Vui lòng chọn nhà cung cấp"
      );
      return;
    }

    const validItems = form.chi_tiet.filter(
      (item) => item.ma_hang
    );

    if (validItems.length === 0) {
      setError(
        "Phiếu nhập phải có ít nhất một mặt hàng"
      );
      return;
    }

    const data = {
      ma_ncc: Number(form.ma_ncc),

      ma_tai_khoan: Number(
        currentUser.id
      ),

      chi_tiet: validItems.map((item) => ({
        ma_hang: Number(item.ma_hang),
        so_luong: Number(item.so_luong),
        don_gia: Number(item.don_gia),
      })),
    };

    try {
      await api.post(
        "/phieu-nhap",
        data
      );

      setMessage(
        "Tạo phiếu nhập thành công"
      );

      setShowForm(false);

      resetForm();

      loadData();

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Không thể tạo phiếu nhập"
      );
    }
  };

  // =====================================================
  // XÁC NHẬN
  // =====================================================

  const handleConfirm = async (id) => {
    const ok = window.confirm(
      "Xác nhận phiếu nhập này? Sau khi xác nhận, tồn kho sẽ được cập nhật."
    );

    if (!ok) return;

    try {
      await api.put(
        `/phieu-nhap/${id}/xac-nhan`
      );

      setMessage(
        "Xác nhận phiếu nhập thành công"
      );

      loadData();

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Không thể xác nhận phiếu nhập"
      );
    }
  };

  // =====================================================
  // XÓA
  // =====================================================

  const handleDelete = async (id) => {
    const ok = window.confirm(
      "Bạn có chắc muốn xóa phiếu nhập này?"
    );

    if (!ok) return;

    try {
      await api.delete(
        `/phieu-nhap/${id}`
      );

      setMessage(
        "Xóa phiếu nhập thành công"
      );

      loadData();

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Không thể xóa phiếu nhập"
      );
    }
  };

  // =====================================================
  // XEM CHI TIẾT
  // =====================================================

  const handleViewDetail = async (id) => {
    try {
      const response = await api.get(
        `/phieu-nhap/${id}`
      );

      setSelectedPhieu(
        response.data
      );

      setShowDetail(true);

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Không thể lấy chi tiết phiếu nhập"
      );
    }
  };

  // =====================================================
  // UI
  // =====================================================

  return (
    <div>

      {/* HEADER */}

      <div className="page-header">

        <div>
          <h1>Phiếu nhập</h1>

          <p>
            Quản lý các phiếu nhập kho
          </p>
        </div>

        <button
          className="primary-button"
          onClick={openCreate}
        >
          + Tạo phiếu nhập
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
              <th>Nhà cung cấp</th>
              <th>Ngày nhập</th>
              <th>Tổng tiền</th>
              <th>Trạng thái</th>
              <th>Thao tác</th>
            </tr>
          </thead>

          <tbody>

            {phieuNhap.length === 0 ? (
              <tr>
                <td
                  colSpan="6"
                  className="empty-cell"
                >
                  Chưa có phiếu nhập
                </td>
              </tr>
            ) : (
              phieuNhap.map((phieu) => (

                <tr key={phieu.id}>

                  <td>
                    <strong>
                      #{phieu.id}
                    </strong>
                  </td>

                  <td>
                    {getNccName(
                      phieu.ma_ncc
                    )}
                  </td>

                  <td>
                    {phieu.ngay_nhap}
                  </td>

                  <td>
                    {formatMoney(
                      phieu.tong_tien
                    )} ₫
                  </td>

                  <td>

                    <span
                      className={`status-badge ${
                        phieu.trang_thai ===
                        "DaNhap"
                          ? "status-success"
                          : "status-pending"
                      }`}
                    >
                      {phieu.trang_thai ===
                      "DaNhap"
                        ? "Đã nhập"
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
                Tạo phiếu nhập
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

              {/* NHÀ CUNG CẤP */}

              <div className="form-group">

                <label>
                  Nhà cung cấp
                </label>

                <select
                  value={form.ma_ncc}
                  onChange={
                    handleNccChange
                  }
                  required
                >

                  <option value="">
                    -- Chọn nhà cung cấp --
                  </option>

                  {nhaCungCap.map((item) => (

                    <option
                      key={item.id}
                      value={item.id}
                    >
                      {item.ten_ncc}
                    </option>

                  ))}

                </select>

              </div>

              {/* CHI TIẾT */}

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
                      className="import-item"
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


                      <div className="form-group">

                        <label>
                          Đơn giá
                        </label>

                        <input
                          type="number"
                          min="0"
                          value={
                            item.don_gia
                          }
                          onChange={(e) =>
                            handleItemChange(
                              index,
                              "don_gia",
                              e.target.value
                            )
                          }
                          required
                        />

                      </div>


                      <div className="import-line-total">

                        <span>
                          Thành tiền
                        </span>

                        <strong>
                          {formatMoney(
                            Number(
                              item.so_luong || 0
                            ) *
                              Number(
                                item.don_gia || 0
                              )
                          )} ₫
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

              {/* TỔNG */}

              <div className="import-total">

                <span>
                  Tổng tiền
                </span>

                <strong>
                  {formatMoney(tongTien)} ₫
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
                  Tạo phiếu nhập
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
                  Phiếu nhập #{selectedPhieu.id}
                </h2>

                <p className="modal-subtitle">
                  {selectedPhieu.ngay_nhap}
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
                  Nhà cung cấp
                </span>

                <strong>
                  {getNccName(
                    selectedPhieu.ma_ncc
                  )}
                </strong>
              </div>

              <div>
                <span>
                  Trạng thái
                </span>

                <strong>
                  {selectedPhieu.trang_thai ===
                  "DaNhap"
                    ? "Đã nhập"
                    : "Nháp"}
                </strong>
              </div>

            </div>

            <div className="table-card detail-table">

              <table>

                <thead>
                  <tr>
                    <th>Hàng hóa</th>
                    <th>Số lượng</th>
                    <th>Đơn giá</th>
                    <th>Thành tiền</th>
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

                        <td>
                          {formatMoney(
                            item.don_gia
                          )} ₫
                        </td>

                        <td>
                          {formatMoney(
                            item.thanh_tien
                          )} ₫
                        </td>

                      </tr>

                    )
                  )}

                </tbody>

              </table>

            </div>

            <div className="import-total">

              <span>
                Tổng tiền
              </span>

              <strong>
                {formatMoney(
                  selectedPhieu.tong_tien
                )} ₫
              </strong>

            </div>

          </div>

        </div>
      )}

    </div>
  );
}

export default PhieuNhap;