CREATE DATABASE IF NOT EXISTS quan_ly_kho
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE quan_ly_kho;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL,
    INDEX idx_users_role (role)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS nhom_hang (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ten_nhom VARCHAR(100) NOT NULL UNIQUE,
    mo_ta VARCHAR(255) NULL,
    INDEX idx_nhom_hang_ten (ten_nhom)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS hang_hoa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ma_nhom INT NOT NULL,
    ten_hang VARCHAR(150) NOT NULL,
    don_vi_tinh VARCHAR(50) NOT NULL,
    ma_barcode VARCHAR(100) NULL UNIQUE,
    gia_nhap INT NOT NULL DEFAULT 0,
    gia_ban INT NOT NULL DEFAULT 0,
    ton_toi_thieu INT NOT NULL DEFAULT 0,
    INDEX idx_hang_hoa_nhom (ma_nhom),
    INDEX idx_hang_hoa_ten (ten_hang),
    CONSTRAINT fk_hang_hoa_nhom FOREIGN KEY (ma_nhom) REFERENCES nhom_hang(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS nha_cung_cap (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ten_ncc VARCHAR(150) NOT NULL,
    so_dien_thoai VARCHAR(20) NULL,
    email VARCHAR(100) NULL,
    dia_chi VARCHAR(255) NULL,
    INDEX idx_ncc_ten (ten_ncc)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS phieu_nhap (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ma_ncc INT NOT NULL,
    ma_tai_khoan INT NOT NULL,
    ngay_nhap VARCHAR(30) NOT NULL,
    tong_tien INT NOT NULL DEFAULT 0,
    trang_thai VARCHAR(30) NOT NULL DEFAULT 'Nhap',
    INDEX idx_phieu_nhap_ncc (ma_ncc),
    INDEX idx_phieu_nhap_user (ma_tai_khoan),
    CONSTRAINT fk_phieu_nhap_ncc FOREIGN KEY (ma_ncc) REFERENCES nha_cung_cap(id),
    CONSTRAINT fk_phieu_nhap_user FOREIGN KEY (ma_tai_khoan) REFERENCES users(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS chi_tiet_phieu_nhap (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ma_phieu_nhap INT NOT NULL,
    ma_hang INT NOT NULL,
    so_luong INT NOT NULL,
    don_gia INT NOT NULL,
    thanh_tien INT NOT NULL,
    INDEX idx_ctpn_phieu (ma_phieu_nhap),
    INDEX idx_ctpn_hang (ma_hang),
    CONSTRAINT fk_ctpn_phieu FOREIGN KEY (ma_phieu_nhap) REFERENCES phieu_nhap(id),
    CONSTRAINT fk_ctpn_hang FOREIGN KEY (ma_hang) REFERENCES hang_hoa(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ton_kho (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ma_hang INT NOT NULL UNIQUE,
    so_luong INT NOT NULL DEFAULT 0,
    ngay_cap_nhat VARCHAR(30) NOT NULL,
    CONSTRAINT fk_ton_kho_hang FOREIGN KEY (ma_hang) REFERENCES hang_hoa(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS lich_su_kho (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ma_hang INT NOT NULL,
    ma_tai_khoan INT NOT NULL,
    loai_giao_dich VARCHAR(30) NOT NULL,
    so_luong INT NOT NULL,
    thoi_gian VARCHAR(30) NOT NULL,
    ghi_chu VARCHAR(255) NULL,
    INDEX idx_lsk_hang (ma_hang),
    INDEX idx_lsk_user (ma_tai_khoan),
    CONSTRAINT fk_lsk_hang FOREIGN KEY (ma_hang) REFERENCES hang_hoa(id),
    CONSTRAINT fk_lsk_user FOREIGN KEY (ma_tai_khoan) REFERENCES users(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS phieu_xuat (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ma_tai_khoan INT NOT NULL,
    ngay_xuat VARCHAR(30) NOT NULL,
    ly_do VARCHAR(255) NULL,
    trang_thai VARCHAR(30) NOT NULL DEFAULT 'Nhap',
    INDEX idx_phieu_xuat_user (ma_tai_khoan),
    CONSTRAINT fk_phieu_xuat_user FOREIGN KEY (ma_tai_khoan) REFERENCES users(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS chi_tiet_phieu_xuat (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ma_phieu_xuat INT NOT NULL,
    ma_hang INT NOT NULL,
    so_luong INT NOT NULL,
    INDEX idx_ctpx_phieu (ma_phieu_xuat),
    INDEX idx_ctpx_hang (ma_hang),
    CONSTRAINT fk_ctpx_phieu FOREIGN KEY (ma_phieu_xuat) REFERENCES phieu_xuat(id),
    CONSTRAINT fk_ctpx_hang FOREIGN KEY (ma_hang) REFERENCES hang_hoa(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS de_xuat_ai (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ma_tai_khoan INT NOT NULL,
    ngay_tao VARCHAR(30) NOT NULL,
    noi_dung TEXT NULL,
    trang_thai VARCHAR(30) NOT NULL DEFAULT 'ChoDuyet',
    ly_do VARCHAR(1000) NULL,
    INDEX idx_de_xuat_user (ma_tai_khoan),
    CONSTRAINT fk_de_xuat_user FOREIGN KEY (ma_tai_khoan) REFERENCES users(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS chi_tiet_de_xuat_ai (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ma_de_xuat INT NOT NULL,
    ma_hang INT NOT NULL,
    so_luong_de_xuat INT NOT NULL,
    ly_do VARCHAR(500) NULL,
    INDEX idx_ctdx_de_xuat (ma_de_xuat),
    INDEX idx_ctdx_hang (ma_hang),
    CONSTRAINT fk_ctdx_de_xuat FOREIGN KEY (ma_de_xuat) REFERENCES de_xuat_ai(id),
    CONSTRAINT fk_ctdx_hang FOREIGN KEY (ma_hang) REFERENCES hang_hoa(id)
) ENGINE=InnoDB;
