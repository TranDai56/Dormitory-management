# HỆ THỐNG QUẢN LÝ KÝ TÚC XÁ SINH VIÊN

Dự án Bài tập lớn Cơ sở Dữ liệu - **Project 2: Quản lý Ký Túc Xá Sinh Viên**.
Được xây dựng dựa trên **sơ đồ EER chuẩn hóa**, cơ sở dữ liệu **MySQL**, backend **Python / Django 5.2**, và giao diện người dùng **Bootstrap 5.3 + Font Awesome + Chart.js**.


## 🚀 Hướng Dẫn Khởi 
### 1. Liên kết với MySQL của bạn
### 2. Kích hoạt Virtual Environment
### 3. Khởi chạy Django Server
## Cấu Trúc Thư Mục Dự Án

```
QL_KTX
│
├── CSDL_QL_KTX.sql           # File SQL tạo bảng, dữ liệu mẫu 
├── README.md               
├── config/                   # Thư mục gốc dự án Django
│   ├── manage.py
│   ├── config/               # Settings, URLs, Views chung, Services nghiệp vụ
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── views.py          # Dashboard, Báo cáo (4 truy vấn), In hóa đơn, Tra cứu
│   │   └── services.py       # Logic tính toán chi phí, doanh thu, kiểm tra ràng buộc
│   │
│   ├── templates/            # Giao diện HTML chuẩn hóa Bootstrap 5
│   │   ├── base.html         # Layout khung (Sidebar, Navbar, Flash messages, CDN)
│   │   ├── dashboard.html    # Trang chủ Dashboard KPIs & Biểu đồ Chart.js
│   │   ├── bao_cao/          # Báo cáo 4 Truy vấn & In hóa đơn
│   │   └── tra_cuu/          # Cổng tra cứu nhanh cho sinh viên
│   │
│   ├── sinh_vien/            # App Quản lý sinh viên (Models, Views, URLs, Templates)
│   ├── phong_o/              # App Quản lý phòng ở & Xếp phòng (kiểm tra sức chứa)
│   ├── dich_vu/              # App Quản lý danh mục dịch vụ
│   ├── chi_phi/              # App Quản lý sử dụng dịch vụ của sinh viên
│   ├── gui_xe/               # App Quản lý xe vé tháng (tối đa 2 xe) & Lượt gửi xe (phí lượt 3+)
│   └── khach_tham/           # App Quản lý khách thăm & Ghi nhận lượt thăm
│
└── venv/                     # Python 3.15 Virtual Environment đã cài sẵn Django & mysqlclient
```
