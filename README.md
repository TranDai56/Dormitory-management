# HỆ THỐNG QUẢN LÝ KÝ TÚC XÁ SINH VIÊN (QL_KTX)

Dự án Bài tập lớn Cơ sở Dữ liệu - **Quản lý Ký Túc Xá Sinh Viên**.
Được xây dựng trên cơ sở dữ liệu **MySQL**, backend **Python / Django**, và giao diện người dùng **Bootstrap 5.3 + Font Awesome + Chart.js**.

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Chạy

### 1. Chuẩn bị Cơ sở Dữ liệu MySQL
- Mở MySQL (MySQL Workbench, Navicat, phpMyAdmin hoặc CLI) và import toàn bộ file `CSDL_QL_KTX.sql`.
- Mở file `config/settings.py` (dòng 60-69) để điều chỉnh `USER` và `PASSWORD` cho phù hợp với MySQL của máy bạn nếu cần.

### 2. Kích hoạt Virtual Environment & Cài thư viện
Mở Terminal / PowerShell tại thư mục gốc `QL_KTX`:
```powershell
# Kích hoạt venv
.\venv\Scripts\Activate.ps1

# (Nếu dùng máy khác chưa có thư viện thì cài đặt)
pip install -r requirements.txt
```

### 3. Khởi chạy Django Server
```powershell
python manage.py runserver
```
Truy cập hệ thống tại: **http://127.0.0.1:8000/**

---

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
