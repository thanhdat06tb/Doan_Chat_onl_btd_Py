import eventlet
eventlet.monkey_patch()

import json
import sqlite3
import threading
import socket
import time
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

# ──────────────── Cấu hình ────────────────
TEN_DB = "chat.db"
GIOI_HAN_LICH_SU = 50
PHONG_MAC_DINH = "Chung"
PORT_TCP = 5555

app = Flask(__name__)
app.config["SECRET_KEY"] = "chat-onl-secret-key"
socketio = SocketIO(app, cors_allowed_origins="*")

# Lưu danh sách người dùng SocketIO: {sid: nickname}
nguoi_dung_online: dict[str, str] = {}
# Lưu danh sách client TCP: {socket: nickname}
tcp_clients: dict[socket.socket, str] = {}


# ──────────────── Database ────────────────
def _tao_db() -> None:
    with sqlite3.connect(TEN_DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts REAL NOT NULL,
                type TEXT NOT NULL,
                nickname TEXT NOT NULL,
                text TEXT NOT NULL,
                room TEXT NOT NULL
            )
        """)


def _luu_tin(thong_diep: dict) -> None:
    with sqlite3.connect(TEN_DB) as conn:
        conn.execute(
            "INSERT INTO messages (ts, type, nickname, text, room) VALUES (?, ?, ?, ?, ?)",
            (
                thong_diep.get("ts", time.time()),
                thong_diep.get("type", "chat"),
                thong_diep.get("nickname", ""),
                thong_diep.get("text", ""),
                PHONG_MAC_DINH,
            ),
        )


def _lay_lich_su() -> list[dict]:
    with sqlite3.connect(TEN_DB) as conn:
        rows = conn.execute(
            """
            SELECT ts, type, nickname, text
            FROM messages
            WHERE room = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (PHONG_MAC_DINH, GIOI_HAN_LICH_SU),
        ).fetchall()
    rows.reverse()
    return [
        {"ts": r[0], "type": r[1], "nickname": r[2], "text": r[3]}
        for r in rows
    ]


# ──────────────── Logic Chung ────────────────
def phat_tin_nhan(thong_diep: dict, loai_phat="ca_hai"):
    """Phát tin nhắn tới cả SocketIO và TCP Client"""
    if loai_phat in ("ca_hai", "sio"):
        socketio.emit("tin_nhan", thong_diep)
    
    if loai_phat in ("ca_hai", "tcp"):
        du_lieu = (json.dumps(thong_diep, ensure_ascii=False) + "\n").encode("utf-8")
        for client_sock in list(tcp_clients.keys()):
            try:
                client_sock.sendall(du_lieu)
            except Exception:
                tcp_clients.pop(client_sock, None)


def phat_trang_thai_online():
    sl = len(nguoi_dung_online) + len(tcp_clients)
    socketio.emit("cap_nhat_online", sl)
    # TCP client hiện tại không xử lý cap_nhat_online trong code ui_client.py


# ──────────────── Routes ────────────────
@app.route("/")
def trang_chu():
    return render_template("index.html")


# ──────────────── SocketIO Events ────────────────
@socketio.on("connect")
def xu_ly_ket_noi():
    print(f"Client SIO connected: {request.sid}")


@socketio.on("disconnect")
def xu_ly_ngat_ket_noi():
    sid = request.sid
    biet_danh = nguoi_dung_online.pop(sid, None)
    if biet_danh:
        thong_bao = {
            "type": "system",
            "nickname": "Hệ thống",
            "text": f"{biet_danh} đã rời phòng (Web).",
            "ts": time.time(),
        }
        _luu_tin(thong_bao)
        phat_tin_nhan(thong_bao)
        phat_trang_thai_online()
    print(f"Client SIO disconnected: {sid}")


