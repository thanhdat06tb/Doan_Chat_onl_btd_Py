# 💬 Chat Server Application (Python)

## 📌 Giới thiệu

Đây là dự án xây dựng **hệ thống Chat Server thời gian thực** sử dụng ngôn ngữ **Python**.
Hệ thống được thiết kế theo mô hình **Client – Server** cho phép nhiều người dùng kết nối và gửi tin nhắn cùng lúc.

Dự án được thực hiện nhằm mục đích:

* Nghiên cứu **Socket Programming**
* Hiểu cơ chế **TCP/IP**
* Áp dụng **Multi-threading**
* Xây dựng **ứng dụng mạng thời gian thực**

---

# 🏗 Kiến trúc hệ thống

Hệ thống sử dụng mô hình:

Client → Server → Client

Mọi tin nhắn từ client sẽ gửi tới **Server**, sau đó server sẽ phân phối lại cho các client khác.

---

# ⚙️ Công nghệ sử dụng

* Python
* Socket Programming
* TCP/IP Protocol
* Threading (Multi-thread)
* Tkinter (GUI)

---

# 📂 Cấu trúc project

```
chat-server-project
│
├── server.py          # Server (Flask + SocketIO + TCP Bridge)
├── client.py          # Entry point chạy giao diện Desktop
├── ui_client.py       # Giao diện Desktop (Tkinter)
├── chat.db            # Database SQLite lưu lịch sử chat
│
├── templates/         # Template HTML cho Web Chat
│   └── index.html
├── img/               # Ảnh demo
│
├── requirements.txt   # Thư viện cần cài đặt
└── README.md
```

---

# 🚀 Cách chạy chương trình

## 0️⃣ Cài đặt thư viện

```bash
pip install -r requirements.txt
```

---

## 1️⃣ Chạy Server

```bash
python server.py
```

Server sẽ khởi động:

* **Web Chat:** `http://localhost:5000`
* **Desktop TCP Bridge:** Port `5555`

---

## 2️⃣ Chạy Client Desktop (Tkinter)

```bash
python client.py
```

Nhập **IP server** (mặc định `127.0.0.1`) và **nickname**, sau đó bấm **Kết nối**.

---

## 3️⃣ 📱 Chạy trên Điện thoại (qua WiFi)

Ứng dụng hỗ trợ truy cập từ điện thoại thông qua trình duyệt web, chỉ cần cùng mạng WiFi.

### Các bước thực hiện:

**Bước 1:** Đảm bảo server đang chạy trên máy tính

```bash
python server.py
```

**Bước 2:** Tìm địa chỉ IP của máy tính

```bash
# Windows
ipconfig

# Tìm dòng "IPv4 Address" của adapter WiFi
# Ví dụ: 192.168.1.100
```

**Bước 3:** Kết nối điện thoại vào **cùng mạng WiFi** với máy tính

**Bước 4:** Mở trình duyệt trên điện thoại và truy cập:

```
http://<IP_máy_tính>:5000
```

Ví dụ: `http://192.168.1.100:5000`

**Bước 5:** Nhập nickname và bắt đầu chat! 🎉

### ⚠️ Lưu ý quan trọng:

* Điện thoại và máy tính phải kết nối **cùng một mạng WiFi**
* Nếu không truy cập được, hãy kiểm tra **Windows Firewall**:
  * Mở **Windows Defender Firewall** → **Advanced Settings**
  * Thêm **Inbound Rule** cho phép kết nối qua **Port 5000** (TCP)
  * Hoặc tạm tắt Firewall để test

---

# 💡 Chức năng hệ thống

* Kết nối nhiều client đồng thời (Web + Desktop)
* Gửi và nhận tin nhắn thời gian thực
* Lưu lịch sử chat vào database SQLite
* 📱 **Hỗ trợ truy cập từ điện thoại** qua trình duyệt (WiFi)
* Giao diện Web hiện đại (Flask + SocketIO)
* Giao diện Desktop (Tkinter + TCP Socket)
* Hiển thị số người online

---

# 🧪 Kiểm thử

| Test Case             | Kết quả          |
| --------------------- | ---------------- |
| Client kết nối Server | Thành công       |
| Gửi tin nhắn          | Thành công       |
| Nhiều client          | Server xử lý tốt |

---

# 📷 Demo

<img width="934" height="1038" alt="image" src="https://github.com/user-attachments/assets/ff6d0fb9-83f3-499b-8a4d-26a8858ce668" />
<img width="1357" height="943" alt="image" src="https://github.com/user-attachments/assets/024eff34-66ef-4879-bbad-b839d4c11704" />



---

# 👨‍💻 Tác giả

Sinh viên: Bùi Thành Đạt
Môn học: Điện toán di động / Lập trình mạng

---

# 📄 License

Project phục vụ mục đích **học tập và nghiên cứu**.

