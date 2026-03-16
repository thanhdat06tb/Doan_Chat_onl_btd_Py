import json
import socket
import sqlite3
import threading
import time

DIA_CHI_MAY = "127.0.0.1"
CONG = 5555
TEN_DB = "chat.db"
GIOI_HAN_LICH_SU = 50
PHONG_MAC_DINH = "Chung"

may_chu = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
may_chu.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
may_chu.bind((DIA_CHI_MAY, CONG))
may_chu.listen()

print(f"Server running on {DIA_CHI_MAY}:{CONG}")

khach_ket_noi: list[socket.socket] = []
khach_lock = threading.Lock()
db_lock = threading.Lock()


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
        cols = {row[1] for row in conn.execute("PRAGMA table_info(messages)")}
        if "room" not in cols:
            conn.execute(
                "ALTER TABLE messages ADD COLUMN room TEXT NOT NULL DEFAULT 'Chung'"
            )


def _luu_tin(thong_diep: dict) -> None:
    with db_lock:
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
    with db_lock:
        with sqlite3.connect(TEN_DB) as conn:
            rows = conn.execute(
                """
                SELECT ts, type, nickname, text, room
                FROM messages
                WHERE room = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (PHONG_MAC_DINH, GIOI_HAN_LICH_SU),
            ).fetchall()
    rows.reverse()
    return [
        {
            "type": row[1],
            "nickname": row[2],
            "text": row[3],
            "ts": row[0],
            "room": row[4],
        }
        for row in rows
    ]


def _gui_json(khach: socket.socket, du_lieu: dict) -> None:
    du_lieu = dict(du_lieu)
    du_lieu.setdefault("ts", time.time())
    payload = (json.dumps(du_lieu, ensure_ascii=False) + "\n").encode("utf-8")
    khach.sendall(payload)


def phat_tin(du_lieu: dict) -> None:
    payload = (json.dumps(du_lieu, ensure_ascii=False) + "\n").encode("utf-8")
    with khach_lock:
        danh_sach = list(khach_ket_noi)
    for khach in danh_sach:
        try:
            khach.sendall(payload)
        except Exception:
            pass


def _phat_he_thong(text: str) -> None:
    du_lieu = {
        "type": "system",
        "nickname": "Hệ thống",
        "text": text,
        "ts": time.time(),
        "room": PHONG_MAC_DINH,
    }
    _luu_tin(du_lieu)
    phat_tin(du_lieu)


def _doc_dong(khach: socket.socket):
    bo_dem = ""
    while True:
        du_lieu = khach.recv(4096)
        if not du_lieu:
            break
        bo_dem += du_lieu.decode("utf-8", errors="replace")
        while "\n" in bo_dem:
            dong, bo_dem = bo_dem.split("\n", 1)
            dong = dong.strip()
            if dong:
                yield dong
    if bo_dem.strip():
        yield bo_dem.strip()


def xu_ly_khach(khach: socket.socket, biet_danh: str) -> None:
    try:
        for dong in _doc_dong(khach):
            try:
                goi = json.loads(dong)
            except json.JSONDecodeError:
                continue
            if goi.get("type") != "chat":
                continue
            text = (goi.get("text") or "").strip()
            if not text:
                continue
            thong_diep = {
                "type": "chat",
                "nickname": biet_danh,
                "text": text,
                "ts": time.time(),
                "room": PHONG_MAC_DINH,
            }
            _luu_tin(thong_diep)
            phat_tin(thong_diep)
    except Exception:
        pass
    finally:
        with khach_lock:
            try:
                khach_ket_noi.remove(khach)
            except ValueError:
                pass
        try:
            khach.close()
        except Exception:
            pass
        _phat_he_thong(f"{biet_danh} đã rời khỏi phòng chat.")


def nhan_ket_noi() -> None:
    _tao_db()
    while True:
        khach, dia_chi = may_chu.accept()
        print(f"Client connected: {dia_chi}")

        try:
            dong = next(_doc_dong(khach))
            goi = json.loads(dong)
        except Exception:
            try:
                khach.close()
            except Exception:
                pass
            continue

        if goi.get("type") != "hello":
            try:
                khach.close()
            except Exception:
                pass
            continue

        biet_danh = (goi.get("nickname") or "Anonymous").strip() or "Anonymous"

        with khach_lock:
            khach_ket_noi.append(khach)

        print(f"Nickname: {biet_danh}")

        lich_su = _lay_lich_su()
        _gui_json(
            khach, {"type": "welcome", "history": lich_su, "room": PHONG_MAC_DINH}
        )
        _phat_he_thong(f"{biet_danh} đã tham gia phòng chat!")

        luong = threading.Thread(
            target=xu_ly_khach, args=(khach, biet_danh), daemon=True
        )
        luong.start()


nhan_ket_noi()