@socketio.on("tham_gia")
def xu_ly_tham_gia(du_lieu):
    biet_danh = (du_lieu.get("nickname") or "Anonymous").strip() or "Anonymous"
    nguoi_dung_online[request.sid] = biet_danh
    print(f"SIO: {biet_danh} joined")

    emit("lich_su", _lay_lich_su())

    thong_bao = {
        "type": "system",
        "nickname": "Hệ thống",
        "text": f"{biet_danh} đã tham gia (Web)!",
        "ts": time.time(),
    }
    _luu_tin(thong_bao)
    phat_tin_nhan(thong_bao)
    phat_trang_thai_online()


@socketio.on("gui_tin")
def xu_ly_gui_tin(du_lieu):
    sid = request.sid
    biet_danh = nguoi_dung_online.get(sid, "Anonymous")
    text = (du_lieu.get("text") or "").strip()
    if not text: return

    thong_diep = {
        "type": "chat",
        "nickname": biet_danh,
        "text": text,
        "ts": time.time(),
    }
    _luu_tin(thong_diep)
    phat_tin_nhan(thong_diep)


# ──────────────── TCP Socket Server ────────────────
def tcp_worker():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_sock.bind(("0.0.0.0", PORT_TCP))
        server_sock.listen(5)
        print(f"TCP Bridge đang chạy tại port {PORT_TCP}")
    except Exception as e:
        print(f"Lỗi khởi động TCP Bridge: {e}")
        return

    while True:
        client_sock, addr = server_sock.accept()
        threading.Thread(target=xu_ly_client_tcp, args=(client_sock,), daemon=True).start()


def xu_ly_client_tcp(sock: socket.socket):
    try:
        buffer = ""
        while True:
            data = sock.recv(1024)
            if not data: break
            buffer += data.decode("utf-8", errors="replace")
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip(): continue
                try:
                    goi = json.loads(line)
                    kieu = goi.get("type")
                    if kieu == "hello":
                        biet_danh = (goi.get("nickname") or "Anonymous").strip()
                        tcp_clients[sock] = biet_danh
                        print(f"TCP: {biet_danh} joined")
                        
                        # Gửi lịch sử
                        lich_su = _lay_lich_su()
                        sock.sendall((json.dumps({"type": "welcome", "history": lich_su}, ensure_ascii=False) + "\n").encode("utf-8"))
                        
                        thong_bao = {
                            "type": "system", "nickname": "Hệ thống",
                            "text": f"{biet_danh} đã tham gia (Desktop)!", "ts": time.time()
                        }
                        _luu_tin(thong_bao)
                        phat_tin_nhan(thong_bao)
                        phat_trang_thai_online()
                        
                    elif kieu == "chat":
                        biet_danh = tcp_clients.get(sock, "Anonymous")
                        thong_diep = {
                            "type": "chat", "nickname": biet_danh,
                            "text": goi.get("text", ""), "ts": time.time()
                        }
                        _luu_tin(thong_diep)
                        phat_tin_nhan(thong_diep)
                except Exception as e:
                    print(f"Lỗi xử lý gói TCP: {e}")
    except Exception:
        pass
    finally:
        biet_danh = tcp_clients.pop(sock, None)
        if biet_danh:
            thong_bao = {
                "type": "system", "nickname": "Hệ thống",
                "text": f"{biet_danh} đã rời phòng (Desktop).", "ts": time.time()
            }
            _luu_tin(thong_bao)
            phat_tin_nhan(thong_bao)
            phat_trang_thai_online()
        sock.close()


# ──────────────── Khởi chạy ────────────────
if __name__ == "__main__":
    _tao_db()
    # Chạy TCP bridge trong background task (tối ưu cho SocketIO)
    socketio.start_background_task(tcp_worker)
    
    print("\n" + "="*40)
    print("SERVER ĐANG CHẠY")
    print(f"- Web Chat: http://localhost:5000")
    print(f"- Desktop Chat: Port {PORT_TCP}")
    print("="*40 + "\n")
    
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
