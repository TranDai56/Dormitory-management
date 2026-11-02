# HỆ THỐNG QUẢN LÝ KÝ TÚC XÁ SINH VIÊN (QL_KTX)

Dự án Bài tập lớn Cơ sở Dữ liệu - **Quản lý Ký Túc Xá Sinh Viên**.
Được xây dựng trên cơ sở dữ liệu **MySQL**, backend **Python / Django**, và giao diện người dùng **Bootstrap 5.3 + Font Awesome + Chart.js**.

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Chạy

### 1. Chuẩn bị Cơ sở Dữ liệu MySQL
### 2. Kích hoạt Virtual Environment & Cài thư viện
### 3. Khởi chạy Django Server

## 📁 Cấu Trúc Thư Mục Dự Án

```
QL_KTX/
│
├── chi_phi/                  # Quản lý sử dụng dịch vụ của sinh viên
├── config/                   # Cấu hình dự án Django (settings, urls, views chung, services)
├── dich_vu/                  # Quản lý danh mục dịch vụ KTX
├── gui_xe/                   # Quản lý xe vé tháng & lượt ra/vào bãi
├── khach_tham/               # Quản lý khách thăm sinh viên
├── phong_o/                  # Quản lý phòng ở & xếp phòng (sức chứa)
├── sinh_vien/                # Quản lý hồ sơ sinh viên nội trú
├── static/                   # Static files (CSS, JS, hình ảnh)
├── templates/                # Giao diện tổng thể (Dashboard, Báo cáo, Tra cứu, In hóa đơn)
├── venv/                     # Môi trường ảo Python
├── manage.py                 # File thực thi lệnh Django
├── CSDL_QL_KTX.sql           # File SQL tạo bảng và nạp dữ liệu mẫu
├── README.md                 # Tài liệu hướng dẫn dự án
├── requirements.txt          # Danh sách thư viện cần thiết
└── .gitignore                # Cấu hình bỏ qua file rác của Git
```
